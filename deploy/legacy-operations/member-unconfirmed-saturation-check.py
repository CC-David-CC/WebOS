#!/usr/bin/env python3
"""Four real local Chrome WebRTC peers test recovery from a full seed when another opted-in transport already exists."""
import functools,hashlib,http.server,importlib.util,json,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def run():
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();sessions={};r={'status':'FAIL','scope':__doc__,'checks':[]}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  value=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const p=Array.from(arguments),done=p.pop();(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:e.stack||String(e)}));','args':args});assert value['ok'],value;return value.get('value')
 def check(name,condition):assert condition,name;r['checks'].append(name);print(json.dumps({'check':name}),flush=True)
 def connect(a,b,bind=True):
  offer=task(a,'const x=await routeFixture.offer();return {id:x.entry.id,token:x.token};');answer=task(b,'const x=await routeFixture.answer(p[0]);return {id:x.entry.id,token:x.token};',[offer['token']]);task(a,'await routeFixture.accept(p[0],p[1]);return true;',[offer['id'],answer['token']]);
  for side,link in [(a,offer['id']),(b,answer['id'])]:d.wait(lambda:js(side,'return routeFixture.entries().some(e=>e.id===arguments[0]&&e.state==="ready");',[link]),30)
  if bind:
   task(a,'await routeFixture.bind(p[0],p[1]);return true;',[offer['id'],js(b,'return routeFixture.actor;')]);task(b,'await routeFixture.bind(p[0],p[1]);return true;',[answer['id'],js(a,'return routeFixture.actor;')])
  return {a:offer['id'],b:answer['id']}
 try:
  for side in 'abcde':
   sessions[side]=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];d.call('/session/'+sessions[side]+'/timeouts',{'script':120000});d.call('/session/'+sessions[side]+'/url',{'url':f'http://127.0.0.1:{server.server_port}/scripts/member-route-webrtc-page.html?side={side}&max=2'});d.wait(lambda:js(side,'return window.fixtureReady===true;'),20)
  controller=js('a','return routeFixture.actor;');wire=task('a','return await routeFixture.createPolicy();')
  for side in 'abcde':task(side,'await routeFixture.init(p[0],p[1]);return true;',[wire,controller])
  ca=connect('c','a');cb=connect('c','b');ab=connect('a','b')
  check('two seed peers are each full with confirmed neighbors',all(js(side,'return routeFixture.stats().topology.neighbors===2;') for side in 'ac'))
  cd=connect('c','d',False);ad=connect('a','d',False)
  for side,link in [('c',cd['c']),('a',ad['a'])]:
   refused=task(side,'try{await routeFixture.bind(p[0],p[1]);return false;}catch(error){return error.message.includes("neighbor allowance");}',[link,js('d','return routeFixture.actor;')]);check('full seed '+side+' rejects its own outbound admission',refused)
  check('returning reader has two incoming admissions but no confirmed neighbors',js('d','const s=routeFixture.stats().topology;return s.admissions===2&&s.neighbors===0;'))
  de=connect('d','e',False);js('d','routeFixture.setRecovery(arguments[0],true);',[de['d']])
  js('c','routeFixture.blockBind(arguments[0]);',[cd['c']]);js('a','routeFixture.blockBind(arguments[0]);',[ad['a']]);task('d','await routeFixture.maintain();return true;')
  check('an ambiguous timeout does not discard either incoming admission',js('d','const s=routeFixture.stats().topology;return s.admissions===2&&s.neighbors===0;'))
  js('c','routeFixture.unblockBind(arguments[0]);',[cd['c']]);js('a','routeFixture.unblockBind(arguments[0]);',[ad['a']]);time.sleep(15.2);task('d','await routeFixture.maintain();return true;')
  check('returning reader confirms a free alternate route without exceeding its neighbor limit',js('d','const s=routeFixture.stats().topology;return s.neighbors>=1&&s.admissions<=2;'))
  check('alternate route serves authenticated channel requests',task('d','return await routeFixture.head(p[0]);',[de['d']])=={'status':'fixture-head'})
  r['sourceSHA256']=hashlib.sha256((ROOT/'network/device-member-introductions.mjs').read_bytes()).hexdigest();r['status']='PASS'
 except Exception:
  r['error']=traceback.format_exc();r['diagnostics']={}
  for side,sid in sessions.items():
   try:r['diagnostics'][side]={'stats':js(side,'return routeFixture?.stats();'),'logs':js(side,'return routeFixture?.logs;'),'browser':d.call('/session/'+sid+'/log',{'type':'browser'})}
   except Exception:pass
 finally:
  for side,sid in sessions.items():
   try:
    budget=task(side,'return await routeFixture.close();');r.setdefault('cleanup',{})[side]=budget
    if any(v!=0 for k,v in budget.items() if k!='closed'):r['status']='FAIL';r['cleanupError']='Outstanding network budget for '+side
   except Exception as e:r['status']='FAIL';r['cleanupError']=str(e)
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r['status']='FAIL';r['browserCleanupError']=str(e)
  server.shutdown();server.server_close();thread.join()
 out=ROOT/'.build/checks/member-unconfirmed-saturation-candidate-r3.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':r['checks'],'error':r.get('error'),'cleanupError':r.get('cleanupError')},indent=2));return r['status']=='PASS'
if __name__=='__main__':raise SystemExit(not run())
