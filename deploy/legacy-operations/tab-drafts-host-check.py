#!/usr/bin/env python3
"""Exercise the compiled host API and its storage gate with real Chrome."""
import functools,importlib.util,json,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
fixture=ROOT/'.build/tab-drafts-host-check.html';assert not fixture.exists();fixture.write_text('<!doctype html><title>Host fixture</title>')
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':30000});origin='http://127.0.0.1:'+str(server.server_port);driver.call('/session/'+sid+'/url',{'url':origin+'/.build/tab-drafts-host-check.html'});driver.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
 bundle=ROOT/'.build/shared-services/catchup-hash-r51';entry=json.loads((bundle/'shared-service.json').read_text())['path'];url='/.build/shared-services/catchup-hash-r51/'+entry
 code='''const done=arguments[arguments.length-1];(async()=>{const {DeviceHistoryHost}=await import(arguments[0]);localStorage.setItem('codi-device-history-consent-v1','accepted-v1');const service=new DeviceHistoryHost(),session={public:{kind:'registered',sub:'user:fixture',sid:'s'}},controller=new AbortController(),owned=[],make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},host={version:2,signal:controller.signal,onDispose:fn=>owned.push(fn),session:()=>session,ui:{make},storage:{}};let a,b,updates=[];
 const component={mount(h){const node=make('div');a=h.storage.deviceHistory.drafts();b=h.storage.deviceHistory.drafts({onChange:(channel,text)=>updates.push([channel,text])});return {element:node,dispose(){}};}},mountApp=(module,h)=>module.mount(h),wrapper=service.wrapApp(component,{mountApp,issuer:location.origin}),view=wrapper.mount(host);document.body.append(view.element);
 const end=performance.now()+10000;while(!a&&performance.now()<end)await new Promise(r=>setTimeout(r,20));if(!a||!b)throw Error('storage gate did not mount host drafts: '+view.element.textContent);const channel='A'.repeat(43);a.write(channel,'host draft');if(b.read(channel)!=='host draft'||updates.length!==1)throw Error('host draft view did not share');view.dispose();for(const fn of owned.reverse())fn();let closed=false;try{a.read(channel);}catch{closed=true;}if(!closed)throw Error('disposed host allowed access');controller.abort();service.close();sessionStorage.clear();return 'PASS compiled host gates, shares and disposes tab drafts';})().then(done,e=>done({error:e.stack||String(e)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[url]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3);fixture.unlink(missing_ok=True)
