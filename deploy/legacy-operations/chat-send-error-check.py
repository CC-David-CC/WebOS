#!/usr/bin/env python3
"""Check the compiled chat preserves an unsaved draft and reports its failure."""
import functools,http.server,importlib.util,json,threading
from pathlib import Path
R=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('d',R/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(R)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 d.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'})
 catalog=json.loads((R/'.build/chat-send-error-r1/apps.json').read_text());app='/.build/chat-send-error-r1/'+str(Path(catalog['apps'][0]['path']).relative_to('assets/desktop'))
 code='''const url=arguments[0],done=arguments[arguments.length-1];(async()=>{
 const {mount}=await import(url),make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},textButton=(label,fn)=>{const n=make('button','',label);n.type='button';n.addEventListener('click',fn);return n;};
 let calls=0,notify;const session={public:{kind:'registered'}},life=new AbortController(),snapshot={actor:'actor',height:0,quorum:1,writable:true,state:{messages:[]},pending:[]};
 const channel={snapshot:async()=>snapshot,queue:async()=>{if(++calls===1)throw Error('disk quota test');},cancel:async()=>{}},service={officialDirectory:async()=>({items:[{category:'official',label:'General chess chat',channel:'c'}]}),joinOfficialChannel:async()=>({channel}),close(){}};
 const host={ui:{make,textButton},session:()=>session,signal:life.signal,network:{config:{}},storage:{deviceHistory:{channels:({onChange})=>{notify=onChange;return service;}}}};const app=mount(host);document.body.append(app.element);const until=performance.now()+5000;while(performance.now()<until&&app.element.querySelector('button[type=submit]').disabled)await new Promise(r=>setTimeout(r,10));
 const form=app.element.querySelector('form'),draft=form.querySelector('textarea'),status=app.element.querySelector('.channel-conversation .app-status');draft.value='My unsaved message';form.requestSubmit();await new Promise(r=>setTimeout(r,100));if(draft.value!=='My unsaved message'||!status.textContent.includes('Message not saved'))throw Error('Draft or error was lost');notify();await new Promise(r=>setTimeout(r,100));if(!status.textContent.includes('Message not saved'))throw Error('Refresh hid save failure');if(!app.element.querySelector('details p').textContent.includes('disk quota test'))throw Error('Technical reason absent from Nerd settings');form.requestSubmit();await new Promise(r=>setTimeout(r,100));if(draft.value||status.textContent.includes('Message not saved')||calls!==2)throw Error('Explicit retry did not clear the failure');app.dispose();life.abort();return 'PASS draft retained, failure visible across refresh, technical reason in Nerd, retry clears';
 })().then(x=>done({value:x}),e=>done({error:e.stack}));'''
 out=d.call('/session/'+sid+'/execute/async',{'script':code,'args':[app]});assert 'error' not in out,out;print(out['value'])
finally:
 if sid:d.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join()
