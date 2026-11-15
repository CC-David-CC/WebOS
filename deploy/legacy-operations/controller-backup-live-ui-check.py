#!/usr/bin/env python3
"""Three public browsers exercise owner backup and validator controls in the actual live desktop."""
import argparse,importlib.util,json,shutil,tempfile,traceback,time,subprocess,urllib.request,urllib.error,uuid,shlex
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];remotes={};runid=uuid.uuid4().hex;r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':3,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; only channel code transferred, no manual connection signaling'};started=time.monotonic()
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
  for side in 'abc':
   profiles[side]=Path(remotes[side]['profile']) if side in remotes else Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':remotes[side]['binary'] if side in remotes else '/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   if side=='a':check('main chat keeps code, moderation and Nerd details collapsed',js(side,'const n=document.querySelector(arguments[0]);const r=n.querySelector("[data-controller-recovery]");return !!r&&r.parentElement?.tagName==="DETAILS"&&!r.parentElement.open&&[...n.querySelectorAll(".channel-controls > details")].every(x=>!x.open);',[selectors[side]]))
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('three browsers opened device-owned chat with recovery tucked under Nerd settings',all(js(side,'const r=document.querySelector(arguments[0]).querySelector("[data-controller-recovery]");return !!r&&!!r.closest("details");',[selectors[side]]) for side in 'abc'))
  click('a','data-recovery-create-validator');validator=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-recovery-validator')],30)
  input_value('b','data-recovery-validator',validator);js('b','document.querySelector(arguments[0]).querySelector("[type=password]").value="correct horse battery staple";',[selectors['b']]);click('b','data-recovery-create-channel');controller=wait('b','return document.querySelector(arguments[0]).value||false;',[node('b','data-recovery-owner')],30);wait('b','return !document.querySelector(arguments[0]).hidden;',[node('b','data-recovery-download')],30)
  call('b','/session/'+sessions['b']+'/goog/cdp/execute',{'cmd':'Browser.setDownloadBehavior','params':{'behavior':'allow','downloadPath':str(profiles['b'])}});js('b','document.querySelector(arguments[0]).click();',[node('b','data-recovery-download')]);download=d.wait(lambda:next(profiles['b'].glob('codi-owner-*.json'),None),30);backup=download.read_text();check('download contains encrypted backup and password field clears',bool(backup) and 'pkcs8' not in backup and js('b','return !document.querySelector(arguments[0]).querySelector("[type=password]").value;',[selectors['b']]))
  click('b','data-channel-copy');code=wait('b','return document.querySelector(arguments[0]).value||false;',[node('b','data-channel-code')],45);input_value('a','data-channel-code',code);click('a','data-recovery-open-validator');wait('a','return document.querySelector(arguments[0]).textContent.includes("Validator opened");',[node('a','data-controller-recovery-status')],45)
  backup_path=profiles['c']/'backup.json';backup_path.write_text(backup);e=call('c','/session/'+sessions['c']+'/element',{'using':'css selector','value':node('c','data-recovery-file')})['element-6066-11e4-a52e-4f735466cecf'];call('c','/session/'+sessions['c']+'/element/'+e+'/value',{'text':str(backup_path),'value':[str(backup_path)]});js('c','document.querySelector(arguments[0]).querySelector("[type=password]").value="correct horse battery staple";',[selectors['c']]);click('c','data-recovery-restore');wait('c','return document.querySelector(arguments[0]).textContent.includes("Owner key restored");',[node('c','data-controller-recovery-status')],45);check('fresh browser restores owner key',value('c','data-recovery-owner')==controller)
  input_value('c','data-channel-code',code);click('c','data-recovery-open-owner');wait('c','return document.querySelector(arguments[0]).textContent.includes("Owner key opened");',[node('c','data-controller-recovery-status')],45);check('restored owner opens original channel',value('c','data-device-select')==controller)
  input_value('c','data-device-draft','Owner recovery live interface test');click('c','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Owner recovery live interface test");',[node('a','data-device-history')],120);check('validator receives the restored owner message',True);check('live chat identifies your own message and the channel owner clearly',bool(wait('c','return document.querySelector(arguments[0]).textContent.includes("You: Owner recovery live interface test");',[node('c','data-device-history')],45)) and bool(wait('a','return document.querySelector(arguments[0]).textContent.includes("Channel owner: Owner recovery live interface test");',[node('a','data-device-history')],45)))
  r['status']='PASS'

 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=js(side,'return {body:document.body.innerText,status:document.querySelector(arguments[0])?.querySelector("[data-device-status]")?.textContent,peer:document.querySelector(arguments[0])?.querySelector("[data-device-peer]")?.options.length};',[selectors.get(side,'body')])
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
