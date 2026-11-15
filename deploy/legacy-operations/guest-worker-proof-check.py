#!/usr/bin/env python3
"""Boot actual browser Linux in a Worker and check shell/shared-file round trips.

This feasibility test does not exercise the production desktop, guest Internet,
or any account transition, and does not install a Worker bridge in the site.
"""
import functools,http.server,importlib.util,json,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
def task(code,args=[]):
 result=driver.call('/session/'+sid+'/execute/async',{'script':'const a=Array.from(arguments),done=a.pop();(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:String(e)}));','args':args});assert result['ok'],result;return result['value']
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':60000});driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/scripts/fixtures/guest-worker-proof.html'})
 def ready():
  fatal=js('return fatal;');assert not fatal,fatal
  return js('return ready&&shell.includes("$")&&shell3.includes("$");')
 driver.wait(ready,120);print('PASS Linux boots and starts independent shells in a dedicated worker',flush=True)
 js('command("export WORKER_SECRET=firstshell; printf \\\"\\nFIRST_READY\\n\\\"\\r");command("printf \\\"\\nSECOND_SECRET=%s\\n\\\" \\\"$WORKER_SECRET\\\"\\r",3);')
 driver.wait(lambda:js('return shell.includes("FIRST_READY")&&shell3.includes("SECOND_SECRET=");'),30)
 assert js('return !shell3.includes("SECOND_SECRET=firstshell");');print('PASS worker shell sessions have independent environments',flush=True)
 assert task('await rpc("write",{path:"/worker-test.txt",text:"worker-file"});return true;')
 js('command("printf \\\"\\nWORKER_READ=\\\"; cat /home/guest/worker-test.txt; printf \\\"\\nWORKER_END\\n\\\"\\r");')
 driver.wait(lambda:js('return shell.includes("WORKER_READ=worker-file")&&shell.includes("WORKER_END");'),30);print('PASS guest shell reads a file created via the worker',flush=True)
 js('command("printf shell-file > /home/guest/from-shell.txt; printf \\\"\\nWORKER_WRITE_DONE\\n\\\"\\r");')
 driver.wait(lambda:js('return shell.includes("WORKER_WRITE_DONE");'),30);assert task('return await rpc("read",{path:"/from-shell.txt"});')=='shell-file';print('PASS worker reads a file created by the guest shell',flush=True)
 assert task('await rpc("stop");return true;');print(json.dumps({'status':'PASS','scope':__doc__}),flush=True)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(timeout=3)
