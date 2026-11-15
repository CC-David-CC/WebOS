#!/usr/bin/env python3
"""Exercise both packaged composers at the actual UTF-8 message limit."""
import functools, importlib.util, json, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'.build')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':60000});driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/'});
 urls=[]
 for folder in ('chat-tab-drafts-quota-r3','chess-tab-drafts-quota-r3'):
  entry=json.loads((ROOT/'.build'/folder/'apps.json').read_text())['apps'][0];urls.append('/'+folder+'/'+entry['path'].removeprefix('assets/desktop/'))
 code='''const done=arguments[arguments.length-1];(async()=>{
 const [urls]=arguments,make=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;},textButton=(label,fn)=>{const n=make('button','',label);n.type='button';n.addEventListener('click',fn);return n;},wait=async(fn)=>{for(let i=0;i<200;i++){if(fn())return;await new Promise(r=>setTimeout(r,20));}throw Error('timed out');};
 for(const [index,url] of urls.entries()){
  const css=document.createElement('link');css.rel='stylesheet';css.href=url.replace('index.mjs','index.css');document.head.append(css);await new Promise((resolve,reject)=>{css.onload=resolve;css.onerror=reject;});const {mount}=await import(url),life=new AbortController(),session={public:{kind:'registered',name:'alice'}},messages=[],state={messages:[],moves:[]};let reject=false,hold=null;
  if(index===1)state.messages=Array.from({length:4},(_,i)=>({id:'message'+i,actor:'actor',text:'A sample conversation message '+i}));
  const channel={channel:'chat-id',snapshot:async()=>({actor:'actor',head:'h',height:0,state,pending:[],readable:true,writable:true,official:true,officialStatus:{caughtUp:true},quorum:1}),queue:async(kind,data)=>{if(reject)throw Error('storage failed');messages.push(data.text);if(hold)await hold;}};
  const game={channel:'game-id',snapshot:async()=>({head:'h',height:0,state,official:true,officialStatus:{caughtUp:true},chess:{terminal:true,result:'*',turn:'w'},pending:[]})};
  const invitation={label:'Chess',game:{config:{channel:'game-id'}},chat:{config:{channel:'chat-id'}}};
  const service={officialDirectory:async()=>({items:[{category:'official',channel:'chat-id',label:'General chess chat',invitation:{config:{channel:'chat-id'}}}]}),joinOfficialChannel:async()=>({channel}),joinChessMatch:async()=>({game,chat:channel,role:'spectator'}),close(){}};
  const host={ui:{make,textButton},session:()=>session,signal:life.signal,network:{config:{deviceChannels:{featuredChessMatch:{invitation}}}},storage:{deviceHistory:{channels:()=>service},downloadGuestFile(){}}};const app=mount(host);app.element.style.cssText='width:372px;height:490px;box-sizing:border-box';document.body.append(app.element);
  const form=app.element.querySelector('form'),draft=form.querySelector('textarea'),send=form.querySelector('button[type=submit]');await wait(()=>!send.disabled);
  const fill=value=>{draft.value=value;draft.dispatchEvent(new Event('input',{bubbles:true}));};
  const empty=[...app.element.querySelectorAll('.app-status')].find(x=>!x.textContent);if(!empty||getComputedStyle(empty).display!=='none')throw Error('empty status consumes space');
  if(index===1){const board=app.element.querySelector('.chess-board'),area=app.element.getBoundingClientRect(),form=app.element.querySelector('.chess-chat-form'),buttons=[...app.element.querySelectorAll('.chess-view-tabs button')],game=buttons.find(x=>x.textContent==='Game'),chat=buttons.find(x=>x.textContent==='Chat');if(board.getBoundingClientRect().bottom>area.bottom||board.getBoundingClientRect().width>325||form.querySelector('.app-status')||getComputedStyle(form.parentElement).display!=='none')throw Error('initial phone game layout wrong');chat.click();if(form.getBoundingClientRect().bottom>area.bottom)throw Error('composer outside phone window');if(getComputedStyle(board).display!=='none'||getComputedStyle(form.parentElement).display==='none'||chat.getAttribute('aria-pressed')!=='true')throw Error('chat view wrong');const h=app.element.querySelector('.chess-chat-history');if(h.scrollHeight<=h.clientHeight||h.scrollHeight-h.clientHeight-h.scrollTop>1)throw Error('first chat view not at latest');h.scrollTop=0;draft.value='keep this draft';game.click();chat.click();if(draft.value!=='keep this draft'||h.scrollTop!==0)throw Error('switch lost draft or reading position');app.element.style.width='700px';await new Promise(r=>requestAnimationFrame(r));if(board.getBoundingClientRect().width<400||getComputedStyle(form.parentElement).display==='none'||getComputedStyle(app.element.querySelector('.chess-view-tabs')).display!=='none')throw Error('desktop view wrong');app.element.style.width='372px';await new Promise(r=>requestAnimationFrame(r));}

  fill('😀'.repeat(1025));if(!app.element.textContent.includes('Message is too long'))throw Error('No length warning');form.requestSubmit();await new Promise(r=>setTimeout(r,50));if(messages.length||draft.value.length!==2050)throw Error('Long message was queued or lost');
  fill('😀'.repeat(1024));if(app.element.textContent.includes('Message is too long'))throw Error('Valid boundary rejected');form.requestSubmit();await wait(()=>messages.length===1&&draft.value==='');
  fill('hello');reject=true;form.requestSubmit();await wait(()=>app.element.textContent.includes('Message not saved'));await new Promise(r=>setTimeout(r,100));if(draft.value!=='hello'||!app.element.textContent.includes('Message not saved'))throw Error('Failure not retained');
  app.dispose();life.abort();app.element.remove();css.remove();
 }
 return 'PASS phone chat opens latest and preserves reading position and drafts; desktop shows both';})().then(done,error=>done({error:error.stack||String(error)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[urls]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3)
