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
   const config=await (await fetch('/config.json')).json();const {beginSession}=await import('/network/identity.mjs');const {PeerPool}=await import('/network/peer-pool.mjs');const {PersistentDeviceStorage}=await import('/assets/desktop/storage-consent.mjs');const {DeviceChannelSession}=await import('/assets/desktop/device-channel-session.mjs');
   const realTimeout=window.setTimeout.bind(window),lookupDelays=[];window.setTimeout=(fn,delay,...args)=>{if(typeof fn==='function'&&String(fn).includes('officialLookupTimer'))lookupDelays.push(delay);return realTimeout(fn,delay,...args);};const originalLookupFetch=window.fetch.bind(window);let lookup404=0;window.fetch=async (...args)=>{const response=await originalLookupFetch(...args);if(new URL(args[0],location.href).pathname==='/official-channel'&&response.status===404)lookup404++;return response;};const session=await beginSession(config,'anonymous');localStorage.setItem('codi-device-history-consent-v1','accepted-v1');const storage=new PersistentDeviceStorage(),permit=await storage.acquire(),pool=new PeerPool(session,config),life=new AbortController();
   const open=async pins=>new DeviceChannelSession({session,issuer:config.identity.issuer,pool,currentSession:()=>session,signal:life.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialChannels:pins,officialDiscovery:true}).open(permit);
   let owner=await open([]),view=owner.attach({signal:life.signal}),group=await view.createChannel({label:'Fixture official',publicRead:true,publicWrite:true}),initial=await group.snapshot();await group.queue('chat',{text:'Real session publication'});
   const until=performance.now()+30000;while((await group.snapshot()).height===0&&performance.now()<until)await new Promise(r=>setTimeout(r,100));const saved=await group.snapshot();if(saved.height===0)throw Error('Local channel did not settle');
   const firstLookupDeadline=performance.now()+10000;while(!lookup404&&performance.now()<firstLookupDeadline)await new Promise(r=>setTimeout(r,50));if(!lookup404)throw Error('No initial 404 lookup before enrollment');const listing=await view.createPublicListing(group.channel);const enrolled=await fetch('/fixture-enroll',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({listing})});if(!enrolled.ok)throw Error('Fixture enrollment failed');const enrolledAt=performance.now(),rediscoveryDeadline=enrolledAt+15000;while(!(await group.snapshot()).official&&performance.now()<rediscoveryDeadline)await new Promise(r=>setTimeout(r,100));if(!(await group.snapshot()).official)throw Error('Open channel did not rediscover enrollment within 15 seconds');const rediscoveryMs=Math.round(performance.now()-enrolledAt);if(!lookupDelays.includes(5000))throw Error('Owner initial official lookup did not schedule 5 second retry');const {fetchOfficialDirectoryPage}=await import('/assets/desktop/official-directory.mjs');const directory=await fetchOfficialDirectoryPage('/official-history',{limit:32}),official=directory.items.find(item=>item.category==='official'&&item.channel===group.channel&&item.label==='Fixture official');if(!official)throw Error('Official directory omitted enrolled channel');
   const userGroup=await view.createChannel({label:'Community room',publicRead:true,publicWrite:true}),userInvite=await view.createChannelInvitation(userGroup.channel),duplicateInvite=await view.createChannelInvitation(group.channel),independent=await view.createChannel({label:'Other room',publicRead:true,publicWrite:true});const concurrent=await Promise.all(['one','two','three'].map(text=>userGroup.queue('chat',{text:'concurrent '+text})));if(new Set(concurrent.map(x=>x.id)).size!==3)throw Error('Concurrent pending saves did not remain distinct');const cancelLife=new AbortController(),cancelView=owner.attach({signal:cancelLife.signal}),cancelHandle=await cancelView.restoreChannel(userGroup.channel),{DeviceChannelArchive}=await import('/assets/desktop/channel-archive.mjs'),originalLoad=DeviceChannelArchive.prototype.load;let releaseHold,holdStarted;const held=new Promise(r=>releaseHold=r),started=new Promise(r=>holdStarted=r);let taken=false;DeviceChannelArchive.prototype.load=async function(...args){if(!taken&&this.pins().channel===userGroup.channel){taken=true;holdStarted();await held;}return originalLoad.apply(this,args);};try{const first=userGroup.queue('chat',{text:'held first'});await started;const other=await Promise.race([independent.queue('chat',{text:'independent while held'}),new Promise((_,reject)=>setTimeout(()=>reject(Error('Other channel was blocked by held operation')),5000))]);if(!other?.id)throw Error('Other channel did not save');const survivor=userGroup.queue('chat',{text:'wait then save'});let cancelled=false;const pending=cancelHandle.queue('chat',{text:'must not save'}).then(()=>false,()=>{cancelled=true;return true;});await new Promise(r=>setTimeout(r,150));cancelLife.abort();await pending;if(!cancelled)throw Error('Waiting send was not cancelled');releaseHold();const completed=await Promise.all([first,survivor]);if(completed[0].id===completed[1].id)throw Error('Waiting sends did not remain distinct');await new Promise(r=>setTimeout(r,500));const snapshot=await userGroup.snapshot(),pendingRows=await userGroup.pending();if(snapshot.state.messages.some(m=>m.text==='must not save')||pendingRows.some(row=>{try{return atob(row.wire.split('.')[1].replaceAll('-','+').replaceAll('_','/')).includes('must not save');}catch{return false;}}))throw Error('Cancelled send was saved');}finally{releaseHold();DeviceChannelArchive.prototype.load=originalLoad;cancelView.close();}view.close();owner.close();await owner.idle();owner=await open([{channel:group.channel,genesisHash:group.genesisHash,endpoint:'/official-history'}]);view=owner.attach({signal:life.signal});group=await view.restoreChannel(group.channel);
   let remote=null;const deadline=performance.now()+40000;while(performance.now()<deadline){const response=await fetch('/fixture-head-status?channel='+encodeURIComponent(group.channel));if(response.ok){remote=await response.json();if(remote.height===saved.height)break;}await new Promise(r=>setTimeout(r,200));}if(remote?.height!==saved.height)throw Error('Automatic publication did not reach the server');
   const visitor=await beginSession(config,'register','visitor_'+crypto.randomUUID().replaceAll('-','').slice(0,12),'Fixture-password-839!'),visitorPool=new PeerPool(visitor,config),visitorLife=new AbortController(),visitorOwner=await new DeviceChannelSession({session:visitor,issuer:config.identity.issuer,pool:visitorPool,currentSession:()=>visitor,signal:visitorLife.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false}).open(permit),visitorView=visitorOwner.attach({signal:visitorLife.signal});const {mountDeviceChannelView}=await import('/served_apps_public/shared/device-channel-view.mjs');const uiLife=new AbortController(),make=(tag,cls='',text='')=>{const el=document.createElement(tag);el.className=cls;el.textContent=text;return el;},textButton=(label,action)=>{const el=make('button','',label);el.type='button';el.addEventListener('click',action);return el;};const host={ui:{make,textButton},w:{},signal:uiLife.signal,session:()=>visitor,storage:{deviceHistory:{channels:({onChange})=>{const view=visitorOwner.attach({signal:uiLife.signal,onChange});return {...view,joinOfficialChannel:async channel=>{const joined=await view.joinOfficialChannel(channel),handle=joined.channel;return {...joined,channel:{...handle,queue:async(...args)=>{window.__fixtureQueueAttempts=(window.__fixtureQueueAttempts||0)+1;if(window.__fixtureQueueAttempts===1)throw Error('This channel is already processing a durable operation');return handle.queue(...args);}}};}};}}},network:{config:{...config,deviceChannels:{officialDiscovery:true}},observeChannelIndex:()=>()=>{},startChannelIndex:async()=>({recent:({query})=>[{category:'user',stream:'chat',channel:userGroup.channel,label:'Community room',description:'Visitors welcome',invitation:userInvite},{category:'user',stream:'chat',channel:group.channel,label:'Duplicate official',description:'',invitation:duplicateInvite}].filter(x=>(x.label+' '+x.description).toLowerCase().includes(query))})}};const realFetch=window.fetch.bind(window);let failDirectory=true,slowSearchStarted=false;window.fetch=(input,options)=>{const url=new URL(input,location.href);if(url.pathname==='/official-directory'){if(failDirectory){failDirectory=false;return Promise.resolve(new Response('{}',{status:503}));}url.searchParams.set('limit','1');if(url.searchParams.get('query')==='no match'){slowSearchStarted=true;return realFetch(url,options).then(response=>new Promise(resolve=>setTimeout(()=>resolve(response),1000)));}return realFetch(url,options);}return realFetch(input,options);};const disabledHost={...host,network:{...host.network,config}};const disabledApp=mountDeviceChannelView(disabledHost);document.body.append(disabledApp.element);await new Promise(r=>setTimeout(r,500));if(!failDirectory||disabledApp.element.textContent.includes('Official list unavailable'))throw Error('Disabled official discovery accessed the service');disabledApp.dispose();disabledApp.element.remove();const app=mountDeviceChannelView(host);document.body.append(app.element);const waitUI=async(fn,ms=15000)=>{const deadline=performance.now()+ms;while(performance.now()<deadline){const value=fn();if(value)return value;await new Promise(r=>setTimeout(r,100));}throw Error('Channel UI timed out: '+app.element.textContent.slice(0,800));};const retry=await waitUI(()=>{const b=app.element.querySelector('[data-official-more]');return b&&!b.hidden&&b.textContent==='Retry official channels'&&b;});if(!app.element.textContent.includes('Official list unavailable'))throw Error('Directory failure not visible');retry.click();const more=await waitUI(()=>{const b=app.element.querySelector('[data-official-more]');return b&&!b.hidden&&b.textContent==='More official channels'&&b;});more.click();await waitUI(()=>app.element.querySelector('[data-official-more]').hidden);const row=await waitUI(()=>[...app.element.querySelectorAll('[data-channel-results] div')].find(x=>x.textContent.includes('Fixture official')&&x.textContent.includes('Official · server-backed')));if(app.element.querySelector('[data-channel-results]').textContent.includes('Duplicate official'))throw Error('Official channel duplicated as user listing');const community=await waitUI(()=>[...app.element.querySelectorAll('[data-channel-results] div')].find(x=>x.textContent.includes('Community room')&&x.textContent.includes('User-created')));community.querySelector('button').click();await waitUI(()=>app.element.querySelector('[data-device-select]').value===userGroup.channel,30000);const search=app.element.querySelector('input[aria-label="Search channels"]');search.value='no match';search.dispatchEvent(new Event('input'));if(app.element.querySelector('[data-channel-results]').textContent.includes('Fixture official'))throw Error('Channel search failed to filter');await waitUI(()=>slowSearchStarted);search.value='fixture official';search.dispatchEvent(new Event('input'));const match=await waitUI(()=>[...app.element.querySelectorAll('[data-channel-results] div')].find(x=>x.textContent.includes('Fixture official')));match.querySelector('button').click();await waitUI(()=>app.element.querySelector('[data-device-select]').value===group.channel,30000);const joined={channel:await visitorView.restoreChannel(group.channel)};if(!(await joined.channel.snapshot()).official)throw Error('Official UI join did not pin channel');const draft=app.element.querySelector('[data-device-draft]');draft.value='retry saved draft';draft.dispatchEvent(new Event('input'));const send=app.element.querySelector('[data-device-queue]');await waitUI(()=>!send.disabled);send.click();await waitUI(()=>window.__fixtureQueueAttempts>=2&&draft.value==='');if(!(await joined.channel.pending()).some(p=>p))throw Error('Retry did not save pending message');
   const guestDeadline=performance.now()+40000;let visitorState;while(performance.now()<guestDeadline){visitorState=await joined.channel.snapshot();if(visitorState.height===saved.height)break;await new Promise(r=>setTimeout(r,200));}if(visitorState?.head!==saved.head||visitorState.state.messages[0]?.text!=='Real session publication')throw Error('Official directory join did not recover server history');app.dispose();uiLife.abort();window.fetch=realFetch;visitorView.close();visitorOwner.close();await visitorOwner.idle();
   const reopenedOwner=await new DeviceChannelSession({session:visitor,issuer:config.identity.issuer,pool:visitorPool,currentSession:()=>visitor,signal:visitorLife.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:true}).open(permit),reopenedView=reopenedOwner.attach({signal:visitorLife.signal}),reopened=await reopenedView.restoreChannel(group.channel);const restoreDeadline=performance.now()+15000;let restored;while(performance.now()<restoreDeadline){restored=await reopened.snapshot();if(restored.official)break;await new Promise(r=>setTimeout(r,100));}if(!restored?.official||restored.head!==saved.head)throw Error('Restored channel was not verified against official directory');let recoveryMs=null,idleMeasurement=null;if(IDLE_MEASURE){const previousFetch=window.fetch.bind(window),polls=[];window.fetch=(input,options)=>{const u=new URL(input,location.href),task=previousFetch(input,options);if(u.pathname==='/official-history')task.then(response=>response.clone().text().then(body=>polls.push({requestTargetBytes:new TextEncoder().encode(u.pathname+u.search).length,responseBodyBytes:new TextEncoder().encode(body).length,at:performance.now()}))).catch(()=>{});return task;};const start=performance.now();await new Promise(r=>setTimeout(r,16000));window.fetch=previousFetch;idleMeasurement={durationMs:Math.round(performance.now()-start),polls};if(polls.length<2)throw Error('Expected at least two idle fallback polls');}if(RESTART_OPEN){await fetch('/fixture-stop',{method:'POST'});await group.queue('chat',{text:'After service restart'});const localDeadline=performance.now()+30000;let later;while(performance.now()<localDeadline){later=await group.snapshot();if(later.height>saved.height)break;await new Promise(r=>setTimeout(r,100));}if(later?.height<=saved.height)throw Error('Second message did not settle');await new Promise(r=>setTimeout(r,6000));await fetch('/fixture-start',{method:'POST'});const resumedAt=performance.now();const syncDeadline=performance.now()+90000;let visitorLater;while(performance.now()<syncDeadline){visitorLater=await reopened.snapshot();if(visitorLater.head===later.head)break;await new Promise(r=>setTimeout(r,300));}if(visitorLater?.head!==later.head||!visitorLater.state.messages.some(m=>m.text==='After service restart'))throw Error('Open visitor failed to recover after service restart');recoveryMs=Math.round(performance.now()-resumedAt);}reopenedView.close();reopenedOwner.close();await reopenedOwner.idle();visitorPool.close();visitorLife.abort();
   await new Promise(r=>setTimeout(r,7000));let repeat;for(let i=0;i<30;i++){try{repeat=await group.syncOfficialHistory();break;}catch(e){if(!e.message.includes('already processing')&& !e.message.includes('earlier durable work'))throw e;await new Promise(r=>setTimeout(r,100));}}view.close();owner.close();await owner.idle();pool.close();storage.close();life.abort();return {kind:session.public.kind,remote,repeat,channel:group.channel,text:saved.state.messages[0].text,recoveryMs,idleMeasurement,rediscoveryMs,lookupDelays};
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
   result=await asyncio.to_thread(browser,origin,offer,registered,restart_open,idle_measure);saved=store.replayed_head(result['channel']);assert result['kind']==('registered' if registered else 'anonymous') and result['repeat']['status']=='up-to-date' and (restart_open or result['remote']['head']==saved['head']) and saved['state']['messages'][0]['text']==result['text']=='Real session publication' and (attempts['uses']>=(3 if before_commit else 2) if restart_open else attempts['uses']==(2 if before_commit else 1)) and attempts['lost']==1 and attempts['heads']>=3
   await runtime.close();runtime=await start_runtime()
   async with outgoing.get('http://127.0.0.1:'+str(runtime.port)+'/official-head',params={'channel':result['channel']},headers={'Host':urlsplit(origin).netloc}) as response:assert response.status==200 and (await response.json())['head']==saved['head']
   print(json.dumps({'status':'PASS','scope':'Actual '+result['kind']+' Chrome publication after fixture failure '+('before commit' if before_commit else 'after commit; no duplicate write')+', runtime restart; no live changes','attempts':attempts,'packagedRuntime':packaged,'issuerLauncher':launcher,'restartWhileOpen':restart_open,'recoveryMs':result['recoveryMs'],'idleMeasurement':result['idleMeasurement'],'rediscoveryMs':result['rediscoveryMs'],'lookupDelays':result['lookupDelays']}))
  finally:
   await runner.cleanup();await outgoing.close();
   if runtime:await runtime.close()
   if wsgi:await asyncio.to_thread(wsgi.shutdown);wsgi.server_close();thread.join(3)
   if issuer_process:issuer_process.terminate();await asyncio.wait_for(issuer_process.wait(),10)
   store.close()

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--before-commit',action='store_true');parser.add_argument('--registered',action='store_true');parser.add_argument('--packaged',action='store_true');parser.add_argument('--issuer-launcher',action='store_true');parser.add_argument('--restart-open',action='store_true');parser.add_argument('--idle-measure',action='store_true');args=parser.parse_args();asyncio.run(main(args.before_commit,args.registered,args.packaged,args.issuer_launcher,args.restart_open,args.idle_measure))
