#!/usr/bin/env python3
"""Signed reconnect burst on a disposable, unchanged-limit loopback steward."""
import asyncio,json,shutil,time,traceback,types,resource,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
async def run():
 args,scope,port,root,seed=m.fixture();args['admission_seconds']=120;directory=args['publisher_state'].directory;server=m.StewardServer(**args);clients=[];checks=[];started=time.monotonic();r={'status':'FAIL','checks':checks,'scope':__doc__}
 def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  await server.start(port)
  for _ in range(32):
   c=m.Client(args,scope);clients.append(c);await c.open()
  check('32 clients sign in',len(server.registry.owners)==32)
  await asyncio.gather(*(c.close() for c in clients))
  for _ in range(100):
   if not server.registry.owners:break
   await asyncio.sleep(.01)
  check('first wave disconnects and frees slots',len(server.registry.owners)==0 and server.wire_count==0)
  for c in clients:await c.open()
  check('all 32 signed sessions reconnect',len(server.registry.owners)==32)
  extra=m.Client(args,scope);clients.append(extra);await extra.open()
  check('new session can join after reconnect burst',len(server.registry.owners)==33)
  for _ in range(95):
   c=m.Client(args,scope);clients.append(c);await c.open()
  check('128 simultaneous signed sessions fit',len(server.registry.owners)==128 and server.wire_count==128)
  tag=m.secrets.token_urlsafe(32);leases=[await c.register() for c in clients]
  for c,l in zip(clients,leases):assert await c.call('CHANNEL_ANNOUNCE',{'lease_id':l['lease_id'],'tag':tag})=={}
  delays=[]
  for c,l in zip(clients,leases):
   before=time.monotonic();reply=await c.call('CHANNEL_LOOKUP',{'lease_id':l['lease_id'],'tag':tag,'limit':4});delays.append((time.monotonic()-before)*1000)
   found=[m.jose.verify(w,m.jose.public_jwk(args['service_key']),m.LEASE) for w in reply['leases']]
   assert len(found)==4 and all(p['session_id']!=c.identity['sid'] for p in found)
  r['lookupMs']={'median':round(sorted(delays)[64],3),'max':round(max(delays),3)};r['egressPayloadBytes']=server.egress.bytes
  check('128 signed sessions announce and discover peers',len(server.registry.leases)==128 and server.registry.channel_bindings==128)
  blocked=m.Client(args,scope);clients.append(blocked);failed=None
  try:await blocked.open()
  except Exception as e:failed=type(e).__name__
  check('129th concurrent connection is refused',failed is not None and len(server.registry.owners)==128)
  await extra.close()
  for _ in range(100):
   if len(server.registry.owners)==127 and server.wire_count==127:break
   await asyncio.sleep(.01)
  replacement=m.Client(args,scope);clients.append(replacement);await replacement.open()
  check('freed slot immediately accepts a new session',len(server.registry.owners)==128)
  r.update(starts=len(server.starts),owners=len(server.registry.owners),fullFailure=failed,peakRssKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,processFds=len(os.listdir('/proc/self/fd')),elapsedSeconds=round(time.monotonic()-started,3))
  r['status']='PASS'
 except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
 finally:
  await asyncio.gather(*(c.close() for c in clients if hasattr(c,'ws')),return_exceptions=True);await server.close();shutil.rmtree(directory);r.update(cleanup=server.registry.snapshot(),fixtureRemoved=not directory.exists())
 return r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=asyncio.run(run());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
