#!/usr/bin/env python3
"""Two fresh live browsers automatically join SYSTEM; test peer-only delivery."""
import argparse,importlib.util,json,shutil,subprocess,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();sessions={};profiles={};windows={};checks=[];r={'status':'FAIL','checks':checks,'scope':__doc__};start=time.monotonic()
def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
def wait(side,code,args=[],seconds=90):return d.wait(lambda:js(side,code,args),seconds)
def check(label,ok=True):assert ok,label;checks.append(label);print(json.dumps({'check':label}),flush=True)
try:
 for side in 'ab':
  profiles[side]=Path(tempfile.mkdtemp(prefix='codi-system-live-'+side+'-',dir=Path.home()/'snap/chromium/common'));sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}})['sessionId']
  d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'});d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}});js(side,"localStorage.setItem('codi-device-history-consent-v1','accepted-v1');");d.call('/session/'+sessions[side]+'/url',{'url':'https://ksu.codes/'})
  wait(side,'return !!window.desktopLab?.session&&desktopLab.surfaces.size>0&&desktopNetwork.appContext().deviceChannelsReady;',seconds=120)
  deadline=time.monotonic()+90
  while time.monotonic()<deadline:
   state=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const done=arguments[arguments.length-1];desktopNetwork.stats().then(done,e=>done({error:e.message}));','args':[]})
   if state.get('deviceChannels',{}).get('channels',0)>=1:break
   time.sleep(.3)
  else:raise AssertionError('SYSTEM did not start without a Chat window')
  windows[side]=js(side,'return [...desktopLab.surfaces.values()][0].launch("chat").id;');selector='[data-window="'+str(windows[side])+'"]';wait(side,'const n=document.querySelector(arguments[0]);return !!n?.querySelector("[data-channel-list-item]")&&n.querySelector("[data-channel-list-item]").textContent==="SYSTEM";',[selector],90)
  js(side,'document.querySelector(arguments[0]).querySelector("[data-channel-list-item]").click();',[selector]);wait(side,'const n=document.querySelector(arguments[0]);return n?.querySelector("[data-device-history]")?.textContent.includes("SYSTEM channel is ready.")&&!n.querySelector(".channel-read-only")?.hidden;',[selector],120)
  check(side+' automatically joined and recovered SYSTEM with posting disabled')
 ids={side:js(side,'return desktopLab.session.id;') for side in 'ab'}
 for side,other in [('a','b'),('b','a')]:wait(side,'const p=desktopNetwork.appContext().pool;return p.list().some(e=>e.peerId===arguments[0]&&e.state==="ready"&&!p.get(e.id).link.closed);',[ids[other]],120)
 check('SYSTEM browsers established a peer connection')
 js('b','window.systemBlockedFetches=0;const original=window.fetch.bind(window);window.fetch=(input,options)=>{const url=new URL(input,location.href);if(url.pathname==="/official-head"||url.pathname==="/official-history"){systemBlockedFetches++;return Promise.reject(Error("fixture blocks SYSTEM server history"));}return original(input,options);};')
 js('b','fetch("/official-head?channel=blocked-test").catch(()=>{});')
 notice='SYSTEM notifications can travel through connected peers.'
 posted=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','-u','codi-official','/srv/codi-connected/venvs/517179c/bin/python','-I','-B','/srv/codi-connected/official-services/system-channel-r2/scripts/official-admin.py','--state','/var/lib/codi-official/state','system-post'],input=notice,text=True,capture_output=True,check=True,timeout=30);r['post']=json.loads(posted.stdout);assert r['post']['height']>=2
 for side in 'ab':wait(side,'return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes(arguments[1]);',['[data-window="'+str(windows[side])+'"]',notice],180)
 check('new SYSTEM notice reaches both peers while server history is blocked for one',js('b','return window.systemBlockedFetches>0;'))
 r['status']='PASS'
except Exception as e:
 r.update(error=str(e),traceback=traceback.format_exc())
 for side in sessions:
  try:r[side+'Diagnostic']=js(side,'return {text:document.body.innerText.slice(-5000),network:desktopNetwork.appContext().meshError};')
  except Exception as x:r[side+'DiagnosticError']=str(x)
finally:
 for side,sid in sessions.items():
  try:d.call('/session/'+sid,method='DELETE')
  except Exception as e:r['status']='FAIL';r[side+'CleanupError']=str(e)
 for profile in profiles.values():shutil.rmtree(profile,ignore_errors=True)
 r['profilesRemoved']=all(not p.exists() for p in profiles.values());r['elapsedSeconds']=round(time.monotonic()-start,2)
a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(checks)}));raise SystemExit(r['status']!='PASS')
