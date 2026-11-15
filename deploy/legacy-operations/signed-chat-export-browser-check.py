#!/usr/bin/env python3
"""Test packaged Chat export against a real, locally signed chat chain."""
import functools, importlib.util, json, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/path); result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
fixture=module('writer_fixture','official-chat-writer-check.py'); verifier=module('chat_verifier','verify-signed-chat-export.py');driver=module('browser_driver','touch-preview-check.py')
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
case=fixture.Checks();case.setUp();sid=None
try:
 heads=[case.writer.append(case.channel,case.genesis,case.record('public first'),case.bind(),case.principal)['head']]
 state=case.registry.replayed_head(case.channel)['state'];heads.append(case.writer.append(case.channel,case.genesis,case.record('public second',sequence=2,previous=state['authors'][0]['last']),case.bind(),case.principal)['head'])
 state=case.registry.replayed_head(case.channel)['state'];heads.append(fixture.mark_spam(case.registry,case.key,message=state['messages'][0]['id'])['head'])
 checkpoint=case.registry.replayed_head(case.channel);blocks=[json.loads(row[0]) for row in case.registry._db.execute('SELECT wire FROM official_replayed_blocks WHERE channel=? ORDER BY height',(case.channel,))]
 wire=case.registry._db.execute('SELECT policy_wire FROM official_channels WHERE channel=?',(case.channel,)).fetchone()[0];config={'channel':case.channel,'genesisHash':case.genesis,'policyWire':wire};entries=[{'height':i+1,'head':head,'block':block} for i,(head,block) in enumerate(zip(heads,blocks))]
 folder=ROOT/'.build/chat-signed-record-r1';server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 try:
  sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':60000});driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'});entry=json.loads((folder/'apps.json').read_text())['apps'][0];app='/'+entry['path'].removeprefix('assets/desktop/')
  code='''const done=arguments[arguments.length-1];(async()=>{
   const [url,config,entries,head,state]=arguments,{mount}=await import(url),make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},textButton=(label,fn)=>{const n=make('button','',label);n.type='button';n.addEventListener('click',fn);return n;};
   const session={public:{kind:'registered',name:'alice'}},life=new AbortController(),reverse=[...entries].reverse();let captured=null,broken=false,caught=false;
   const handle={channel:config.channel,snapshot:async()=>({channel:config.channel,actor:'me',head,height:entries.length,state,pending:[{id:'unsent',kind:'chat',data:{text:'PRIVATE UNSENT DRAFT'},status:'pending'}],readable:true,writable:true,official:true,officialStatus:{caughtUp:caught},quorum:1}),history:async({before,limit})=>{const start=before?Number(before.slice(1)):0,end=Math.min(reverse.length,start+limit);return {entries:reverse.slice(start,end),next:end<reverse.length?'p'+end:null,incomplete:broken};}};
   const service={officialDirectory:async()=>({items:[{category:'official',channel:config.channel,label:'General chess chat',invitation:{config}}]}),joinOfficialChannel:async()=>({channel:handle}),close(){}};
   const host={ui:{make,textButton},session:()=>session,signal:life.signal,network:{config:{}},storage:{downloadGuestFile:(name,bytes)=>{captured={name,raw:new TextDecoder().decode(bytes)};},deviceHistory:{channels:()=>service}}};
   const app=mount(host);document.body.append(app.element);const wait=async(fn)=>{for(let i=0;i<200;i++){if(fn())return;await new Promise(r=>setTimeout(r,20));}throw Error('Timed out: '+app.element.textContent);};
   const button=[...app.element.querySelectorAll('button')].find(b=>b.textContent==='Download signed chat record (.json)');await wait(()=>app.element.textContent.includes('Loading messages'));if(!button.disabled)throw Error('Unverified history allowed');caught=true;window.dispatchEvent(new Event('online'));await wait(()=>!button.disabled);button.click();await wait(()=>captured);const good=captured;captured=null;broken=true;button.click();await wait(()=>app.element.textContent.includes('Complete signed history is not available'));if(captured)throw Error('Incomplete history downloaded');app.dispose();life.abort();return good;
  })().then(done,error=>done({error:error.stack||String(error)}));'''
  result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[app,config,entries,checkpoint['head'],checkpoint['state']]});assert 'error' not in result,result;assert 'PRIVATE UNSENT DRAFT' not in result['raw'];verified=verifier.verify(result['raw'].encode(),case.channel);assert verified['height']==3 and verified['operations']==3
  print('PASS packaged Chat exports verified messages and signed moderation; unsent draft excluded and incomplete history refused')
 finally:
  if sid:driver.call('/session/'+sid,method='DELETE')
  server.shutdown();server.server_close();thread.join(3)
finally:case.tearDown()
