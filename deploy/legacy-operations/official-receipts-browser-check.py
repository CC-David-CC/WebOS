#!/usr/bin/env python3
"""Real issuer, SQLite, writer and distinct Chromium sessions for receipts."""
import asyncio,importlib.util,json,os,socket,sys,tempfile,threading
from pathlib import Path
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server
from aiohttp import ClientSession,web
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'codiserver-server-v0.3.0')]
from codiauth.service import Config
from origin_service.lifecycle import Service
from origin_service.official_authority import OfficialAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from steward.official_access import initialize
from steward.official_upload_policy import initialize as init_policy
from steward.official_receipts import initialize as init_receipts
from steward.official_chat_custody import provision
from steward.official_registry import OfficialChannelRegistry
from steward.official_runtime import OfficialRuntime
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)

def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def command(sid,script,args=[]):
 result=driver.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[arguments.length-1];(async()=>{'+script+'})().then(value=>done({value}),error=>done({error:error.stack||String(error)}));','args':args})
 if 'error' in result:raise AssertionError(result['error'])
 return result['value']
def open_browser(origin,mode,name):
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 try:
  driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':origin+'/'});driver.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  command(sid,"""
   const [mode,name,serviceURL]=arguments,config=await(await fetch('/config.json')).json();
   const {beginSession}=await import('/network/identity.mjs'),{PeerPool}=await import('/network/peer-pool.mjs');const {PersistentDeviceStorage,DeviceChannelSession}=serviceURL?await import(serviceURL):{...(await import('/assets/desktop/storage-consent.mjs')),...(await import('/assets/desktop/device-channel-session.mjs'))};
   const session=await beginSession(config,mode,name,'pass!');localStorage.setItem('codi-device-history-consent-v1','accepted-v1');const storage=new PersistentDeviceStorage(),permit=await storage.acquire(),pool=new PeerPool(session,config),life=new AbortController();
   const owner=await new DeviceChannelSession({session,issuer:config.identity.issuer,pool,currentSession:()=>session,signal:life.signal,identityPolicy:config.identity,automaticRounds:true,automaticPeers:false,trafficLimits:false,officialDiscovery:true,officialReceipts:true}).open(permit),view=owner.attach({signal:life.signal}),page=await view.officialDirectory({limit:32}),item=page.items.find(x=>x.label==='General chess chat');
   const channel=(await view.joinOfficialChannel(item.channel)).channel;window.fixture={owner,view,channel,storage,pool,life,session,config};
   const until=performance.now()+30000;while(performance.now()<until){const s=await channel.snapshot();if(s.officialStatus.caughtUp)return {subject:session.public.sub};await new Promise(r=>setTimeout(r,100));}throw Error('initial recovery timed out');
  """,[mode,name,os.environ.get('CODI_RECEIPTS_TEST_SERVICE','')]);return sid
 except BaseException:
  driver.call('/session/'+sid,method='DELETE');raise
def wait_message(sid,text,delivered=False,timeout=55000):
 return command(sid,"""
  const [text,delivered,timeout]=arguments,end=performance.now()+timeout;let s,m;
  while(performance.now()<end){s=await window.fixture.channel.snapshot();m=s.state.messages.find(x=>x.text===text);if(m&&!s.pending.some(x=>x.data?.text===text)&&(!delivered||s.officialStatus.deliveredMessages.includes(m.id)))return {id:m.id,status:s.officialStatus};await new Promise(r=>setTimeout(r,200));}
  throw Error('message/receipt timed out '+JSON.stringify({text,delivered,height:s?.height,status:s?.officialStatus,pending:s?.pending}));
 """,[text,delivered,timeout])
def exercise(origin,app_url,css_url):
 sessions=[]
 try:
  alice=open_browser(origin,'register','receiptalice');sessions.append(alice)
  if os.environ.get('CODI_RECEIPTS_FAULT')=='1':
   command(alice,"window.fixture.receiptFails=0;window.fixture.blockReceipts=true;window.fixture.originalFetch=window.fetch.bind(window);window.fetch=(input,options)=>{const u=new URL(input instanceof Request?input.url:String(input),location.href);let receipt=false;try{receipt=!!JSON.parse(options?.body||'{}').receipt;}catch{}if(window.fixture.blockReceipts&&u.pathname==='/official-ingest/use'&&receipt){window.fixture.receiptFails++;return Promise.resolve(new Response('{}',{status:503,headers:{'Content-Type':'application/json'}}));}return window.fixture.originalFetch(input,options);};return true;")
  command(alice,"await window.fixture.channel.queue('chat',{text:'First signed message'});return true;")
  first=wait_message(alice,'First signed message');assert not first['status']['deliveredMessages']
  if os.environ.get('CODI_RECEIPTS_FAULT')=='1':
   command(alice,"const end=performance.now()+40000;while(performance.now()<end&&!window.fixture.receiptFails)await new Promise(r=>setTimeout(r,100));if(!window.fixture.receiptFails)throw Error('Receipt failure was not exercised');window.fixture.blockReceipts=false;return true;")
   print('PASS receipt failure did not block chat; retrying',flush=True)
  same=open_browser(origin,'login','receiptalice');sessions.append(same);wait_message(same,'First signed message')
  import time;time.sleep(18)
  state=wait_message(alice,'First signed message');assert first['id'] not in state['status']['deliveredMessages'],'Same account falsely marked delivery'
  bob=open_browser(origin,'register','receiptbob');sessions.append(bob);wait_message(bob,'First signed message');delivered=wait_message(alice,'First signed message',True)
  command(alice,"""
   const [appURL,cssURL]=arguments,{mount}=await import(appURL),f=window.fixture,make=(tag,cls='',text='')=>{const el=document.createElement(tag);el.className=cls;el.textContent=text;return el;},textButton=(label,fn)=>{const el=make('button','',label);el.type='button';el.addEventListener('click',fn);return el;};
   const link=document.createElement('link');link.rel='stylesheet';link.href=cssURL;document.head.append(link);
   const host={ui:{make,textButton},session:()=>f.session,signal:f.life.signal,network:{config:f.config},storage:{deviceHistory:{channels:({onChange})=>f.owner.attach({signal:f.life.signal,onChange})}}};f.app=mount(host);document.body.append(f.app.element);
   const end=performance.now()+30000;while(performance.now()<end){const item=[...f.app.element.querySelectorAll('.channel-message')].find(x=>x.textContent.includes('First signed message'));if(item?.dataset.delivery==='delivered'){if(!item.getAttribute('aria-label')?.includes('Delivered to another account')||!item.title.includes('confirmed saving'))throw Error('Delivered accessibility label is inaccurate');return true;}await new Promise(r=>setTimeout(r,100));}throw Error('Chat did not display Delivered: '+f.app.element.textContent);
  """,[app_url,css_url])
  command(bob,"window.fixture.originalFetch=window.fetch.bind(window);window.fixture.offline=true;window.fetch=(input,options)=>{const u=new URL(input instanceof Request?input.url:String(input),location.href);return window.fixture.offline&&u.pathname.startsWith('/official-')?Promise.resolve(new Response('{}',{status:503,headers:{'Content-Type':'application/json'}})):window.fixture.originalFetch(input,options);};return true;")
  command(alice,"await window.fixture.channel.queue('chat',{text:'Message while Bob is offline'});return true;")
  second=wait_message(alice,'Message while Bob is offline');time.sleep(18);state=wait_message(alice,'Message while Bob is offline');assert second['id'] not in state['status']['deliveredMessages'],'Offline recipient falsely marked delivery'
  command(alice,"const n=[...window.fixture.app.element.querySelectorAll('.channel-message')].find(x=>x.textContent.includes('Message while Bob is offline'));if(!n||n.dataset.delivery!=='sent')throw Error('Offline recipient should still show Sent');return true;")
  command(bob,"window.fixture.offline=false;window.dispatchEvent(new Event('online'));return true;")
  wait_message(bob,'Message while Bob is offline');wait_message(alice,'Message while Bob is offline',True)
  command(alice,"const end=performance.now()+10000;while(performance.now()<end){const n=[...window.fixture.app.element.querySelectorAll('.channel-message')].find(x=>x.textContent.includes('Message while Bob is offline'));if(n?.dataset.delivery==='delivered')return true;await new Promise(r=>setTimeout(r,100));}throw Error('Chat did not update to Delivered after reconnect');")
  print('PASS two accounts, same-account exclusion, offline/reconnect and Delivered UI',flush=True)
 finally:
  for sid in reversed(sessions):
   try:command(sid,"const f=window.fixture;f.app?.dispose();f.app?.element.remove();f.view.close();f.owner.close();await f.owner.idle();f.pool.close();f.storage.close();f.life.abort();return true;")
   finally:driver.call('/session/'+sid,method='DELETE')

async def main():
 os.umask(0o077)
 with tempfile.TemporaryDirectory(prefix='codi-receipts-') as directory:
  root=Path(directory);public=root/'public';public.mkdir();(public/'index.html').write_text('<!doctype html>');origin='http://127.0.0.1:'+str(free_port());db=root/'official.sqlite';ledger=root/'access.sqlite';keys=root/'keys';keys.mkdir(mode=0o700)
  issuer=Service(Config(root/'issuer',public,origin=origin,rate_per_minute=1000));wsgi=make_server('127.0.0.1',0,OfficialAuthority(issuer),server_class=BoundedServer,handler_class=QuietHandler);thread=threading.Thread(target=wsgi.serve_forever,daemon=True);thread.start();config=issuer.config()
  registry=OfficialChannelRegistry(db);init_policy(db);initialize(ledger);init_receipts(db);provision(db,keys)
  package=os.environ.get('CODI_RECEIPTS_PACKAGE')
  if package:
   policy=root/'policy.json';policy.write_text(json.dumps(config['identity']));listen=free_port()
   process=await asyncio.create_subprocess_exec(sys.executable,'-I','-B',str(Path(package).resolve()/'scripts/run-official-runtime.py'),'--database',str(db),'--ledger',str(ledger),'--issuer-policy',str(policy),'--validator-key-dir',str(keys),'--port',str(listen),'--receipts',stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   line=await asyncio.wait_for(process.stdout.readline(),15)
   if not line:raise RuntimeError('Packaged runtime failed: '+(await process.stderr.read()).decode())
   assert json.loads(line)['port']==listen
   class PackagedRuntime:
    port=listen
    async def close(self):
     if process.returncode is None:process.terminate();await asyncio.wait_for(process.wait(),15)
     if process.returncode!=0:raise RuntimeError('Packaged runtime exited unexpectedly')
   runtime=PackagedRuntime()
  else:runtime=await OfficialRuntime(database=db,ledger=ledger,issuer_policy=config['identity'],validator_key_dir=keys,receipts=True).start()
  outgoing=ClientSession();app=web.Application(client_max_size=8*1048576)
  async def proxy(request):
   target=runtime.port if request.path.startswith('/official-') else wsgi.server_port;headers={k:v for k,v in request.headers.items() if k.lower() not in ('connection','transfer-encoding','host')};headers['Host']=urlsplit(origin).netloc
   async with outgoing.request(request.method,'http://127.0.0.1:'+str(target)+request.raw_path,headers=headers,data=await request.read() if request.can_read_body else None,allow_redirects=False) as response:return web.Response(status=response.status,body=await response.read(),headers={'Content-Type':response.headers.get('Content-Type','application/json')})
  async def asset(request):
   file=(ROOT/request.match_info['path']).resolve()
   if not file.is_relative_to(ROOT) or file.suffix not in ('.mjs','.css') or not file.is_file():raise web.HTTPNotFound()
   return web.Response(body=file.read_bytes(),content_type='text/css' if file.suffix=='.css' else 'text/javascript')
  app.router.add_route('*','/api/v1/{tail:.*}',proxy);app.router.add_route('*','/official-{tail:.*}',proxy);app.router.add_get('/config.json',lambda _:web.json_response(config));app.router.add_get('/',lambda _:web.Response(text='<!doctype html>',content_type='text/html'));app.router.add_get(r'/{path:.*\.(?:mjs|css)}',asset)
  runner=web.AppRunner(app,access_log=None);await runner.setup();await web.TCPSite(runner,'127.0.0.1',urlsplit(origin).port).start()
  catalog=json.loads((ROOT/'.build/receipt-app-test/apps.json').read_text());entry=catalog['apps'][0];app_url='/.build/receipt-app-test/'+str(Path(entry['path']).relative_to('assets/desktop'));css_url=str(Path(app_url).parent/entry['styles'][0])
  try:await asyncio.to_thread(exercise,origin,app_url,css_url)
  finally:await runner.cleanup();await outgoing.close();await runtime.close();await asyncio.to_thread(wsgi.shutdown);wsgi.server_close();thread.join(3);registry.close()
if __name__=='__main__':asyncio.run(main())
