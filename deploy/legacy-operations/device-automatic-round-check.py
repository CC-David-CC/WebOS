#!/usr/bin/env python3
"""Automatic fixed-validator recovery through actual Chat/Rooms and native RTC.

Minimal owned window renderer/local-development identities; real native Storage
API, keys, votes and archives. No v86, real account issuer or live site changes.
"""
import os,signal,argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=mod('replica_app_driver',ROOT/'scripts/touch-preview-check.py');builder=mod('replica_app_builder',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled=None):
 sessions={};profiles={};windows={};processes={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-replica-app-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':4,'actualRTCLinks':0,'actualBrowserLaunches':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=30):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def ready(side,w):wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]");',[w])
 def node(w,selector):return '[data-window="'+str(w)+'"] '+selector
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-auto-round-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  value=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=value['sessionId'];pid=value['capabilities']['goog:processID'];processes[side]=(pid,(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1'});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
  wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]")||!!hostSessionCase.node(arguments[0])?.querySelector(".storage-consent button:first-of-type:not(:disabled)");',[w])
  if not js(side,'return !!hostSessionCase.node(arguments[0]).querySelector("[data-device-channels]");',[w]):click(side,node(w,'.storage-consent button'))
  ready(side,w);js(side,'hostSessionCase.view=hostSessionCase.facades.get(arguments[0]);',[w])
 def connect(a,b):
  offer=task(a,'return hostSessionCase.view.offer();');answer=task(b,'return hostSessionCase.view.answer(params[0]);',[offer['token']]);task(a,'return hostSessionCase.view.accept(params[0],params[1]);',[offer['peerId'],answer['token']]);wait(a,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceReplicaReady;',[offer['peerId']]);wait(b,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceReplicaReady;',[answer['peerId']]);task(a,'return hostSessionCase.group.bindValidator(params[0]);',[offer['peerId']]);r['actualRTCLinks']+=1;return {a:offer['peerId'],b:answer['peerId']}
 def queue(side,text):
  wait(side,'return !hostSessionCase.node(arguments[0]).querySelector("[data-device-queue]").disabled;',[windows[side]]);js(side,'const d=hostSessionCase.node(arguments[0]).querySelector("[data-device-draft]");d.value=arguments[1];d.dispatchEvent(new Event("input"));',[windows[side],text]);click(side,node(windows[side],'[data-device-queue]'));wait(side,'return hostSessionCase.node(arguments[0]).querySelector("[data-device-draft]").value==="";',[windows[side]])
 def height(side,wanted,seconds=75):
  return d.wait(lambda:task(side,'return (await hostSessionCase.group.snapshot()).height===params[0];',[wanted]),seconds)
 def crash(side):
  pid,ticks=processes[side];proc=Path('/proc')/str(pid);args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').split();assert ('--user-data-dir='+str(profiles[side])).encode() in args and not any(a.startswith(b'--type=') for a in args) and os.readlink(proc/'exe').endswith('/chrome') and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==ticks;os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop(side),method='DELETE');return {'pid':pid,'startTicks':ticks,'signal':'SIGKILL'}

 try:
  assets=folder/'assets/desktop';assets.mkdir(parents=True);r['appBuild']=builder.build(ROOT.parent/'served_apps_public',assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['appCatalogSHA256']=hashlib.sha256((assets/'apps.json').read_bytes()).hexdigest()
  files={str(p.relative_to(ROOT)) for p in (ROOT/'assets/desktop').glob('*.mjs')};files.update(str(p.relative_to(ROOT)) for p in (ROOT/'network').glob('*.mjs'));files.update(['networking.js','desktop-apps.js','assets/vendor/chess/chess.mjs','scripts/fixtures/device-session-page.mjs','scripts/fixtures/device-session-bootstrap.js']);r['sourceSHA256']={}
  for n in sorted(files):
   data=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(data).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  source=(ROOT/'networking.js').read_text();assert source.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(source.replace('const disabled=true;','const disabled=false;'))
  fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text()
  if compiled:
   c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];assert len(c['apps'])==1;src=compiled/Path(app['path']).parent.relative_to('assets/desktop');raw=(src/'index.mjs').read_bytes();assert hashlib.sha256(raw).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(raw);r['actualCompiledCoreSHA256']=app['sha256']
   for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
   for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  (folder/'bootstrap.js').write_bytes((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_bytes());(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned app replica integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcd':
   start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Automatic validator "+params[0])).channel;',[side])
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Automatic app quorum",controller:params[0],validators:params[1],publicWrite:true});return (await hostSessionCase.view.channels())[0];',[actors['a'],list(actors.values())])
  for side in 'bcd':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  check('actual native app hosts enable one shared automatic worker per validator session',all(task(side,'const s=await hostSessionCase.group.snapshot();return s.automaticRounds&&s.quorum===3&&hostSessionCase.owner().stats().scheduler.channels===1;') for side in 'abcd'))
  links={}
  for i,a in enumerate('abcd'):
   for b in 'abcd'[i+1:]:links[a+b]=connect(a,b)
  ordered=sorted(actors,key=lambda side:actors[side]);writer=ordered[1];queue(writer,'An ordinary Send click needs no manual quorum command')
  for side in sessions:height(side,1)
  check('one actual Chat Send converges four independent accepted histories automatically',all(task(side,'const s=await hostSessionCase.group.snapshot();return s.height===1&&s.pending.length===0&&s.state.messages.length===1;') for side in sessions))
  dead=ordered[1];r['ownedLeaderCrash']=crash(dead);writer=ordered[0];room=js(writer,'return hostSessionCase.open("rooms");');ready(writer,room);task(writer,'hostSessionCase.view=hostSessionCase.facades.get(params[0]);hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[1].channel);return true;',[room,config]);queue(writer,'The group elects another leader after the old browser dies');js(writer,'hostSessionCase.detachedAuto=hostSessionCase.node(arguments[0]).querySelector("[data-device-channels]");hostSessionCase.close(arguments[0]);hostSessionCase.detachedText=hostSessionCase.detachedAuto.textContent;',[windows[writer]])
  for side in sessions:height(side,2)
  rounds={side:task(side,'const h=await hostSessionCase.group.history({limit:1});return h.entries[0].block.header.round;') for side in sessions};check('survivors automatically persist view changes and finish the exact pending message after leader SIGKILL',all(v>=1 for v in rounds.values()) and all(task(side,'const s=await hostSessionCase.group.snapshot();return s.pending.length===0&&s.state.messages.length===2;') for side in sessions))
  check('automatic completion survives the sending window and never revives its detached UI',js(writer,'return !hostSessionCase.detachedAuto.isConnected&&hostSessionCase.detachedAuto.textContent===hostSessionCase.detachedText;'))
  start(dead);task(dead,'hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0].channel);return true;',[config]);check('restarted browser restores its original author and prior accepted floor',task(dead,'const s=await hostSessionCase.group.snapshot();return s.actor===params[0]&&s.height===1;',[actors[dead]]))
  for side in list(sessions):
   if side!=dead:connect(dead,side)
  height(dead,2);check('a newly reconnected validator automatically replays the missed certified block',task(dead,'const s=await hostSessionCase.group.snapshot();return s.height===2&&s.state.messages.length===2&&s.pending.length===0;'))
  writer=ordered[2];queue(writer,'All four continue after automatic history repair')
  for side in sessions:height(side,3)
  check('all validators continue at the next height without resetting any accepted floor',all(task(side,'return (await hostSessionCase.group.snapshot()).state.messages.length===3;') for side in sessions))
  # Wait for the real short binding lifetime; no mocked clock or grant bypass.
  time.sleep(11)
  writer=ordered[3];d.wait(lambda:task(writer,'return (await hostSessionCase.group.validatorPeers()).length===0;'),15);check('expired native bindings lose authority while live transports and bounded discovery hints remain',task(writer,'const s=await hostSessionCase.stats();return s.network.peers.filter(p=>p.state==="ready").length===3&&s.network.deviceChannels.replicas.bindingHints===3;'));queue(writer,'Fresh link proofs renew expired validator bindings automatically')
  for side in sessions:height(side,4)
  check('actual short-lived binding expiry is recovered with fresh reciprocal proofs',all(task(side,'return (await hostSessionCase.group.validatorPeers()).length===3;') for side in sessions))
  faulty=ordered[3];task(faulty,'await hostSessionCase.falseRepair();return true;')
  for side in sessions:
   if side!=faulty:
    wait(side,'const s=hostSessionCase.owner().stats();return s.scheduler.jobs===0&&s.replicas.jobs===0&&s.replicas.pending===0;');task(side,'const p=(await hostSessionCase.group.validatorPeers()).find(p=>p.actor===params[0]);if(p)await hostSessionCase.group.bindValidator(p.peerId);return true;',[actors[faulty]])
  wait(faulty,'return hostSessionCase.badHistoryReads>0;');check('a higher peer counter and correctly transported invalid block cannot advance the local floor',all(task(side,'return (await hostSessionCase.group.snapshot()).height===4;') for side in sessions));js(faulty,'hostSessionCase.restoreFalseRepair();')
  for side in sessions:wait(side,'return hostSessionCase.owner().stats().scheduler.jobs===0;')
  wire=task(faulty,'return hostSessionCase.group.advanceView(1000000);');proxy=ordered[2];js(proxy,'hostSessionCase.copyPromise(arguments[0]);',[wire])
  learners=ordered[:2]
  for side in learners:
   wait(side,'const s=hostSessionCase.owner().stats();return s.scheduler.jobs===0&&s.replicas.jobs===0&&s.replicas.pending===0;');task(side,'const p=(await hostSessionCase.group.validatorPeers()).find(p=>p.actor===params[0]);if(p)await hostSessionCase.group.bindValidator(p.peerId);return true;',[actors[faulty]])
  wait(proxy,'return hostSessionCase.copiedPromiseReplies>=2;');check('one real future promise and its copy under another peer identity cannot satisfy distinct-signer view adoption',all(task(side,'return (await hostSessionCase.group.replicaStatus()).round===0;') for side in learners));js(proxy,'hostSessionCase.restoreCopiedPromise();')
  writer=ordered[2];queue(writer,'A single future-round voter cannot force the other validators to jump')
  for side in sessions:height(side,5)
  check('three honest voters complete normally despite an unsupported huge peer view',all(task(side,'return (await hostSessionCase.group.history({limit:1})).entries[0].block.header.round===0;') for side in sessions))
  cuts={}
  for side in sessions:
   other=[actors[x] for x in (ordered[2:] if side in ordered[:2] else ordered[:2])];cuts[side]=task(side,'return (await hostSessionCase.group.validatorPeers()).filter(p=>params[0].includes(p.actor)).map(p=>p.peerId);',[other])
  for side in sessions:js(side,'for(const id of arguments[0])desktopNetwork.appContext().pool.closeEntry(id);',[cuts[side]])
  writer=ordered[3];queue(writer,'The same saved original resumes after a two-against-two partition');pending=task(writer,'return (await hostSessionCase.group.snapshot()).pending[0];');time.sleep(3)
  check('an actual2by2 RTC partition preserves pending data without inventing an accepted quorum',all(task(side,'return (await hostSessionCase.group.snapshot()).height===5;') for side in sessions) and task(writer,'const p=(await hostSessionCase.group.snapshot()).pending[0];return p.id===params[0].id&&p.wire===params[0].wire;',[pending]))
  calc=js(writer,'return hostSessionCase.open("calculator");');wait(writer,'return !!hostSessionCase.node(arguments[0]).querySelector(".calculator-result");',[calc]);js(writer,'const n=hostSessionCase.node(arguments[0]).querySelector("input");n.value="6*7";n.form.requestSubmit();',[calc]);check('quorum loss leaves the unrelated actual Calculator usable',js(writer,'return hostSessionCase.node(arguments[0]).querySelector(".calculator-result").textContent==="42";',[calc]))
  for a in ordered[:2]:
   for b in ordered[2:]:connect(a,b)
  for side in sessions:height(side,6)
  check('after transport restoration automatic recovery accepts the original exactly once',all(task(side,'const s=await hostSessionCase.group.snapshot();return s.pending.length===0&&s.state.messages.length===6&&s.state.messages.at(-1).id===params[0].id;',[pending]) for side in sessions) and task(writer,'const h=await hostSessionCase.group.history({limit:1});return h.entries[0].block.operations[0].proposal===params[0].wire;',[pending]))
  for side in sessions:wait(side,'const s=hostSessionCase.owner().stats();return s.scheduler.jobs===0&&s.tasks===0&&s.replicas.tasks===0;')
  baseline=task(writer,'return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};')
  for i in range(30):
   window=js(writer,'return hostSessionCase.open("chat");');ready(writer,window);js(writer,'hostSessionCase.close(arguments[0]);',[window])
  wait(writer,'const s=hostSessionCase.owner().stats();return s.tasks===0&&s.scheduler.jobs===0&&s.replicas.tasks===0&&s.replicas.responses===0;')
  check('thirty real app reopens keep one automatic engine and return view accounting to the warm baseline',task(writer,'const s=hostSessionCase.owner().stats(),b=(await hostSessionCase.stats()).network.budget;return s.scheduler.channels===1&&s.views===params[0].owner.views&&b.metadataBytes===params[0].network.metadataBytes;',[baseline]))
  check('idle applications retain one timer per desktop and no active consensus work',all(task(side,'const s=await hostSessionCase.stats();return s.network.deviceChannels.scheduler.timers===1&&s.network.deviceChannels.scheduler.deadlines===0&&s.network.budget.consensusJobs===0&&s.network.budget.repairJobs===0;') for side in sessions))
  r['status']='PASS'

 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot()};')
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:
    r[side+'Cleanup']=task(side,'const result=await hostSessionCase.closeAll();result.automatic=hostSessionCase.owner().stats().scheduler;return result;');assert r[side+'Cleanup']['automatic']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0};budget=r[side+'Cleanup']['network'].get('budget',{})
    if any(v!=0 for k,v in budget.items() if k!='closed'):r.update(status='FAIL',error='App replica cleanup retained network charges',cleanupSide=side)
   except Exception as x:r.update(status='FAIL',error='Automatic round cleanup failed',cleanupSide=side);r[side+'CleanupError']=str(x)
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as x:r[side+'BrowserCleanupError']=str(x)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for profile in profiles.values():shutil.rmtree(profile)
  tmp.cleanup();r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists())
 r['elapsedSeconds']=round(time.monotonic()-started,3);return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
