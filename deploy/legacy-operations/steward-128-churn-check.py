#!/usr/bin/env python3
"""Five 128-session signed discovery/renewal/churn rounds on a separate loopback steward."""
import asyncio,importlib.util,json,os,shutil,time,traceback,multiprocessing as mp
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('resource_case',ROOT/'scripts/steward-128-resource-check.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);m=b.m
async def run(rounds=5):
 args,scope,port,root,seed=m.fixture();directory=args['publisher_state'].directory;args['publisher_state']=None;args['admission_seconds']=120
 parent,child=mp.get_context('fork').Pipe();server=mp.get_context('fork').Process(target=b.worker,args=(args,port,child));clients=[];leases=[];checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'rounds':[]}
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def stats():
  st=Path('/proc/'+str(server.pid)+'/status').read_text().splitlines();return {'rssKiB':int(next(v.split()[1] for v in st if v.startswith('VmRSS:'))),'hwmKiB':int(next(v.split()[1] for v in st if v.startswith('VmHWM:'))),'fds':len(os.listdir('/proc/'+str(server.pid)+'/fd'))}
 async def start(c):
  c.sequence=0;await c.open();lease=await c.register();assert await c.call('CHANNEL_ANNOUNCE',{'lease_id':lease['lease_id'],'tag':tag})=={};return lease
 try:
  server.start();assert parent.poll(10);msg=parent.recv();assert msg[0]=='ready',msg;tag=m.secrets.token_urlsafe(32)
  for _ in range(128):
   c=m.Client(args,scope);clients.append(c);leases.append(await start(c))
  check('128 signed sessions registered and announced',len(clients)==128)
  for cycle in range(rounds):
   await asyncio.sleep(4)
   indexes=[(cycle*16+i)%128 for i in range(16)]
   await asyncio.gather(*(clients[i].close() for i in indexes))
   for i in indexes:leases[i]=await start(clients[i])
   delays=[];wire_bytes=0
   for i,c in enumerate(clients):
    if i not in indexes:
     signed=(await c.call('RENEW',{'lease_id':leases[i]['lease_id'],'counter':leases[i]['renewal_counter']+1}))['lease'];leases[i]=m.jose.verify(signed,m.jose.public_jwk(args['service_key']),m.LEASE)
    before=time.monotonic();reply=await c.call('CHANNEL_LOOKUP',{'lease_id':leases[i]['lease_id'],'tag':tag,'limit':4});delays.append((time.monotonic()-before)*1000);assert len(reply['leases'])==4
    for token in reply['leases']:
     wire_bytes+=len(token.encode());record=m.jose.verify(token,m.jose.public_jwk(args['service_key']),m.LEASE);assert record['session_id']!=c.identity['sid']
   r['rounds'].append({'number':cycle+1,'reconnected':len(indexes),'lookups':len(delays),'lookupMedianMs':round(sorted(delays)[64],2),'lookupMaxMs':round(max(delays),2),'signedSampleBytes':wire_bytes,'server':stats()})
   print(json.dumps({'round':cycle+1,**r['rounds'][-1]['server']}),flush=True)
  check('all rounds renew leases and discover signed peers after reconnects',len(r['rounds'])==rounds)
  check('server resource measurements remain below configured budgets',all(x['server']['hwmKiB']<384*1024 and x['server']['fds']<512 for x in r['rounds']))
  await asyncio.gather(*(c.close() for c in clients));clients.clear();parent.send('stop');assert parent.poll(10);msg=parent.recv();check('server cleans registry and connection state',msg[0]=='closed' and msg[1]['owners']==0 and msg[2:]==(0,0));r['status']='PASS'
 except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
 finally:
  await asyncio.gather(*(c.close() for c in clients if hasattr(c,'ws')),return_exceptions=True)
  if server.is_alive():
   try:parent.send('stop')
   except Exception:pass
   server.join(10)
   if server.is_alive():server.terminate();server.join(5);r.update(status='FAIL',cleanupError='server did not stop')
  if server.pid and server.exitcode!=0:r.update(status='FAIL',workerExit=server.exitcode)
  parent.close();child.close();shutil.rmtree(directory);r.update(fixtureRemoved=not directory.exists(),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--rounds',type=int,default=5,choices=range(1,21));a=p.parse_args();assert not a.output.exists();r=asyncio.run(run(a.rounds));a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
