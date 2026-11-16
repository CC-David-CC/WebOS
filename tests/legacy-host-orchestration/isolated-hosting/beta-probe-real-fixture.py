#!/usr/bin/env python3
"""Real sealed issuer/gateway with disposable local account state; fixture only."""
import asyncio,hashlib,json,os,pathlib,socket,subprocess,sys,tempfile,time,urllib.request
from aiohttp import web
root=pathlib.Path(sys.argv[1]);native=pathlib.Path(sys.argv[2]);worker=pathlib.Path(sys.argv[3]);python=sys.executable
sys.path[:0]=[str(worker),str(worker/'codiserver-server-v0.3.0')]
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway

def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
async def main():
 issuer_port=port();origin='http://127.0.0.1:'+str(port());cmd=[python,'-B',str(native/'scripts/serve-connected.py'),'--port',str(issuer_port),'--runtime-dir',str(root/'runtime'),'--origin',origin,'--user-files']
 process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);runner=None
 try:
  for _ in range(150):
   if process.poll() is not None:raise RuntimeError('issuer fixture exited')
   try:
    with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{issuer_port}/config.json',headers={'Host':origin.split('//')[1]}),timeout=.5) as r:config=json.load(r)
    break
   except OSError:await asyncio.sleep(.05)
  else:raise RuntimeError('issuer fixture unavailable')
  for name in ('gateway','files'):(root/name).mkdir(mode=0o700)
  store=UserStore(root/'gateway',root/'files');initialize_ledger(store);initialize_transfers(store)
  gateway=FileGateway(store,config['identity'],max_requests_per_minute=2048);runner=web.AppRunner(gateway.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gateway_port=site._server.sockets[0].getsockname()[1]
  (root/'policy.json').write_text(json.dumps({'identity':config['identity']},sort_keys=True,separators=(',',':')));(root/'ready.json').write_text(json.dumps({'origin':origin,'issuer':issuer_port,'gateway':gateway_port}));print('ready',flush=True)
  await asyncio.Event().wait()
 finally:
  if runner:await runner.cleanup()
  if process.poll() is None:process.terminate();process.wait(timeout=10)
try:asyncio.run(main())
except KeyboardInterrupt:pass
