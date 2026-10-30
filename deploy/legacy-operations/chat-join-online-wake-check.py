#!/usr/bin/env python3
"""Check retry timing and cleanup in the packaged Chat app."""
import functools,importlib.util,json,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
folder=ROOT/'.build/chat-join-retry-r1';server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':20000});driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'});entry=json.loads((folder/'apps.json').read_text())['apps'][0];app='/'+entry['path'].removeprefix('assets/desktop/')
 code='''const done=arguments[arguments.length-1];(async()=>{const {mount}=await import(arguments[0]),make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},textButton=(label,fn)=>{const n=make('button','',label);n.type='button';n.addEventListener('click',fn);return n;},life=new AbortController(),session={public:{kind:'registered',name:'alice'}};let calls=0,closed=false;const times=[],start=performance.now();
 const handle={channel:'a',snapshot:async()=>({actor:'actor',head:'h',height:0,state:{messages:[]},pending:[],readable:true,writable:true,official:true,officialStatus:{caughtUp:true},quorum:1})};
 const service={officialDirectory:async()=>({items:[{category:'official',channel:'a',label:'General chess chat',invitation:{config:{channel:'a'}}}]}),joinOfficialChannel:async()=>{times.push(performance.now()-start);if(++calls<3)throw Error('join failed');return {channel:handle};},close(){closed=true;}};const host={ui:{make,textButton},session:()=>session,signal:life.signal,network:{config:{}},storage:{deviceHistory:{channels:()=>service},downloadGuestFile(){}}};const app=mount(host);document.body.append(app.element);
 await new Promise(r=>setTimeout(r,150));window.dispatchEvent(new Event('online'));window.dispatchEvent(new Event('online'));const until=performance.now()+6000;while(performance.now()<until&&app.element.querySelector('.channel-title').textContent!=='General chess chat')await new Promise(r=>setTimeout(r,25));if(calls!==3||app.element.querySelector('.channel-title').textContent!=='General chess chat'||times[1]<100||times[1]>800||times[2]-times[1]<1800||times[2]-times[1]>2600)throw Error('Retry did not back off correctly: '+JSON.stringify(times));app.dispose();life.abort();await new Promise(r=>setTimeout(r,150));if(!closed||calls!==3)throw Error('Retry not cleaned up');return 'PASS online event wakes retry immediately without duplicate opens';})().then(done,error=>done({error:error.stack||String(error)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[app]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3)
