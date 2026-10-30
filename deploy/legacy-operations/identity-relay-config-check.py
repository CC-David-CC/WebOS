#!/usr/bin/env python3
"""Real loopback config composition; configured issuer failure never falls back."""
import asyncio,importlib.util,json,sys
from pathlib import Path
from aiohttp import web,ClientSession
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('guest_relay',ROOT/'guest-relay/server.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
ORIGIN='https://127.0.0.1:8446'
async def start(handler,wildcard=False):
 app=web.Application();app.router.add_get('/{path:.*}' if wildcard else '/config.json',handler);runner=web.AppRunner(app,access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();return runner,site._server.sockets[0].getsockname()[1]
async def main():
 results=[]
 for case in ['valid','split','wrong-origin','local-mode','oversize','non-object','bad-json','redirect','unavailable']:
  async def source(request):
   assert request.headers['Host']=='127.0.0.1:8446'
   if case=='redirect':raise web.HTTPFound('/elsewhere')
   if case=='non-object':return web.json_response([])
   if case=='bad-json':return web.Response(body=b'{broken')
   if case=='oversize':return web.Response(body=b' '*65537)
   config={'identity':{'mode':'local-development' if case=='local-mode' else 'server','issuer':'https://wrong.invalid' if case=='wrong-origin' else ORIGIN},'rtc':{'iceServers':[]}}
   if case=='split':
    response=web.StreamResponse();await response.prepare(request);data=json.dumps(config).encode();await response.write(data[:7]);await asyncio.sleep(.01);await response.write(data[7:]);await response.write_eof();return response
   return web.json_response(config)
  issuer,port=await start(source)
  if case=='unavailable':await issuer.cleanup()
  relay=module.Relay(ORIGIN,identity_config_port=port);frontend,front_port=await start(relay.assets,True)
  try:
   async with ClientSession() as client:
    async with client.get(f'http://127.0.0.1:{front_port}/config.json') as response:
     if case in ['valid','split']:
      assert response.status==200;config=await response.json();assert config['identity']['mode']=='server' and config['guestNetwork']['relayPath']=='/guest-network'
     else:assert response.status==502 and 'local-development' not in await response.text()
   results.append({'case':case,'status':'PASS'})
  finally:await frontend.cleanup();await issuer.cleanup()
 report={'status':'PASS','scope':'Real loopback HTTP config composition; no public rollout','cases':results}
 (ROOT/'.build/checks/identity-relay-config-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
asyncio.run(main())
