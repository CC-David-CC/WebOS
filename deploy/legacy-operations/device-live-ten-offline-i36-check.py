#!/usr/bin/env python3
"""Ten public browsers test i36 offline backlog and restart on one home network."""
import argparse,importlib.util,json,shutil,tempfile,traceback,time,subprocess,urllib.request,urllib.error,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];remotes={};runid=uuid.uuid4().hex;r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':10,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; only channel code transferred, no manual connection signaling'};started=time.monotonic()
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
  for side,target,port,binary,driver,profilebase in [('b','maint@10.0.7.105',19537,'/usr/bin/chromium','/usr/bin/chromedriver','/tmp')]:
   publicip=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'curl','-4','-fsS','--max-time','10','https://api.ipify.org'],text=True,timeout=20).strip()
   profile=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'mktemp','-d',profilebase+'/codi-group-test-XXXXXXXX'],text=True,timeout=15).strip();assert profile.startswith(profilebase+'/codi-group-test-')
   pidfile='/tmp/codi-group-test-'+runid+'-'+side+'.pid';command='umask 077; echo $$ > '+pidfile+'; exec '+driver+' --port='+str(port)+' --allowed-ips=127.0.0.1'
   proc=subprocess.Popen(['ssh','-o','BatchMode=yes',target,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(port)+':127.0.0.1:'+str(port),target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   remotes[side]={'target':target,'localport':port,'profile':profile,'profilebase':profilebase,'pidfile':pidfile,'driver':proc,'tunnel':tunnel,'binary':binary};r.setdefault('externalHosts',{})[side]={'publicIP':publicip,'name':'i36'}
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
  js('a','[...document.querySelector(arguments[0]).querySelectorAll(".channel-controls button")].find(b=>b.textContent==="Create channel").click();',[selectors['a']]);wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],90)
  wait('a','const b=[...document.querySelector(arguments[0]).querySelectorAll(".channel-controls button")].find(b=>b.textContent==="Show channel code");return !!b&&!b.disabled;',[selectors['a']],90);js('a','[...document.querySelector(arguments[0]).querySelectorAll(".channel-controls button")].find(b=>b.textContent==="Show channel code").click();',[selectors['a']]);code=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-channel-code')],60)
  for side in 'bcdefghij':
   js(side,'const e=document.querySelector(arguments[0]);e.querySelector("[data-channel-code]").value=arguments[1];[...e.querySelectorAll(".channel-controls button")].find(b=>b.textContent==="Join channel").click();',[selectors[side],code]);wait(side,'return !!document.querySelector(arguments[0]).value;',[node(side,'data-device-select')],90)
  check('nine participants joined with only a channel code',True)
  input_value('a','data-device-draft','Automatic WAN history');click('a','data-device-queue')
  for side in 'abcdefghij':wait(side,'return document.querySelector(arguments[0]).textContent.includes("Automatic WAN history");',[node(side,'data-device-history')],120)
  check('all ten receive the channel message',True)
  for side in 'bcdefghij':
   input_value(side,'data-device-draft','Automatic reply '+side);click(side,'data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node('a','data-device-history'),'Automatic reply '+side],120)
  for side in 'abcdefghij':
   for sender in 'bcdefghij':wait(side,'return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node(side,'data-device-history'),'Automatic reply '+sender],120)
  check('all nine replies reach every participant',True)
  call('b','/session/'+sessions.pop('b'),method='DELETE');check('remote browser closes while its channel stays saved on its device',True)
  for number in range(12):
   message='Offline backlog '+str(number);input_value('a','data-device-draft',message);click('a','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node('a','data-device-history'),message],120)
  check('online participant saved twelve messages while remote browser was closed',True)
  side='b';v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':remotes[side]['binary'],'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
  wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
  if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
   e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
  wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
  wait(side,'return !!document.querySelector(arguments[0]).value;',[node(side,'data-device-select')],90)
  for number in range(12):wait(side,'return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[node(side,'data-device-history'),'Offline backlog '+str(number)],120)
  check('restarted remote browser restored its saved channel and caught up on all twelve offline messages',True)
  input_value('b','data-device-draft','Reply after browser restart');click('b','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Reply after browser restart");',[node('a','data-device-history')],120)
  check('restarted remote browser can send after catching up',True)
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
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
