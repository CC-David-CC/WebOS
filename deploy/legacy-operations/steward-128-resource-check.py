#!/usr/bin/env python3
"""128 signed loopback clients against a separate temporary steward process."""
import asyncio,json,multiprocessing as mp,os,resource,shutil,time,traceback,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
def worker(args,port,conn):
 async def main():
  resource.setrlimit(resource.RLIMIT_NOFILE,(512,512));s=m.StewardServer(**args)
  try:
   await s.start(port);conn.send(('ready',os.getpid()))
   while not conn.poll():await asyncio.sleep(.05)
   conn.recv()
  finally:
   await s.close();conn.send(('closed',s.registry.snapshot(),len(s.socket_egress),s.wire_count))
 try:asyncio.run(main())
 except BaseException as e:conn.send(('error',repr(e)));raise
async def run():
 args,scope,port,root,seed=m.fixture();directory=args['publisher_state'].directory;args['publisher_state']=None;args['admission_seconds']=120
 parent,child=mp.get_context('fork').Pipe();p=mp.get_context('fork').Process(target=worker,args=(args,port,child));clients=[];checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks}
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def memory():
  status=Path('/proc/'+str(p.pid)+'/status').read_text().splitlines();return {k:int(next(v.split()[1] for v in status if v.startswith(k+':'))) for k in ('VmRSS','VmHWM')}
 try:
  p.start();assert parent.poll(10);msg=parent.recv();assert msg[0]=='ready',msg
  r['serverIdleKiB']=memory();tag=m.secrets.token_urlsafe(32)
  for _ in range(128):
   c=m.Client(args,scope);clients.append(c);await c.open()
  check('128 independent signed sessions connect',len(clients)==128)
  leases=[await c.register() for c in clients]
  for c,l in zip(clients,leases):assert await c.call('CHANNEL_ANNOUNCE',{'lease_id':l['lease_id'],'tag':tag})=={}
  delays=[]
  for c,l in zip(clients,leases):
   begin=time.monotonic();reply=await c.call('CHANNEL_LOOKUP',{'lease_id':l['lease_id'],'tag':tag,'limit':4});delays.append((time.monotonic()-begin)*1000);assert len(reply['leases'])==4
   for token in reply['leases']:m.jose.verify(token,m.jose.public_jwk(args['service_key']),m.LEASE)
  r['serverLoadedKiB']=memory();r['serverFds']=len(os.listdir('/proc/'+str(p.pid)+'/fd'));r['lookupMs']={'median':round(sorted(delays)[64],3),'max':round(max(delays),3)};r['elapsedSeconds']=round(time.monotonic()-started,3)
  check('128 signed clients discover other peers',len(delays)==128)
  check('server stays within its 384MiB memory and 512 descriptor budgets',r['serverLoadedKiB']['VmHWM']<384*1024 and r['serverFds']<512)
  await asyncio.gather(*(c.close() for c in clients));clients.clear();parent.send('stop');assert parent.poll(10);msg=parent.recv();check('server cleans connections and registry',msg[0]=='closed' and msg[1]['owners']==0 and msg[2:]==(0,0));r['status']='PASS'
 except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
 finally:
  await asyncio.gather(*(c.close() for c in clients if hasattr(c,'ws')),return_exceptions=True)
  if p.is_alive():
   try:parent.send('stop')
   except Exception:pass
   p.join(10)
   if p.is_alive():p.terminate();p.join(5);r['status']='FAIL';r['cleanupError']='server did not stop promptly'
  if p.pid and p.exitcode!=0:r['status']='FAIL';r['workerExit']=p.exitcode
  parent.close();child.close();shutil.rmtree(directory);r['fixtureRemoved']=not directory.exists()
 return r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=asyncio.run(run());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
