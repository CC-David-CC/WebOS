#!/usr/bin/env python3
"""Loopback fixture: real native issuer/guest, exact gateway, disposable state."""
import asyncio,hashlib,http.server,json,os,pathlib,signal,subprocess,sys,tempfile,threading,time,urllib.request
from aiohttp import web
R=pathlib.Path(os.environ['CODI_NATIVE_BASE']);N=pathlib.Path(os.environ['CODI_NATIVE_NEXT']);G=pathlib.Path(os.environ['CODI_GATEWAY_ROOT']);B=pathlib.Path(os.environ['CODI_BASELINE']);P=os.environ['CODI_PYTHON'];C=os.environ['CODI_CADDY'];origin='http://127.0.0.1:19983';IP=19984;GP=19985;CONTROL=19986;ADMIN=19987
assert hashlib.sha256((R/'connected-release.json').read_bytes()).hexdigest()=='1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'
assert hashlib.sha256((N/'connected-release.json').read_bytes()).hexdigest()=='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21'
assert hashlib.sha256((G/'files-service.json').read_bytes()).hexdigest()=='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'
def verify(root,manifest,pin):
 raw=(root/manifest).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('manifest pin mismatch')
 records=json.loads(raw)['files'];found=set()
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   item=pathlib.Path(parent)/name
   if item.is_symlink():raise ValueError('symlink in release')
  for name in files:
   item=pathlib.Path(parent)/name;rel=item.relative_to(root).as_posix();found.add(rel)
   if not item.is_file() or item.stat().st_nlink!=1:raise ValueError('unsafe release file')
   if rel==manifest:continue
   b=item.read_bytes();record=records.get(rel)
   if not record or len(b)!=record['bytes'] or hashlib.sha256(b).hexdigest()!=record['sha256']:raise ValueError('release digest mismatch '+rel)
 if found!=set(records)|{manifest}:raise ValueError('release inventory mismatch')
pins=[(R,'connected-release.json','1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'),(N,'connected-release.json','853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21'),(G,'files-service.json','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')]
for args in pins:verify(*args)
sys.path[:0]=[str(G),str(G/'codiserver-server-v0.3.0')]
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway
async def main():
 with tempfile.TemporaryDirectory(prefix='codi-native-continuity-') as temp:
  t=pathlib.Path(temp);state=t/'gateway';data=t/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);log=open(t/'issuer.log','w+');proc=None;next_started=False
  def config():
   with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{IP}/config.json',headers={'Host':'127.0.0.1:19983'}),timeout=.5) as r:return json.load(r)
  def start(root,next_version):
   cmd=[P,'-B',str(root/'scripts/serve-connected.py'),'--port',str(IP),'--runtime-dir',str(t/'runtime'),'--origin',origin,'--user-files']
   if next_version:cmd.append('--beta-opfs-file-content')
   q=subprocess.Popen(cmd,stdout=log,stderr=log)
   for i in range(200):
    if q.poll() is not None:log.flush();raise RuntimeError((t/'issuer.log').read_text())
    try:return q,config()
    except OSError:time.sleep(.05)
   q.terminate();q.wait();raise RuntimeError('issuer timeout')
  proc,original=start(R,False);identity=original['identity'];assert 'fileStorage' not in original
  guest=subprocess.Popen([P,'-B',str(R/'guest-relay/server.py'),'--port',str(GP),'--origin',origin,'--identity-config-port',str(IP),'--no-guest-network'],stdout=log,stderr=log)
  store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store);gateway=FileGateway(store,identity,max_requests_per_minute=2048);runner=web.AppRunner(gateway.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gport=site._server.sockets[0].getsockname()[1]
  conf=t/'Caddyfile';conf.write_text(f'''{{\n admin 127.0.0.1:{ADMIN}\n}}\n{origin} {{\n header Cache-Control no-store\n header Cross-Origin-Embedder-Policy require-corp\n header Cross-Origin-Opener-Policy same-origin\n handle /gateway/* {{\n reverse_proxy 127.0.0.1:{gport}\n }}\n handle /config.json {{\n reverse_proxy 127.0.0.1:{GP}\n }}\n @issuer path /api/* /discovery.json /.well-known/*\n handle @issuer {{\n reverse_proxy 127.0.0.1:{IP}\n }}\n handle {{\n root * {B}\n file_server\n }}\n}}\n''');caddy=subprocess.Popen([C,'run','--config',str(conf),'--adapter','caddyfile'],stdout=log,stderr=log)
  class Control(http.server.BaseHTTPRequestHandler):
   def do_GET(self):
    nonlocal proc,next_started
    if self.path!='/restart' or next_started:self.send_error(400);return
    try:
     proc.terminate();proc.wait(timeout=15);proc,updated=start(N,True);extra=updated.pop('fileStorage');assert extra=={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2};assert updated==original;next_started=True;self.send_response(200);self.end_headers()
    except BaseException as e:print('restart failure',repr(e),flush=True);self.send_error(500)
   def log_message(self,*args):pass
  ctrl=http.server.HTTPServer(('127.0.0.1',CONTROL),Control);thread=threading.Thread(target=ctrl.serve_forever,daemon=True);thread.start()
  try:
   for _ in range(100):
    if caddy.poll() is not None or guest.poll() is not None:log.flush();raise RuntimeError((t/'issuer.log').read_text())
    try:
     with urllib.request.urlopen(origin+'/config.json',timeout=.5) as r:assert json.load(r)==original
     break
    except OSError:await asyncio.sleep(.1)
   else:raise RuntimeError('frontend startup timed out')
   print('ready '+origin,flush=True);await asyncio.Event().wait()
  finally:
   await asyncio.to_thread(ctrl.shutdown);ctrl.server_close();thread.join(2)
   for p in (caddy,guest,proc):
    if p and p.poll() is None:p.terminate();p.wait(timeout=15)
   await runner.cleanup()
   for args in pins:verify(*args)
   print('PASS complete native and gateway inventories after fixture',flush=True)
try:asyncio.run(main())
except KeyboardInterrupt:pass
