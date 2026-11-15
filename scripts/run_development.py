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
import uuid
from urllib.parse import urlsplit
from aiohttp import web
from webos_accounts import AccountsService, Config
from webos_accounts.file_authority import FileAuthority
from webos_storage import UserStore, DEFAULT_ACCOUNT_FOLDERS, FileGateway, initialize_ledger, initialize_transfers


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


async def create_application(public_root, private_root, origin):
    origin = validate_origin(origin)
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
            def config(self):
                value = super().config()
                value['gateway'] = {'version': 'codi-user-files/1', 'basePath': '/gateway', 'fileBytes': 128 * 1024 * 1024}
                return value
        accounts = DevelopmentAccounts(Config(private_root / 'identity', public_root, origin=origin, rate_per_minute=1000))
        authority = FileAuthority(accounts)
        store = UserStore(private_root / 'storage-state', private_root / 'account-files', initial_folders=DEFAULT_ACCOUNT_FOLDERS)
        if new:
            # Only explicitly new development state is initialized. Retained
            # state is validated by FileGateway and never silently repaired.
            initialize_ledger(store); initialize_transfers(store)
        gateway = FileGateway(store, accounts.config()['identity'], max_requests_per_minute=4096)
        app = web.Application(client_max_size=192 * 1024 * 1024)
        app.add_subapp('/gateway', gateway.app())
        async def account_request(request):
            for name in ('Host',):
                if len(request.headers.getall(name, [])) != 1:
                    raise web.HTTPBadRequest(text='Unique request headers required')
            body = b''
            if request.method == 'POST':
                for name in ('Origin', 'Content-Type', 'Content-Length'):
                    if len(request.headers.getall(name, [])) != 1:
                        raise web.HTTPBadRequest(text='Unique request headers required')
                if request.headers.get('Transfer-Encoding') or request.content_length is None or not 0 < request.content_length <= 65536:
                    raise web.HTTPRequestEntityTooLarge(max_size=65536, actual_size=request.content_length or 0)
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
            return await asyncio.to_thread(invoke)
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
            return web.FileResponse(current, headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff',
                'Cross-Origin-Opener-Policy': 'same-origin', 'Cross-Origin-Embedder-Policy': 'require-corp',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; worker-src 'self' blob:; frame-src 'self'; object-src 'none'; base-uri 'none'"})
        app.router.add_get('/{tail:.*}', asset)
        metadata['status'] = 'ready'; marker.write_text(json.dumps(metadata) + '\n')
        async def release(_app):
            os.close(lock)
        app.on_cleanup.append(release)
        return app
    except BaseException:
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
        app = await create_application(args.public_root, args.private_root, origin)
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
    asyncio.run(run(parser.parse_args()))
