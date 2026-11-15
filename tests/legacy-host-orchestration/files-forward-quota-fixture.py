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
  if active:c['fileStorage']={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}
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
  root=pathlib.Path(temp);issuer=Issuer(Config(root/'issuer',BASE,origin=origin,rate_per_minute=180));server=make_server('127.0.0.1',0,Head(GatewayAuthority(issuer)),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store);gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=2048)
  fault={'armed':None,'taken':None,'count':0}
  @web.middleware
  async def quota_controls(request,handler):
   path=request.path
   if path.startswith('/gateway/__quota/arm/'):
    mode=path.rsplit('/',1)[-1]
    if mode not in ('create','write','close'):return web.Response(status=400)
    fault.update(armed=mode,taken=None);return web.json_response(fault)
   if path=='/gateway/__quota/blank':return web.Response(text='<html><body>Disposable storage test</body></html>',content_type='text/html')
   if path=='/gateway/__quota/take':
    mode=fault['armed'];fault.update(armed=None,taken=mode)
    if mode:fault['count']+=1
    return web.json_response({'mode':mode})
   if path=='/gateway/__quota/status':return web.json_response(fault)
   return await handler(request)
  app=gateway.app();app.middlewares.insert(0,quota_controls);runner=web.AppRunner(app,access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gport=site._server.sockets[0].getsockname()[1];conf=root/'Caddyfile'
  instrument=root/'instrument';instrument.mkdir();source=CAND/'storage/browser/releases/3daf09a753455be1dc07ce183097b6535a999d2cc2124f9d0e6df25c7180be3a/opfs/worker.mjs'; raw=source.read_bytes()
  if hashlib.sha256(raw).hexdigest()!='9d97301fb4e9e20173bc0c2f57aa2e23c479b5dac0b2b193b76d0716fef7ca1e':raise ValueError('worker source pin mismatch')
  inject="""async function __injectQuota(){const __fault=(await (await fetch('/gateway/__quota/take')).json()).mode;
if(__fault){const __create=FileSystemFileHandle.prototype.createWritable;FileSystemFileHandle.prototype.createWritable=async function(...args){if(__fault==='create')throw new DOMException('injected quota','QuotaExceededError');const out=await __create.apply(this,args);return {write:async(...a)=>{if(__fault==='write')throw new DOMException('injected quota','QuotaExceededError');return out.write(...a)},close:async(...a)=>{if(__fault==='close')throw new DOMException('injected quota','QuotaExceededError');return out.close(...a)},abort:(...a)=>out.abort(...a)}}}};
"""
  needle=b"if(action==='write'){"
  if raw.count(needle)!=1:raise ValueError('worker injection anchor changed')
  (instrument/'quota-worker.mjs').write_bytes(inject.encode()+raw.replace(b"from './core.mjs'",b"from '/storage/browser/releases/3daf09a753455be1dc07ce183097b6535a999d2cc2124f9d0e6df25c7180be3a/opfs/core.mjs'",1).replace(needle,needle+b'await __injectQuota();',1))
  def render(new):
   selected=CAND if new else BASE
   upstream=os.environ.get('CODI_FORWARD_GATEWAY_UPSTREAM',f'127.0.0.1:{gport}')
   overrides=f'''handle /__quota/worker.mjs {{\n root * {instrument}\n rewrite * /quota-worker.mjs\n file_server\n }}\n @bare_shell {{\n path /app.js /desktop-apps.js\n not {{\n query simplified=1\n }}\n}}\n handle @bare_shell {{\n root * {os.environ.get('CODI_FORWARD_PUBLIC_BASE','/tmp/codi-files-forward-independent-inputs/public-base')}\n file_server\n}}\n handle /config.json {{\n reverse_proxy 127.0.0.1:{server.server_port}\n }}\n @issuer path /api/* /discovery.json /.well-known/*\n handle @issuer {{\n reverse_proxy 127.0.0.1:{server.server_port}\n }}\n handle /gateway/client.mjs {{\n root * {selected}\n file_server\n }}\n handle /gateway/* {{\n reverse_proxy {upstream}\n }}\n handle {{\n root * {selected}\n file_server\n }}\n'''
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
