#!/usr/bin/env python3
"""Browser crash test for an experimental recovery vote fence."""
import functools,http.server,importlib.util,json,os,shutil,signal,tempfile,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
with tempfile.TemporaryDirectory(prefix='codi-vote-fixture-') as folder,tempfile.TemporaryDirectory(prefix='codi-vote-profile-',dir=Path.home()/'snap/chromium/common') as profile:
 root=Path(folder)
 for name in ['network','assets/desktop','assets/vendor/chess']:
  shutil.copytree(ROOT/name,root/name,ignore=shutil.ignore_patterns('__pycache__'))
 p=root/'scripts/fixtures';p.mkdir(parents=True);shutil.copyfile(ROOT/'scripts/fixtures/official-recovery-vote-page.mjs',p/'official-recovery-vote-page.mjs')
 (root/'index.html').write_text('<main id="gate"></main><script type="module" src="/scripts/fixtures/official-recovery-vote-page.mjs"></script>')
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=folder));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);sid=None
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  value=d.call('/session/'+sid+'/execute/async',{'script':'const args=Array.from(arguments),done=args.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value['value']
 def start():
  global sid
  value=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+profile]}}}});sid=value['sessionId'];pid=value['capabilities']['goog:processID'];d.call('/session/'+sid+'/url',{'url':origin});d.wait(lambda:js('return window.fixtureReady===true;'),15);d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});d.wait(lambda:js('return window.storageReady===true||!!document.querySelector(".storage-consent button:not(:disabled)");'),15);
  if not js('return window.storageReady===true;'):
   e=d.call('/session/'+sid+'/element',{'using':'css selector','value':'.storage-consent button:not(:disabled)'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sid+'/element/'+e+'/click',{})
  d.wait(lambda:js('return window.storageReady===true;'),15);return pid
 try:
  pid=start();record=task('return voteFixture.begin();');assert record['vote'];advanced=task('return voteFixture.advancedFence();');assert all(v for k,v in advanced.items() if k not in ("retiredError","resume")),advanced;actual=[task('return voteFixture.actualRace(args[0]);',[mode]) for mode in ('race','normal-first','recovery-first')];assert all(x['oneWinner'] and x['loserRefused'] for x in actual) and actual[1]['normalWon'] and not actual[2]['normalWon'],actual;guards=task('return voteFixture.guards(args[0]);',[record]);assert all(guards.values()),guards;race=task('return voteFixture.concurrent(args[0]);',[record]);assert all(race.values()),race;proc=Path('/proc')/str(pid);assert ('--user-data-dir='+profile).encode() in (proc/'cmdline').read_bytes().replace(b'\0',b' ').split();os.kill(pid,signal.SIGKILL);d.call('/session/'+sid,method='DELETE');sid=None;start();result=task('return voteFixture.reopen(args[0]);',[record]);assert all(result.values()),result;advanced_resume=task('return voteFixture.advancedResume(args[0]);',[advanced['resume']]);assert all(advanced_resume.values()),advanced_resume;print(json.dumps({'status':'PASS','checks':['advanced committed head rejects stale recovery fence and blocks view-change write after replica reopen','actual prepare and recovery vote exclude each other in both orders and a race','guarded normal and recovery transactions select one','concurrent competing votes have one winner','strict vote committed before return','advanced accepted head and recovery fence survive browser SIGKILL','same vote restored after browser SIGKILL','conflicting other-role vote refused','same proposal other-role vote accepted'],'scope':'local isolated prototype; no live transition or validator retirement'}))
 finally:
  if sid:
   try:js('voteFixture.close();')
   finally:d.call('/session/'+sid,method='DELETE')
  server.shutdown();server.server_close();thread.join(timeout=3)
