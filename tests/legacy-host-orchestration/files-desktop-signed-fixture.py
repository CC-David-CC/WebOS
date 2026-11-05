#!/usr/bin/env python3
"""Disposable signed desktop; Linux guest enabled only by explicit test flag."""
import asyncio, hashlib, importlib.util, os, pathlib, re, shutil, socket, subprocess, sys, tempfile, threading
from wsgiref.simple_server import make_server
from aiohttp import web
ROOT=pathlib.Path(__file__).resolve().parents[1]; ACTIVE=ROOT/'active-system'
GATEWAY=pathlib.Path(os.environ.get('CODI_GATEWAY_ROOT','/tmp/codi-beta-batch-mount-built'));BUNDLE=pathlib.Path(os.environ.get('CODI_APPS_BUNDLE','/tmp/codi-files-boundary-bundle'));CADDY=os.environ.get('CODI_CADDY','/tmp/codi-microduck-hosting-evidence/caddy')
sys.path.insert(0,str(ACTIVE));sys.path.insert(0,str(GATEWAY))
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway
PORT=int(os.environ.get('CODI_DESKTOP_FIXTURE_PORT','19975')); ORIGIN=f'http://127.0.0.1:{PORT}'
# Caddy can use SO_REUSEPORT: a listening old fixture must be rejected before
# a second Caddy starts, or traffic can alternate between independent accounts.
def require_free_port():
 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
  probe.bind(('127.0.0.1', PORT))

def require_sole_listener(pid):
 result=subprocess.run(['ss','-ltnp',f'sport = :{PORT}'],check=True,capture_output=True,text=True)
 listeners=[line for line in result.stdout.splitlines()[1:] if line.strip()]
 pids={int(n) for line in listeners for n in re.findall(r'pid=(\d+)',line)}
 if len(listeners)!=1 or pids!={pid}: raise RuntimeError('Fixture port has another or unidentifiable listener')

SDK=pathlib.Path(os.environ.get('CODI_SDK','/tmp/codi-files-boundary-sdk.mjs'))
assert hashlib.sha256(SDK.read_bytes()).hexdigest()=='44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869'
assert hashlib.sha256((GATEWAY/'files-service.json').read_bytes()).hexdigest()=='c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960'
spec=importlib.util.spec_from_file_location('desktop_staging',ACTIVE/'scripts/serve-connected.py');staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
class Issuer(Service):
 def config(self):
  config=super().config();config['gateway']={'version':'codi-user-files/1','basePath':'/gateway','fileBytes':128*1024*1024};config['fileStorage']={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2};return config
async def main():
 require_free_port()
 with tempfile.TemporaryDirectory(prefix='codi-desktop-files-') as tmp:
  root=pathlib.Path(tmp);public=staging.stage(root/'public',bundled=BUNDLE);(public/'gateway_service').mkdir(exist_ok=True);shutil.copy2(SDK,public/'gateway_service/client.mjs');shutil.copytree(ACTIVE/'gateway_service/vendor/js-sha256',public/'gateway_service/hash')
  issuer=Issuer(Config(root/'issuer',public,origin=ORIGIN));server=make_server('127.0.0.1',0,staging.HeadSupport(GatewayAuthority(issuer)),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store);gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=2048);runner=web.AppRunner(gateway.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
  cfg=root/'Caddyfile';csp_rule=" header Content-Security-Policy \"script-src 'self' 'wasm-unsafe-eval'; worker-src 'self'; object-src 'none'\"\n" if os.environ.get('CODI_TEST_STRICT_CSP')=='1' else '';guest_rule='' if os.environ.get('CODI_TEST_REAL_LINUX')=='1' else ' handle /assets/terminal/v2/image.json {\n respond 404\n }\n';cfg.write_text('{\n admin off\n}\n'+ORIGIN+' {\n'+csp_rule+guest_rule+' handle /gateway/* {\n reverse_proxy 127.0.0.1:'+str(port)+'\n }\n handle {\n reverse_proxy 127.0.0.1:'+str(server.server_port)+'\n }\n}\n');caddy=subprocess.Popen([CADDY,'run','--config',str(cfg),'--adapter','caddyfile'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for _ in range(100):
    if caddy.poll() is not None:raise RuntimeError(caddy.stderr.read().decode())
    try:r,w=await asyncio.open_connection('127.0.0.1',PORT);w.close();await w.wait_closed();break
    except OSError:await asyncio.sleep(.05)
   else:raise RuntimeError('fixture failed to start')
   require_sole_listener(caddy.pid)
   print('desktop signed fixture ready '+ORIGIN,flush=True);await asyncio.Event().wait()
  finally:
   caddy.terminate();caddy.wait(timeout=5);await runner.cleanup();await asyncio.to_thread(server.shutdown);thread.join(2);server.server_close()
try:asyncio.run(main())
except KeyboardInterrupt:pass
