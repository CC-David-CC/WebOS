#!/usr/bin/env python3
"""Isolated 100-session signed inventory and tiny-edit burst, no large upload."""
import asyncio, base64, hashlib, importlib.util, json, os, random, resource, statistics, sys, time, unittest
from collections import Counter
from aiohttp import ClientConnectionError, ClientPayloadError, ClientSession, ClientTimeout, TCPConnector
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
class Retryable(Exception):
 pass
class Light(m.AccountAdmission):
 async def start_gateway(self,**kwargs):
  kwargs.setdefault('max_requests_per_minute',2048);return await super().start_gateway(**kwargs)
 async def post(self,path,value,**kwargs):
  try:
   result=await super().post(path,value,**kwargs)
   if getattr(self,'counting',False):
    self.responses[('gateway' if kwargs.get('gateway') else 'issuer',result[0])]+=1
    if result[0] in (429,503):raise Retryable(str(result[0]))
   return result
  except Retryable:raise
  except (ClientConnectionError, ClientPayloadError, OSError) as error:
   if getattr(self,'counting',False):
    self.responses[('gateway' if kwargs.get('gateway') else 'issuer','transport')]+=1
    self.diagnostics.append({'path':path,'error_type':type(error).__name__,'message':str(error)[:120]})
   raise Retryable('transport') from error
  except Exception:
   if getattr(self,'counting',False):self.responses[('gateway' if kwargs.get('gateway') else 'issuer','unparsed_or_transport')]+=1
   raise
 async def runTest(self):
  if os.environ.get('CODI_FRESH_CONNECTIONS')=='1':
   await self.client.close();self.client=ClientSession(timeout=ClientTimeout(total=60),trust_env=False,connector=TCPConnector(force_close=True))
  elif os.environ.get('CODI_POOL_LIMIT')=='20':
   await self.client.close();self.client=ClientSession(timeout=ClientTimeout(total=60),trust_env=False,connector=TCPConnector(limit=20,keepalive_timeout=2 if os.environ.get('CODI_POOL_KEEPALIVE')=='2' else 15))
  self.responses=Counter();self.diagnostics=[];self.counting=False;accounts=[];setup_start=time.monotonic()
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
  retries=Counter()
  async def work(kind,account):
   nonlocal inflight
   started=time.monotonic();inflight+=1;stats['client_inflight']=max(stats['client_inflight'],inflight);session,key,_=account
   try:
    for attempt in range(3):
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
      times[kind].append(time.monotonic()-started);return
     except Retryable as error:
      # Mirror's rate-limited automatic retry is ~24–36 seconds initially.
      # A write is not retried here because an ambiguous outcome needs CAS.
      if kind=='edit' or attempt==2:raise
      retries[str(error)]+=1;await asyncio.sleep(random.uniform(24,36) if str(error)=='429' else random.uniform(12,18))
   except Exception as error:errors.append({'kind':kind,'error':str(error)[:180]})
   finally:inflight-=1
  sampler=asyncio.create_task(monitor());start=time.monotonic();cpu_start=time.process_time();waiter=asyncio.create_task(guard.wait());waves=[]
  async def wave(number):
   begin=time.monotonic();before=len(times['inventory'] if number==0 else times['recheck']);kind='inventory' if number==0 else 'recheck'
   tasks=[asyncio.create_task(work(kind,a)) for a in accounts]
   if number==0:tasks += [asyncio.create_task(work('edit',a)) for a in accounts[:8]]
   group=asyncio.gather(*tasks)
   try:
    done,_=await asyncio.wait([group,waiter],timeout=120,return_when=asyncio.FIRST_COMPLETED)
    if group not in done:raise RuntimeError('memory guard or workload timeout')
    await group
   finally:
    for task in tasks:task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
   current=times[kind][before:];waves.append({'wave':number+1,'elapsed_s':round(time.monotonic()-begin,3),'inventory':summary(current)})
  try:
   await wave(0)
   for number in (1,2):
    await asyncio.sleep(5);await wave(number)
  finally:
   waiter.cancel();stop.set();await sampler
  elapsed=time.monotonic()-start;cpu=time.process_time()-cpu_start
  for _,_,principal in accounts[:8]:
   if self.store.read(principal,'note.txt')['bytes']!=b'edit':errors.append({'kind':'verify','error':'edit not present'})
  print(json.dumps({'scope':'isolated signed loopback single-process fixture; 100 sessions, three consecutive simultaneous inventory waves 5 seconds apart and eight four-byte edits in first wave; inventory retry on 429 with 24–36s jitter; 503/transport with 12–18s jitter; no large uploads','fresh_connections':os.environ.get('CODI_FRESH_CONNECTIONS')=='1','connector_limit':20 if os.environ.get('CODI_POOL_LIMIT')=='20' else 100,'client_keepalive_s':2 if os.environ.get('CODI_POOL_KEEPALIVE')=='2' else 15,'setup_s':round(setup,3),'total_s':round(elapsed,3),'cpu_s':round(cpu,3),'client_operations_max_inflight':stats['client_inflight'],'gateway_active_max_sampled':stats['gateway_active'],'gateway_waiting_max_sampled':stats['gateway_waiting'],'sampled_rss_mib':round(stats['rss_kib']/1024,1),'process_peak_rss_mib':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1),'responses':{f'{k[0]}:{k[1]}':v for k,v in self.responses.items()},'gateway_requests_in_current_window':self.gateway.requests,'same_rate_window':window_before==int(time.monotonic())//60,'retries':dict(retries),'transport_diagnostics':self.diagnostics[:30],'waves':waves,'edit':summary(times['edit']),'errors_sample':errors[:20],'error_count':len(errors)}),flush=True)
  self.assertFalse(errors,'See reported workload failures')
  self.assertEqual(len(times['inventory']),100);self.assertEqual(len(times['recheck']),200);self.assertEqual(len(times['edit']),8)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Light()]));sys.exit(not result.wasSuccessful())
