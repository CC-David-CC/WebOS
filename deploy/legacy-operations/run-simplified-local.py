#!/usr/bin/env python3
"""Run the simplified desktop, issuer and account file gateway on loopback.

Development preview only: private account state persists in ignored directories.
Linux guest networking is intentionally disabled in this local launcher.
"""
import argparse
import asyncio
import importlib.util
import hashlib
import re
from pathlib import Path
import shutil
import sys
import threading
from wsgiref.simple_server import make_server
from aiohttp import ClientSession, ClientTimeout, web

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"codiserver-server-v0.3.0"))
from codiauth.service import Config
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer, QuietHandler
from gateway_service.auth import initialize_ledger, MAX_REQUEST_BYTES
from gateway_service.transfers import initialize_transfers
from gateway_service.user_store import UserStore
from gateway_service.http import FileGateway

spec=importlib.util.spec_from_file_location('codi_staging',ROOT/'scripts/serve-connected.py')
staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)

async def main(port,speech_assets=None,isolated=False,access_policy=None,geoip=None,browser_relay=False):
    origin=f'http://127.0.0.1:{port}'
    runtime=ROOT/'.build'/('simplified-local-test-'+str(port) if isolated else 'simplified-local');runtime.mkdir(parents=True,exist_ok=True,mode=0o700)
    public=runtime/'public'
    if public.exists():shutil.rmtree(public)
    staging.stage(public)
    if speech_assets:
        source=Path(speech_assets).resolve()
        if not (source/'client.mjs').is_file() or not (source/'worker.mjs').is_file():raise ValueError('Invalid speech asset directory')
        shutil.copytree(source,public/'assets/speech',dirs_exist_ok=True)
    data=runtime/'account-data' if isolated else ROOT/'storage/accounts/data';state=runtime/'account-state' if isolated else ROOT/'storage/accounts/state'
    for folder in (data,state):folder.mkdir(parents=True,exist_ok=True,mode=0o700)
    store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store)
    browser_policy=ROOT.parent/'apps/system/browser/relay/policy.json'
    browser_sha=hashlib.sha256(browser_policy.read_bytes()).hexdigest() if browser_relay else None
    class Issuer(Service):
        def config(self):
            config=super().config();config['gateway']={'version':'codi-user-files/1','basePath':'/gateway','fileBytes':8*1024*1024}
            if browser_sha:config['browserRelay']={'version':'codi-browser-relay/1','basePath':'/browser-relay','policySHA256':browser_sha}
            return config
    issuer=Issuer(Config(runtime/'issuer',public,origin=origin,rate_per_minute=1000))
    application=GatewayAuthority(issuer)
    if browser_relay:
        from origin_service.browser_authority import BrowserAuthority
        application=BrowserAuthority(issuer,browser_sha,application)
    application=staging.HeadSupport(application);geo=None
    if access_policy:
        from network_policy.login import LoginFilter
        from network_policy.policy import LocalCountryDatabase
        geo=LocalCountryDatabase(geoip) if geoip else None
        application=LoginFilter(application,access_policy,trusted_proxies=['127.0.0.1'],geo=geo)
    http=make_server('127.0.0.1',0,application,server_class=BoundedServer,handler_class=QuietHandler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=4096)
    gateway_runner=web.AppRunner(gateway.app(),access_log=None);await gateway_runner.setup()
    gateway_site=web.TCPSite(gateway_runner,'127.0.0.1',0);await gateway_site.start()
    gateway_port=gateway_site._server.sockets[0].getsockname()[1]
    outgoing=ClientSession(timeout=ClientTimeout(total=150),trust_env=False,auto_decompress=False)
    async def proxy(request):
        # The reference issuer caps in-memory static responses at 64 MiB.
        # Stream larger immutable app assets like production Caddy does.
        if request.method in ('GET','HEAD') and re.fullmatch(r'/assets/desktop/apps/[a-z][a-z0-9-]{0,31}/[0-9a-f]{64}/(?:[A-Za-z0-9_@+.-]+/)*[A-Za-z0-9_@+.-]+',request.path):
            relative=Path(request.path.lstrip('/'));cursor=public
            for part in relative.parts:
                if part in ('.','..'):raise web.HTTPForbidden()
                cursor=cursor/part
                if cursor.is_symlink():raise web.HTTPForbidden()
            if cursor.is_file() and cursor.stat().st_size>64*1024*1024:
                return web.FileResponse(cursor,headers={'Cross-Origin-Resource-Policy':'same-origin','X-Content-Type-Options':'nosniff','Cache-Control':'no-store'})
        target=('http://127.0.0.1:'+str(gateway_port) if request.raw_path.startswith('/gateway/') else 'http://127.0.0.1:'+str(http.server_port))+request.raw_path
        hop={'connection','keep-alive','transfer-encoding','upgrade','te','trailer'}
        headers={k:v for k,v in request.headers.items() if k.lower() not in hop}
        if access_policy:
            # This local proxy is the only upstream connection to the issuer;
            # never forward a browser-supplied value for the trusted header.
            headers={k:v for k,v in headers.items() if k.lower()!='x-codi-client-ip'}
            headers['X-Codi-Client-IP']=request.remote or ''
        async with outgoing.request(request.method,target,headers=headers,data=request.content if request.can_read_body else None,allow_redirects=False) as upstream:
            response_headers={k:v for k,v in upstream.headers.items() if k.lower() not in hop}
            # JupyterLab compiles JSON-schema validators at runtime. Scope its
            # required eval permission to notebook documents and workers only;
            # all other desktop pages keep the stricter policy.
            if re.fullmatch(r'/assets/desktop/apps/notebook/[0-9a-f]{64}/node_modules/jupyterlite/.*', request.path):
                csp=response_headers.get('Content-Security-Policy','')
                if "script-src 'self' 'wasm-unsafe-eval'" not in csp:raise RuntimeError('Unexpected notebook security policy')
                response_headers['Content-Security-Policy']=csp.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' 'unsafe-eval'")
            if re.fullmatch(r'/assets/desktop/apps/browser/[0-9a-f]{64}/src/engine-worker\.js', request.path):
                csp=response_headers.get('Content-Security-Policy','')
                if "script-src 'self' 'wasm-unsafe-eval'" not in csp:raise RuntimeError('Unexpected browser worker security policy')
                response_headers['Content-Security-Policy']=csp.replace("script-src 'self' 'wasm-unsafe-eval'", "script-src 'self' blob: 'wasm-unsafe-eval'")
            response=web.StreamResponse(status=upstream.status,headers=response_headers)
            await response.prepare(request)
            async for chunk in upstream.content.iter_chunked(65536):await response.write(chunk)
            await response.write_eof();return response
    app=web.Application(client_max_size=MAX_REQUEST_BYTES,handler_args={'auto_decompress':False})
    if browser_relay:
        sys.path.insert(0,str(ROOT.parent/'apps/system/browser'))
        from relay.wisp import Relay
        from relay.download import Downloader
        from browser_service.sessions import BrowserSessions
        from browser_service.http import BrowserHTTP
        from network_policy.policy import PolicyLoader
        access=PolicyLoader(access_policy or ROOT/'network_policy/default.json',geo)
        async def unavailable(_request):return None
        relay=Relay(policy_path=browser_policy,origin=origin,authenticate=unavailable,source=lambda request:request.remote,network_check=lambda ip:access.check('outgoing',ip))
        BrowserHTTP(BrowserSessions(issuer.config()['identity'],browser_sha),relay,origin=origin,secure_cookie=False,downloader=Downloader(relay)).routes(app)
    app.router.add_route('*','/{tail:.*}',proxy)
    runner=web.AppRunner(app,access_log=None);await runner.setup();await web.TCPSite(runner,'127.0.0.1',port).start()
    print(f'Simplified local preview: {origin}/',flush=True)
    print(f'Account files: {data}; permissions: {state}; login state: {runtime / "issuer"}',flush=True)
    try:await asyncio.Event().wait()
    finally:
        await runner.cleanup();await outgoing.close();await gateway_runner.cleanup();await asyncio.to_thread(http.shutdown);thread.join(2);http.server_close()
        if geo:geo.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=18130);parser.add_argument('--speech-assets',type=Path,help='Optional local speech model and runtime directory');parser.add_argument('--isolated',action='store_true',help='Use separate disposable state for testing');parser.add_argument('--access-policy',type=Path,help='Optional local IP/country policy');parser.add_argument('--geoip',type=Path,help='Optional local DB-IP Country Lite database');parser.add_argument('--browser-relay',action='store_true',help='Enable the experimental registered-only Browser relay locally');args=parser.parse_args()
    if not 1<=args.port<=65535:parser.error('Invalid port')
    try:asyncio.run(main(args.port,args.speech_assets,args.isolated,args.access_policy,args.geoip,args.browser_relay))
    except KeyboardInterrupt:pass
