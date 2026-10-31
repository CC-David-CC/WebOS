#!/usr/bin/env python3
"""Bounded local 100-account mixed storage exercise; not a production capacity test."""
import asyncio,base64,hashlib,importlib.util,json,os,resource,statistics,sys,time,unittest
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('admission_fixture',ROOT/'file-account-admission-capacity.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from gateway_service.policy import Principal
jose=module.jose
def memory():
 fields={}
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith(('VmRSS:','VmHWM:','Threads:')):
   key,value=line.split(':',1);fields[key]=int(value.strip().split()[0])
 return fields
class Mixed(module.AccountAdmission):
 async def runTest(self):
  accounts=[];setup_samples=[];started=time.monotonic();before_setup=memory()
  for i in range(100):
   session,key=await self.enter('mixed'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.store.ensure_user(principal);self.store.put(principal,'note.txt',b'data');accounts.append((session,key,principal))
   if (i+1)%10==0:setup_samples.append({'accounts':i+1,**memory()})
  setup=time.monotonic()-started;self.issuer.c=replace(self.issuer.c,rate_per_minute=60);remaining=60-time.monotonic()%60
  if remaining<15:await asyncio.sleep(remaining+.1)
  burst=os.environ.get('CODI_BURST')=='1';unsmoothed=os.environ.get('CODI_UNSMOOTHED')=='1';semaphore=asyncio.Semaphore(128 if unsmoothed else 100 if burst else 3);latency={'inventory':[],'edit':[],'upload':[]};service={'inventory':[],'edit':[],'upload':[]};launch=time.monotonic();payload=b'x'*(8*1024*1024);digest=hashlib.sha256(b'data').hexdigest()
  async def work(kind,account):
   queued=time.monotonic()
   async with semaphore:
    start=time.monotonic();session,key,_=account
    if kind=='inventory':
     raw=jose.dumps({'resource':'my-files','operation':'inventory-versions'});status,result,headers=await self.authorize(session,key,raw);self.assertEqual(status,200,result);status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw);self.assertEqual(status,200,result);self.assertTrue(result['complete']);self.assertEqual(result['entries'][0]['bytes'],4)
    elif kind=='edit':
     status,result,_=await self.rpc(session,key,'replace','note.txt',data=base64.b64encode(b'edit').decode(),previousSHA256=digest);self.assertEqual(status,200,result)
    else:
     status,result,_,_=await self.binary_upload(session,key,'upload.bin',payload);self.assertEqual(status,200,result);self.assertEqual(result['sha256'],hashlib.sha256(payload).hexdigest())
    elapsed=time.monotonic();service[kind].append(elapsed-start);latency[kind].append(elapsed-queued)
  if burst:
   results=await asyncio.gather(*(work('inventory',account) for account in accounts),return_exceptions=True)
   failures=[str(x)[:160] for x in results if isinstance(x,BaseException)]
   print(json.dumps({'scope':'local fixture: 100 signed inventory operations started simultaneously, no retry','successes':100-len(failures),'failures':len(failures),'sampleErrors':failures[:3],'elapsedSeconds':round(time.monotonic()-launch,3),'gatewayRequests':self.gateway.requests,'memoryAfter':memory()}),flush=True)
   return
  tasks=[asyncio.create_task(work('upload',accounts[99]))]
  for i,account in enumerate(accounts):
   tasks.append(asyncio.create_task(work('inventory',account)))
   if i<8:tasks.append(asyncio.create_task(work('edit',account)))
  await asyncio.gather(*tasks)
  for _,_,p in accounts[:8]:self.assertEqual(self.store.read(p,'note.txt')['bytes'],b'edit')
  self.assertEqual(self.store.read(accounts[99][2],'upload.bin')['sha256'],hashlib.sha256(payload).hexdigest())
  def summary(values):
   ordered=sorted(values);return {'count':len(values),'p50Ms':round(statistics.median(values)*1000,1),'p95Ms':round(ordered[max(0,(len(values)*95+99)//100-1)]*1000,1),'maxMs':round(ordered[-1]*1000,1)}
  print(json.dumps({'scope':('local single-process HTTP fixture; 100 independent accounts, one file each, 8 edits, one 8 MiB upload, '+('unsmoothed concurrency' if unsmoothed else 'application-controlled concurrency 3')+'; not 100-browser or sustained capacity'),'setupSeconds':round(setup,3),'memoryBeforeSetup':before_setup,'memoryDuringSetup':setup_samples,'memoryAfterWorkload':memory(),'workloadSeconds':round(time.monotonic()-launch,3),'gatewayRequests':self.gateway.requests,'endToEnd':{k:summary(v) for k,v in latency.items()},'serviceTime':{k:summary(v) for k,v in service.items()},'peakProcessRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),flush=True)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Mixed()]));sys.exit(not result.wasSuccessful())
