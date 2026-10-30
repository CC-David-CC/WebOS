#!/usr/bin/env python3
"""Exercise shared tab draft state, account isolation and refresh in Chrome."""
import functools,importlib.util,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
fixture=ROOT/'.build/tab-chat-drafts-check.html';assert not fixture.exists();fixture.write_text('<!doctype html><title>Draft fixture</title>')
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/.build/tab-chat-drafts-check.html'})
 code='''const done=arguments[arguments.length-1];(async()=>{const {createTabChatDrafts}=await import('/assets/desktop/tab-chat-drafts.mjs'),life=new AbortController(),otherLife=new AbortController(),id='A'.repeat(43),otherChannel='B'.repeat(43),events=[];let allowed=true;const current=()=>{if(!allowed)throw Error('account changed');},make=(scope,signal,onChange=()=>{})=>createTabChatDrafts({scope,signal,current,onChange});window.first=make('account-a',life.signal);window.second=make('account-a',life.signal,(ch,text)=>events.push([ch,text]));window.other=make('account-b',otherLife.signal);
 first.write(id,'draft one');if(second.read(id)!=='draft one'||other.read(id)!==''||second.read(otherChannel)!==''||events.length!==1)throw Error('scope, channel or event mismatch');second.write(id,'newer text');if(first.clearIfEqual(id,'draft one')||first.read(id)!=='newer text')throw Error('old send erased newer edit');if(!first.clearIfEqual(id,'newer text')||second.read(id)!=='')throw Error('matching send did not clear');first.write(id,'survive refresh');
 for(const task of [()=>first.write(id,'x'.repeat(4097)),()=>first.write('bad','x')]){let failed=false;try{task();}catch{failed=true;}if(!failed)throw Error('invalid input accepted');}
 let leaked=false;const bad=createTabChatDrafts({scope:'account-a',signal:life.signal,current,storage:{getItem(){return null;},setItem(){throw Error('quota');},removeItem(){}},onChange:()=>{leaked=true;}});const before=events.length;try{bad.write(id,'unsaved');throw Error('quota accepted');}catch(e){if(e.message==='quota accepted')throw e;}if(leaked||events.length!==before)throw Error('failed write broadcast');bad.close();
 allowed=false;let denied=false;try{first.write(id,'wrong account');}catch{denied=true;}if(!denied)throw Error('retired session can write');allowed=true;second.close();const beforeClose=events.length;first.write(otherChannel,'different channel');if(events.length!==beforeClose)throw Error('closed listener notified');first.close();other.close();life.abort();otherLife.abort();return 'PASS shared drafts, isolation, stale-send protection, quota failure and disposal';})().then(done,e=>done({error:e.stack||String(e)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[]});assert isinstance(result,str),result;print(result)
 driver.call('/session/'+sid+'/refresh',{},'POST')
 code='''const done=arguments[arguments.length-1];(async()=>{const {createTabChatDrafts}=await import('/assets/desktop/tab-chat-drafts.mjs'),life=new AbortController(),a=createTabChatDrafts({scope:'account-a',signal:life.signal,current(){}}),b=createTabChatDrafts({scope:'account-b',signal:life.signal,current(){}}),id='A'.repeat(43);if(a.read(id)!=='survive refresh'||b.read(id)!=='')throw Error('refresh or account isolation failed');a.write(id,'');a.write('B'.repeat(43),'');a.close();b.close();life.abort();return 'PASS saved draft survives a same-tab refresh';})().then(done,e=>done({error:e.stack||String(e)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3);fixture.unlink(missing_ok=True)
