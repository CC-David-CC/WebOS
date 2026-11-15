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
  for side in 'abcd': start(side)
  members={side:task(side,'return voteFixture.createMember();') for side in 'abcd'}
  ordered=sorted(members.values(),key=lambda x:x['actor']);leader=next(side for side in 'abcd' if members[side]['actor']==ordered[0]['actor']);active=[leader]+[side for side in 'abcd' if side!=leader][:2];lag=next(side for side in 'abcd' if side not in active)
  config=task('a','return voteFixture.groupPolicy(args[0],args[1]);',[members['a'],ordered])
  for side in 'abcd':task(side,'return voteFixture.groupOpen(args[0],args[1]);',[members[side],config])
  proposed=task(leader,'return voteFixture.groupPropose(args[0],args[1]);',[members[leader],config]);prepares=[proposed['prepareVote']]
  for side in active[1:]:prepares.append(task(side,'return (await groupReplica.prepare(args[0])).prepareVote;',[proposed['proposal']]))
  prepared={'header':proposed['proposal']['header'],'prepare':prepares};commits=[task(side,'return groupReplica.commit(args[0]);',[prepared]) for side in active]
  block={'header':prepared['header'],'operations':proposed['proposal']['operations'],'prepare':prepares,'commit':commits}
  accepted=[task(side,'const x=await groupReplica.accept(args[0]);return {head:x.position.head,height:x.position.height,checkpoint:x.checkpoint};',[block]) for side in active];assert len({x['head'] for x in accepted})==1 and all(x['height']==1 for x in accepted)
  bundle=task('a','return voteFixture.groupBundle(args[0],args[1],args[2]);',[config,ordered,accepted[0]['checkpoint']]);assert bundle['trusted']['head']==accepted[0]['head']
  lag_refused=task(lag,'try{await voteFixture.groupVote(args[0],args[1]);return false;}catch{return true;}',[members[lag],bundle]);assert lag_refused
  votes=[task(side,'return voteFixture.groupVote(args[0],args[1]);',[members[side],bundle]) for side in active];assert len({v['old'] for v in votes})==3
  caught=task(lag,'return (await groupReplica.sync(args[0])).position.head;',[accepted[0]['checkpoint']]);assert caught==bundle['trusted']['head'];lag_vote=task(lag,'return voteFixture.groupVote(args[0],args[1]);',[members[lag],bundle]);assert lag_vote['old'] not in [v['old'] for v in votes]
  selected=[v['old'] for v in votes]+[v['new'] for v in votes]
  cert=task(lag,'return voteFixture.multiVerify(args[0],args[1],args[1],args[2]);',[bundle,ordered,selected]);assert cert['oldVotes']==3 and cert['newVotes']==3
  deficient=task(lag,'try{await voteFixture.multiVerify(args[0],args[1],args[1],args[2]);return false;}catch{return true;}',[bundle,ordered,selected[1:]]);assert deficient
  deficient_new=task(lag,'try{await voteFixture.multiVerify(args[0],args[1],args[1],args[2]);return false;}catch{return true;}',[bundle,ordered,selected[:-1]]);assert deficient_new
  archive=task(lag,'return voteFixture.groupArchive(...args);',[config,ordered,bundle,selected,accepted[0]['checkpoint']]);assert archive['verified']
  blocked=[task(side,'try{await groupReplica.changeView(1);return false;}catch(e){return e.message.includes("guarded");}') for side in 'abcd'];assert all(blocked)
  print(json.dumps({'status':'PASS','checks':['three independent validators commit the same chat block','behind validator refuses recovery at newer head','three current validators persist recovery votes at the accepted head','behind validator catches up and can vote on the accepted head','joint recovery certificate verifies and requires both quorums','checkpoint anchored recovery archive stores and re-verifies certificate','each voting validator refuses a subsequent normal view change'],'scope':'four local browser profiles, fixture relays messages; no independent WAN or authority transition'}))
 finally:
  for side,sid in sessions.items():
   try:js(side,'voteFixture.groupClose();voteFixture.close();')
   finally:d.call('/session/'+sid,method='DELETE')
  server.shutdown();server.server_close();thread.join(timeout=3)
