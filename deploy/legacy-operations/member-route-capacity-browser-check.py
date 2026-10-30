#!/usr/bin/env python3
"""Real Chrome signed routed relay saturation with mocked transport links."""
import functools,hashlib,http.server,importlib.util,json,threading,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def run():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();session=None;result={'status':'FAIL','scope':__doc__}
 try:
  session=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
  d.call('/session/'+session+'/url',{'url':f'http://127.0.0.1:{server.server_port}/scripts/member-route-capacity-browser.html'})
  result['message']=d.wait(lambda:d.call('/session/'+session+'/execute/sync',{'script':'return document.body.textContent.startsWith("PASS:")&&document.body.textContent','args':[]}),15)
  result['sourceSHA256']=hashlib.sha256((ROOT/'network/device-member-introductions.mjs').read_bytes()).hexdigest();result['fixtureSHA256']=hashlib.sha256((ROOT/'scripts/member-route-capacity-browser.mjs').read_bytes()).hexdigest();result['status']='PASS'
 except Exception:
  result['error']=traceback.format_exc()
  if session:result['browserLog']=d.call('/session/'+session+'/log',{'type':'browser'})
 finally:
  if session:d.call('/session/'+session,method='DELETE')
  server.shutdown();server.server_close();thread.join()
 out=ROOT/'.build/checks/member-route-capacity-browser-r1-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result['status']=='PASS'
if __name__=='__main__':raise SystemExit(not run())
