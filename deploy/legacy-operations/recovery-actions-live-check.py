#!/usr/bin/env python3
"""Test public desktop recovery in one disposable, network-isolated browser."""
import argparse,importlib.util,json,shutil,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();profile=Path(tempfile.mkdtemp(prefix='codi-recovery-live-',dir=Path.home()/'snap/chromium/common'));sid=None;checks=[];r={'status':'FAIL','checks':checks,'scope':__doc__};start=time.monotonic()
def js(source,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':source,'args':args})
def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked;'),180)
 js('window.keepVM=v86Instance;window.testDesk=[...desktopLab.surfaces.values()][0];testDesk.launch("text");');d.wait(lambda:js('return !!document.querySelector(".guest-editor");'),60);js('window.draft=document.querySelector(".guest-editor");draft.value="unsaved recovery test";draft.dispatchEvent(new Event("input",{bubbles:true}));')
 d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.enable','params':{}});d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0}});d.wait(lambda:js('return desktopLab.lifecycle.blocked&&!document.querySelector("#desktop-recovery").hidden;'),30)
 check('offline screen offers retry without a page refresh',js('const l=document.querySelector("#desktop-recovery"),b=[...l.querySelectorAll("button")];return l.textContent.includes("Keep this tab open while we reconnect")&&b.some(x=>!x.hidden&&x.textContent==="Try again now")&&!b.some(x=>!x.hidden&&/refresh|reload/i.test(x.textContent));'))
 d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}});d.wait(lambda:js('return !desktopLab.lifecycle.blocked&&document.querySelector("#desktop-recovery").hidden;'),90)
 check('connection recovery retains the same Linux session and unsaved text',js('return v86Instance===keepVM&&draft.isConnected&&draft.value==="unsaved recovery test";'));r['status']='PASS'
except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
finally:
 if sid:
  try:d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}})
  except Exception:pass
  try:d.call('/session/'+sid,method='DELETE')
  except Exception as e:r.update(status='FAIL',cleanupError=str(e))
 shutil.rmtree(profile);r.update(profileRemoved=not profile.exists(),elapsedSeconds=round(time.monotonic()-start,3));a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}),flush=True)
raise SystemExit(r['status']!='PASS')
