#!/usr/bin/env python3
"""Exercise operator introduction switch against an owned public browser profile."""
import argparse,importlib.util,json,shutil,subprocess,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
def run():
 profile=Path(tempfile.mkdtemp(prefix='codi-gate-live-',dir=Path.home()/'snap/chromium/common'));sid=None;checks=[];r={'status':'FAIL','checks':checks,'liveSite':'https://ksu.codes/','scope':__doc__,'productionChanged':True}
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const done=arguments[arguments.length-1];(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:e.message}));','args':[]});assert v['ok'],v;return v['value']
 def operator(state):return subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','/srv/codi-connected/venvs/517179c/bin/python','/srv/codi-connected/admin/anonymous-introductions.py',state],text=True,timeout=20).strip()
 def check(name,value):assert value,name;checks.append(name);print(name,flush=True)
 try:
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}});sid=v['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':120000});d.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'});d.wait(lambda:js('return !!window.desktopLab?.session&&window.desktopLab.surfaces.size>0;'),90);d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':'https://ksu.codes'}})
  wid=js('window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');sel='[data-window="'+str(wid)+'"]';d.wait(lambda:js('return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[sel]),90)
  if not js('return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[sel]):
   e=d.call('/session/'+sid+'/element',{'using':'css selector','value':sel+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sid+'/element/'+e+'/click',{})
  d.wait(lambda:js('return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[sel]),90);js('document.querySelector(arguments[0]).querySelector(".channel-controls button").click();',[sel]);d.wait(lambda:task('return (await desktopNetwork.stats()).discovery?.status==="ready";'),60);check('anonymous channel discovers while enabled',True)
  r['disableOutput']=operator('disabled');d.wait(lambda:task('const s=(await desktopNetwork.stats()).discovery;return s&&s.status!=="ready";'),30);check('disabling interrupts an existing anonymous introduction session',True)
  r['enableOutput']=operator('enabled');d.wait(lambda:task('return (await desktopNetwork.stats()).discovery?.status==="ready";'),90);check('anonymous introductions recover after re-enabling',True);r['status']='PASS'
 except Exception:
  r['traceback']=traceback.format_exc()
 finally:
  try:r['finalPolicy']=operator('enabled')
  except Exception:r['status']='FAIL';r['restoreError']=traceback.format_exc()
  if sid:
   try:d.call('/session/'+sid,method='DELETE')
   except Exception:r['status']='FAIL';r['cleanupError']=traceback.format_exc()
  shutil.rmtree(profile);r['ownedProfileRemoved']=not profile.exists()
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':r['checks'],'traceback':r.get('traceback'),'restoreError':r.get('restoreError')}));raise SystemExit(r['status']!='PASS')
