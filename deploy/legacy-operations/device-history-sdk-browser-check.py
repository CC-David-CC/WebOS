#!/usr/bin/env python3
"""Sealed candidate frontend with actual local issuer, Chrome and v86 Linux.

Public release files only are staged. The disposable reference issuer has its
own keys/SQLite; no production account, native unit, guest Internet or VM fixture
is used. This tests the paused desktop and normal app loader, not new P2P rules.
"""
import argparse,hashlib,importlib.util,json,secrets,shutil,sys,tempfile,threading,traceback
from pathlib import Path
from wsgiref.simple_server import make_server
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from origin_service.lifecycle import Service
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
s=importlib.util.spec_from_file_location('sdk_preview_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Heads:
 def __init__(self,app):self.app=app
 def __call__(self,env,start):
  if env.get('REQUEST_METHOD')!='HEAD':return self.app(env,start)
  env=dict(env,REQUEST_METHOD='GET');body=self.app(env,start)
  try:
   for _ in body:pass
  finally:
   if hasattr(body,'close'):body.close()
  return []
def run(release):
 checks=[];sid=None;server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-device-sdk-');folder=Path(tmp.name)
 r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':1,'actualV86Desktops':1,'productionChanged':False,'guestInternetTested':False,'nativeSystemdTested':False}
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),e=>done({ok:false,error:e.stack}));','args':args});assert v['ok'],v;return v.get('value')
 try:
  public=folder/'public';public.mkdir();manifest=json.loads((release/'release.json').read_bytes());r['manifestSHA256']=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest()
  for n,record in manifest['files'].items():
   p=release/n;assert not p.is_symlink() and p.is_file() and record=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
   dest=public/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  # Bind first so the issuer Host/origin pin uses the actual owned loopback port.
  server=make_server('127.0.0.1',0,lambda env,start:[],server_class=BoundedServer,handler_class=QuietHandler);origin='http://127.0.0.1:'+str(server.server_port)
  issuer=Service(Config(folder/'issuer',public,origin=origin,rate_per_minute=1000),base_path='');server.set_app(Heads(issuer));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':90000});d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&document.querySelector(".xterm")&&terminalSessions.get(2)?.view;'),150)
  check('sealed candidate boots real anonymous Linux and xterm with the unchanged kernel',js('return guestFiles.ready&&currentSession.public.kind==="anonymous";'))
  check('paused chat starts no networking pool, history service, prompt or history database',task('const s=await desktopNetwork.stats();return s.peers.length===0&&!s.budget&&localStorage.getItem("codi-device-history-consent-v1")===null&&(await indexedDB.databases()).every(d=>!d.name.startsWith("codi-device-channel"))&&!performance.getEntriesByType("resource").some(r=>r.name.includes("/services/device-history/"));'))
  js('window.sdkDesktop=[...surfaces.values()][0];window.sdkVM=v86Instance;window.sdkFS=v86Instance.fs9p;')
  task('await guestFiles.write("/Documents/host-upgrade.txt","Before edit");window.sdkEditor=openGuestEditor(sdkDesktop,"/Documents/host-upgrade.txt");return true;')
  d.wait(lambda:js('return document.querySelector("[data-window=\\\""+sdkEditor.id+"\\\"] .guest-editor")?.value==="Before edit";'),20)
  js('const input=document.querySelector("[data-window=\\\""+sdkEditor.id+"\\\"] .guest-editor");input.value="Saved after shared-host upgrade";input.dispatchEvent(new Event("input",{bubbles:true}));const b=[...input.closest(".window").querySelectorAll("button")].find(b=>b.textContent==="Save");b.click();')
  d.wait(lambda:task('return new TextDecoder().decode(await guestFiles.read("/Documents/host-upgrade.txt"))==="Saved after shared-host upgrade";'),20)
  check('normal Files/Text guest document save still reaches the actual shared Linux filesystem',True)
  js('sendTerminal(2,"export DEVICE_HOST_KEEP=first; printf \\\"\\\\nSDK_FIRST_READY\\\\n\\\"; command -v nano\\r");window.sdkSecond=sdkDesktop.launch("terminal");')
  d.wait(lambda:js('return terminalSessions.get(sdkSecond.id)?.view&&terminalSessions.get(2).screen.text().includes("\\nSDK_FIRST_READY\\n");'),30)
  js('sendTerminal(sdkSecond.id,"printf \\\"\\\\nSDK_SECOND_%s\\\\n\\\" \\\"${DEVICE_HOST_KEEP-unset}\\\"\\r");')
  d.wait(lambda:js('return terminalSessions.get(sdkSecond.id).screen.text().includes("\\nSDK_SECOND_unset\\n");'),25)
  check('multiple terminal windows retain distinct guest shell environments and nano remains installed',js('return terminalSessions.get(2).screen.text().includes("/usr/bin/nano")||terminalSessions.get(2).screen.text().includes("/bin/nano");'))
  # Warm all unchanged app bundles through the actual sealed index/catalog.
  opened=0
  for cycle in range(3):
   for app in ['calculator','help','text','files','chat','rooms','terminal']:
    w=js('return sdkDesktop.launch(arguments[0]);',[app]);wid=w['id'];opened+=1
    d.wait(lambda:js('return !!document.querySelector("[data-window=\\\""+arguments[0]+"\\\"]")?.appView;',[wid]),20)
    if app in ['chat','rooms']:assert js('return !!document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] [data-chat-disabled]")&&!document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] [data-storage-consent]");',[wid])
    js('const win=document.querySelector("[data-window=\\\""+arguments[0]+"\\\"]");win.querySelector("[aria-label=Close]").click();',[wid])
  check('all seven sealed app bundles reopen/close through the new host without activating paused chat',opened==21 and js('return v86Instance===sdkVM&&v86Instance.fs9p===sdkFS;'))
  r['appOpenCloseCycles']=opened;r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:r['diagnostics']=js('return {state:window.desktopLab?.guestState,text:document.body.innerText.slice(-2200),shell:typeof terminalSessions!=="undefined"?terminalSessions.get(2)?.screen.text().slice(-1500):null};')
   except Exception as diag:r['diagnosticError']=str(diag)
 finally:
  if sid:
   try:js('desktopLifecycle?.stop();bootRecovery?.stop();clearInterval(identityTimer);desktopNetwork.close();for(const surface of surfaces.values())for(const win of surface.root.querySelectorAll(".window"))disposePublicAppView(win);v86Instance?.destroy();')
   except Exception as e:r['cleanupError']=str(e)
   d.call('/session/'+sid,method='DELETE');r['ownedBrowserClosed']=True
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  tmp.cleanup();r['fixtureRemoved']=not folder.exists()
 r['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
