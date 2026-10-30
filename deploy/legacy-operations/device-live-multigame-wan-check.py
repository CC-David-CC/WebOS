#!/usr/bin/env python3
"""Three public browsers on three networks use three simultaneous chess windows."""
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
  for side,target,port,binary,driver,profilebase in [('b','maint@100.105.243.29',19536,'/snap/chromium/current/usr/lib/chromium-browser/chrome','/snap/chromium/current/usr/lib/chromium-browser/chromedriver','/home/maint/snap/chromium/common'),('j','maint@10.0.7.105',19537,'/usr/bin/chromium','/usr/bin/chromedriver','/tmp')]:
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
  for side in 'abj':
   profiles[side]=Path(remotes[side]['profile']) if side in remotes else Path(tempfile.mkdtemp(prefix='codi-live-p2p-'+side+'-',dir=Path.home()/'snap/chromium/common'))
   v=call(side,'/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':remotes[side]['binary'] if side in remotes else '/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];call(side,'/session/'+sessions[side]+'/timeouts',{'script':180000});call(side,'/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});wait(side,'return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;',seconds=90);call(side,'/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
   wid=js(side,'window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("rooms").id;');selectors[side]='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-chess-match]");',[selectors[side]],90)
   if not js(side,'return !!document.querySelector(arguments[0]).querySelector("[data-chess-match]");',[selectors[side]]):
    e=call(side,'/session/'+sessions[side]+'/element',{'using':'css selector','value':selectors[side]+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];call(side,'/session/'+sessions[side]+'/element/'+e+'/click',{})
   wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-chess-match]");',[selectors[side]],90)
   js(side,'for(const e of document.querySelector(arguments[0]).querySelectorAll("details"))e.open=true;',[selectors[side]])
  check('three browsers opened chess',True)
  def root(sel):return sel+' [data-chess-match]'
  def press(side,sel,n):wait(side,'return !document.querySelector(arguments[0]).querySelectorAll("button")[arguments[1]].disabled;',[root(sel),n],90);js(side,'document.querySelector(arguments[0]).querySelectorAll("button")[arguments[1]].click();',[root(sel),n])
  def setfield(side,sel,field,value):js(side,'document.querySelector(arguments[0]).querySelector(arguments[1]).value=arguments[2];',[root(sel),field,value])
  def extra(side):
   wid=js(side,'return testDesktop.launch("rooms").id;');sel='[data-window="'+str(wid)+'"]';wait(side,'return !!document.querySelector(arguments[0])?.querySelector("[data-chess-match]");',[sel],90);return sel
  wins={side:[selectors[side],extra(side),extra(side)] for side in 'abj'}
  press('b',wins['b'][0],0);black=wait('b','return document.querySelector(arguments[0]).querySelector("[data-chess-player]").value||false;',[root(wins['b'][0])],60)
  for i in range(3):
   aw=wins['a'][i];press('a',aw,0);wait('a','return !!document.querySelector(arguments[0]).querySelector("[data-chess-player]").value;',[root(aw)],60);setfield('a',aw,'[aria-label="Opponent\'s player key"]',black);setfield('a',aw,'[aria-label="Match name"]','Match '+str(i+1));press('a',aw,1);code=wait('a','return document.querySelector(arguments[0]).querySelector("[data-chess-code]").value||false;',[root(aw)],90)
   for side in 'bj':
    sel=wins[side][i];setfield(side,sel,'[data-chess-code]',code)
    if side=='b':setfield(side,sel,'[data-chess-player]',black)
    press(side,sel,2);wait(side,'return document.querySelector(arguments[0]).textContent.includes(arguments[1]);',[root(sel),'Playing as '+('black' if side=='b' else 'spectator')],90)
  check('three match windows join independently across all three networks',True)
  check('each window lists all three distinct saved match names',all(js(side,'return [...document.querySelector(arguments[0]).querySelector("[data-chess-saved]").options].map(x=>x.textContent).sort().join("|")==="Match 1|Match 2|Match 3";',[root(sel)]) for side in 'abj' for sel in wins[side]))
  for i,san in enumerate(['e4','d4','c4']):
   setfield('a',wins['a'][i],'[aria-label="Chess move"]',san);press('a',wins['a'][i],4)
   for side in 'abj':wait(side,'return document.querySelector(arguments[0]).querySelector("[data-chess-moves]").textContent.includes(arguments[1]);',[root(wins[side][i]),san],120)
  check('three concurrent games keep their moves separate',all(js(side,'const s=document.querySelector(arguments[0]).querySelector("[data-chess-moves]").textContent;return s.includes(arguments[1])&&arguments[2].every(x=>!s.includes(x));',[root(wins[side][i]),san,[v for v in ['e4','d4','c4'] if v!=san]]) for side in 'abj' for i,san in enumerate(['e4','d4','c4'])))
  for i in range(3):
   setfield('j',wins['j'][i],'[aria-label="Chat message"]','conversation '+str(i));press('j',wins['j'][i],5);wait('a','return document.querySelector(arguments[0]).querySelector("[data-chess-chat]").textContent.includes(arguments[1]);',[root(wins['a'][i]),'conversation '+str(i)],120)
  check('three game conversations stay separate',all(js('a','const s=document.querySelector(arguments[0]).querySelector("[data-chess-chat]").textContent;return s.includes(arguments[1])&&arguments[2].every(x=>!s.includes(x));',[root(wins['a'][i]),'conversation '+str(i),['conversation '+str(j) for j in range(3) if j!=i]]) for i in range(3)))
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
