#!/usr/bin/env python3
"""Disposable signed desktop plus loopback-only test counters; never deploy."""
import asyncio, hashlib, importlib.util, os, pathlib, shutil, subprocess, sys, tempfile, threading
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
SDK=pathlib.Path(os.environ.get('CODI_SDK','/tmp/codi-files-boundary-sdk.mjs'))
assert hashlib.sha256(SDK.read_bytes()).hexdigest()=='44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869'
assert hashlib.sha256((GATEWAY/'files-service.json').read_bytes()).hexdigest()=='c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960'
spec=importlib.util.spec_from_file_location('desktop_staging',ACTIVE/'scripts/serve-connected.py');staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
class Issuer(Service):
 def config(self):
  config=super().config();config['gateway']={'version':'codi-user-files/1','basePath':'/gateway','fileBytes':128*1024*1024};config['fileStorage']={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2};return config
async def main():
 with tempfile.TemporaryDirectory(prefix='codi-desktop-files-') as tmp:
  root=pathlib.Path(tmp);public=staging.stage(root/'public',bundled=BUNDLE);(public/'gateway_service').mkdir(exist_ok=True);shutil.copy2(SDK,public/'gateway_service/client.mjs');shutil.copytree(ACTIVE/'gateway_service/vendor/js-sha256',public/'gateway_service/hash')
  issuer=Issuer(Config(root/'issuer',public,origin=ORIGIN));server=make_server('127.0.0.1',0,staging.HeadSupport(GatewayAuthority(issuer)),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store);gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=2048)
  counts={'requests':0,'commits':0}
  @web.middleware
  async def fixture_counter(request,handler):
   if request.path=='/gateway/__fixture_counts':return web.json_response(counts)
   if request.path=='/gateway/__fixture_reset':counts.update(requests=0,commits=0);return web.json_response(counts)
   mutation=request.path=='/gateway/upload' and request.method=='POST'
   if mutation:counts['requests']+=1
   response=await handler(request)
   if mutation and 200<=response.status<300:counts['commits']+=1
   return response
  app=gateway.app();app.middlewares.insert(0,fixture_counter);runner=web.AppRunner(app,access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();port=site._server.sockets[0].getsockname()[1]
  cfg=root/'Caddyfile';guest_rule='' if os.environ.get('CODI_TEST_REAL_LINUX')=='1' else ' handle /assets/terminal/v2/image.json {\n respond 404\n }\n';cfg.write_text('{\n admin off\n}\n'+ORIGIN+' {\n'+guest_rule+' handle /gateway/* {\n reverse_proxy 127.0.0.1:'+str(port)+'\n }\n handle {\n reverse_proxy 127.0.0.1:'+str(server.server_port)+'\n }\n}\n');caddy=subprocess.Popen([CADDY,'run','--config',str(cfg),'--adapter','caddyfile'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for _ in range(100):
    if caddy.poll() is not None:raise RuntimeError(caddy.stderr.read().decode())
    try:r,w=await asyncio.open_connection('127.0.0.1',PORT);w.close();await w.wait_closed();break
    except OSError:await asyncio.sleep(.05)
   else:raise RuntimeError('fixture failed to start')
   print('desktop signed fixture ready '+ORIGIN,flush=True);await asyncio.Event().wait()
  finally:
   caddy.terminate();caddy.wait(timeout=5);await runner.cleanup();await asyncio.to_thread(server.shutdown);thread.join(2);server.server_close()
try:asyncio.run(main())
except KeyboardInterrupt:pass
