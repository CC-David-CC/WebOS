#!/usr/bin/env python3
"""Private loopback fixture: sealed candidate issuer and dd8, disposable state."""
import asyncio,hashlib,json,os,pathlib,subprocess,sys,tempfile,time,urllib.request
from aiohttp import web
P=pathlib.Path; root=P(__file__).resolve().parents[1]
issuer=P(os.environ['CODI_ISSUER']);gw=P(os.environ['CODI_GATEWAY_ROOT']);assets=P(os.environ['CODI_MAIN_ASSETS']);port=int(os.environ.get('CODI_FORWARD_PORT','19920'));origin=f'http://127.0.0.1:{port}'; python=sys.executable

def verify(path,name,pin):
 raw=(path/name).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('manifest mismatch')
 entries=json.loads(raw)['files']; actual={}
 for p in path.rglob('*'):
  if p.is_symlink() or not(p.is_dir() or p.is_file()):raise ValueError('unsafe source')
  if p.is_file() and p.name!=name:
   b=p.read_bytes();actual[p.relative_to(path).as_posix()]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if entries!=actual:raise ValueError('source inventory mismatch')
verify(issuer,'connected-release.json','8149949e9b4d7ef878ae1e0a208943b1b32e4883e2698f4b1a433c49a4aa3055')
verify(gw,'files-service.json','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')
cache=json.loads((assets/'assets/desktop/cache-manifest.json').read_bytes())
assert cache['id']=='f2e2ed4d3b75e8c40992a18bf83db7937fe90615bf1151e1b51ed3b0a8012f4a'
assert hashlib.sha256(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==cache['id']
for name,rec in cache['files'].items():
 b=(assets/name).read_bytes();assert {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}==rec
sys.path.insert(0,str(gw));sys.path.insert(0,str(gw/'codiserver-server-v0.3.0'))
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway
async def main():
 with tempfile.TemporaryDirectory(prefix='codi-main-signed-') as t:
  state=P(t);ip=port+3;cmd=[python,'-B',str(issuer/'scripts/serve-connected.py'),'--port',str(ip),'--runtime-dir',str(state/'issuer'),'--origin',origin,'--user-files','--opfs-file-content-origin',origin]
  log=open(state/'issuer.log','w+');iproc=subprocess.Popen(cmd,stdout=log,stderr=log);caddy=None;runner=None
  try:
   for _ in range(200):
    if iproc.poll() is not None:raise RuntimeError('issuer exited')
    try:
     with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{ip}/config.json',headers={'Host':f'127.0.0.1:{port}'}),timeout=.3) as r: config=json.load(r)
     break
    except OSError:await asyncio.sleep(.1)
   else:raise RuntimeError('issuer timeout')
   assert config['fileStorage']=={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}
   (state/'state').mkdir(mode=0o700);(state/'data').mkdir(mode=0o700);store=UserStore(state/'state',state/'data');initialize_ledger(store);initialize_transfers(store);g=FileGateway(store,config['identity'],max_requests_per_minute=2048);runner=web.AppRunner(g.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gp=site._server.sockets[0].getsockname()[1]
   conf=state/'Caddyfile';conf.write_text(f'''{{\n admin 127.0.0.1:{port+1}\n}}\n{origin} {{\n header Cache-Control no-store\n header Cross-Origin-Embedder-Policy require-corp\n header Cross-Origin-Opener-Policy same-origin\n header /assets/desktop/offline-worker.js Service-Worker-Allowed /\n handle /assets/terminal/v2/image.json {{\n  respond 404\n }}\n @issuer path /config.json /api/* /discovery.json /.well-known/*\n handle @issuer {{\n  reverse_proxy 127.0.0.1:{ip}\n }}\n handle /gateway/client.mjs {{\n  root * {gw}\n  rewrite * /gateway_service/client.mjs\n  file_server\n }}\n handle /gateway/* {{\n  reverse_proxy 127.0.0.1:{gp}\n }}\n handle {{\n  root * {assets}\n  file_server\n }}\n}}\n''')
   caddy=subprocess.Popen([os.environ['CODI_CADDY'],'run','--config',str(conf),'--adapter','caddyfile'],stdout=log,stderr=log)
   for _ in range(100):
    if caddy.poll() is not None:raise RuntimeError('caddy exited')
    try:r,w=await asyncio.open_connection('127.0.0.1',port);w.close();await w.wait_closed();break
    except OSError:await asyncio.sleep(.1)
   else:raise RuntimeError('caddy timeout')
   print('READY',origin,flush=True);await asyncio.Event().wait()
  finally:
   if caddy:caddy.terminate();caddy.wait(timeout=10)
   if runner:await runner.cleanup()
   iproc.terminate();iproc.wait(timeout=10);log.close()
try:asyncio.run(main())
except KeyboardInterrupt:pass
