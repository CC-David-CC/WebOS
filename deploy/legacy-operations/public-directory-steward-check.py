#!/usr/bin/env python3
"""Authenticated WebSocket public metadata persists across steward restart."""
import asyncio,importlib.util,json,shutil,subprocess,sys,time,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));import types;f=types.ModuleType('fixture');f.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],f.__dict__)
from steward.server import StewardServer
async def main():
 args,scope,port,root,seed=f.fixture();directory=args['publisher_state'].directory;now=int(time.time());records=json.loads(subprocess.check_output([str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'),str(ROOT/'scripts/public-directory-signed-fixture.mjs'),str(now)],text=True));checks=[];server=None;clients=[]
 def check(name,ok):
  if not ok:raise AssertionError(name)
  checks.append(name)
 async def open_client():
  c=f.Client(args,scope);clients.append(c);await c.open();lease=await c.register();return c,lease['lease_id']
 try:
  server=StewardServer(**args);await server.start(port);a,lease=await open_client();reply=await a.call('INDEX_PUBLISH',{'lease_id':lease,'wire':records['a']['listing']});check('owner-signed public listing is accepted over authenticated WebSocket',bool(reply.get('sequence')))
  duplicate=await a.call('INDEX_PUBLISH',{'lease_id':lease,'wire':records['a']['listing']});check('unchanged signed listing does not advance the feed',duplicate.get('sequence') is None)
  page=await a.call('INDEX_SEARCH',{'lease_id':lease,'query':'alpha','after':'','limit':2});check('signed reference can be searched without copying a code',len(page['items'])==1 and page['items'][0]['wire']==records['a']['listing'])
  peer,peer_lease=await open_client();entered=threading.Event();release=threading.Event();original=server.public_directory.publish
  def held(*values):
   entered.set()
   if not release.wait(5):raise TimeoutError('fixture held too long')
   return original(*values)
  server.public_directory.publish=held;pending=asyncio.create_task(a.call('INDEX_PUBLISH',{'lease_id':lease,'wire':records['b']['listing']}))
  try:
   assert await asyncio.to_thread(entered.wait,3);started=time.monotonic();reply=await peer.call('JOIN_LOOKUP',{'lease_id':peer_lease,'limit':4});check('slow directory disk work does not block peer introductions',time.monotonic()-started<1 and 'leases' in reply)
  finally:release.set();await pending;server.public_directory.publish=original
  await peer.close();clients.remove(peer)
  await a.close();clients.remove(a);await server.close();server=StewardServer(**args);await server.start(port);b,lease=await open_client();page=await b.call('INDEX_SEARCH',{'lease_id':lease,'query':'alpha','after':'','limit':2});check('listing survives steward restart with no owner online',len(page['items'])==1 and page['items'][0]['wire']==records['a']['listing'])
  try:result=await b.call('INDEX_PUBLISH',{'lease_id':lease,'wire':records['privateChannel']['listing']});refused=result=={'error':'unavailable'}
  except f.ConnectionClosed:refused=True
  check('private reference is refused',refused)
 finally:
  for c in clients:
   try:await c.close()
   except Exception:pass
  if server:await server.close()
  shutil.rmtree(directory)
 args2,scope2,port2,_,_=f.fixture();directory2=args2['publisher_state'].directory;badpath=directory2/'public-channels.sqlite3';badpath.write_bytes(b'not a sqlite database');badpath.chmod(0o600);broken=None;left=right=None
 try:
  broken=StewardServer(**args2);await broken.start(port2);left=f.Client(args2,scope2);right=f.Client(args2,scope2);await left.open();await right.open();l=await left.register();await right.register();result=await left.call('INDEX_SEARCH',{'lease_id':l['lease_id'],'query':'','after':'','limit':2});sample=await left.call('JOIN_LOOKUP',{'lease_id':l['lease_id'],'limit':4});check('corrupt directory fails closed while peer introductions still work',result=={'error':'unavailable'} and len(sample['leases'])==1 and badpath.read_bytes()==b'not a sqlite database')
 finally:
  if left:await left.close()
  if right:await right.close()
  if broken:await broken.close()
  shutil.rmtree(directory2)
 print(json.dumps({'status':'PASS','checks':checks,'scope':'real signed WebSocket and private SQLite; no live deployment'}))
asyncio.run(main())
