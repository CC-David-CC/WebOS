#!/usr/bin/env python3
"""Exercise asynchronous guest file calls, stale folder reads, and in-flight edits."""
import functools,http.server,importlib.util,os,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
def js(code):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':[]})
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];d.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/scripts/fixtures/async-guest-apps.html'+('?compiled' if os.environ.get('CODI_ASYNC_COMPILED')=='1' else '')});d.wait(lambda:js('return window.fixtureReady;'),15)
 js('window.asyncGuest=guest;window.guest={...guest,list:()=>[{path:"/doc.txt",name:"doc.txt",size:8,dir:false}],stat:p=>({path:p,size:8,dir:false})};window.syncFiles=openApp("files",{path:"/"});window.syncEditor=openApp("text",{editor:{path:"/doc.txt",text:"",loaded:false,dirty:false}});');d.wait(lambda:js('return syncFiles.app.element.textContent.includes("doc.txt")&&syncEditor.app.element.querySelector("textarea").value==="original";'),10);js('syncFiles.close();syncEditor.close();window.guest=asyncGuest;');print('PASS current synchronous guest listing and stat remain compatible',flush=True)
 js('window.files=openApp("files",{path:"/"});');d.wait(lambda:js('return files.app.element.textContent.includes("doc.txt");'),10)
 js('const f=files.app.element.querySelector("form"),p=f.querySelector("input");p.value="/slow";f.requestSubmit();');d.wait(lambda:js('return typeof gates.slow==="function";'),10)
 js('const f=files.app.element.querySelector("form"),p=f.querySelector("input");p.value="/fast";f.requestSubmit();');d.wait(lambda:js('return files.app.element.textContent.includes("x.txt");'),10)
 js('gates.slow();');d.wait(lambda:js('return files.app.element.textContent.includes("x.txt");'),10);assert js('return files.app.element.querySelector("[data-path]").dataset.path==="/fast/x.txt";');print('PASS older folder response cannot replace newer navigation',flush=True)
 js('window.editor=openApp("text",{editor:{path:"/doc.txt",text:"",loaded:false,dirty:false}});');d.wait(lambda:js('return editor.app.element.querySelector("textarea").value==="original";'),10)
 js('window.delayWrite=true;const a=editor.app.element.querySelector("textarea");a.value="first";a.dispatchEvent(new Event("input",{bubbles:true}));[...editor.app.element.querySelectorAll("button")].find(b=>b.textContent==="Save").click();');d.wait(lambda:js('return typeof gates.write==="function";'),10)
 js('const a=editor.app.element.querySelector("textarea");a.value="newer";a.dispatchEvent(new Event("input",{bubbles:true}));[...editor.app.element.querySelectorAll("button")].find(b=>b.textContent==="Save").click();gates.write();');d.wait(lambda:js('return editor.app.element.textContent.includes("newer edits are unsaved");'),10);assert js('return getData("/doc.txt")==="first"&&editor.app.element.querySelector("textarea").value==="newer"&&writes===1;');print('PASS a delayed save preserves newer unsaved edits and suppresses overlapping saves',flush=True)
 js('window.confirm=()=>true;window.delayRead=true;[...editor.app.element.querySelectorAll("button")].find(b=>b.textContent==="Reload").click();');d.wait(lambda:js('return typeof gates.read==="function";'),10)
 js('const a=editor.app.element.querySelector("textarea");a.value="latest";a.dispatchEvent(new Event("input",{bubbles:true}));gates.read();');d.wait(lambda:js('return editor.app.element.textContent.includes("Newer edits kept");'),10);assert js('return editor.app.element.querySelector("textarea").value==="latest";');print('PASS a delayed reload cannot overwrite newer edits',flush=True)
 js('files.close();editor.close();');print('PASS application cleanup completed',flush=True)
finally:
 if sid:d.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(timeout=3)
