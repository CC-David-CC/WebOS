#!/usr/bin/env python3
"""Ten local browsers use a sealed package and local introduction service."""
import argparse,hashlib,importlib.util,json,shutil,tempfile,traceback,time,subprocess,urllib.request,urllib.error,uuid,shlex
from pathlib import Path
from urllib.parse import urljoin,urlsplit
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run(url='https://ksu.codes/',all_senders=False,without_i35=False,burst=False,without_i34=False):
 parsed=urlsplit(url)
 if (parsed.scheme!='http' or parsed.hostname!='127.0.0.1') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.path.endswith('/'):
  raise ValueError('Test URL must be an HTTPS directory URL')
 origin=parsed.scheme+'://'+parsed.netloc
 sessions={};profiles={};selectors={};checks=[];remotes={};runid=uuid.uuid4().hex;r={'status':'FAIL','scope':__doc__,'measurementCaveat':'receiver MutationObserver timestamps corrected by measured browser clock offsets; wire hooks attach to existing and subsequently accessed links with 100ms scans; earliest frames on new links may be missed; records RPC metadata without payloads; includes scheduling/rendering and offset uncertainty','checks':checks,'actualBrowsers':0,'serverAccountsCreated':0,'liveSite':url,'transport':'WebRTC; only channel code transferred, no manual connection signaling'};started=time.monotonic()
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
  with urllib.request.urlopen(urljoin(url,'config.json'),timeout=10) as response:site_config=json.load(response)
  with urllib.request.urlopen(urljoin(url,'assets/desktop/network-release.json'),timeout=10) as response:graph=json.load(response)
  directory=graph['coreDirectory'];record=graph['core']['networking.js']
  if not directory.startswith('assets/desktop/core-v') or '..' in directory:raise RuntimeError('Invalid network bundle path')
  with urllib.request.urlopen(urljoin(url,directory+'/networking.js'),timeout=10) as response:raw=response.read()
  if len(raw)!=record['bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:raise RuntimeError('Network bundle does not match its manifest')
  network=raw.decode('utf-8');r['networkBundleSHA256']=record['sha256'];config=site_config.get('deviceChannels') or {}
  enabled=config.get('version')=='codi-device-channels/1' and config.get('channelIndex') is True
  injected="version:'codi-device-channels/1'" in network and 'channelIndex:true' in network
  if 'const disabled=false;' not in network or not (enabled or injected):raise RuntimeError('Test site does not enable device channels and channel discovery')
  targets=[]
  for side,target,port,binary,driver,profilebase in (row for row in targets if not(without_i35 and row[1]=='codi-i35') and not(without_i34 and row[1]=='codi-i34')):
   publicip=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip()
   profile=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'mktemp','-d',profilebase+'/codi-group-test-XXXXXXXX'],text=True,timeout=15).strip();assert profile.startswith(profilebase+'/codi-group-test-')
   pidfile='/tmp/codi-group-test-'+runid+'-'+side+'.pid';command='umask 077; echo $$ > '+pidfile+'; exec '+driver+' --port='+str(port)+' --allowed-ips=127.0.0.1'
   proc=subprocess.Popen(['ssh','-o','BatchMode=yes',target,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   remotes[side]={'target':target,'localport':port,'profile':profile,'profilebase':profilebase,'pidfile':pidfile,'driver':proc,'tunnel':tunnel,'binary':binary};r.setdefault('externalHosts',{})[side]={'publicIP':publicip,'name':{'b':'i34','c':'i35','j':'i36'}[side]}
   def ready():
    if proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('Remote ChromeDriver or tunnel ended on '+side)
    try:
     with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/status',timeout=1) as f:return json.load(f)['value']['ready']
    except OSError:return False
   d.wait(ready,25)
  for side in 'abcdefghij':
   profiles[side]=Path(remotes[side]['profile']) if side in remotes else Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':remotes[side]['binary'] if side in remotes else '/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowsers']+=1;call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':url});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('ten browsers opened device-owned chat',True)
  name='Ten Finder '+runid[:12]
  js('a','const n=document.querySelector(arguments[0]);[...n.querySelectorAll("input")].find(x=>x.getAttribute("aria-label")==="Device channel label").value=arguments[1];n.querySelector("[data-directory-create]").click();',[selectors['a'],name]);wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],90)
  for side in 'bcdefghij':
   js(side,'const q=document.querySelector(arguments[0]).querySelector("input[type=search]");q.value=arguments[1];q.dispatchEvent(new Event("input",{bubbles:true}));',[selectors[side],name])
   wait(side,'return [...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].some(x=>x.textContent==="Join");',[selectors[side]],90)
   js(side,'[...document.querySelector(arguments[0]).querySelectorAll("[data-channel-results] button")].find(x=>x.textContent==="Join").click();',[selectors[side]]);wait(side,'return !!document.querySelector(arguments[0]).value;',[node(side,'data-device-select')],90)
  check('nine participants found and joined the channel',True)
  for side in 'abcdefghij':
   wait(side,'const pool=desktopNetwork.appContext().pool;return pool.list().some(p=>{const link=pool.get(p.id)?.link;return !!link&&!link.closed&&typeof link.onDeviceMember==="function"&&typeof link.sendDeviceMember==="function";});',seconds=90)
   installed=js(side,'''const pool=desktopNetwork.appContext().pool;window.__stageTrace=[];const seen=new WeakSet();let count=0;const attach=link=>{if(!link||seen.has(link)||typeof link.onDeviceMember!=="function"||typeof link.sendDeviceMember!=="function")return;seen.add(link);count++;const recv=link.onDeviceMember,send=link.sendDeviceMember;const record=(direction,b)=>{window.__stageTrace.push({name:"member-wire",start:Date.now(),end:Date.now(),direction,op:b?.op||null,method:b?.method||null,request:b?.request_id||null,code:b?.code||null,retryMs:b?.retry_after_ms||null,peer:link.connectionId});if(window.__stageTrace.length>4000)window.__stageTrace.shift();};link.onDeviceMember=async function(a,...args){record("receive",a.body);return recv.call(this,a,...args);};link.sendDeviceMember=async function(b,...args){record("send",b);return send.call(this,b,...args);};};const originalGet=pool.get.bind(pool);pool.get=function(id){const entry=originalGet(id);attach(entry?.link);return entry;};const scan=()=>{for(const p of pool.list())attach(originalGet(p.id)?.link);};scan();window.__wireTraceTimer=setInterval(scan,100);window.__loopLag=[];let last=performance.now();window.__loopLagTimer=setInterval(()=>{const now=performance.now();window.__loopLag.push(Math.max(0,now-last-100));if(window.__loopLag.length>2000)window.__loopLag.shift();last=now;},100);return count;''')
   assert installed>0, 'No member link available for diagnostics on '+side
  r['clockCalibration']={};r['traceMeasurements']=[]
  for side in 'abcdefghij':
   trials=[]
   for _ in range(3):
    before=time.time()*1000;remote=js(side,'return Date.now();');after=time.time()*1000;trials.append({'offsetMs':remote-(before+after)/2,'uncertaintyMs':(after-before)/2+1})
   r['clockCalibration'][side]=min(trials,key=lambda x:x['uncertaintyMs'])
  senders='abcdefghij' if all_senders else 'aj'
  for sender in senders:
   message='Trace '+sender+' '+runid[:8]
   for recipient in 'abcdefghij':
    js(recipient,'window.__loopLag=[];')
    js(recipient,'const root=document.querySelector(arguments[0]);window.__codiTrace?.observer?.disconnect();const t={message:arguments[1],arrival:null};const record=()=>{if(t.arrival===null&&root.querySelector("[data-device-history]").textContent.includes(t.message))t.arrival=Date.now();};t.observer=new MutationObserver(record);t.observer.observe(root.querySelector("[data-device-history]"),{childList:true,subtree:true,characterData:true});window.__codiTrace=t;record();',[selectors[recipient],message])
   click_time=js(sender,'const n=document.querySelector(arguments[0]);n.querySelector("[data-device-draft]").value=arguments[1];const t=Date.now();n.querySelector("[data-device-queue]").click();return t;',[selectors[sender],message]);seen={};deadline=time.monotonic()+120
   while len(seen)<10 and time.monotonic()<deadline:
    for recipient in 'abcdefghij':
     if recipient in seen:continue
     stamp=js(recipient,'return window.__codiTrace?.arrival||null;')
     if stamp is not None:seen[recipient]=round((stamp-r['clockCalibration'][recipient]['offsetMs']-click_time+r['clockCalibration'][sender]['offsetMs'])/1000,3)
    if len(seen)<10:time.sleep(.25)
   row={'sender':sender,'arrivalsSeconds':seen,'allReceived':len(seen)==10,'clickTimeMs':click_time,'stages':{}};
   for side in 'abcdefghij':
    row['stages'][side]=js(side,'const out=window.__stageTrace||[];window.__stageTrace=[];return out;');row.setdefault('loopLagMs',{})[side]=js(side,'const values=[...(window.__loopLag||[])].sort((a,b)=>a-b);return {samples:values.length,p95:values.length?values[Math.floor((values.length-1)*0.95)]:null,max:values.length?values[values.length-1]:null};')
   r['traceMeasurements'].append(row);print(json.dumps({'sender':sender,'allReceived':row['allReceived']}),flush=True);assert len(seen)==10,'Timed message did not reach every profile'
  check(str(len(senders))+' instrumented messages reached all participants',True)
  if burst:
   selected='abj';messages={side:'Burst '+side+' '+runid[:8] for side in selected}
   for recipient in 'abcdefghij':
    js(recipient,'''const container=document.querySelector(arguments[0]),root=container.querySelector("[data-device-history]"),channel=container.querySelector("[data-device-select]").value,messages=arguments[1];window.__burstTimes={};window.__acceptedTimes={};const record=()=>{const text=root.textContent;for(const [sender,value] of Object.entries(messages))if(!window.__burstTimes[sender]&&text.includes(value))window.__burstTimes[sender]=Date.now();};window.__burstObserver=new MutationObserver(record);window.__burstObserver.observe(root,{childList:true,subtree:true,characterData:true});record();let busy=false;window.__acceptedTimer=setInterval(()=>{if(busy)return;busy=true;const open=indexedDB.open('codi-device-channel-archive-v1');open.onerror=()=>{busy=false;};open.onsuccess=()=>{const db=open.result;try{const tx=db.transaction('heads','readonly'),request=tx.objectStore('heads').getAll();tx.oncomplete=()=>{try{const entry=request.result.find(row=>row.key?.[1]===channel),state=entry&&JSON.parse(entry.checkpoint).state;for(const [sender,value] of Object.entries(messages))if(!window.__acceptedTimes[sender]&&state?.messages?.some(m=>m.text===value))window.__acceptedTimes[sender]=Date.now();}finally{db.close();busy=false;}};tx.onerror=()=>{db.close();busy=false;};}catch{db.close();busy=false;}};},400);''',[selectors[recipient],messages])
   for side in 'abcdefghij':js(side,'window.__stageTrace=[];')
   start_ms=time.time()*1000+5000
   for side in selected:
    js(side,'const root=document.querySelector(arguments[0]),text=arguments[1],delay=Math.max(0,arguments[2]-Date.now());setTimeout(()=>{const button=root.querySelector("[data-device-queue]");window.__burstClick={at:Date.now(),disabled:button.disabled};root.querySelector("[data-device-draft]").value=text;button.click();},delay);',[selectors[side],messages[side],start_ms+r['clockCalibration'][side]['offsetMs']])
   deadline=time.monotonic()+125;seen={}
   while len(seen)<10 and time.monotonic()<deadline:
    for recipient in 'abcdefghij':
     if recipient in seen:continue
     matched=js(recipient,'const text=document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent;return arguments[1].every(value=>text.includes(value));',[selectors[recipient],list(messages.values())])
     if matched:seen[recipient]=round(time.time()-start_ms/1000,3)
    if len(seen)<10:time.sleep(.3)
   clicks={side:js(side,'return window.__burstClick||null;') for side in selected};observed={side:js(side,'window.__burstObserver.disconnect();clearInterval(window.__acceptedTimer);return {display:window.__burstTimes,accepted:window.__acceptedTimes};') for side in 'abcdefghij'}
   wire={side:js(side,'return window.__stageTrace||[];') for side in 'abcdefghij'}
   failure_snapshots={}
   for side in 'abcdefghij':
    try:failure_snapshots[side]=call(side,'/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(s=>done({member:s.deviceChannels?.members?.failures||[],replica:s.deviceChannels?.replicas?.failures||[],timing:(s.deviceChannels?.peerOrganization||[]).map(x=>({member:x.memberTiming||[],round:x.roundTiming||[]}))}),e=>done({error:e.message}));','args':[]})
    except Exception as error:failure_snapshots[side]={'error':str(error)}
   r['burst']={'senders':selected,'allMessagesArrivalSeconds':seen,'allReceived':len(seen)==10,'clicks':clicks,'individualArrivalTimes':{s:v['display'] for s,v in observed.items()},'acceptedTimes':{s:v['accepted'] for s,v in observed.items()},'wireMetadata':wire,'localFailureSnapshots':failure_snapshots};check('three concurrent messages reached all participants',len(seen)==10 and all(clicks[s] and not clicks[s]['disabled'] for s in selected))
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
  r.update(ownedProfilesRemoved=all(not p.exists() for side,p in profiles.items() if side not in remotes) and all(v.get('cleanup')=='clean' for v in remotes.values()),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--url',default='https://ksu.codes/');p.add_argument('--all-senders',action='store_true');p.add_argument('--without-i35',action='store_true');p.add_argument('--without-i34',action='store_true');p.add_argument('--burst',action='store_true');a=p.parse_args();assert not a.output.exists();r=run(a.url,a.all_senders,a.without_i35,a.burst,a.without_i34);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
