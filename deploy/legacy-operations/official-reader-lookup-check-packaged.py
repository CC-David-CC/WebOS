#!/usr/bin/env python3
"""Real Chrome/session/issuer/official HTTP/loopback ingest; temporary state."""
import argparse,asyncio,importlib.util,json,os,secrets,socket,sys,tempfile,threading,time
from pathlib import Path
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server
from aiohttp import ClientSession,web

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth.service import Config
from origin_service.lifecycle import Service
from origin_service.official_authority import OfficialAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from steward.official_access import OfficialAccess,initialize
from steward.official_submission import OfficialSubmission
from steward.official_submission_http import OfficialSubmissionHTTP
from steward.official_ingest_http import OfficialIngestServer
from steward.official_read_http import OfficialReadServer
from steward.official_local_transport import LocalOfficialTransport
from steward.official_registry import OfficialChannelRegistry
from steward.official_upload_policy import OfficialUploadPolicy,initialize as initialize_upload_policy
from steward.official_runtime import OfficialRuntime
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)

def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]

def browser(origin,offer,registered=False,restart_open=False,idle_measure=False):
 session=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 try:
  driver.call('/session/'+session+'/timeouts',{'script':120000});driver.call('/session/'+session+'/url',{'url':origin+'/'});driver.call('/session/'+session+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  code='''const done=arguments[arguments.length-1];(async()=>{
 const config=await(await fetch('/config.json')).json(),{beginSession}=await import('/network/identity.mjs'),{PeerPool}=await import('/network/peer-pool.mjs'),{PersistentDeviceStorage}=await import('/.build/official-fast-test-exports.mjs'),{DeviceChannelSession}=await import('/.build/official-fast-test-exports.mjs');
 const realTimeout=window.setTimeout.bind(window),delays=[];window.setTimeout=(fn,delay,...args)=>{if(typeof fn==='function'&&String(fn).includes('officialLookupTimer'))delays.push(delay);return realTimeout(fn,delay,...args);};const prior=window.fetch.bind(window);let release;const gate=new Promise(r=>release=r);let held=false;window.fetch=async(...args)=>{const response=await prior(...args);if(!held&&new URL(args[0],location.href).pathname==='/official-channel'&&response.status===404){held=true;await gate;}return response;};
 const session=await beginSession(config,'anonymous');localStorage.setItem('codi-device-history-consent-v1','accepted-v1');const storage=new PersistentDeviceStorage(),permit=await storage.acquire(),pool=new PeerPool(session,config),life=new AbortController(),owner=await new DeviceChannelSession({session,issuer:config.identity.issuer,pool,currentSession:()=>session,signal:life.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:false}).open(permit),view=owner.attach({signal:life.signal}),group=await view.createChannel({label:'Reader test',publicRead:true,publicWrite:true});const cfg=(await view.channels()).find(x=>x.channel===group.channel),visitor=await beginSession(config,'register','reader_'+crypto.randomUUID().replaceAll('-','').slice(0,12),'Fixture-password-839!'),visitorPool=new PeerPool(visitor,config),visitorLife=new AbortController(),visitorOwner=await new DeviceChannelSession({session:visitor,issuer:config.identity.issuer,pool:visitorPool,currentSession:()=>visitor,signal:visitorLife.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:true}).open(permit),visitorView=visitorOwner.attach({signal:visitorLife.signal}),reader=(await visitorView.createIdentity('Reader')).channel;await visitorView.openChannel(cfg,reader);const deadline=performance.now()+10000;while(!held&&performance.now()<deadline)await new Promise(r=>setTimeout(r,20));if(!held)throw Error('Expected held initial 404');release();const until=performance.now()+5000;while(!delays.length&&performance.now()<until)await new Promise(r=>setTimeout(r,20));if(delays[0]!==60000)throw Error('Non-owner retry was '+delays[0]);visitorView.close();visitorOwner.close();await visitorOwner.idle();visitorPool.close();visitorLife.abort();view.close();owner.close();await owner.idle();pool.close();storage.close();life.abort();return {delay:delays[0],kind:session.public.kind};
 })().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));'''
  code=code.replace('RESTART_OPEN','true' if restart_open else 'false').replace('IDLE_MEASURE','true' if idle_measure else 'false')
  if registered:code=code.replace("beginSession(config,'anonymous')","beginSession(config,'register','fixture_'+crypto.randomUUID().replaceAll('-','').slice(0,12),'Fixture-password-839!')")
  value=driver.call('/session/'+session+'/execute/async',{'script':code,'args':[]})
  assert value['ok'],value;return value['value']
 finally:driver.call('/session/'+session,method='DELETE')

async def main(before_commit=False,registered=False,packaged=False,launcher=False,restart_open=False,idle_measure=False):
 fixture=json.loads((ROOT/'.build/checks/official-browser-offer-export-r1.json').read_text())['offerFixture'];offer=fixture['offer']
 (ROOT/'.build/official-services').mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='codi-official-upload-') as temp, tempfile.TemporaryDirectory(prefix='browser-',dir=ROOT/'.build/official-services') as package_temp:
  root=Path(temp);public=root/'public';public.mkdir();(public/'index.html').write_text('<!doctype html><title>Official upload fixture</title>');origin='http://127.0.0.1:'+str(port())
  issuer_process=None;wsgi=None;thread=None
  if launcher:
   issuer_port=port();runtime_dir=root/'issuer-runtime';runtime_dir.mkdir(mode=0o700);issuer_process=await asyncio.create_subprocess_exec(sys.executable,str(ROOT/'scripts/serve-connected.py'),'--port',str(issuer_port),'--runtime-dir',str(runtime_dir),'--origin',origin,'--official-channels',stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   line=await asyncio.wait_for(issuer_process.stdout.readline(),30)
   if not line:raise RuntimeError('Issuer failed: '+(await issuer_process.stderr.read()).decode())
   async with ClientSession() as boot:
    async with boot.get('http://127.0.0.1:'+str(issuer_port)+'/config.json',headers={'Host':urlsplit(origin).netloc}) as response:issuer_config=await response.json()
  else:
   issuer=Service(Config(root/'issuer',public,origin=origin,rate_per_minute=1000));wsgi=make_server('127.0.0.1',0,OfficialAuthority(issuer),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=wsgi.serve_forever,daemon=True);thread.start();issuer_port=wsgi.server_port;issuer_config=issuer.config()
  store=OfficialChannelRegistry(root/'official.sqlite');store._db.execute('INSERT INTO official_channels(channel,genesis_hash,policy_wire,label,description,enabled,enrolled_at) VALUES(?,?,?,?,?,1,0)',(offer['channel'],fixture['genesisHash'],fixture['policyWire'],'fixture',''))
  allowed=set();initialize_upload_policy(root/'official.sqlite');initialize(root/'access.sqlite');package=Path(package_temp)/'package'
  for base in ('official.sqlite','access.sqlite'):
   for suffix in ('','-wal','-shm','-journal'):
    path=root/(base+suffix)
    if path.exists():path.chmod(0o600)
  if packaged:
   export_spec=importlib.util.spec_from_file_location('official_package',ROOT/'scripts/export-official-service.py');export_module=importlib.util.module_from_spec(export_spec);export_spec.loader.exec_module(export_module);export_module.export(package);(root/'policy.json').write_text(json.dumps(issuer_config['identity']))
  class PackageRuntime:
   def __init__(self,process,port):self.process=process;self.port=port
   async def close(self):
    self.process.terminate();await asyncio.wait_for(self.process.wait(),10)
    if self.process.returncode!=0:raise RuntimeError('Packaged runtime did not stop cleanly')
  async def start_runtime():
   if not packaged:return await OfficialRuntime(database=root/'official.sqlite',ledger=root/'access.sqlite',issuer_policy=issuer_config['identity']).start()
   listen=port();process=await asyncio.create_subprocess_exec(sys.executable,str(package/'scripts/run-official-runtime.py'),'--database',str(root/'official.sqlite'),'--ledger',str(root/'access.sqlite'),'--issuer-policy',str(root/'policy.json'),'--port',str(listen),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   line=await asyncio.wait_for(process.stdout.readline(),10)
   if not line:raise RuntimeError('Packaged runtime failed: '+(await process.stderr.read()).decode())
   if json.loads(line)['port']!=listen:raise RuntimeError('Wrong packaged runtime port')
   return PackageRuntime(process,listen)
  runtime=await start_runtime()
  outgoing=ClientSession();app=web.Application(client_max_size=8*1048576);attempts={'uses':0,'lost':0,'heads':0}
  async def official(request):
   headers={k:v for k,v in request.headers.items() if k.lower() not in ('connection','transfer-encoding','host')};headers['Host']=urlsplit(origin).netloc
   if runtime is None:return web.json_response({'error':'fixture outage'},status=503)
   async with outgoing.request(request.method,'http://127.0.0.1:'+str(runtime.port)+request.raw_path,headers=headers,data=await request.read() if request.can_read_body else None,allow_redirects=False) as response:return web.Response(status=response.status,body=await response.read(),headers={'Content-Type':response.headers.get('Content-Type','application/json')})
  app.router.add_post('/official-ingest/challenge',official)
  async def use(request):
   attempts['uses']+=1
   if before_commit and attempts['lost']==0:
    assert len(allowed)==1 and store.replayed_head(next(iter(allowed)))['height']==0
    attempts['lost']+=1;return web.json_response({'error':'fixture unavailable before commit'},status=503)
   response=await official(request)
   if not before_commit and response.status==200 and attempts['lost']==0:attempts['lost']+=1;return web.json_response({'error':'fixture lost successful response'},status=503)
   return response
  app.router.add_post('/official-ingest/use',use)
  async def api(request):
   headers={k:v for k,v in request.headers.items() if k.lower() not in ('connection','transfer-encoding','host')};headers['Host']=urlsplit(origin).netloc
   async with outgoing.request(request.method,'http://127.0.0.1:'+str(issuer_port)+request.raw_path,headers=headers,data=await request.read()) as response:return web.Response(status=response.status,body=await response.read(),headers={'Content-Type':response.headers.get('Content-Type','application/json')})
  async def asset(request):
   relative=request.match_info['path'];file=(ROOT/relative).resolve()
   if not file.is_relative_to(ROOT) or file.suffix!='.mjs' or not file.is_file():raise web.HTTPNotFound()
   data=file.read_bytes()
   if os.environ.get('CODI_TEST_BASELINE')=='1' and relative=='assets/desktop/device-channel-session.mjs':
    old=b"e.officialLookupMisses=Math.min(5,(e.officialLookupMisses||0)+1);const delay=e.actor===e.config.channel&&e.trafficProfile!='limited'?Math.min(60000,5000*2**(e.officialLookupMisses-1)):60000;"
    old=old.replace(b"!='limited'",b"!=='limited'")
    assert data.count(old)==1;data=data.replace(old,b'const delay=60000;')
   return web.Response(body=data,content_type='text/javascript')
  async def enroll(request):
   value=await request.json();entry=store.enroll(value['listing'],now=int(time.time()));allowed.add(entry['channel']);return web.json_response({'channel':entry['channel']})
  async def head(request):
   attempts['heads']+=1
   return await official(request)
  async def status(request):
   tip=store.replayed_head(request.query['channel']);return web.json_response({'height':tip['height'],'head':tip['head']})
  async def stop_runtime(request):
   nonlocal runtime
   await runtime.close();runtime=None;return web.json_response({'stopped':True})
  async def resume_runtime(request):
   nonlocal runtime
   runtime=await start_runtime();return web.json_response({'started':True})
  app.router.add_post('/fixture-stop',stop_runtime);app.router.add_post('/fixture-start',resume_runtime)
  app.router.add_post('/fixture-enroll',enroll)
  app.router.add_get('/official-head',head)
  app.router.add_get('/official-directory',official)
  app.router.add_get('/official-channel',official)
  app.router.add_get('/official-history',official)
  app.router.add_get('/fixture-head-status',status)
  app.router.add_route('*','/api/v1/{tail:.*}',api);app.router.add_get('/config.json',lambda _:web.json_response(issuer_config));app.router.add_get('/',lambda _:web.Response(text='<!doctype html><title>Fixture</title>',content_type='text/html'));app.router.add_get(r'/{path:.*\.mjs}',asset)
  runner=web.AppRunner(app,access_log=None);await runner.setup();await web.TCPSite(runner,'127.0.0.1',int(urlsplit(origin).port)).start()
  try:
   result=await asyncio.to_thread(browser,origin,offer,registered,restart_open,idle_measure);assert result['delay']==60000
   print(json.dumps({'status':'PASS','scope':'real Chrome non-owner retains one-minute missing-listing retry','delayMs':result['delay']}))
  finally:
   await runner.cleanup();await outgoing.close();
   if runtime:await runtime.close()
   if wsgi:await asyncio.to_thread(wsgi.shutdown);wsgi.server_close();thread.join(3)
   if issuer_process:issuer_process.terminate();await asyncio.wait_for(issuer_process.wait(),10)
   store.close()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--before-commit',action='store_true');parser.add_argument('--registered',action='store_true');parser.add_argument('--packaged',action='store_true');parser.add_argument('--issuer-launcher',action='store_true');parser.add_argument('--restart-open',action='store_true');parser.add_argument('--idle-measure',action='store_true');args=parser.parse_args();asyncio.run(main(args.before_commit,args.registered,args.packaged,args.issuer_launcher,args.restart_open,args.idle_measure))
