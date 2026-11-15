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
 p=root/'scripts/fixtures';p.mkdir(parents=True);shutil.copyfile(ROOT/'scripts/fixtures/official-recovery-vote-page.mjs',p/'official-recovery-vote-page.mjs');(root/'index.html').write_text('<main id="gate"></main><script type="module" src="/scripts/fixtures/official-recovery-vote-page.mjs"></script>')
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
  pids={side:start(side) for side in 'abcdef'};members={side:task(side,'return voteFixture.createMember();') for side in 'abcdef'};assert len({m['actor'] for m in members.values()})==6
  old=sorted((members[s] for s in 'abcd'),key=lambda x:x['actor']);new=sorted((members[s] for s in 'cdef'),key=lambda x:x['actor']);bundle=task('a','return voteFixture.createBundle(args[0],args[1],args[2]);',[members['a'],old,new]);
  for side in 'abcdef':
   derived=task(side,'return voteFixture.deriveBundle(args[0],args[1],args[2]);',[bundle,old,new]);assert derived==bundle['trusted'];task(side,'return voteFixture.multiInit(args[0],args[1]);',[members[side],derived])
  assert task('f','try{await voteFixture.deriveBundle({...args[0],trusted:{...args[0].trusted,genesisHash:args[0].trusted.head}},args[1],args[2]);return false;}catch{return true;}',[bundle,old,new])
  votes={side:task(side,'return voteFixture.multiVote(args[0]);',[bundle]) for side in 'abcde'};selected=[votes[s]['old'] for s in 'abc']+[votes[s]['new'] for s in 'cde']
  for insufficient in (selected[1:],selected[:-1]):
   too_few=task('d','try{await voteFixture.multiVerify(args[0],args[1],args[2],args[3]);return false;}catch{return true;}',[bundle,old,new,insufficient]);assert too_few
  result=task('d','return voteFixture.multiVerify(args[0],args[1],args[2],args[3]);',[bundle,old,new,selected]);assert result['oldVotes']==result['newVotes']==3
  assert task('d','try{await voteFixture.multiVerify(args[0],args[1],args[1],args[2]);return false;}catch{return true;}',[bundle,old,selected])
  transition=task('d','return voteFixture.verifyTransition(args[0],args[1],args[2],args[3]);',[bundle,old,new,selected]);assert transition['generation']==1 and all(transition[k] for k in ('controllerChanged','headChanged','replayRefused','forgedRefused')),transition;other_transition=task('e','return voteFixture.verifyTransition(args[0],args[1],args[2],args[3]);',[bundle,old,new,list(reversed(selected))]);assert other_transition['head']==transition['head']
  archived=task('a','return voteFixture.saveArchive(args[0],args[1],args[2],args[3]);',[bundle,old,new,selected]);assert archived['head']==transition['head'];negative=task('a','return voteFixture.archiveNegatives(args[0],args[1]);',[bundle,archived]);assert all(negative.values()),negative;concurrency=task('d','return voteFixture.archiveConcurrency(args[0],args[1]);',[bundle,archived]);assert all(concurrency.values()),concurrency
  offer=task('a','return recoveryRTC.offer();');answer=task('f','return recoveryRTC.answer(args[0],args[1],args[2]);',[offer,bundle['trusted']['channel'],bundle['trusted']['genesisHash']]);task('a','return recoveryRTC.accept(args[0]);',[answer]);d.wait(lambda:js('a','return recoveryData?.readyState==="open";') and js('f','return recoveryData?.readyState==="open";'),30)
  js('a','const p=JSON.parse(outgoingRecoveryProof);p.transitions[0].votes[0]=p.transitions[0].votes[0].slice(0,-2)+"AA";recoveryRTC.send(JSON.stringify(p));');d.wait(lambda:js('f','return recoveryReceipts.length===1;'),30);assert js('f','return recoveryReceipts[0].ok===false;')
  js('a','recoveryRTC.send(outgoingRecoveryProof);');d.wait(lambda:js('f','return recoveryReceipts.length===2;'),30);assert js('f','return recoveryReceipts[1].ok&&recoveryReceipts[1].head===arguments[0];',[transition['head']]);received=task('f','return voteFixture.loadArchive(args[0]);',[bundle]);assert received['floor']['head']==transition['head']
  profile=str(Path(profiles)/'a');proc=Path('/proc')/str(pids['a']);assert ('--user-data-dir='+profile).encode() in (proc/'cmdline').read_bytes().replace(b'\0',b' ').split();os.kill(pids['a'],signal.SIGKILL);d.call('/session/'+sessions.pop('a'),method='DELETE');start('a');task('a','return voteFixture.multiResume(args[0],args[1]);',[members['a'],bundle['trusted']]);assert task('a','return voteFixture.multiVote(args[0]);',[bundle])==votes['a'];reloaded=task('a','return voteFixture.loadArchive(args[0]);',[bundle]);assert reloaded['hash']==archived['hash'] and reloaded['floor']['head']==transition['head'];assert task('d','return voteFixture.multiVerify(args[0],args[1],args[2],args[3]);',[bundle,old,new,selected])['oldVotes']==3
  print(json.dumps({'status':'PASS','checks':['six browsers independently verify recovery-enabled genesis; wrong genesis pin refused','either committee below quorum is rejected','overlapping old and new committees each reach three-of-four quorum','separate browsers derive same in-memory transition and reject replay','fresh browser handles concurrent and reordered equivalent proof; corrupt and rollback proofs rejected','RTC peer rejects corrupted proof and stores verified proof','restart revalidates saved proof and votes'],'scope':'local browsers; manually signaled raw RTCDataChannel carries archived proof, fixture-distributed votes; no product transport, independent WAN, live transition or distributed finality'}))
 finally:
  for side,sid in sessions.items():
   try:js(side,'voteFixture.close();')
   finally:d.call('/session/'+sid,method='DELETE')
  server.shutdown();server.server_close();thread.join(timeout=3)
