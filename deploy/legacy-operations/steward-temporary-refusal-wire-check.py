#!/usr/bin/env python3
"""Exercise actual steward close codes for duplicate sessions and invalid authentication."""
import asyncio,json,sys,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
f=types.ModuleType('fixture');f.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],f.__dict__)
from websockets.exceptions import ConnectionClosed
async def main():
 args,scope,port,_,_=f.fixture();server=f.StewardServer(**args);await server.start(port);checks=[];clients=[]
 async def expect_close(client,code,patch=None):
  try:await client.open(patch);raise AssertionError('unexpected authentication success')
  except ConnectionClosed as e:assert e.rcvd and e.rcvd.code==code,(code,e.rcvd)
 try:
  original=f.Client(args,scope);clients.append(original);await original.open();await original.register()
  duplicate=f.Client(args,scope);duplicate.key=original.key;duplicate.identity=original.identity;clients.append(duplicate);await expect_close(duplicate,1013);checks.append('duplicate active session receives retryable refusal')
  await original.close()
  for _ in range(100):
   if not server.registry.owners:break
   await asyncio.sleep(.05)
  assert not server.registry.owners
  returning=f.Client(args,scope);returning.key=original.key;returning.identity=original.identity;clients.append(returning);await returning.open();await returning.register();checks.append('same session authenticates after previous socket closes')
  invalid=f.Client(args,scope);clients.append(invalid);await expect_close(invalid,1008,{'nonce':'wrong-nonce'});checks.append('invalid authentication remains a policy failure')
 finally:
  await asyncio.gather(*(c.close() for c in clients if hasattr(c,'ws')),return_exceptions=True);await server.close()
 print(json.dumps({'status':'PASS','checks':checks,'scope':'Actual local steward and signed WebSocket sessions; no browser or live deployment.'},indent=2))
asyncio.run(asyncio.wait_for(main(),30))
