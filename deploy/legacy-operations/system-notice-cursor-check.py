#!/usr/bin/env python3
"""Check notification baseline, acknowledgements and safe rendering in Chrome."""
import functools,importlib.util,threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sid=None
try:
 sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/url',{'url':'http://127.0.0.1:'+str(server.server_port)+'/scripts/fixtures/system-autojoin-empty.html'})
 code='''const done=arguments[arguments.length-1];(async()=>{
 const network=await(await fetch('/networking.js')).text(),prefix=network.split('// All applications share this session pool')[0];(0,eval)(prefix+'\\n;globalThis.cursorFactory=createSystemNoticeCursor;');
 const app=await(await fetch('/app.js')).text(),start=app.indexOf('function clearSystemAnnouncement()'),end=app.indexOf('function icon(',start);if(start<0||end<0)throw Error('Announcement UI missing');(0,eval)(app.slice(start,end)+'\\n;globalThis.showNotice=showSystemAnnouncement;');
 const key='test-system-'+crypto.randomUUID(),channel='system',state=(messages,caughtUp=true,error=null)=>({official:true,officialStatus:{caughtUp,error},state:{messages}}),m=(i,text,actor=channel)=>({index:i,text,actor});let cursor=cursorFactory(localStorage,key,channel);
 if(cursor.inspect(state([m(1,'old')],false))!==null||localStorage.getItem(key)!==null)throw Error('Unverified baseline accepted');
 if(cursor.inspect(state([m(1,'old')]))!==null||localStorage.getItem(key)!=='1')throw Error('First visit baseline incorrect');
 if(cursor.inspect(state([m(1,'old'),m(2,'bad','other')]))!==null)throw Error('Non-system author accepted');
 const notice=cursor.inspect(state([m(1,'old'),m(2,'<img src=x onerror=alert(1)>')]));if(!notice||notice.index!==2)throw Error('New announcement missing');
 showNotice(notice.text,()=>cursor.acknowledge(notice.index));const box=document.querySelector('#system-announcement');if(box.querySelector('img')||box.querySelector('[data-system-message]').textContent!==notice.text)throw Error('Announcement was not rendered as text');
 box.querySelector('button').click();if(document.querySelector('#system-announcement')||localStorage.getItem(key)!=='2')throw Error('Dismissal did not persist');
 cursor=cursorFactory(localStorage,key,channel);if(cursor.inspect(state([m(1,'old'),m(2,'seen')]))!==null)throw Error('Acknowledged announcement repeated');
 const later=cursor.inspect(state([m(3,'while away')]));if(!later||later.text!=='while away')throw Error('Missed announcement not recovered');
 localStorage.removeItem(key);return 'PASS verified baseline, unseen recovery, dismissal persistence and safe text rendering';
 })().then(done,e=>done({error:e.stack||String(e)}));'''
 result=driver.call('/session/'+sid+'/execute/async',{'script':code,'args':[]});assert isinstance(result,str),result;print(result)
finally:
 if sid:driver.call('/session/'+sid,method='DELETE')
 server.shutdown();server.server_close();thread.join(3)
