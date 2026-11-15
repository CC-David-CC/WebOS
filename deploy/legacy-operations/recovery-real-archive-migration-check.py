#!/usr/bin/env python3
"""Six separate Chrome profiles verify an experimental recovery quorum."""
import functools,http.server,importlib.util,json,os,shutil,signal,tempfile,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
with tempfile.TemporaryDirectory(prefix='codi-quorum-fixture-') as folder,tempfile.TemporaryDirectory(prefix='codi-quorum-profiles-',dir=Path.home()/'snap/chromium/common') as profiles:
 root=Path(folder)
 for name in ['network','assets/desktop','assets/vendor/chess']:shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
 p=root/'scripts/fixtures';p.mkdir(parents=True);shutil.copyfile(ROOT/'scripts/fixtures/recovery-real-archive-page.mjs',p/'official-recovery-vote-page.mjs');(root/'index.html').write_text('<main id="gate"></main><script type="module" src="/scripts/fixtures/official-recovery-vote-page.mjs"></script>')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=folder));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);sessions={}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  value=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const args=Array.from(arguments),done=args.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value['value']
 def start(side):
  profile=str(Path(profiles)/side);value=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+profile]}}}});sessions[side]=value['sessionId'];pid=value['capabilities']['goog:processID'];d.call('/session/'+sessions[side]+'/url',{'url':origin});d.wait(lambda:js(side,'return window.fixtureReady===true;'),15);d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});d.wait(lambda:js(side,'return window.storageReady===true||!!document.querySelector(".storage-consent button:not(:disabled)");'),15)
  if not js(side,'return window.storageReady===true;'):
   e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':'.storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
  d.wait(lambda:js(side,'return window.storageReady===true;'),15);return pid
 try:
  start('a')
  before=task('a','return voteFixture.create();');assert before['count']==1
  after=task('a','return voteFixture.migrate();');assert after['head']==before['head'] and after['count']==before['count'] and after['checkpoint']==before['checkpoint'] and after['message']=='A real saved migration message' and after['blocked'] and after['retry'] and after['stale'],after
  for side,mode in [('b','append-first'),('c','race')]:
   start(side);task(side,'return voteFixture.create();');out=task(side,'return voteFixture.migrate(args[0]);',[mode]);assert out.get('appendFirstStaleRefused') if mode=='append-first' else out.get('raceOneWinner'),out
  pid=start('d');task('d','return voteFixture.create();');interrupted=task('d','return voteFixture.migrate(args[0]);',['before-vote']);profile=str(Path(profiles)/'d');proc=Path('/proc')/str(pid);assert ('--user-data-dir='+profile).encode() in (proc/'cmdline').read_bytes().replace(b'\0',b' ').split();os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop('d'),method='DELETE');start('d');resumed=task('d','return voteFixture.resumeFence(args[0]);',[interrupted]);assert resumed['headRestored'] and resumed['validAppendBlocked'] and resumed['competingRefused'] and resumed['voteRestored'] and resumed['signature'],resumed
  start('e');cancel_before=task('e','return voteFixture.create();');cancelled=task('e','return voteFixture.cancelUpgrade();');assert cancelled['reached'] and cancelled['cancelled'] and cancelled['head']==cancel_before['head'] and cancelled['count']==1 and cancelled['message']=='A real saved migration message',cancelled
  for side,mode in [('f','close'),('g','forget')]:
   start(side);baseline=task(side,'return voteFixture.create();');result=task(side,'return voteFixture.interruptUpgrade(args[0]);',[mode]);assert result['reached'] and result['refused'] and result['version']==1 and result['head']==baseline['head'] and result['message']=='A real saved migration message',result
  pid=start('h');task('h','return voteFixture.create();');upgraded=task('h','return voteFixture.upgradeOnly();');profile=str(Path(profiles)/'h');proc=Path('/proc')/str(pid);assert ('--user-data-dir='+profile).encode() in (proc/'cmdline').read_bytes().replace(b'\0',b' ').split();os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop('h'),method='DELETE');start('h');restored=task('h','return voteFixture.resumeUpgrade(args[0]);',[upgraded]);assert restored['head']==upgraded['head'] and restored['checkpoint']==upgraded['checkpoint'] and restored['message']=='A real saved migration message',restored
  print(json.dumps({'status':'PASS','checks':['actual replica signs and commits message to v1 archive','caller cancellation, archive close and consent withdrawal during upgrade retain signed v1 history','v2 upgrade closes existing v1 archive and rejects a v1 reopen','v2 migration survives browser SIGKILL before any recovery fence','v2 schema migration preserves signed checkpoint and message','opt-in archive re-verifies checkpoint, operation index and history','wrong scope, database and forged archive are refused; overridden load is ignored','signed recovery authority is checked before fencing a real saved archive','atomic fence checks saved head and blocks real archive append','exact fence retry succeeds and stale expected head is refused','new-only recovery vote is saved after verified archive fence and is repeatable','pending original remains writable while fenced','second channel commits its own message while first channel is fenced','fence and actual append race has exactly one winner','append first makes stale fence fail','browser crash preserves fence against valid competing recovery and valid append; exact retry succeeds'], 'scope':'eight local browser profiles with opt-in archive and experimental authenticated wrapper; raw primitive remains unauthenticated; no deployment'}))

 finally:
  for side,sid in sessions.items():
   try:js(side,'voteFixture.close();')
   finally:d.call('/session/'+sid,method='DELETE')
  server.shutdown();server.server_close();thread.join(timeout=3)
