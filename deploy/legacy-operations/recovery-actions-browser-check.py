#!/usr/bin/env python3
"""Real-browser recovery actions with a disposable local status service."""
import functools,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Handler(http.server.SimpleHTTPRequestHandler):
 down=False;requests=0
 def log_message(self,*args):pass
 def do_GET(self):
  if self.path=='/api/v1/desktop-status':
   type(self).requests+=1;raw=json.dumps({'version':'codi-desktop-status/1','epoch':'00000000-0000-0000-0000-000000000001','serverTime':int(time.time()),'maintenance':None}).encode();self.send_response(503 if self.down else 200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
  else:super().do_GET()
def main(source=ROOT):
 root=Path(tempfile.mkdtemp(prefix='codi-recovery-actions-'));profile=Path(tempfile.mkdtemp(prefix='codi-recovery-browser-',dir=Path.home()/'snap/chromium/common'));server=thread=sid=None;checks=[];result={'status':'FAIL','checks':checks,'scope':'One disposable Chrome profile, local status fixture; no actual guest VM or server outage.'}
 def js(source,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':source,'args':args})
 def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 try:
  for name in ['assets/desktop/lifecycle.mjs','network/strict-json.mjs']:
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,p)
  (root/'index.html').write_text('''<!doctype html><title>Recovery fixture</title><main id="workspace"><input id="draft" value="unsaved draft"></main><script type="module">import {startLifecycle} from "/assets/desktop/lifecycle.mjs";window.startLifecycle=startLifecycle;window.life=startLifecycle({config:{identity:{apiBase:"/api/v1"},desktopLifecycle:{version:"codi-desktop-lifecycle/1",statusPath:"/api/v1/desktop-status"}},roots:()=>[document.querySelector("#workspace")],pollMs:10000});</script>''')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':origin+'/'});d.wait(lambda:js('return !!window.life?.state.epoch&&!life.state.blocked;'),20)
  Handler.down=True;js('window.dispatchEvent(new Event("offline"));');d.wait(lambda:js('return life.state.blocked&&!document.querySelector("#desktop-recovery").hidden;'),10)
  check('outage offers in-tab recovery without page refresh',js('const l=document.querySelector("#desktop-recovery"),b=[...l.querySelectorAll("button")];return l.textContent.includes("Keep this tab open while we reconnect")&&b.some(x=>!x.hidden&&x.textContent==="Try again now")&&!b.some(x=>!x.hidden&&/refresh|reload/i.test(x.textContent))&&document.querySelector("#workspace").inert;'))
  check('retry action receives focus',js('return document.activeElement.textContent==="Try again now";'))
  before=Handler.requests;Handler.down=False;js('[...document.querySelectorAll("#desktop-recovery button")].find(b=>b.textContent==="Try again now").click();');d.wait(lambda:js('return !life.state.blocked&&document.querySelector("#desktop-recovery").hidden;'),10)
  check('manual retry checks now and keeps the draft',Handler.requests>before and js('return !document.querySelector("#workspace").inert&&document.querySelector("#draft").value==="unsaved draft";'))
  Handler.down=True;js('life.stop();window.life=startLifecycle({config:{identity:{apiBase:"/api/v1"},desktopLifecycle:{version:"codi-desktop-lifecycle/1",statusPath:"/api/v1/desktop-status"}},roots:()=>[document.querySelector("#workspace")],pollMs:10000,hasRunningGuest:()=>false,initiallyDisconnected:true});');d.wait(lambda:js('return life.state.blocked;'),10)
  check('missing guest gives an honest unsaved-work warning',js('return document.querySelector("#desktop-recovery").textContent.includes("Unsaved work from an earlier tab was not automatically saved.");'))
  check('recovery does not reload the page',js('return performance.getEntriesByType("navigation")[0]?.type!=="reload"&&document.querySelector("#draft").value==="unsaved draft";'))
  result['status']='PASS'
 except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
 finally:
  if sid:
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:result.update(status='FAIL',cleanupError=str(e))
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=5)
  shutil.rmtree(root);shutil.rmtree(profile);result.update(fixtureRemoved=not root.exists(),profileRemoved=not profile.exists())
 return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--release',type=Path,default=ROOT);a=p.parse_args();assert not a.output.exists();r=main(a.release.resolve());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
