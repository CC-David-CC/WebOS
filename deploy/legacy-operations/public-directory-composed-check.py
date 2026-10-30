#!/usr/bin/env python3
"""Exercise the packaged desktop in two owned browsers with a local steward."""
import argparse,asyncio,functools,http.server,importlib.util,json,shutil,tempfile,threading,traceback,types,sqlite3,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Handler(http.server.SimpleHTTPRequestHandler):
 config=None
 def log_message(self,*args): pass
 def do_GET(self):
  if self.path=='/config.json' and self.config is not None:
   data=json.dumps(self.config).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  else: super().do_GET()
def run(release, short=False, interrupt=False, refuse=False):
 result={'status':'FAIL','checks':[],'release':str(release),'scope':'Two fresh local Chrome profiles, exact candidate assets and a local test steward; no WAN or live deployment.'}; sessions={};profiles={};selectors={};server=None;thread=None;loop=None;lt=None;steward=None
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def wait(side,code,args=[],seconds=90):return d.wait(lambda:js(side,code,args),seconds)
 def check(name):result['checks'].append(name);print(json.dumps({'check':name}),flush=True)
 try:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(release)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  m=types.ModuleType('steward_fixture');m.__file__=str(ROOT/'scripts/steward-network-check.py');exec((ROOT/'scripts/steward-network-check.py').read_text().split('async def main():',1)[0],m.__dict__)
  args,scope,port,root,seed=m.fixture();seed['stewards'][0]['limits']['lease_seconds']=10 if short else 120;args['seed']=m.jose.sign(seed,root,'codi-seed/1');args['admission_seconds']=12 if short else 300;args['origins'].append(origin);result['fixtureLeaseSeconds']=seed['stewards'][0]['limits']['lease_seconds'];result['fixtureAdmissionSeconds']=args['admission_seconds'];loop=asyncio.new_event_loop();lt=threading.Thread(target=loop.run_forever,daemon=True);lt.start();instrumented=types.ModuleType('steward.instrumented_test');instrumented.__package__='steward';source=(release/'steward/server.py').read_text();needle='        except (Exception,):\n            # No token';assert source.count(needle)==1;source=source.replace(needle,"        except (Exception,) as error:\n            self.test_errors.append(type(error).__name__)\n            # No token");exec(compile(source,'<fixture-steward>','exec'),instrumented.__dict__);steward=instrumented.StewardServer(**args);steward.test_errors=result['serverErrorTypes']=[];quota=steward.quota;result['quotaRefusals']=[]
  def observed_quota(kind,size=0):
   try:return quota(kind,size)
   except ValueError as e:result['quotaRefusals'].append({'kind':kind,'reason':str(e)});raise
  steward.quota=observed_quota;asyncio.run_coroutine_threadsafe(steward.start(port),loop).result(timeout=15)
  Handler.config=json.loads((release/'config.json').read_text());Handler.config['discovery']={'pin':{'realm':args['realm'],'rootKey':args['root_key'],'endpoints':[args['endpoint']],'allowLoopback':True},'seed':args['seed'],'descriptor':steward.descriptor(),'scope':scope}
  for side in 'a':
   profiles[side]=Path(tempfile.mkdtemp(prefix='codi-composed-peer-',dir=Path.home()/'snap/chromium/common'))
   sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}})['sessionId']
   d.call('/session/'+sessions[side]+'/url',{'url':origin+'/'});wait(side,'return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
   wid=js(side,'return [...desktopLab.surfaces.values()][0].launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';sel=selectors[side];wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel]);
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel]):
    el=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+el+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel])
  check('packaged owner desktop opened chat')
  js('a','const n=document.querySelector(arguments[0]);[...n.querySelectorAll("input")].find(x=>x.getAttribute("aria-label")==="Device channel label").value="Composed peer check";n.querySelector("[data-directory-create]").click();',[selectors['a']]);wait('a','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]").value;',[selectors['a']])
  dbpath=args['publisher_state'].directory/'public-channels.sqlite3'
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   with sqlite3.connect(dbpath) as db: count=db.execute("SELECT count(*) FROM channel_directory WHERE label=?",('Composed peer check',)).fetchone()[0]
   if count:break
   time.sleep(.25)
  assert count,'owner publication was not stored'
  d.call('/session/'+sessions.pop('a'),method='DELETE')
  asyncio.run_coroutine_threadsafe(steward.close(),loop).result(timeout=15)
  steward=instrumented.StewardServer(**args);steward.test_errors=result['serverErrorTypes']
  asyncio.run_coroutine_threadsafe(steward.start(port),loop).result(timeout=15)
  Handler.config['discovery']['descriptor']=steward.descriptor()
  check('creator offline and introduction service restarted with stored reference')
  side='b';profiles[side]=Path(tempfile.mkdtemp(prefix='codi-composed-peer-',dir=Path.home()/'snap/chromium/common'))
  sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}})['sessionId']
  d.call('/session/'+sessions[side]+'/url',{'url':origin+'/'});wait(side,'return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  wid=js(side,'return [...desktopLab.surfaces.values()][0].launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';sel=selectors[side];wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel])
  if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel]):
   el=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+el+'/click',{})
  wait(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel])
  js('b','const q=document.querySelector(arguments[0]).querySelector("input[type=search]");q.value="Composed peer check";q.dispatchEvent(new Event("input",{bubbles:true}));',[selectors['b']]);wait('b','return [...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].some(x=>x.textContent==="Join");',[selectors['b']],25)
  check('fresh browser found offline owner channel without a code')
  side='a';sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}})['sessionId']
  d.call('/session/'+sessions[side]+'/url',{'url':origin+'/'});wait(side,'return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  wid=js(side,'return [...desktopLab.surfaces.values()][0].launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';sel=selectors[side];wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel]);js(side,'const n=document.querySelector(arguments[0]);if(!n.querySelector("[data-device-channels]"))n.querySelector(".storage-consent button:not(:disabled)")?.click();',[sel]);wait(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-select]")?.value;',[sel],120)
  js('b','[...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].find(x=>x.textContent==="Join").click();',[selectors['b']]);wait('b','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]").value;',[selectors['b']]);check('second browser discovered and joined channel')
  for side,other in [('a','b'),('b','a')]:
   text='Packaged peer message '+side;wait(side,'return !document.querySelector(arguments[0]).querySelector("[data-device-queue]").disabled;',[selectors[side]]);js(side,'const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value=arguments[1];n.querySelector("[data-device-queue]").click();',[selectors[side],text]);wait(other,'return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes(arguments[1]);',[selectors[other],text],120)
  check('both peers exchanged messages')
  if refuse:
   async def inject_refusal():
    send=steward.send;trigger={'armed':True}
    async def fault_once(ws,token):
     if trigger['armed']:
      trigger['armed']=False;result['injectedUnavailable']=True;raise instrumented.Unavailable('fixture temporary capacity')
     return await send(ws,token)
    steward.send=fault_once
   asyncio.run_coroutine_threadsafe(inject_refusal(),loop).result(timeout=10)
   d.call('/session/'+sessions['a']+'/timeouts',{'script':180000})
   recovered=d.call('/session/'+sessions['a']+'/execute/async',{'script':'const done=arguments[arguments.length-1];(async()=>{for(let i=0;i<600;i++){const s=await desktopNetwork.stats();if(s.discovery?.status==="ready"&&s.discovery.recoveries>0)return done(true);await new Promise(r=>setTimeout(r,100));}done(false);})().catch(()=>done(false));','args':[]})
   assert result.get('injectedUnavailable') and recovered,'temporary refusal did not recover';check('browser reauthenticated after temporary server refusal')
  if interrupt:
   async def interrupt_connections():
    clients=list(steward.clients.values());assert len(clients)==2
    await asyncio.gather(*(ws.close(1013,'temporary test interruption') for ws,_ in clients))
   asyncio.run_coroutine_threadsafe(interrupt_connections(),loop).result(timeout=10)
   for side in 'ab':
    d.call('/session/'+sessions[side]+'/timeouts',{'script':180000})
    value=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];(async()=>{for(let i=0;i<600;i++){const s=await desktopNetwork.stats();if(s.discovery?.status==="ready"&&s.discovery.recoveries>0)return done(true);await new Promise(r=>setTimeout(r,100));}done(false);})().catch(()=>done(false));','args':[]});assert value,'introduction service did not recover on '+side
   check('both browsers recovered after retryable server disconnect')
  d.call('/session/'+sessions.pop('b'),method='DELETE')
  for number in range(8):
   message='Message while away '+str(number)
   wait('a','return !document.querySelector(arguments[0]).querySelector("[data-device-queue]").disabled;',[selectors['a']])
   js('a','const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value=arguments[1];n.querySelector("[data-device-queue]").click();',[selectors['a'],message]);wait('a','return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes(arguments[1]);',[selectors['a'],message],120)
  sessions['b']=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles['b'])]}}}})['sessionId']
  d.call('/session/'+sessions['b']+'/url',{'url':origin+'/'});wait('b','return !!window.desktopLab?.session&&desktopLab.surfaces.size>0;');d.call('/session/'+sessions['b']+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  wid=js('b','return [...desktopLab.surfaces.values()][0].launch("chat").id;');selectors['b']='[data-window="'+str(wid)+'"]';sel=selectors['b'];wait('b','return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel])
  js('b','const n=document.querySelector(arguments[0]);if(!n.querySelector("[data-device-channels]"))n.querySelector(".storage-consent button:not(:disabled)")?.click();',[sel])
  wait('b','return !!document.querySelector(arguments[0]).querySelector("[data-device-select]")?.value;',[sel],120)
  wait('b','const t=document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent;return Array.from({length:8},(_,i)=>"Message while away "+i).every(x=>t.includes(x));',[sel],120);check('reopened browser recovered eight messages sent while away')
  result['status']='PASS' 
 except Exception as e:
  result['error']=str(e);result['traceback']=traceback.format_exc()
  for side in sessions:
   try:
    result.setdefault('diagnostics',{})[side]=js(side,'return document.body.innerText.slice(-5000);')
    result.setdefault('directoryError',{})[side]=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.appContext().startChannelIndex().then(d=>d.search({query: "Composed peer check"})).then(x=>done({page:x}),e=>done({error:e.message,stack:e.stack}));','args':[]});
    result.setdefault('network',{})[side]=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(done,e=>done({error:e.message}));','args':[]})
   except Exception:pass
 finally:
  for sid in sessions.values():
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:result['status']='FAIL';result['cleanupError']=str(e)
  for p in profiles.values():shutil.rmtree(p,ignore_errors=True)
  result['profilesRemoved']=all(not p.exists() for p in profiles.values())
  if steward and loop:asyncio.run_coroutine_threadsafe(steward.close(),loop).result(timeout=15)
  if loop:loop.call_soon_threadsafe(loop.stop)
  if lt:lt.join(timeout=5)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=5)
  if 'args' in locals():shutil.rmtree(args['publisher_state'].directory,ignore_errors=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--refuse',action='store_true');p.add_argument('--short',action='store_true');p.add_argument('--interrupt',action='store_true');p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.release.resolve(),a.short,a.interrupt,a.refuse);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':r['checks']}));raise SystemExit(r['status']!='PASS')
