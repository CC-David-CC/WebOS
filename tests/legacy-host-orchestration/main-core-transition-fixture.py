#!/usr/bin/env python3
"""Disposable signed beta-like fixture; routing switch is test-only."""
import asyncio,hashlib,http.server,json,os,pathlib,subprocess,sys,tempfile,threading
from wsgiref.simple_server import make_server
from aiohttp import web
ROOT=pathlib.Path(__file__).resolve().parents[1];ACTIVE=ROOT/'active-system';GW=pathlib.Path(os.environ['CODI_GATEWAY_ROOT']);BASE=pathlib.Path(os.environ.get('CODI_FORWARD_BASE','/tmp/codi-files-forward-independent-inputs/public-3ad'));CAND=pathlib.Path(os.environ.get('CODI_FORWARD_CANDIDATE','/tmp/codi-files-forward-independent-inputs/public-e359'));CADDY=os.environ['CODI_CADDY'];PORT=int(os.environ.get('CODI_FORWARD_PORT','19973'));CONTROL=PORT+1;ADMIN=PORT+2;origin=f'http://127.0.0.1:{PORT}'
assert hashlib.sha256((GW/'files-service.json').read_bytes()).hexdigest()=='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'
assert hashlib.sha256((GW/'gateway_service/client.mjs').read_bytes()).hexdigest()=='44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869'
sys.path.insert(0,str(ACTIVE));sys.path.insert(0,str(GW));sys.path.insert(0,str(GW/'codiserver-server-v0.3.0'))
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway
active=True
class Issuer(Service):
 def config(self):
  c=super().config();c['gateway']={'version':'codi-user-files/1','basePath':'/gateway','fileBytes':134217728}
  return c
class Head:
 def __init__(self,app):self.app=app
 def __call__(self,env,start):
  if env.get('REQUEST_METHOD')!='HEAD':return self.app(env,start)
  env=dict(env,REQUEST_METHOD='GET');result=self.app(env,start)
  try:
   for _ in result:pass
  finally:
   if hasattr(result,'close'):result.close()
  return []
async def main():
 global active
 with tempfile.TemporaryDirectory(prefix='codi-opfs-controlled-') as temp:
  root=pathlib.Path(temp);issuer=Issuer(Config(root/'issuer',BASE,origin=origin,rate_per_minute=180));server=make_server('127.0.0.1',0,Head(GatewayAuthority(issuer)),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store);gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=2048);runner=web.AppRunner(gateway.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gport=site._server.sockets[0].getsockname()[1];conf=root/'Caddyfile'
  def render(new):
   selected=CAND if new else BASE
   upstream=os.environ.get('CODI_FORWARD_GATEWAY_UPSTREAM',f'127.0.0.1:{gport}')
   overrides=f'''@bare_shell {{\n path /app.js /desktop-apps.js\n not {{\n query simplified=1\n }}\n}}\n handle @bare_shell {{\n root * {os.environ.get('CODI_FORWARD_PUBLIC_BASE','/tmp/codi-files-forward-independent-inputs/public-base')}\n file_server\n}}\n handle /config.json {{\n reverse_proxy 127.0.0.1:{server.server_port}\n }}\n @issuer path /api/* /discovery.json /.well-known/*\n handle @issuer {{\n reverse_proxy 127.0.0.1:{server.server_port}\n }}\n handle /gateway/client.mjs {{\n root * {selected}\n file_server\n }}\n handle /gateway/* {{\n reverse_proxy {upstream}\n }}\n handle {{\n root * {selected}\n file_server\n }}\n'''
   conf.write_text(f'''{{\n admin 127.0.0.1:{ADMIN}\n}}\n{origin} {{\n header Cache-Control no-store\n header Cross-Origin-Embedder-Policy require-corp\n header Cross-Origin-Opener-Policy same-origin\n header /assets/desktop/offline-worker.js Service-Worker-Allowed /\n handle /assets/terminal/v2/image.json {{\n respond 404\n }}\n {overrides}\n}}\n''')
  render(False);caddy=subprocess.Popen([CADDY,'run','--config',str(conf),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  class Control(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    global active
    if self.path!='/on':self.send_error(400);return
    try:
     render(True);subprocess.run([CADDY,'reload','--address',f'127.0.0.1:{ADMIN}','--config',str(conf),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);active=True;self.send_response(200);self.end_headers()
    except Exception as e:print('switch failed',repr(e),flush=True);self.send_error(500)
   def log_message(self,*args):pass
  ctrl=http.server.HTTPServer(('127.0.0.1',CONTROL),Control);ct=threading.Thread(target=ctrl.serve_forever,daemon=True);ct.start()
  try:
   for _ in range(100):
    if caddy.poll() is not None:raise RuntimeError(caddy.stderr.read().decode())
    try:r,w=await asyncio.open_connection('127.0.0.1',PORT);w.close();await w.wait_closed();break
    except OSError:await asyncio.sleep(.05)
   else:raise RuntimeError('Caddy start failed')
   print('controlled fixture ready',origin,'gateway',gport,'state',state,'data',data,flush=True);await asyncio.Event().wait()
  finally:
   await asyncio.to_thread(ctrl.shutdown);ctrl.server_close();ct.join(2);caddy.terminate();caddy.wait(timeout=5);await runner.cleanup();await asyncio.to_thread(server.shutdown);thread.join(2);server.server_close()
try:asyncio.run(main())
except KeyboardInterrupt:pass
