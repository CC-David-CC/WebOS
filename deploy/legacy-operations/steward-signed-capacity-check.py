#!/usr/bin/env python3
"""Bounded signed WebSocket introduction load on a disposable loopback server."""
import asyncio,json,secrets,shutil,time,traceback,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
async def run():
 args,scope,port,root,seed=m.fixture();args['admission_seconds']=120;directory=args['publisher_state'].directory
 server=m.StewardServer(**args);clients=[];checks=[];started=time.monotonic();result={'status':'FAIL','checks':checks,'scope':'32 authenticated signed WebSocket clients on loopback; no browser RTC, WAN, or live server changes'}
 def check(name,value):
  assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  await server.start(port);tag=secrets.token_urlsafe(32)
  for i in range(32):
   client=m.Client(args,scope);clients.append(client);await client.open()
  check('32 independently signed sessions authenticated',len(server.registry.owners)==32)
  leases=[await c.register() for c in clients]
  for c,l in zip(clients,leases):assert await c.call('CHANNEL_ANNOUNCE',{'lease_id':l['lease_id'],'tag':tag})=={}
  check('32 leases announce one channel',server.registry.channel_bindings==32)
  timings=[]
  for c,l in zip(clients,leases):
   t=time.monotonic();response=await c.call('CHANNEL_LOOKUP',{'lease_id':l['lease_id'],'tag':tag,'limit':4});timings.append((time.monotonic()-t)*1000)
   peers=[m.jose.verify(w,m.jose.public_jwk(args['service_key']),m.LEASE) for w in response['leases']]
   assert len(peers)==4 and all(p['session_id']!=c.identity['sid'] for p in peers)
  check('each signed lookup returns four verified other leases',len(timings)==32)
  result['lookupMs']={'min':round(min(timings),3),'median':round(sorted(timings)[16],3),'max':round(max(timings),3)}
  result['egressAfterInitialLookups']=len(server.egress.entries)
  count=0
  for _ in range(16):
   for c,l in zip(clients,leases):
    response=await c.call('CHANNEL_LOOKUP',{'lease_id':l['lease_id'],'tag':tag,'limit':4});assert len(response['leases'])==4;count+=1
  result.update(additionalLookups=count,egressAfterBurst=len(server.egress.entries),elapsedSeconds=round(time.monotonic()-started,3))
  check('32 peers continue after the previous 256-message shared limit',count==512 and len(server.registry.owners)==32)
  result['status']='PASS'
 except Exception as e:result.update(error=repr(e),traceback=traceback.format_exc())
 finally:
  await asyncio.gather(*(c.close() for c in clients),return_exceptions=True);await server.close();shutil.rmtree(directory);result.update(cleanup=server.registry.snapshot(),fixtureRemoved=not directory.exists())
 return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=asyncio.run(run());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
