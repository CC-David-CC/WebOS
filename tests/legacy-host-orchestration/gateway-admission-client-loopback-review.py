#!/usr/bin/env python3
"""Run experimental JS client against actual loopback issuer/gateway; no live data."""
import asyncio,base64,importlib.util,json,os,secrets,sys
from pathlib import Path
from aiohttp import web
from cryptography.hazmat.primitives import serialization
ROOT=Path(__file__).resolve().parents[1];os.chdir(ROOT)
sys.path.insert(0,str(ROOT/'active-system/codiserver-server-v0.3.0'));import codiauth.service
sys.path.insert(0,os.environ['CODI_GATEWAY_RATE_ROOT']);import gateway_service.http
spec=importlib.util.spec_from_file_location('gateway_checks',ROOT/'active-system/scripts/gateway-http-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from origin_service.experimental_gateway_admission import AdmissionAuthority
spec=importlib.util.spec_from_file_location('gateway_service.experimental_admission',ROOT/'active-system/gateway_service/experimental_admission.py');mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
async def main():
 t=m.HTTP('runTest');await t.asyncSetUp()
 try:
  t.issuer_server.set_app(AdmissionAuthority(t.issuer));session,key=await t.enter('alice');await t.runner.cleanup()
  t.gateway=mod.ExperimentalFileGateway(t.store,t.issuer.config()['identity'],max_requests_per_minute=2048)
  original=t.gateway.handle;rotate=[False]
  async def handler(request):
   if request.path=='/test-rotate':rotate[0]=True;return web.Response(text='armed')
   if rotate[0] and request.path=='/gateway/challenge-v2':rotate[0]=False;t.gateway.admission_epoch=secrets.token_urlsafe(32)
   # Fixture stands in for the same-origin reverse proxy; Node's fetch sends the
   # loopback gateway address as Host instead of the public proxy's host.
   headers=request.headers.copy();headers['Host']=t.gateway.host
   return await original(request.clone(headers=headers))
  t.gateway.handle=handler;t.runner=web.AppRunner(t.gateway.app(),access_log=None);await t.runner.setup();site=web.TCPSite(t.runner,'127.0.0.1',0);await site.start();t.gateway_url='http://127.0.0.1:'+str(site._server.sockets[0].getsockname()[1])
  config=t.issuer.config();config['gateway']={'version':'codi-user-files/1','basePath':'/gateway'}
  der=key.private_bytes(serialization.Encoding.DER,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  env={**os.environ,'CODI_ADMISSION_TEST':json.dumps({'origin':t.origin,'gateway':t.gateway_url,'config':config,'session':session,'key':base64.b64encode(der).decode()})}
  proc=await asyncio.create_subprocess_exec('/tmp/codi-files-move-node/bin/node','tests/gateway-admission-client-review.mjs',env=env,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
  out,err=await asyncio.wait_for(proc.communicate(),30)
  if proc.returncode:raise RuntimeError('Client test failed: '+err.decode())
  print(out.decode().strip())
 finally:await t.asyncTearDown()
asyncio.run(main())
