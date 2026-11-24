#!/usr/bin/env python3
"""One loopback development process: Accounts, signed file grants, Storage and built assets."""
import argparse
import asyncio
import fcntl
import io
import json
import os
from pathlib import Path
import re
import signal
import socket
import stat
import sys
from importlib.util import module_from_spec, spec_from_file_location
import uuid
from urllib.parse import urlsplit
from aiohttp import web
from webos_weather import install as install_weather
from webos_accounts import AccountsService, Config
from webos_accounts.file_authority import FileAuthority
from webos_storage import UserStore, DEFAULT_ACCOUNT_FOLDERS, FileGateway, initialize_ledger, initialize_transfers
from webos_storage.transfers import Quotas


def load_app(name, slug):
    packaged = Path(__file__).resolve().parent / name
    source = Path(__file__).resolve().parents[1] / 'apps' / slug / 'server'
    folder = packaged if packaged.is_dir() else source
    spec = spec_from_file_location(name, folder / '__init__.py', submodule_search_locations=[str(folder)])
    package = module_from_spec(spec)
    sys.modules[name] = package
    spec.loader.exec_module(package)

def monitor_for(origin, accounts):
    value = os.environ.get('WEBOS_REMOTE_DESKTOP_PROFILE')
    if value is None:
        return None, None
    path = Path(value)
    info = path.lstat()
    if not path.is_absolute() or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022:
        raise ValueError('A protected monitor profile file is required')
    profile = json.loads(path.read_text())
    if set(profile) != {'owner', 'command'}:
        raise ValueError('Exact monitor profile required')
    load_app('remote_desktop_backend', 'remote-desktop')
    from remote_desktop_backend.relay import OwnerRelay, PATH
    from remote_desktop_backend.sessions import active_session
    monitor = OwnerRelay(origin, profile['owner'], profile['command'],
                         lambda owner, sid: active_session(accounts, owner, sid))
    return PATH, monitor


def compute_gateway_type(directory, monitor, chat=None, mail=None, management=None):
    render_enabled = bool(os.environ.get('WEBOS_IMAGE_RENDER_COMMAND'))
    monitor_enabled = os.environ.get('WEBOS_GPU_MONITOR') == '1'
    if not (monitor_enabled or render_enabled or monitor or chat or mail or management):
        return FileGateway
    from webos_compute.jobs import Jobs
    from webos_storage.policy import Denied


    if render_enabled:
        load_app('image_studio_backend','image-studio')
        from image_studio_backend.gateway import render_image, validate
    if monitor_enabled:
        load_app('gpu_monitor_backend','gpu-monitor')
        from gpu_monitor_backend.fleet import FleetCache

    class ComputeGateway(FileGateway):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.jobs = Jobs(directory,render_image) if render_enabled else None
            self.fleet = FleetCache(self.queue_counts) if monitor_enabled else None

        def queue_counts(self):
            if self.jobs:
                counts=self.jobs.counts()
                return {**counts,'workers':{'llm-49':{'nvidia:0':counts}}}
            return {'waiting':0,'running':0,'uncertain':0,'workers':{}}

        def _dispatch(self,principal,request):
            resource = request.get('resource')
            if resource == 'account-management' and management is not None:
                from webos_accounts.management import ManagementError
                try:
                    return management.dispatch(principal, request)
                except ManagementError as exc:
                    raise web.HTTPForbidden(text=str(exc)) from None
            if resource == 'mailcraft' and mail is not None:
                return mail.issue(principal, request)
            if resource == 'chat' and chat is not None:
                if request.get('operation') == 'listen':
                    return chat.issue(principal, request)
                return chat.store.dispatch(principal, request)
            if resource == 'remote-desktop' and monitor:
                return monitor.issue(principal, request)
            if resource not in ('gpu-monitor','compute','image-studio'):
                return super()._dispatch(principal,request)
            if principal.kind != 'registered' or not principal.sub:
                raise Denied('Sign in to use compute services')
            op = request.get('operation')
            if resource=='gpu-monitor' and self.fleet and op=='snapshot' and set(request)=={'operation','resource'}:
                return self.fleet.snapshot()
            if resource=='compute' and self.jobs and op=='compute-status' and set(request)=={'operation','resource','job'} and isinstance(request['job'],str):
                return self.jobs.status(principal.sub,request['job'])
            if resource=='image-studio' and self.jobs and op=='image-render':
                payload={k:v for k,v in request.items() if k not in ('operation','resource')}
                validate(payload)
                return self.jobs.submit(principal.sub,payload)
            raise Denied('Compute operation unavailable')

    return ComputeGateway


