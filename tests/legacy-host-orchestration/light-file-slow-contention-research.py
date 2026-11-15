#!/usr/bin/env python3
"""Four deliberately paused uploads vs 100 signed inventories; local only."""
import asyncio,hashlib,importlib.util,json,random,resource,sqlite3,struct,subprocess,sys,time,unittest
from collections import Counter
from pathlib import Path
from wsgiref.simple_server import make_server
import threading,tempfile
from aiohttp import ClientSession,ClientTimeout,web
from dataclasses import replace
P=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('fixtures',P/'file-account-admission-capacity.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from gateway_service.policy import Principal
from gateway_service.user_store import UserStore
from gateway_service.auth import initialize_ledger
from gateway_service.transfers import initialize_transfers
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
jose=m.jose

def rss_kib():
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmRSS:'):return int(line.split()[1])
 raise RuntimeError('RSS unavailable')
class Contention(m.AccountAdmission):
 async def asyncSetUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='codi-slow-file-');self.root=Path(self.temp.name);public=self.root/'public';public.mkdir();(public/'index.html').write_text('test')
  self.origin='http://127.0.0.1:19866';self.issuer_server=BoundedServer(('127.0.0.1',0),QuietHandler);self.issuer=Service(Config(self.root/'issuer',public,origin=self.origin,rate_per_minute=1000));self.issuer_server.set_app(GatewayAuthority(self.issuer));self.thread=threading.Thread(target=self.issuer_server.serve_forever,daemon=True);self.thread.start()
  state=self.root/'state';data=self.root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700);self.store=UserStore(state,data);initialize_ledger(self.store);initialize_transfers(self.store);self.client=ClientSession(timeout=ClientTimeout(total=30),trust_env=False);await self.start_gateway(max_requests_per_minute=2048);gateway_port=int(self.gateway_url.rsplit(':',1)[1]);self.gateway_url=self.origin
  self.proxy=subprocess.Popen([sys.executable,str(P/'light-file-socket-proxy-launch.py'),str(gateway_port)],cwd=self.root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);await asyncio.sleep(.2)
  if self.proxy.poll() is not None:raise RuntimeError('socket proxy failed')
  cfg=self.root/'Caddyfile';cfg.write_text('http://127.0.0.1:19866 {\n handle /gateway/* {\n reverse_proxy 127.0.0.1:19865\n }\n handle {\n reverse_proxy 127.0.0.1:'+str(self.issuer_server.server_port)+'\n }\n}\n')
  self.caddy=subprocess.Popen(['/tmp/codi-microduck-hosting-evidence/caddy','run','--config',str(cfg),'--adapter','caddyfile'],cwd=self.root,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  for _ in range(100):
   if self.caddy.poll() is not None:raise RuntimeError('Caddy failed')
   try:r,w=await asyncio.open_connection('127.0.0.1',19866);w.close();await w.wait_closed();break
   except OSError:await asyncio.sleep(.05)
  else:raise RuntimeError('Caddy start timed out')
  self.counting=False;self.responses=Counter();self.transport=[]
 async def asyncTearDown(self):
  await self.client.close()
  for p in (self.caddy,self.proxy):
   p.terminate()
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.kill();p.wait()
  await self.runner.cleanup();await asyncio.to_thread(self.issuer_server.shutdown);self.thread.join(2);self.issuer_server.server_close();self.temp.cleanup()
 async def post(self,path,value,*,gateway=False,headers=None,raw=None):
  fields={'Host':'127.0.0.1:19866','Origin':self.origin,'Content-Type':'application/json',**(headers or {})};body=raw if raw is not None else jose.dumps(value)
  try:
   async with self.client.post(self.origin+path,data=body.encode(),headers=fields) as response:
    text=await response.text();status=response.status
    if self.counting:self.responses[('gateway' if gateway else 'issuer',status)]+=1
    try:obj=json.loads(text)
    except json.JSONDecodeError:obj={'error':'non-JSON response'}
    return status,obj,dict(response.headers)
  except Exception as error:
   if self.counting:self.transport.append({'path':path,'kind':type(error).__name__,'message':str(error)[:100]})
   raise
 async def runTest(self):
  accounts=[];setup=time.monotonic()
  for i in range(104):
   session,key=await self.enter('slow'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.store.ensure_user(principal);self.store.put(principal,'note.txt',b'data');accounts.append((session,key,principal))
  setup=time.monotonic()-setup;self.issuer.c=replace(self.issuer.c,rate_per_minute=60);payload=b'x'*8192;sha=hashlib.sha256(payload).hexdigest();streams=[]
  try:
   # Preauthorize each upload, then send headers and only one payload byte.
   for session,key,principal in accounts[:4]:
    meta={'resource':'my-files','operation':'create','path':'slow.bin','format':'codi-binary-upload/1','size':len(payload),'sha256':sha};raw=jose.dumps(meta);status,_,auth=await self.authorize(session,key,raw);self.assertEqual(status,200);encoded=raw.encode();reader,writer=await asyncio.open_connection('127.0.0.1',19866)
    header=('POST /gateway/upload HTTP/1.1\r\nHost: 127.0.0.1:19866\r\nOrigin: '+self.origin+'\r\nContent-Type: application/octet-stream\r\nContent-Length: '+str(4+len(encoded)+len(payload))+'\r\nAuthorization: '+auth['Authorization']+'\r\nConnection: close\r\n\r\n').encode()
    writer.write(header+struct.pack('>I',len(encoded))+encoded+payload[:1]);await writer.drain();streams.append((reader,writer,principal))
   for _ in range(100):
    if self.gateway.active==4:break
    await asyncio.sleep(.05)
   self.assertEqual(self.gateway.active,4,'four uploads must occupy four gateway slots')
   self.responses.clear();self.counting=True;max_active=0;max_wait=0;peak=rss_kib();samples=[];failures=[];latencies=[];first_outcome={};phase="initial";start=time.monotonic()
   async def monitor():
    nonlocal max_active,max_wait,peak
    while True:
     max_active=max(max_active,self.gateway.active);max_wait=max(max_wait,self.gateway.waiting);peak=max(peak,rss_kib())
     if peak>768*1024:raise RuntimeError('memory guard exceeded')
     await asyncio.sleep(.025)
   async def inventory(account):
    t=time.monotonic();session,key,_=account
    try:
     raw=jose.dumps({'resource':'my-files','operation':'inventory-versions'});status,result,headers=await self.authorize(session,key,raw)
     if status!=200:raise RuntimeError('authorize '+str(status))
     status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw)
     if status!=200:raise RuntimeError('inventory '+str(status))
     if not result.get('complete'):raise RuntimeError('incomplete inventory')
     latencies.append(time.monotonic()-t)
    except Exception as error:
     message=str(error)[:120];failures.append({'type':type(error).__name__,'message':message,'after_s':round(time.monotonic()-t,3)})
     if phase=='initial':first_outcome[account[2].sub]='429' if '429' in message else 'other'
   monitor_task=asyncio.create_task(monitor());tasks=[asyncio.create_task(inventory(a)) for a in accounts[4:]]
   try:
    await asyncio.sleep(7)
    if monitor_task.done():await monitor_task
    at_release={'completed':len(latencies),'failed':len(failures),'active':self.gateway.active,'waiting':self.gateway.waiting}
    for _,writer,_ in streams:writer.write(payload[1:]);await writer.drain()
    upload_status=[]
    for reader,_,_ in streams:upload_status.append((await asyncio.wait_for(reader.readline(),15)).decode(errors='replace').strip())
    await asyncio.wait_for(asyncio.gather(*tasks),30)
   finally:
    monitor_task.cancel();await asyncio.gather(monitor_task,return_exceptions=True)
    for task in tasks:task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
   for _,_,principal in streams:self.assertEqual(self.store.read(principal,'slow.bin')['sha256'],sha)
   # New independent, freshly signed inventory attempts after the stalled
   # uploads complete; never replay an upload or assume ambiguous writes failed.
   first_failures=list(failures);first_responses=dict(self.responses);first_success=len(latencies);recovery_start=time.monotonic();release_window=self.gateway.window;phase='recovery'
   print(json.dumps({'phase':'before-recovery','at_release':at_release,'first_success':first_success,'first_failures':len(first_failures),'failure_sample':first_failures[:12],'first_responses':{f'{a}:{b}':n for (a,b),n in first_responses.items()},'upload_status':upload_status,'gateway_requests':self.gateway.requests,'gateway_window':release_window}),flush=True)
   async def retry_later(account):
    # Match the mirror's approximate first automatic retry schedule; the
    # 502/transport path is 12–18 s, 429 is 24–36 s. No write is replayed.
    kind=first_outcome.get(account[2].sub,'other')
    await asyncio.sleep(random.uniform(24,36) if kind=='429' else random.uniform(12,18))
    await inventory(account)
   monitor_task=asyncio.create_task(monitor());recovery_tasks=[asyncio.create_task(retry_later(a)) for a in accounts[4:] if a[2].sub in first_outcome]
   try:
    done,pending=await asyncio.wait(recovery_tasks,timeout=50)
    if monitor_task.done():await monitor_task
   finally:
    for task in recovery_tasks:task.cancel()
    await asyncio.gather(*recovery_tasks,return_exceptions=True);monitor_task.cancel();await asyncio.gather(monitor_task,return_exceptions=True)
   recovery={'attempted':len(recovery_tasks),'success':len(latencies)-first_success,'failures':len(failures)-len(first_failures),'pending_at_timeout':len(pending),'elapsed_s':round(time.monotonic()-recovery_start,3),'same_gateway_window':release_window==self.gateway.window,'response_delta':{f'{a}:{b}':n-first_responses.get((a,b),0) for (a,b),n in self.responses.items() if n-first_responses.get((a,b),0)}}
   values=sorted(latencies);print(json.dumps({'recovery_after_release':recovery,'first_wave_failures':len(first_failures),'scope':'isolated Caddy + 16-connection socket proxy; four 8 KiB uploads held at one byte for seven seconds; 100 concurrent signed inventories followed by jittered fresh-proof read-only retries','setup_s':round(setup,3),'elapsed_s':round(time.monotonic()-start,3),'hold_s':7,'at_release':at_release,'light_success_after_recovery':len(latencies),'light_failure_count_total':len(failures),'failure_sample':failures[:12],'light_success_p95_s':round(values[(len(values)*95+99)//100-1],3) if values else None,'responses':{f'{a}:{b}':n for (a,b),n in self.responses.items()},'transport':self.transport[:12],'upload_status':upload_status,'gateway_active_max':max_active,'gateway_waiting_max':max_wait,'sampled_rss_mib':round(peak/1024,1),'process_peak_rss_mib':round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1)}),flush=True)
   self.assertTrue(all(' 200 ' in x for x in upload_status))
  finally:
   for _,writer,_ in streams:writer.close();await writer.wait_closed()
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Contention()]));sys.exit(not result.wasSuccessful())
