#!/usr/bin/env python3
"""Unauthenticated slow challenge bodies against an isolated proxy fixture."""
import asyncio,importlib.util,json,resource,sys,time,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('slow_fixture',P/'light-file-slow-contention-research.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from gateway_service.policy import Principal
from dataclasses import replace
jose=m.jose
class Preauth(m.Contention):
 async def runTest(self):
  accounts=[];setup=time.monotonic()
  for i in range(100):
   session,key=await self.enter('preauth'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.store.ensure_user(principal);self.store.put(principal,'note.txt',b'data');accounts.append((session,key,principal))
  setup=time.monotonic()-setup;self.issuer.c=replace(self.issuer.c,rate_per_minute=60);streams=[];tasks=[];peak=m.rss_kib();max_active=0;max_wait=0;failures=[];latencies=[]
  try:
   # Incomplete, unauthenticated JSON challenge bodies: no signed proof is
   # required for this phase. Do not point this isolated test at live hosts.
   for _ in range(16):
    reader,writer=await asyncio.open_connection('127.0.0.1',19866);header=('POST /gateway/challenge HTTP/1.1\r\nHost: 127.0.0.1:19866\r\nOrigin: '+self.origin+'\r\nContent-Type: application/json\r\nContent-Length: 100\r\nConnection: close\r\n\r\n').encode();writer.write(header+b'{');await writer.drain();streams.append((reader,writer))
   for _ in range(40):
    if self.gateway.active==4 and self.gateway.waiting>=10:break
    await asyncio.sleep(.025)
   print(json.dumps({'phase':'preauth-stalled','active':self.gateway.active,'waiting':self.gateway.waiting,'connections_open':len(streams)}),flush=True)
   self.assertEqual(self.gateway.active,4);self.assertGreaterEqual(self.gateway.waiting,10)
   self.responses.clear();self.counting=True;started=time.monotonic()
   async def monitor():
    nonlocal peak,max_active,max_wait
    while True:
     peak=max(peak,m.rss_kib());max_active=max(max_active,self.gateway.active);max_wait=max(max_wait,self.gateway.waiting)
     if peak>768*1024:raise RuntimeError('memory guard exceeded')
     await asyncio.sleep(.025)
   async def work(account):
    start=time.monotonic();session,key,_=account
    try:
     raw=jose.dumps({'resource':'my-files','operation':'inventory-versions'});status,out,headers=await self.authorize(session,key,raw)
     if status!=200:raise RuntimeError('authorize '+str(status))
     status,out,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw)
     if status!=200:raise RuntimeError('inventory '+str(status))
     latencies.append(time.monotonic()-start)
    except Exception as error:failures.append({'type':type(error).__name__,'message':str(error)[:120],'after_s':round(time.monotonic()-start,3)})
   monitor_task=asyncio.create_task(monitor());tasks=[asyncio.create_task(work(a)) for a in accounts]
   try:
    await asyncio.sleep(7)
    if monitor_task.done():await monitor_task
    snapshot={'success':len(latencies),'failures':len(failures),'active':self.gateway.active,'waiting':self.gateway.waiting}
    done,pending=await asyncio.wait(tasks,timeout=15)
   finally:
    monitor_task.cancel();await asyncio.gather(monitor_task,return_exceptions=True)
    for task in tasks:task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
   print(json.dumps({'scope':'isolated Caddy + 16 socket-proxy connections; 16 incomplete unauthenticated challenge bodies, then 100 signed light inventories, no retry','setup_s':round(setup,3),'elapsed_s':round(time.monotonic()-started,3),'after_7s':snapshot,'success':len(latencies),'failures':len(failures),'pending_cancelled':len(pending),'responses':{f'{a}:{b}':n for (a,b),n in self.responses.items()},'failure_sample':failures[:8],'gateway_active_max':max_active,'gateway_waiting_max':max_wait,'sampled_rss_mib':round(peak/1024,1),'process_peak_rss_mib':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)}),flush=True)
  finally:
   for _,writer in streams:writer.close()
   await asyncio.gather(*(writer.wait_closed() for _,writer in streams),return_exceptions=True)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Preauth()]));sys.exit(not result.wasSuccessful())