def validate_origin(value):
    parsed = urlsplit(value)
    if (not parsed.hostname or parsed.username is not None or parsed.password is not None
            or parsed.path or parsed.query or parsed.fragment or parsed.geturl() != value
            or any(char.isspace() for char in value)):
        raise ValueError('Canonical origin without credentials, path or query required')
    try:
        parsed.port
    except ValueError as error:
        raise ValueError('Valid origin port required') from error
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost', '::1')):
        raise ValueError('HTTPS origin required outside loopback')
    return value


def private_directory(path):
    path = Path(path).absolute()
    if '..' in path.parts or any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Direct private directories required')
    info = path.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError('Owned private directory (0700) required')
    return path


async def create_application(public_root, private_root, origin, *, account_transfers=8, shared_transfers=16, agent_operations=False, guest_network_policy=None):
    if type(account_transfers) is not int or not 1 <= account_transfers <= 8 or type(shared_transfers) is not int or not account_transfers <= shared_transfers <= 32:
        raise ValueError('Bounded account/shared transfer limits required')
    origin = validate_origin(origin)
    network = None
    if guest_network_policy is not None:
        from guest_service.viewer import ViewerNetwork
        network = ViewerNetwork.installed(origin, guest_network_policy)
    address = urlsplit(origin)
    if agent_operations and (address.scheme != 'http' or address.hostname not in ('127.0.0.1', 'localhost', '::1')):
        raise ValueError('Development agent operations require a direct loopback origin')
    if agent_operations:
        from webos_accounts.delegation import CHALLENGE as AGENT_CHALLENGE, PATHS as AGENT_PATHS, MAX_TRANSPORT_BYTES, DelegationAuthority
    public_root = Path(public_root).absolute()
    private_root = Path(private_root).absolute()
    source_root = Path(__file__).resolve().parent.parent
    if private_root.is_relative_to(source_root) or source_root.is_relative_to(private_root):
        raise ValueError('Account state must be outside the source checkout')
    if public_root.is_relative_to(private_root) or private_root.is_relative_to(public_root):
        raise ValueError('Public assets and private account state must be disjoint')
    if not (public_root / 'index.html').is_file() or any(p.is_symlink() for p in (public_root, *public_root.parents)):
        raise ValueError('Direct built public asset root with index.html required')
    new = not private_root.exists()
    if new:
        private_root.mkdir(mode=0o700)
    private_directory(private_root)
    lock = os.open(private_root / '.development.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    gateway = None
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        marker = private_root / 'development.json'
        if not new:
            if marker.is_symlink() or not marker.is_file():
                raise ValueError('Unknown or incomplete development state; preserve it for review')
            metadata = json.loads(marker.read_text())
            if metadata.get('schema') != 'webos-development-state/2' or metadata.get('status') != 'ready' or metadata.get('origin') != origin:
                raise ValueError('Unsupported or incomplete development state')
        else:
            metadata = {'schema': 'webos-development-state/2', 'status': 'initializing', 'instanceId': str(uuid.uuid4()), 'origin': origin}
            marker.write_text(json.dumps(metadata) + '\n'); marker.chmod(0o600)
        for name in ('identity', 'storage-state', 'account-files'):
            folder = private_root / name
            if new:
                folder.mkdir(mode=0o700)
            private_directory(folder)
        class DevelopmentAccounts(AccountsService):
            def account(self, data):
                # The registration trigger also protects issuer entry points outside this gateway.
                import sqlite3
                from webos_accounts import Failure
                try:
                    return super().account(data)
                except sqlite3.IntegrityError as exc:
                    if str(exc) == 'reserved WebOS username':
                        raise Failure(400, 'Username unavailable') from None
                    raise

            def config(self):
                value = super().config()
                value['gateway'] = {'version': 'codi-user-files/1', 'basePath': '/gateway', 'fileBytes': 128 * 1024 * 1024,
                                    'concurrentTransfers': account_transfers, 'sharedConcurrentTransfers': shared_transfers}
                if network is not None:
                    network.configure(value)
                if agent_operations:
                    value['agentOperations'] = {'version': 'webos-agent-operations/1'}
                return value
        accounts = DevelopmentAccounts(Config(private_root / 'identity', public_root, origin=origin, rate_per_minute=1000))
        authority = FileAuthority(accounts)
        if agent_operations:
            authority = DelegationAuthority(accounts, authority)
        if network is not None:
            authority = network.authority(accounts, authority)
        store = UserStore(private_root / 'storage-state', private_root / 'account-files', initial_folders=DEFAULT_ACCOUNT_FOLDERS)
        if new:
            # Only explicitly new development state is initialized. Retained
            # state is validated by FileGateway and never silently repaired.
            initialize_ledger(store); initialize_transfers(store)
        quotas = Quotas(store, concurrent_uses=account_transfers, shared_concurrent_uses=shared_transfers)
        monitor_path, monitor = monitor_for(origin, accounts)
        chat = None
        if os.environ.get('WEBOS_REGISTERED_CHAT') == '1':
            load_app('webos_chat_backend', 'webos-chat')
            from webos_chat_backend.chat import ChatStore
            from webos_chat_backend.live import LiveChat, PATH as chat_stream
            chat = LiveChat(ChatStore(private_root / 'chat-state', accounts.db), origin)
        mail = None
        if os.environ.get('WEBOS_MAILCRAFT_SSO') == '1':
            from mailcraft_sso import MailGateway
            from remote_desktop_backend.sessions import active_session
            binding_file = Path(os.environ['CREDENTIALS_DIRECTORY']) / 'mailcraft-bindings'
            mail = MailGateway(origin, binding_file, lambda subject, sid: active_session(accounts, subject, sid))
        management = None
        if os.environ.get('WEBOS_ACCOUNT_MANAGEMENT') == '1':
            from webos_accounts.management import AccountManagement
            management = AccountManagement(accounts, chat.store if chat else None)
        gateway_type = compute_gateway_type(private_root, monitor, chat, mail, management)
        gateway = gateway_type(store, accounts.config()['identity'], quotas=quotas, max_requests_per_minute=4096)
        app = web.Application(client_max_size=192 * 1024 * 1024)
        install_weather(app)
        app.add_subapp('/gateway', gateway.app())
        if monitor is not None:
            app.router.add_get(monitor_path, monitor.websocket)
        if chat is not None:
            app.router.add_post(chat_stream, chat.stream)
            app.on_shutdown.append(chat.shutdown)
        async def account_request(request):
            for name in ('Host',):
                if len(request.headers.getall(name, [])) != 1:
                    raise web.HTTPBadRequest(text='Unique request headers required')
            body = b''
            if request.method == 'POST':
                for name in ('Origin', 'Content-Type', 'Content-Length'):
                    if len(request.headers.getall(name, [])) != 1:
                        raise web.HTTPBadRequest(text='Unique request headers required')
                is_agent_request = agent_operations and (request.path == AGENT_CHALLENGE or request.path in AGENT_PATHS)
                limit = MAX_TRANSPORT_BYTES if is_agent_request else 65536
                if is_agent_request and request.headers.get('Content-Encoding'):
                    raise web.HTTPBadRequest(text='Plain JSON request required')
                if request.headers.get('Transfer-Encoding') or request.content_length is None or not 0 < request.content_length <= limit:
                    raise web.HTTPRequestEntityTooLarge(max_size=limit, actual_size=request.content_length or 0)
                body = await request.read()
            if len(request.headers.getall('Authorization', [])) > 1:
                raise web.HTTPBadRequest(text='Unique authorization required')
            env = {'REQUEST_METHOD': request.method, 'PATH_INFO': request.path, 'QUERY_STRING': request.query_string,
                   'CONTENT_LENGTH': str(len(body)), 'CONTENT_TYPE': request.headers.get('Content-Type', ''),
                   'HTTP_HOST': request.headers.get('Host', ''), 'HTTP_ORIGIN': request.headers.get('Origin', ''),
                   'HTTP_AUTHORIZATION': request.headers.get('Authorization', ''), 'REMOTE_ADDR': request.remote or 'unknown',
                   'wsgi.input': io.BytesIO(body), 'wsgi.url_scheme': urlsplit(origin).scheme, 'SERVER_PROTOCOL': 'HTTP/1.1'}
            def invoke():
                response = {}
                def start(status, headers, exc_info=None):
                    response['status'] = int(status.split()[0]); response['headers'] = headers
                stream = authority(env, start)
                try:
                    data = b''.join(stream)
                finally:
                    if hasattr(stream, 'close'): stream.close()
                return web.Response(status=response['status'], headers=response['headers'], body=data)
            response = await asyncio.to_thread(invoke)
            if network is not None:
                network.account_response(request, response)
            return response
        if network is not None:
            app.router.add_get('/guest-network', network.relay)
        if mail is not None:
            mail.register(app)
        if management:
            from account_management_http import install as install_account_management
            install_account_management(app, management, origin)
        app.router.add_route('*', '/api/{tail:.*}', account_request)
        app.router.add_get('/config.json', account_request)
        app.router.add_get('/.well-known/codi-issuer.json', account_request)
        app.router.add_get('/healthz', lambda request: web.json_response({'status': 'ok', 'scope': 'development', 'instanceId': metadata['instanceId']}))
        async def asset(request):
            name = request.match_info.get('tail') or 'index.html'
            if not re.fullmatch(r'(?:[A-Za-z0-9_@+-][A-Za-z0-9_@+.-]*/)*[A-Za-z0-9_@+-][A-Za-z0-9_@+.-]*', name):
                raise web.HTTPNotFound()
            current = public_root
            for part in name.split('/'):
                current = current / part
                if current.is_symlink(): raise web.HTTPNotFound()
            if not current.is_file(): raise web.HTTPNotFound()
            # WordCraft prints its generated PDF in a same-origin blob frame. Keep
            # that permission off the desktop/other apps and keep object-src disabled.
            csp = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; worker-src 'self' blob:; frame-src 'self'; object-src 'none'; base-uri 'none'"
            if name == 'index.html' or re.fullmatch(r'assets/desktop/apps/narrator/[0-9a-f]{64}/index\.html', name):
                csp = csp.replace("default-src 'self';", "default-src 'self'; media-src 'self' blob:;")
            if name == 'index.html':
                csp = csp.replace("connect-src 'self'", "connect-src 'self' https://noaa-gfs-bdp-pds.s3.amazonaws.com https://noaa-gefs-pds.s3.amazonaws.com https://noaa-cfs-pds.s3.amazonaws.com https://data.ecmwf.int https://opengeo.ncep.noaa.gov https://nowcoast.noaa.gov https://mapservices.weather.noaa.gov https://gibs.earthdata.nasa.gov https://api.weather.gov https://tiles.openfreemap.org https://www.gdacs.org https://mesonet.agron.iastate.edu https://eonet.gsfc.nasa.gov").replace("img-src 'self' data: blob:", "img-src 'self' data: blob: https://radar.weather.gov https://opengeo.ncep.noaa.gov https://nowcoast.noaa.gov https://tiles.openfreemap.org https://gibs.earthdata.nasa.gov https://mapservices.weather.noaa.gov")
            return web.FileResponse(current, headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
                'Cross-Origin-Opener-Policy': 'same-origin', 'Cross-Origin-Embedder-Policy': 'require-corp',
                'Content-Security-Policy': csp.replace("frame-src 'self'", "frame-src 'self' blob:") if name == 'wordcraft/index.html' else csp})
        app.router.add_get('/{tail:.*}', asset)
        metadata['status'] = 'ready'; marker.write_text(json.dumps(metadata) + '\n')
        async def release(_app):
            try:
                if jobs := getattr(gateway, 'jobs', None):
                    jobs.close()
                    await asyncio.to_thread(jobs.thread.join)
            finally:
                os.close(lock)
        app.on_cleanup.append(release)
        return app
    except BaseException:
        try:
            if jobs := getattr(gateway, 'jobs', None):
                jobs.close()
                await asyncio.to_thread(jobs.thread.join)
        finally:
            os.close(lock)
        raise


