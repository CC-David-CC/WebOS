#!/usr/bin/env python3
"""Test the exact composed public release on an owned local Chrome profile."""
import argparse,functools,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(release):
 server=None;thread=None;sid=None;profile=Path(tempfile.mkdtemp(prefix='codi-live-release-',dir=Path.home()/'snap/chromium/common'));checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'liveChanged':False,'v86Required':False,'release':str(release)}
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def check(name,v):assert v,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(release)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]},'goog:loggingPrefs':{'browser':'ALL'}}}});sid=v['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':180000});d.call('/session/'+sid+'/url',{'url':origin+'/'});d.wait(lambda:js('return !!window.desktopLab&&window.desktopLab.surfaces.size>0&&!!window.desktopLab.session;'),90)
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  wid=js('window.testDesktop=[...surfaces.values()][0];return testDesktop.launch("chat").id;');selector='[data-window="'+str(wid)+'"]';d.wait(lambda:js('return !!document.querySelector(arguments[0])?.querySelector(".storage-consent button:not(:disabled),[data-device-channels]");',[selector]),60)
  if not js('return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selector]):
   element=d.call('/session/'+sid+'/element',{'using':'css selector','value':selector+' .storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sid+'/element/'+element+'/click',{})
  d.wait(lambda:js('return !!document.querySelector(arguments[0])?.querySelector("[data-device-channels]");',[selector]),90)
  check('exact built release opens device-owned chat after storage consent',js('return !!document.querySelector(arguments[0]).querySelector("[data-device-channels]");',[selector]))
  check('network enables the device channel mode',js('return desktopNetwork.appContext().deviceMode&&desktopNetwork.appContext().deviceChannelsReady&&!desktopNetwork.appContext().disabled;'))
  js('document.querySelector(arguments[0]).querySelector("[data-directory-create]").click();',[selector]);d.wait(lambda:js('return !!document.querySelector(arguments[0]).querySelector("[data-device-select]").value;',[selector]),60)
  d.wait(lambda:js('return !document.querySelector(arguments[0]).querySelector("[data-device-queue]").disabled;',[selector]),60)
  js('const root=document.querySelector(arguments[0]),draft=root.querySelector("[data-device-draft]");draft.value="Packaged local channel test";draft.dispatchEvent(new Event("input",{bubbles:true}));root.querySelector("[data-device-queue]").click();',[selector])
  d.wait(lambda:js('return document.querySelector(arguments[0]).querySelector("[data-device-history]").textContent.includes("Packaged local channel test");',[selector]),60)
  check('packaged chat creates a channel and accepts a local message',True)
  js('document.querySelector(arguments[0]).querySelector("[aria-label=Close]").click();',[selector]);check('chat window closes',not js('return !!document.querySelector(arguments[0]);',[selector]));r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:r['diagnostic']=js('return {body:document.body.innerText,errors:window.onerror,network:desktopNetwork?.appContext?.() ? {disabled:desktopNetwork.appContext().disabled,deviceMode:desktopNetwork.appContext().deviceMode,ready:desktopNetwork.appContext().deviceChannelsReady}:null};')
   except Exception as x:r['diagnosticError']=str(x)
 finally:
  if sid:
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r['cleanupError']=str(e);r['status']='FAIL'
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  shutil.rmtree(profile);r['ownedProfileRemoved']=not profile.exists()
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.release.resolve());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error'),'checks':len(r['checks'])}));raise SystemExit(r['status']!='PASS')
