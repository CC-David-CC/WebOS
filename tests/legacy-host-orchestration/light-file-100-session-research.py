#!/usr/bin/env python3
"""Isolated 100-session signed inventory and tiny-edit burst, no large upload."""
import asyncio, base64, hashlib, importlib.util, json, os, resource, statistics, sys, time, unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('admission_fixture',P/'file-account-admission-capacity.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from gateway_service.policy import Principal
jose=m.jose

def rss_kib():
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmRSS:'):return int(line.split()[1])
 raise RuntimeError('RSS unavailable')
def summary(values):
 if not values:return None
 a=sorted(values);return {'n':len(a),'p50_ms':round(statistics.median(a)*1000,1),'p95_ms':round(a[(len(a)*95+99)//100-1]*1000,1),'p99_ms':round(a[(len(a)*99+99)//100-1]*1000,1),'max_ms':round(a[-1]*1000,1)}
class Light(m.AccountAdmission):
 async def post(self,path,value,**kwargs):
  try:
   result=await super().post(path,value,**kwargs)
   if getattr(self,'counting',False):self.responses[('gateway' if kwargs.get('gateway') else 'issuer',result[0])]+=1
   return result
  except Exception:
   if getattr(self,'counting',False):self.responses[('gateway' if kwargs.get('gateway') else 'issuer','unparsed_or_transport')]+=1
   raise
 async def runTest(self):
  self.responses=Counter();self.counting=False;accounts=[];setup_start=time.monotonic()
  for i in range(100):
   session,key=await self.enter('light'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600)
   self.store.ensure_user(principal);self.store.put(principal,'note.txt',b'data');accounts.append((session,key,principal))
  setup=time.monotonic()-setup_start;self.issuer.c=replace(self.issuer.c,rate_per_minute=60)
  # Start with a fresh fixed gateway-rate window; bound the possible wait.
  remaining=60-time.monotonic()%60
  if remaining<15:await asyncio.sleep(remaining+.1)
  window_before=int(time.monotonic())//60;self.counting=True;times={'inventory':[],'edit':[],'recheck':[]};errors=[];stats={'rss_kib':rss_kib(),'gateway_active':0,'gateway_waiting':0,'client_inflight':0};inflight=0;stop=asyncio.Event();guard=asyncio.Event()
  async def monitor():
   while not stop.is_set():
    stats['rss_kib']=max(stats['rss_kib'],rss_kib());stats['gateway_active']=max(stats['gateway_active'],self.gateway.active);stats['gateway_waiting']=max(stats['gateway_waiting'],self.gateway.waiting)
    if stats['rss_kib']>768*1024:guard.set();return
    await asyncio.sleep(.025)
  async def work(kind,account):
   nonlocal inflight
   started=time.monotonic();inflight+=1;stats['client_inflight']=max(stats['client_inflight'],inflight);session,key,_=account
   try:
    if kind in ('inventory','recheck'):
     raw=jose.dumps({'resource':'my-files','operation':'inventory-versions'});status,result,headers=await self.authorize(session,key,raw)
     if status!=200:raise RuntimeError('authorize status '+str(status))
     status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw)
     if status!=200:raise RuntimeError('inventory status '+str(status))
     if not result['complete'] or not any(x['path']=='note.txt' and x['bytes']==4 for x in result['entries']):raise RuntimeError('invalid inventory')
    else:
     status,result,_=await self.rpc(session,key,'replace','note.txt',data=base64.b64encode(b'edit').decode(),previousSHA256=hashlib.sha256(b'data').hexdigest())
     if status!=200:raise RuntimeError('edit status '+str(status))
    times[kind].append(time.monotonic()-started)
   except Exception as error:errors.append({'kind':kind,'error':str(error)[:180]})
   finally:inflight-=1
  sampler=asyncio.create_task(monitor());start=time.monotonic();cpu=time.process_time()
  tasks=[asyncio.create_task(work('inventory',a)) for a in accounts]+[asyncio.create_task(work('edit',a)) for a in accounts[:8]]
  waiter=asyncio.create_task(guard.wait());group=asyncio.gather(*tasks)
  try:
   done,_=await asyncio.wait([group,waiter],timeout=90,return_when=asyncio.FIRST_COMPLETED)
   if group not in done:raise RuntimeError('memory guard or 90-second workload timeout')
   await group
  finally:
   for task in tasks:task.cancel()
   await asyncio.gather(*tasks,return_exceptions=True);waiter.cancel();stop.set();await sampler
  elapsed=time.monotonic()-start;cpu=time.process_time()-cpu
  initial_errors=list(errors);initial_response_counts=dict(self.responses);initial_requests=self.gateway.requests
  # A second, immediate wave demonstrates the unchanged shared per-minute
  # gateway budget; it is deliberately not retried or counted as phase-one success.
  recheck_start=time.monotonic()
  await asyncio.wait_for(asyncio.gather(*(work('recheck',a) for a in accounts[:30])),timeout=30)
  recheck_elapsed=time.monotonic()-recheck_start
  for _,_,principal in accounts[:8]:
   if self.store.read(principal,'note.txt')['bytes']!=b'edit':errors.append({'kind':'verify','error':'edit not present'})
  print(json.dumps({'scope':'isolated signed loopback single-process fixture; 100 distinct sessions each with one four-byte file; 100 simultaneous inventories and 8 tiny edits; no retries or large transfers','setup_s':round(setup,3),'workload_s':round(elapsed,3),'cpu_s':round(cpu,3),'client_operations_max_inflight':stats['client_inflight'],'gateway_active_max_sampled':stats['gateway_active'],'gateway_waiting_max_sampled':stats['gateway_waiting'],'sampled_rss_mib':round(stats['rss_kib']/1024,1),'process_peak_rss_mib':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1),'initial_responses':{f'{k[0]}:{k[1]}':v for k,v in initial_response_counts.items()},'initial_gateway_requests':initial_requests,'total_responses_after_recheck':{f'{k[0]}:{k[1]}':v for k,v in self.responses.items()},'gateway_requests_after_recheck':self.gateway.requests,'recheck_s':round(recheck_elapsed,3),'recheck':summary(times['recheck']),'same_rate_window':window_before==int(time.monotonic())//60,'inventory':summary(times['inventory']),'edit':summary(times['edit']),'initial_errors':initial_errors[:20],'initial_error_count':len(initial_errors),'all_errors_sample':errors[:20],'all_error_count':len(errors)}),flush=True)
  self.assertFalse(initial_errors,'See reported first-wave failures')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Light()]));sys.exit(not result.wasSuccessful())
