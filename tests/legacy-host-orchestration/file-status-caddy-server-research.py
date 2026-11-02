#!/usr/bin/env python3
"""Disposable Caddy -> loopback issuer/gateway fixture; no real account state."""
import asyncio, importlib.util, os, pathlib, shutil, subprocess, sys, tempfile, threading
from wsgiref.simple_server import make_server
from aiohttp import web
ROOT=pathlib.Path(__file__).resolve().parents[1]/'active-system';sys.path.insert(0,str(ROOT))
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from gateway_service.http import FileGateway
async def main():
 with tempfile.TemporaryDirectory(prefix='codi-caddy-files-') as tmp:
  root=pathlib.Path(tmp);public=root/'public';public.mkdir();(public/'index.html').write_text('<!doctype html><title>Isolated Caddy file test</title>')
  for d in ('network','gateway_service','storage/browser'):(public/d).mkdir(parents=True,exist_ok=True)
  for d,names in [('network',('crypto.mjs','identity.mjs','strict-json.mjs')),('gateway_service',('client.mjs',)),('storage/browser',('mirror.mjs',))]:
   for n in names:shutil.copy2(ROOT/d/n,public/d/n)
  # The combined file client loads its verifier beside the served client.
  (public/'gateway_service/hash').mkdir()
  for n in ('core.mjs','shared.mjs','verify-worker.mjs'):shutil.copy2(ROOT/'gateway_service/vendor/js-sha256'/n,public/'gateway_service/hash'/n)
  origin='http://127.0.0.1:19864';issuer=Service(Config(root/'issuer',public,origin=origin,rate_per_minute=60));server=make_server('127.0.0.1',0,GatewayAuthority(issuer),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);store=UserStore(state,data);initialize_ledger(store);initialize_transfers(store)
  gateway=FileGateway(store,issuer.config()['identity'],max_requests_per_minute=2048);runner=web.AppRunner(gateway.app(),access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();gport=site._server.sockets[0].getsockname()[1]
  proxy=None
  if os.environ.get('CODI_USE_SOCKET_PROXY')=='1':
   proxy=subprocess.Popen([sys.executable,str(pathlib.Path(__file__).with_name('light-file-socket-proxy-launch.py')),str(gport)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   await asyncio.sleep(.25)
   if proxy.poll() is not None:raise RuntimeError('isolated socket proxy exited: '+proxy.stderr.read().decode(errors='replace'))
   gport=19865
  gate=None;gate_runner=None
  if os.environ.get('CODI_LAYERED')=='1':
   if proxy is None:raise RuntimeError('layered test requires isolated socket proxy')
   spec=importlib.util.spec_from_file_location('gate_proto',pathlib.Path(__file__).with_name('layered-file-gate-research.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);gate=mod.Gate('http://127.0.0.1:19865');await gate.start();gate_app=web.Application(client_max_size=192*1024*1024);gate_app.router.add_route('*','/{tail:.*}',gate.handle);gate_runner=web.AppRunner(gate_app,access_log=None);await gate_runner.setup();await web.TCPSite(gate_runner,'127.0.0.1',19867).start();gport=19867
  cfg=root/'Caddyfile';cfg.write_text('http://127.0.0.1:19864 {\n handle /gateway/* {\n reverse_proxy 127.0.0.1:'+str(gport)+'\n }\n handle {\n reverse_proxy 127.0.0.1:'+str(server.server_port)+'\n }\n}\n')
  # Opt-in proxy matches the live 16-connection limit; TLS remains absent.
  caddy=subprocess.Popen(['/tmp/codi-microduck-hosting-evidence/caddy','run','--config',str(cfg),'--adapter','caddyfile'],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   for _ in range(100):
    if caddy.poll() is not None:raise RuntimeError('isolated Caddy exited')
    try:
     r,w=await asyncio.open_connection('127.0.0.1',19864);w.close();await w.wait_closed();break
    except OSError:await asyncio.sleep(.05)
   else:raise RuntimeError('isolated Caddy did not start')
   print('isolated caddy fixture ready 127.0.0.1:19864',flush=True);await asyncio.Event().wait()
  finally:
   caddy.terminate()
   try:caddy.wait(timeout=5)
   except subprocess.TimeoutExpired:caddy.kill();caddy.wait()
   if gate_runner is not None:await gate_runner.cleanup();await gate.close()
   if proxy is not None:
    proxy.terminate()
    try:proxy.wait(timeout=5)
    except subprocess.TimeoutExpired:proxy.kill();proxy.wait()
   await runner.cleanup();await asyncio.to_thread(server.shutdown);thread.join(2);server.server_close()
try:asyncio.run(main())
except KeyboardInterrupt:pass
