#!/usr/bin/env python3
"""Exercise the built Chat app's default and read-only SYSTEM selection."""
import functools,importlib.util,json,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'.build/system-chat-app-r1'
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'});entry=json.loads((folder/'apps.json').read_text())['apps'][0];app='/'+entry['path'].removeprefix('assets/desktop/')
 script='''const done=arguments[arguments.length-1];(async()=>{
 const {mount}=await import(arguments[0]),make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},textButton=(label,fn)=>{const n=make('button','',label);n.type='button';n.addEventListener('click',fn);return n;};
 const session={public:{kind:'registered',name:'test'}},life=new AbortController(),items=[{category:'official',channel:'s',label:'SYSTEM'},{category:'official',channel:'g',label:'General chess chat'}];
 const service={officialDirectory:async()=>({items}),joinOfficialChannel:async channel=>({channel:{channel,snapshot:async()=>({height:1,readable:true,writable:channel==='g',actor:'local',state:{messages:channel==='s'?[{id:'notice',actor:'system',text:'Test announcement'}]:[],moderation:[]},pending:[],officialStatus:{caughtUp:true}})}}),close(){}};
 const host={ui:{make,textButton},session:()=>session,signal:life.signal,network:{config:{}},storage:{deviceHistory:{channels:()=>service}}},app=mount(host);document.body.append(app.element);
 const wait=async(fn)=>{for(let i=0;i<100;i++){if(fn())return;await new Promise(r=>setTimeout(r,20));}throw Error('View update timed out: '+app.element.textContent);};
 await wait(()=>app.element.querySelector('.channel-title')?.textContent==='General chess chat'&&!app.element.querySelector('.channel-composer button').disabled);
 const system=[...app.element.querySelectorAll('.channel-list-item')].find(n=>n.textContent==='SYSTEM');if(!system)throw Error('SYSTEM missing');system.click();await wait(()=>app.element.querySelector('.channel-title')?.textContent==='SYSTEM'&&app.element.textContent.includes('Test announcement'));
 if(!app.element.querySelector('.channel-composer button').disabled||!app.element.querySelector('.channel-composer textarea').disabled||!app.element.textContent.includes('System announcements are read-only.'))throw Error('SYSTEM must be read-only');
 app.dispose();life.abort();return 'PASS General opens by default; SYSTEM shows announcements and disables sending';
 })().then(done,e=>done({error:e.stack||String(e)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':script,'args':[app]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3)
