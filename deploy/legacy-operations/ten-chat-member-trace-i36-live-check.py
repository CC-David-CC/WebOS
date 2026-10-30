#!/usr/bin/env python3
"""Ten browsers on two home-connected hosts discover a channel and exchange messages."""
import argparse,importlib.util,json,shutil,tempfile,traceback,time,subprocess,urllib.request,urllib.error,uuid,shlex,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];remotes={};runid=uuid.uuid4().hex;r={'status':'FAIL','measurementCaveat':'Coordinator elapsed time until each UI shows an accepted message, concurrently observed after the click; excludes pending/unconfirmed entries, includes local acceptance, UI and command scheduling, not wire latency; renderer heap excludes native/browser processes.', 'scope':__doc__,'checks':checks,'actualBrowsers':10,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; only channel code transferred, no manual connection signaling'};started=time.monotonic()
 def call(side,path,data=None,method=None):
  if side not in remotes:return d.call(path,data,method)
  req=urllib.request.Request('http://127.0.0.1:'+str(remotes[side]['localport'])+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
  try:
   with urllib.request.urlopen(req,timeout=120) as response:return json.load(response)['value']
  except urllib.error.HTTPError as error:raise RuntimeError(error.read().decode()) from error
 def js(side,code,args=[]):return call(side,'/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def wait(side,code,args=[],seconds=60):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def node(side,attr):return selectors[side]+' ['+attr+']'
 def click(side,attr):
  selector=node(side,attr);wait(side,'const n=document.querySelector(arguments[0]);return !!n&&!n.disabled;',[selector]);js(side,'document.querySelector(arguments[0]).click();',[selector])
 def value(side,attr):return js(side,'return document.querySelector(arguments[0]).value;',[node(side,attr)])
 def input_value(side,attr,v):js(side,'const n=document.querySelector(arguments[0]);n.value=arguments[1];n.dispatchEvent(new Event("input",{bubbles:true}));',[node(side,attr),v])
 def generous(side):
  wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-apply-global-allowance')],60)
  for key in ['uploadBytes','downloadBytes','serveBytes']:
   sel=selectors[side]+' [data-device-global-quota="'+key+'"]';js(side,'const n=document.querySelector(arguments[0]);n.value="65536";n.dispatchEvent(new Event("input",{bubbles:true}));',[sel])
  click(side,'data-device-apply-global-allowance');wait(side,'return !document.querySelector(arguments[0]).disabled;',[node(side,'data-device-apply-global-allowance')],60)
 def trace_history(side,seconds):
  start=time.monotonic();samples=[]
  while time.monotonic()-start<seconds:
   for who in (r.get('currentParent','a'),side):
    try:
     v=call(who,'/session/'+sessions[who]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(x=>done({device:x.deviceChannels,budget:x.budget}),e=>done({error:e.message}));','args':[]})
     v['side']=who;v['t']=round(time.monotonic()-start,1);samples.append(v)
    except Exception as e:samples.append({'side':who,'error':str(e)})
   if js(side,'return document.querySelector(arguments[0]).textContent.includes("Small group initial message");',[node(side,'data-device-history')]):r.setdefault('trace',{})[side]=samples;return True
   time.sleep(5)
  r.setdefault('trace',{})[side]=samples
  raise AssertionError('History recovery timed out for '+side)
 try:
  for side,target,port,binary,driver,profilebase in [('j','maint@10.0.7.105',19537,'/usr/bin/chromium','/usr/bin/chromedriver','/tmp')]:
   publicip=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip()
   profile=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'mktemp','-d',profilebase+'/codi-group-test-XXXXXXXX'],text=True,timeout=15).strip();assert profile.startswith(profilebase+'/codi-group-test-')
   pidfile='/tmp/codi-group-test-'+runid+'-'+side+'.pid';command='umask 077; echo $$ > '+pidfile+'; exec '+driver+' --port='+str(port)+' --allowed-ips=127.0.0.1'
   proc=subprocess.Popen(['ssh','-o','BatchMode=yes',target,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   remotes[side]={'target':target,'localport':port,'profile':profile,'profilebase':profilebase,'pidfile':pidfile,'driver':proc,'tunnel':tunnel,'binary':binary};r.setdefault('externalHosts',{})[side]={'publicIP':publicip,'name':'Moonpie' if side=='b' else 'i36'}
   def ready():
    if proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('Remote ChromeDriver or tunnel ended on '+side)
    try:
     with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1) as f:return json.load(f)['value']['ready']
    except OSError:return False
   d.wait(ready,25)
  for side in 'abcdefghij':
   profiles[side]=Path(remotes[side]['profile']) if side in remotes else Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':remotes[side]['binary'] if side in remotes else '/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('ten browsers opened device-owned chat',True)
  name='Ten Finder '+runid[:12];r['temporaryLabel']=name
  js('a','const n=document.querySelector(arguments[0]);[...n.querySelectorAll("input")].find(x=>x.getAttribute("aria-label")==="Device channel label").value=arguments[1];n.querySelector("[data-directory-create]").click();',[selectors['a'],name]);wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],90)
  for side in 'bcdefghij':
   js(side,'const q=document.querySelector(arguments[0]).querySelector("input[type=search]");q.value=arguments[1];q.dispatchEvent(new Event("input",{bubbles:true}));',[selectors[side],name])
   wait(side,'return [...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].some(x=>x.textContent==="Join");',[selectors[side]],90)
   js(side,'[...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].find(x=>x.textContent==="Join").click();',[selectors[side]]);wait(side,'return !!document.querySelector(arguments[0]).value;',[node(side,'data-device-select')],90)
  check('nine participants found and joined the channel',True)
  input_value('a','data-device-draft','Automatic WAN history');click('a','data-device-queue')
  for side in 'abcdefghij':wait(side,'return document.querySelector(arguments[0]).textContent.includes("Automatic WAN history");',[node(side,'data-device-history')],120)
  check('all ten receive the channel message',True)
  for side in 'abcdefghij':
   js(side,"""window.__memberTrace={events:[],overflow:0,links:[]};window.__attachMemberTrace=()=>{for(const p of desktopNetwork.appContext().pool.list()){const l=desktopNetwork.appContext().pool.get(p.id)?.link;if(!l||l.__traceInstalled)continue;l.__traceInstalled=true;const send=l.sendDeviceMember,receive=l.onDeviceMember,trace=window.__memberTrace;const record=(direction,b)=>{if(!b||!['call','result','error','get'].includes(b.op))return;if(trace.events.length>=3000){trace.overflow++;return;}trace.events.push({at:Date.now(),direction,peer:p.id,op:b.op,method:b.method||'',request:b.request_id||''});};l.sendDeviceMember=function(b,...args){record('out',b);return send.call(this,b,...args);};if(receive)l.onDeviceMember=function(a,...args){record('in',a?.body);return receive.call(this,a,...args);};trace.links.push({link:l,send,receive});}};window.__attachMemberTrace();""")
  r['clockCalibration']={}
  for side in 'abcdefghij':
   samples=[]
   for attempt in range(3):
    before=time.time()*1000;remote=js(side,'return Date.now();');after=time.time()*1000;samples.append({'rttMs':round(after-before,2),'offsetMs':round(remote-(before+after)/2,2)})
   r['clockCalibration'][side]=min(samples,key=lambda x:x['rttMs'])
  r['deliverySamples']=[];r['rendererHeapBefore']={side:call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}}) for side in 'abcdefghij'}
  for sender in 'bcdefghij':
   message='Automatic reply '+sender
   for side in 'abcdefghij':js(side,'window.__attachMemberTrace();')
   for side in 'abcdefghij':
    js(side,"""const node=document.querySelector(arguments[0]),message=arguments[1];window.__deliveryTrace?.observer?.disconnect();const trace=window.__deliveryTrace={first:{}};const check=()=>{for(const x of node.children){if(x.tagName!=='DIV'||!x.textContent.includes(message))continue;const kind=x.hasAttribute('data-pending-message')?'localPending':x.hasAttribute('data-peer-pending-message')?'peerUnconfirmed':'accepted';trace.first[kind]??=Date.now();}};trace.observer=new MutationObserver(check);trace.observer.observe(node,{subtree:true,childList:true,characterData:true});check();""",[node(side,'data-device-history'),message])
   startedMessage=time.monotonic();startedWall=time.time()*1000;input_value(sender,'data-device-draft',message);click(sender,'data-device-queue');arrivals={} 
   def observe(side):
    script="""const selector=arguments[0],message=arguments[1],done=arguments[arguments.length-1],node=document.querySelector(selector);if(!node){done(false);return;}let finished=false,observer,timer;const started=Date.now();const finish=value=>{if(finished)return;finished=true;observer?.disconnect();clearTimeout(timer);done({found:value,started,visible:Date.now()});};const check=()=>{if([...node.children].some(x=>x.tagName==='DIV'&&!x.hasAttribute('data-pending-message')&&!x.hasAttribute('data-peer-pending-message')&&x.textContent.includes(message)))finish(true);};observer=new MutationObserver(check);observer.observe(node,{subtree:true,childList:true,characterData:true});timer=setTimeout(()=>finish(false),120000);check();"""
    result=call(side,'/session/'+sessions[side]+'/execute/async',{'script':script,'args':[node(side,'data-device-history'),message]});observed=time.time()*1000
    if not result.get('found'):raise AssertionError('Accepted message timed out for '+side)
    offset=r['clockCalibration'][side]['offsetMs'];return side,{'responseSeconds':round(time.monotonic()-startedMessage,3),'browserVisibleSeconds':round((result['visible']-offset-startedWall)/1000,3),'responseLagMs':round(observed-(result['visible']-offset),1),'observerStartSeconds':round((result['started']-offset-startedWall)/1000,3)}
   with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    arrivals=dict(executor.map(observe,'abcdefghij'))
   for side in 'abcdefghij':
    trace=js(side,'window.__deliveryTrace.observer.disconnect();return window.__deliveryTrace.first;');offset=r['clockCalibration'][side]['offsetMs'];arrivals[side]['firstUiSeconds']={key:round((stamp-offset-startedWall)/1000,3) for key,stamp in trace.items()}
   r['deliverySamples'].append({'sender':sender,'startedWallMs':startedWall,'allObservedSeconds':max(v['responseSeconds'] for v in arrivals.values()),'browserMeasurements':arrivals});print(json.dumps({'message':sender,'allObservedSeconds':max(v['responseSeconds'] for v in arrivals.values()),'pi':arrivals['j']}),flush=True)
  r['memberTraces']={side:js(side,"""const trace=window.__memberTrace;for(const {link,send,receive} of trace.links){link.sendDeviceMember=send;link.onDeviceMember=receive;delete link.__traceInstalled;}return {events:trace.events,overflow:trace.overflow};""") for side in 'abcdefghij'}
  r['rendererHeapAfter']={side:call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}}) for side in 'abcdefghij'}
  check('all nine replies reach every participant',True)
  old=js('j','return desktopNetwork.appContext().pool.list().map(x=>x.id);');js('j','for(const p of desktopNetwork.appContext().pool.list())desktopNetwork.appContext().pool.closeEntry(p.id,"test connection interruption");')
  wait('j','return desktopNetwork.appContext().pool.list().some(p=>!arguments[0].includes(p.id)&&p.state==="ready");',[old],120)
  input_value('a','data-device-draft','After automatic reconnect');click('a','data-device-queue');wait('j','return document.querySelector(arguments[0]).textContent.includes("After automatic reconnect");',[node('j','data-device-history')],120)
  check('remote peer reconnects automatically and receives new history',True)
  input_value('j','data-device-draft','Reply after automatic reconnect');click('j','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Reply after automatic reconnect");',[node('a','data-device-history')],120)
  check('reconnected remote peer can send a message',True)
  r['status']='PASS'

 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=js(side,'return {body:document.body.innerText,status:document.querySelector(arguments[0])?.querySelector("[data-device-status]")?.textContent,peer:document.querySelector(arguments[0])?.querySelector("[data-device-peer]")?.options.length};',[selectors.get(side,'body')]);r[side+'Network']=call(side,'/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(done,e=>done({error:e.message}));','args':[]})
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:call(side,'/session/'+sid,method='DELETE')
   except Exception as e:r['status']='FAIL';r[side+'CleanupError']=str(e)
  for side,remote in remotes.items():
   remote['tunnel'].terminate();remote['tunnel'].wait(timeout=10);remote['driver'].terminate();remote['driver'].wait(timeout=10)
   code='import os,signal,sys,shutil;from pathlib import Path;p=Path(sys.argv[1]);f=Path(sys.argv[2]);assert p.parent==Path(sys.argv[3]) and p.name.startswith("codi-group-test-");pid=int(f.read_text()) if f.exists() else 0;cmd=Path("/proc")/str(pid)/"cmdline";raw=cmd.read_bytes() if cmd.exists() else b"";assert not raw or b"chromedriver" in raw;os.kill(pid,signal.SIGTERM) if raw else None;shutil.rmtree(p);f.unlink(missing_ok=True);print("clean")'
   try:remote['cleanup']=subprocess.check_output(['ssh','-o','BatchMode=yes',remote['target'],'python3','-c',shlex.quote(code),remote['profile'],remote['pidfile'],remote['profilebase']],text=True,timeout=30).strip()
   except Exception as e:r['status']='FAIL';r[side+'CleanupError']=str(e)
  for side,p in profiles.items():
   if side not in remotes:shutil.rmtree(p)
  if r.get('temporaryLabel'):
   code='import sqlite3,sys,json; db=sqlite3.connect("/var/lib/codi-connected/ksu/steward/ledger/public-channels.sqlite3"); label=sys.argv[1]; rows=db.execute("SELECT scope,channel FROM channel_directory WHERE label=?",(label,)).fetchall(); assert len(rows)<=1; db.execute("DELETE FROM channel_directory WHERE label=?",(label,)); db.commit(); print(json.dumps(len(rows)))'
   try:r['removedTestReference']=json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','runuser','-u','codi-steward','--','/usr/bin/python3','-c',shlex.quote(code),shlex.quote(r['temporaryLabel'])],text=True,timeout=30))
   except Exception as e:r['status']='FAIL';r['directoryCleanupError']=str(e)
  r.update(ownedProfilesRemoved=all(not p.exists() for side,p in profiles.items() if side not in remotes) and all(v.get('cleanup')=='clean' for v in remotes.values()),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