async def run(args):
    os.umask(0o077)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Retained state binds its issuer origin, including port. Allow a stopped
    # listener to restart while prior connections remain in TIME_WAIT.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', args.port)); sock.listen(128); sock.setblocking(False)
    origin = validate_origin(args.origin) if args.origin else 'http://127.0.0.1:' + str(sock.getsockname()[1])
    try:
        app = await create_application(args.public_root, args.private_root, origin, account_transfers=args.account_transfers,
                                       shared_transfers=args.shared_transfers, agent_operations=args.agent_operations,
                                       guest_network_policy=args.guest_network_policy)
        runner = web.AppRunner(app, access_log=None); await runner.setup()
        await web.SockSite(runner, sock).start()
        print(json.dumps({'origin': origin, 'scope': 'development-only'}), flush=True)
        stop = asyncio.Event()
        for sig in (signal.SIGTERM, signal.SIGINT):
            asyncio.get_running_loop().add_signal_handler(sig, stop.set)
        try:
            await stop.wait()
        finally:
            await runner.cleanup()
    finally:
        sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-root', type=Path, required=True)
    parser.add_argument('--private-root', type=Path, required=True)
    parser.add_argument('--port', type=int, default=18140)
    parser.add_argument('--origin', help='Explicit HTTPS test-site origin behind a trusted local proxy; listener remains loopback')
    parser.add_argument('--account-transfers', type=int, default=8, help='Concurrent file transfers per account (1–8)')
    parser.add_argument('--shared-transfers', type=int, default=16, help='Concurrent file transfers across the test service (account limit–32)')
    parser.add_argument('--agent-operations', action='store_true', help='Enable scoped operation grants for direct loopback testing')
    parser.add_argument('--guest-network-policy', type=Path, help='Protected egress policy for the optional guest worker')
    asyncio.run(run(parser.parse_args()))
