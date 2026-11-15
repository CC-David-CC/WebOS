#!/usr/bin/env python3
"""Two anonymous actual public desktop profiles connect and exchange signed channel messages."""
import argparse,importlib.util,json,os,shutil,socket,subprocess,tempfile,traceback,time,urllib.request,urllib.error,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 sessions={};profiles={};selectors={};checks=[];remote_driver=None;forward=None;remote_profile=None;runid=uuid.uuid4().hex;remote_port=19536;local_port=19536;target='maint@100.105.243.29';r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':2,'serverAccountsCreated':0,'liveSite':'https://ksu.codes/','transport':'WebRTC; peer invitation manually transferred by test driver','remoteHost':'Moonpie','remotePublicIP':'24.126.137.85'};started=time.monotonic()
 def call(side,path,data=None,method=None):
  if side=='a':return d.call(path,data,method)
  req=urllib.request.Request('http://127.0.0.1:'+str(local_port)+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'},method=method)
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
 try:
  r['remotePublicIP']=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'curl','-4','-fsS','--max-time','8','https://api.ipify.org'],text=True,timeout=15).strip()
  remote_profile=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'mktemp','-d','/home/maint/snap/chromium/common/codi-live-wan-XXXXXXXX'],text=True,timeout=15).strip();assert remote_profile.startswith('/home/maint/snap/chromium/common/codi-live-wan-')
  pidfile='/tmp/codi-live-wan-'+runid+'.pid';command='umask 077; echo $$ > '+pidfile+'; exec /snap/chromium/current/usr/lib/chromium-browser/chromedriver --port='+str(remote_port)+' --allowed-ips=127.0.0.1'
  remote_driver=subprocess.Popen(['ssh','-o','BatchMode=yes',target,command],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  forward=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:'+str(local_port)+':127.0.0.1:'+str(remote_port),target],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  def ready():
   if remote_driver.poll() is not None or forward.poll() is not None:raise RuntimeError('Moonpie driver or SSH tunnel ended')
   try:
    with urllib.request.urlopen('http://127.0.0.1:'+str(local_port)+'/status',timeout=1) as f:return json.load(f)['value']['ready']
   except OSError:return False
  d.wait(ready,20)
  for side in 'ab':
   profiles[side]=Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common')) if side=='a' else Path(remote_profile)
   v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=120);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selectors[side]]):
    e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('two anonymous browsers opened device-owned chat',True)
  js('a','document.querySelector(arguments[0]).checked=true;',[node('a','data-device-public-read')]);click('a','data-device-create');wait('a','return !!document.querySelector(arguments[0]).value;',[node('a','data-device-select')],60)
  input_value('a','data-device-draft','Peer history live test');click('a','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Peer history live test");',[node('a','data-device-history')],90);check('first browser accepted a signed local channel message',True)
  click('a','data-device-offer');offer=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-device-connection-out')],90)
  input_value('b','data-device-connection-in',offer);click('b','data-device-answer');answer=wait('b','return document.querySelector(arguments[0]).value||false;',[node('b','data-device-connection-out')],90)
  input_value('a','data-device-connection-in',answer);click('a','data-device-accept')
  for side in 'ab':wait(side,'return document.querySelector(arguments[0]).options.length>0;',[node(side,'data-device-peer')],90)
  check('two browsers establish an actual WebRTC peer connection',True)
  for side in 'ab':
   r[side+'Ice']=call(side,'/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1],pool=desktopNetwork.appContext().pool,entry=pool.firstReady();(async()=>{const stats=await entry.link.pc.getStats(),transport=[...stats.values()].find(v=>v.type==="transport"&&v.selectedCandidatePairId),pair=transport&&stats.get(transport.selectedCandidatePairId),local=pair&&stats.get(pair.localCandidateId),remote=pair&&stats.get(pair.remoteCandidateId);return {localType:local?.candidateType,localAddress:local?.address,remoteType:remote?.candidateType,remoteAddress:remote?.address,protocol:local?.protocol};})().then(done,e=>done({error:e.message}));','args':[]})
  click('a','data-device-export');share=wait('a','return document.querySelector(arguments[0]).value||false;',[node('a','data-device-share')],60);input_value('b','data-device-share',share);click('b','data-device-import');wait('b','return document.querySelector(arguments[0]).textContent.includes("Peer history live test");',[node('b','data-device-history')],120);check('reader verifies and receives signed channel history',True)
  actor=value('b','data-device-member-key');assert actor;input_value('a','data-device-member-subject',actor);click('a','data-device-allow-write');wait('b','return !document.querySelector(arguments[0]).disabled;',[node('b','data-device-queue')],120)
  input_value('b','data-device-draft','Reply from second browser');click('b','data-device-queue');wait('a','return document.querySelector(arguments[0]).textContent.includes("Reply from second browser");',[node('a','data-device-history')],120);check('authorized second browser sends a signed reply',True)
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
  if 'a' in profiles:shutil.rmtree(profiles['a'])
  if forward:forward.terminate();forward.wait(timeout=10)
  if remote_driver:remote_driver.terminate();remote_driver.wait(timeout=10)
  if remote_profile:
   cleanup='import os,signal,sys,time,shutil;from pathlib import Path;p=Path(sys.argv[1]);f=Path(sys.argv[2]);pid=int(f.read_text()) if f.exists() else 0;cmd=Path("/proc")/str(pid)/"cmdline";raw=cmd.read_bytes() if cmd.exists() else b"";assert not raw or b"chromedriver" in raw and b"--port=19536" in raw;os.kill(pid,signal.SIGTERM) if raw else None;time.sleep(1);busy=any(str(p).encode() in q.read_bytes() and "chromium-browser/chrome" in os.readlink(q.parent/"exe") for q in Path("/proc").glob("[0-9]*/cmdline") if q.exists() and (q.parent/"exe").exists());assert not busy;shutil.rmtree(p);f.unlink(missing_ok=True);print("clean")'
   try:r['remoteCleanup']=subprocess.check_output(['ssh','-o','BatchMode=yes',target,'python3','-c',__import__('shlex').quote(cleanup),remote_profile,pidfile],text=True,timeout=30).strip()
   except Exception as e:r['status']='FAIL';r['remoteCleanupError']=str(e)
  r.update(ownedProfilesRemoved=('a' not in profiles or not profiles['a'].exists()) and r.get('remoteCleanup')=='clean',elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
