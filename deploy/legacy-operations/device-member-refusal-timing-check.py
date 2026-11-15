#!/usr/bin/env python3
"""Eight native browsers form bounded RTC neighbors, then a ninth joins and leaves.

Local-development identities, real Storage API/IDB/crypto/RTC and packaged apps;
explicit signaling, no v86/live activation/large-mesh or joint-membership claim.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=mod('member_driver',ROOT/'scripts/touch-preview-check.py');builder=mod('member_apps',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled=None,credits=False,production_cadence=False,trace_wakes=False):
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-member-peers-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':9,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits,'productionRoundCadence':production_cadence,'traceWakes':trace_wakes}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-member-peers-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&peers=1&inline=1&data=1'+('&credits=1' if credits else '')});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
  wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels],.storage-consent button:first-of-type:not(:disabled)");',[w])
  if not js(side,'return !!hostSessionCase.node(arguments[0]).querySelector("[data-device-channels]");',[w]):click(side,'[data-window="'+str(w)+'"] .storage-consent button')
  wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]");',[w]);js(side,'hostSessionCase.view=hostSessionCase.facades.get(arguments[0]);',[w])
 def bind(side,peer,method='bindMember'):
  # Setup retries only an idempotent, already-authorized binding after an
  # explicit busy refusal. Protocol negatives and saturation checks do not.
  def attempt():
   v=task(side,'try{await hostSessionCase.group[params[1]](params[0]);return {bound:true};}catch(error){if(error.code!=="unavailable")throw error;return {bound:false};}',[peer,method])
   if not v['bound']:r['setupBusyRefusals']=r.get('setupBusyRefusals',0)+1
   return v['bound']
  return d.wait(attempt,30)
 def connect(a,b,validator=False,delay_signaling=False):
  # Automatic introductions may finish a connection before this explicit seed
  # setup reaches it. Reuse that actual established path rather than racing it.
  remote=js(b,'return hostSessionCase.public().sid;');existing=js(a,'return desktopNetwork.appContext().pool.list().find(e=>e.peerId===arguments[0]&&!desktopNetwork.appContext().pool.get(e.id).link.closed)?.id;',[remote])
  if existing:
   wait(a,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[existing]);local=js(a,'return hostSessionCase.public().sid;');other=js(b,'return desktopNetwork.appContext().pool.list().find(e=>e.peerId===arguments[0]&&!desktopNetwork.appContext().pool.get(e.id).link.closed)?.id;',[local]);wait(b,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[other])
   if validator:bind(a,existing,'bindValidator')
   return {a:existing,b:other}
  offer=task(a,'return hostSessionCase.view.offer();')
  if a=='h':js(a,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,send=link.channel.send.bind(link.channel);link.channel.send=wire=>{const parts=wire.split("."),body=parts.length===3?JSON.parse(atob(parts[1].replaceAll("-","+").replaceAll("_","/"))):null;if(!hostSessionCase.droppedHello&&body?.kind==="hello"){hostSessionCase.droppedHello=true;return;}return send(wire);};',[offer['peerId']])
  answer=task(b,'return hostSessionCase.view.answer(params[0]);',[offer['token']])
  if delay_signaling:js(a,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,rtc=link.rtc.bind(link);link.rtc=async(method,...args)=>{const value=await rtc(method,...args);if(method==="setRemoteDescription"){const until=performance.now()+10000;while(!(link.sentHello&&link.receivedHello)&&performance.now()<until)await new Promise(r=>setTimeout(r,10));hostSessionCase.delayedSignalingSawHello=link.sentHello&&link.receivedHello;}return value;};',[offer['peerId']])
  task(a,'return hostSessionCase.view.accept(params[0],params[1]);',[offer['peerId'],answer['token']]);wait(a,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[offer['peerId']]);wait(b,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[answer['peerId']]);r['actualRTCLinks']+=1
  if validator:bind(a,offer['peerId'],'bindValidator')
  return {a:offer['peerId'],b:answer['peerId']}
 def height(side,n):return d.wait(lambda:task(side,'return (await hostSessionCase.group.snapshot()).height===params[0];',[n]),75)
 def metrics(label):
  result={}
  for side in sessions:
   data=task(side,'const stats=await hostSessionCase.stats();return {wire:hostSessionCase.wireMeter,wakeTrace:hostSessionCase.wakeTrace,coreTrace:hostSessionCase.coreTrace,runtime:hostSessionCase.lastRuntime?{version:hostSessionCase.lastRuntime.version,dueMs:hostSessionCase.lastRuntime.next-performance.now(),phase:hostSessionCase.lastRuntime.phase}:null,rpcProfile:hostSessionCase.rpcProfile,budget:stats.network.budget,peers:stats.network.peers.length,scheduler:hostSessionCase.owner().stats().scheduler,organization:hostSessionCase.owner().stats().peerOrganization[0]};');data['rendererHeap']=d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}});result[side]=data
  r.setdefault('measurements',{})[label]={'elapsedSeconds':round(time.monotonic()-started,3),'participants':result,'scope':'Exact signed RTCDataChannel sent payload bytes/frames since startup; native renderer heap via CDP without forced GC; shared policy accounting. Excludes ICE/TURN/UDP/browser-process RAM and v86.'}
 def permission(actor,read,write,n):
  # Actual first-party controller buttons create the pending permission operation.
  js('a','const n=hostSessionCase.node(arguments[0]);n.querySelector("[data-device-connection-in]").closest("details").open=true;n.querySelector("[data-device-member-subject]").value=arguments[1];',[windows['a'],actor]);selector='[data-device-allow-write]' if write else '[data-device-allow-read]' if read else '[data-device-remove-access]';wait('a','return !hostSessionCase.node(arguments[0]).querySelector(arguments[1]).disabled;',[windows['a'],selector]);click('a','[data-window="'+str(windows['a'])+'"] '+selector)
  for side in 'abcd':height(side,n)
 try:
  assets=folder/'assets/desktop';assets.mkdir(parents=True);r['appBuild']=builder.build(ROOT.parent/'served_apps_public',assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['appCatalogSHA256']=hashlib.sha256((assets/'apps.json').read_bytes()).hexdigest();files={str(p.relative_to(ROOT)) for p in (ROOT/'assets/desktop').glob('*.mjs')};files.update(str(p.relative_to(ROOT)) for p in (ROOT/'network').glob('*.mjs'));files.update(['networking.js','desktop-apps.js','assets/vendor/chess/chess.mjs','scripts/fixtures/device-session-page.mjs','scripts/fixtures/device-session-bootstrap.js']);r['sourceSHA256']={}
  for n in sorted(files):
   data=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(data).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  source=(ROOT/'networking.js').read_text();assert source.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(source.replace('const disabled=true;','const disabled=false;'));fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text()
  if compiled:
   c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];assert len(c['apps'])==1;src=compiled/Path(app['path']).parent.relative_to('assets/desktop');raw=(src/'index.mjs').read_bytes();assert hashlib.sha256(raw).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(raw);r['actualCompiledCoreSHA256']=app['sha256']
   for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
   for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  fixture+='\nconst profiledCall=DeviceReplicaExchange.prototype.call;hostSessionCase.rpcProfile={};DeviceReplicaExchange.prototype.call=function(entry,pins,method,value,options){const role=this.stats().profile,key=[role,method,method===\"status\"?(value?.brief===true?\"brief\":\"full\"):null].filter(Boolean).join(\"/\"),rows=hostSessionCase.rpcProfile,bounded=Object.hasOwn(rows,key)||Object.keys(rows).length<64?key:\"other\",row=rows[bounded]??={calls:0,success:0,failed:0,inputBytes:0,outputBytes:0};row.calls++;row.inputBytes+=new TextEncoder().encode(JSON.stringify(value)).length;const task=profiledCall.call(this,entry,pins,method,value,options);task.then(result=>{row.success++;row.outputBytes+=new TextEncoder().encode(JSON.stringify(result)).length;},()=>row.failed++);return task;};\n';
  if trace_wakes:
   fixture=fixture.replace('const f=window.hostSessionCase;',"const f=window.hostSessionCase;f.wakeTrace=[];const {DeviceReplicaScheduler}=await import('./assets/desktop/device-history-host.mjs');f.coreTrace=[];const maintain=DeviceReplicaRound.prototype.maintain;DeviceReplicaRound.prototype.maintain=async function(runtime,...args){f.lastRuntime=runtime;const before={at:Math.round(performance.now()),version:runtime.version,next:runtime.next,phase:runtime.phase};try{const result=await maintain.call(this,runtime,...args);f.coreTrace.push({...before,ended:Math.round(performance.now()),versionAfter:runtime.version,result});if(f.coreTrace.length>64)f.coreTrace.shift();return result;}catch(e){throw e;}};const observedWake=DeviceReplicaScheduler.prototype.wake;DeviceReplicaScheduler.prototype.wake=function(channel,...args){f.lastScheduler=this;f.wakeTrace.push({channel,at:Math.round(performance.now()),stack:new Error().stack.slice(0,2200)});if(f.wakeTrace.length>64)f.wakeTrace.shift();return observedWake.call(this,channel,...args);};")
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0,categories:{}};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){const bytes=new TextEncoder().encode(wire).length;f.wireMeter.bytes+=bytes;f.wireMeter.frames++;let key="unparsed";try{const payload=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(wire.split(".")[1].replaceAll("-","+").replaceAll("_","/")),c=>c.charCodeAt(0)))),body=payload.kind==="application"?JSON.parse(payload.text):null;key=[payload.kind,body?.mode,body?.body?.op,body?.body?.method].filter(Boolean).join("/").slice(0,160);}catch{}if(!Object.hasOwn(f.wireMeter.categories,key)&&Object.keys(f.wireMeter.categories).length>=64)key="other";const row=f.wireMeter.categories[key]??={bytes:0,frames:0};row.bytes+=bytes;row.frames++;return measuredSend.call(this,wire);};')
  bootstrap=(ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text()
  if production_cadence:
   accelerated='{tickMs:200,idleMs:30000,viewMs:2000,maxViewMs:16000,rpcMs:750,stepMs:12000}';assert bootstrap.count(accelerated)==1;bootstrap=bootstrap.replace(accelerated,'{}');r['roundCadenceScope']='Default production scheduler settings (tick1000ms/step60000ms); other fixture topology/10s byte windows/6s credits remain explicit QA settings.'
  (folder/'bootstrap.js').write_text(bootstrap);(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcdefgh':start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Automatic peer actor "+params[0])).channel;',[side])
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Bounded automatic member mesh",controller:params[0],validators:params[1],publicRead:true,publicWrite:true});return (await hostSessionCase.view.channels())[0];',[actors['a'],[actors[s] for s in 'abcd']])
  for side in 'bcdefgh':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  for side in 'bcd':connect(side,'a',True)
  d.wait(lambda:all(task(s,'return (await hostSessionCase.group.validatorPeers()).length===3;') for s in 'abcd'),120)
  links={}
  for a in 'efgh':
   # Explicit seed setup honors already admitted automatic work. Always choose
   # a least-loaded validator rather than assuming its initial slot stayed free.
   b=min('abcd',key=lambda side:task(side,'return hostSessionCase.owner().stats().peerOrganization[0].admissions??hostSessionCase.owner().stats().peerOrganization[0].neighbors;'))
   links[a]=connect(a,b);bind(a,links[a][a])
  check('an intentionally missing initial hello recovers through bounded negotiated handshake retries',js('h','return hostSessionCase.droppedHello===true;') and any(task(s,'return desktopNetwork.appContext().pool.list().some(p=>desktopNetwork.appContext().pool.get(p.id).link.helloRetries>0);') for s in sessions))
  check('eight native sessions start from four validator paths and four explicit leaf seeds',all(task(s,'return hostSessionCase.owner().stats().peerOrganization[0].maxNeighbors===6;') for s in sessions))
  d.wait(lambda:all(task(s,'const p=hostSessionCase.owner().stats().peerOrganization[0];return p.connected>0&&p.neighbors>=2;') for s in 'efgh'),120)
  snapshots={s:task(s,'return hostSessionCase.owner().stats().peerOrganization[0];') for s in sessions};r['afterIntroductions']=snapshots;metrics('eightIntroduced')
  check('each ordinary leaf establishes another real peer without fixture signaling or binding for that peer',all(snapshots[s]['connected']>0 and snapshots[s]['neighbors']>=2 for s in 'efgh'))
  check('automatic neighbors stay bounded rather than creating the full eight-node mesh',all(v['neighbors']<=6 and v['pending']<=2 and v['contacts']<=32 for v in snapshots.values()) and sum(v['neighbors'] for v in snapshots.values())<56)
  for side in sessions:task(side,'const saved=await hostSessionCase.view.savedChannel(params[0].channel);return hostSessionCase.group.setTrafficProfile("limited",saved.version);',[config])
  check('low-data preferences are independent durable metadata for this device channel',all(task(s,'return (await hostSessionCase.view.savedChannel(params[0].channel)).trafficProfile==="limited"&&(await hostSessionCase.group.snapshot()).trafficProfile==="limited";',[config]) for s in sessions))
  for name,ok in task('e','return hostSessionCase.contactCases();'):check(name,ok)
  source=next(s for s in 'efgh' if js(s,'return hostSessionCase.introductions.some(p=>p.answered&&!p.entry.link.closed); '))
  replay=task(source,'return hostSessionCase.replayIntroduction();');r['replayAttempt']=replay;check('an otherwise fresh signed introduction cannot reuse an already completed nonce',replay['refused'] and any(js(s,'return hostSessionCase.topologyFailures.some(v=>v.request===arguments[0]&&v.error==="Introduction nonce already used");',[replay['request']]) for s in sessions))
  task('a','return hostSessionCase.group.queue("chat",{text:"Certified content crosses automatically introduced member paths"});')
  for side in sessions:height(side,1)
  check('all eight archives converge through accepted history using shared peer transports',all(task(s,'const v=await hostSessionCase.group.snapshot();return v.state.messages.length===1&&v.pending.length===0;') for s in sessions))
  wait('e','const s=hostSessionCase.owner().stats(),b=desktopNetwork.appContext().pool.resourceBudget.snapshot();return b.repairJobs===0&&s.scheduler.jobs===0;')
  check('saturated network-repair slots leave native app snapshots readable',task('e','const budget=desktopNetwork.appContext().pool.resourceBudget,leases=[];try{while(budget.snapshot().repairJobs<budget.limits().repairJobs)leases.push(budget.slot("repairJobs"));const used=budget.snapshot().repairJobs,s=await hostSessionCase.group.snapshot();return s.height===1&&used===budget.limits().repairJobs;}finally{for(const release of leases)release();}'))
  # Remove an ordinary leaf seed, preserving its automatically introduced paths.
  task('e','desktopNetwork.appContext().pool.closeEntry(params[0]);return true;',[links['e']['e']])
  for side in sessions:js(side,'hostSessionCase.rejectNextMemberHeadFor=arguments[0];',[actors['e']])
  task('a','return hostSessionCase.group.queue("chat",{text:"A lost seed is repaired through the remaining member graph"});')
  for side in sessions:height(side,2)
  check('acknowledged update hints survive temporary provider refusal without waiting for the five-minute idle poll',sum(js(s,'return hostSessionCase.rejectedMemberHeads||0;') for s in sessions)>0)
  check('an ordinary member retains catch-up after its explicit seed connection is closed',task('e','const s=await hostSessionCase.group.snapshot();return s.height===2&&s.state.messages.length===2;'))
  target=next(s for s in 'bcdefgh' if task(s,'return (await hostSessionCase.group.memberPeers()).some(p=>p.actor===params[0]);',[actors['a']]));peer=task(target,'return (await hostSessionCase.group.memberPeers()).find(p=>p.actor===params[0]).peerId;',[actors['a']]);before=task(target,'return hostSessionCase.owner().stats().peerOrganization[0].rejected;');js('a','hostSessionCase.poisonContacts=true;');refused=task(target,'try{await hostSessionCase.group.refreshPeers(params[0]);return false;}catch{return true;}',[peer]);js('a','hostSessionCase.poisonContacts=false;');assert refused and task(target,'return hostSessionCase.owner().stats().peerOrganization[0].rejected>params[0];',[before])
  check('a signed transport carrying a forged contact is refused without changing accepted state',all(task(s,'return (await hostSessionCase.group.snapshot()).height===2;') for s in sessions))
  def fully_idle(side,scheduled=True):
   return task(side,'const snapshot=await hostSessionCase.group.snapshot(),stats=hostSessionCase.owner().stats(),p=stats.peerOrganization[0],budget=desktopNetwork.appContext().pool.resourceBudget.snapshot();return p.healthy&&p.pending===0&&p.jobs===0&&stats.scheduler.jobs===0&&snapshot.automation.active===false&&snapshot.pending.length===0&&stats.tasks===0&&[stats.members,stats.replicas].every(v=>v.pending===0&&v.jobs===0&&v.tasks===0&&v.responses===0&&v.preflights===0&&v.bindingJobs===0)&&(!stats.traffic||stats.traffic.pending===0&&stats.traffic.jobs===0)&&budget.queuedBytes===0&&budget.crypto===0&&budget.consensusJobs===0&&budget.repairJobs===0&&(!params[0]||!hostSessionCase.lastRuntime||hostSessionCase.lastRuntime.next>performance.now()&&hostSessionCase.coreTrace.at(-1).version===hostSessionCase.lastRuntime.version);',[scheduled])
  d.wait(lambda:all(fully_idle(s) for s in sessions),90)
  if trace_wakes:
   r['queuedWakeEntrance']=task('a','const snapshot=await hostSessionCase.group.snapshot(),stats=hostSessionCase.owner().stats(),p=stats.peerOrganization[0],budget=desktopNetwork.appContext().pool.resourceBudget.snapshot();const old=p.healthy&&p.pending===0&&p.jobs===0&&stats.scheduler.jobs===0&&snapshot.automation.active===false&&snapshot.pending.length===0&&stats.tasks===0&&[stats.members,stats.replicas].every(v=>v.pending===0&&v.jobs===0&&v.tasks===0&&v.responses===0&&v.preflights===0&&v.bindingJobs===0)&&(!stats.traffic||stats.traffic.pending===0&&stats.traffic.jobs===0)&&budget.queuedBytes===0&&budget.crypto===0&&budget.consensusJobs===0&&budget.repairJobs===0;hostSessionCase.lastScheduler.wake(hostSessionCase.group.channel);const runtime=hostSessionCase.lastRuntime,last=hostSessionCase.coreTrace.at(-1);return {oldPredicate:old,strictPredicate:old&&runtime.next>performance.now()&&last.version===runtime.version,dueMs:runtime.next-performance.now(),lastVersion:last.version,currentVersion:runtime.version};')
   check('the idle entrance refuses a real queued native wake that the older no-active-job predicate misses',r['queuedWakeEntrance']['oldPredicate'] and not r['queuedWakeEntrance']['strictPredicate'])
   d.wait(lambda:all(fully_idle(s) for s in sessions),90)
  r['idleEntryScope']='No owner/member/replica/credit/consensus/transport work, no pending originals, inactive native automation, healthy bounded topology; same20s/4096signed-byte oracle; traced validators also drain due/version-mismatched queued wakes, with an explicit actual-wake negative entrance probe.'
  metrics('lowDataIdleStart');time.sleep(20);metrics('lowDataIdleEnd');idleBefore=r['measurements']['lowDataIdleStart'];idleAfter=r['measurements']['lowDataIdleEnd'];r['idleWindow']={'seconds':round(idleAfter['elapsedSeconds']-idleBefore['elapsedSeconds'],3),'payloadBytes':sum(idleAfter['participants'][s]['wire']['bytes']-idleBefore['participants'][s]['wire']['bytes'] for s in sessions),'scope':'Signed application payload only; excludes ICE/DTLS/TURN headers, periodic checks beyond this window, HTTP/assets and v86.'}
  check('idle application traffic is measured over the twenty-second window',r['idleWindow']['seconds']>=20 and r['idleWindow']['payloadBytes']>=0)
  attack=task('e','return hostSessionCase.badInlineRead();');victim=next(s for s in sessions if js(s,'return hostSessionCase.public().sid;')==attack['to']);check('a correctly signed RPC with a tampered inline value fails its scoped hash before reading content',attack['changed'] and attack['refused'] and task(victim,'return hostSessionCase.owner().stats().members.inlineRejected>0;'))
  metrics('burstStart')
  burst=["Ordered low-data batch message "+str(i) for i in range(8)];task('a','for(const text of params[0])await hostSessionCase.group.queue("chat",{text});return true;',[burst])
  for side in sessions:height(side,3)
  metrics('burstAccepted')
  check('eight queued messages share one certified block and retain their durable send order',all(task(s,'const v=await hostSessionCase.group.snapshot(),h=await hostSessionCase.group.history({limit:1});return v.pending.length===0&&JSON.stringify(v.state.messages.slice(-8).map(m=>m.text))===JSON.stringify(params[0])&&h.entries[0].block.operations.length===8;',[burst]) for s in sessions))
  for side in sessions:wait(side,'const p=hostSessionCase.owner().stats().peerOrganization[0];return p.pending===0&&p.jobs===0;',seconds=60)
  final={s:task(s,'return hostSessionCase.owner().stats().peerOrganization[0];') for s in sessions};r['afterSeedLoss']=final;metrics('eightAfterSeedLoss')
  check('replacement work returns to bounded idle state without new per-app engines',all(v['neighbors']<=6 and v['pending']==0 and v['timers']==0 for v in final.values()))
  ordinaryWriter=next(s for s in 'efgh' if task(s,'return (await hostSessionCase.group.memberPeers()).some(p=>params[0].includes(p.actor));',[[actors[x] for x in 'abcd']]));ordinaryBurst=["Ordinary mobile sender batch "+str(i) for i in range(4)];
  for side in 'abcd':js(side,'hostSessionCase.rejectNextMemberSubmitFor=arguments[0];',[actors[ordinaryWriter]])
  task(ordinaryWriter,'for(const text of params[0])await hostSessionCase.group.queue("chat",{text});return true;',[ordinaryBurst])
  for side in sessions:height(side,4)
  for side in sessions:d.wait(lambda:task(side,'const s=await hostSessionCase.group.snapshot();return s.pending.length===0&&params[0].every(text=>s.state.messages.some(m=>m.text===text));',[ordinaryBurst]),90)
  timing=task(ordinaryWriter,'return hostSessionCase.owner().stats().peerOrganization[0].memberTiming;');r['controlledRefusalTiming']=timing;r['validatorTiming']={side:task(side,'return hostSessionCase.owner().stats().peerOrganization[0];') for side in 'abcd'};check('a direct refusal triggers measured reconciliation before retry',any(x['event']=='refusal-sync-start' for x in timing) and any(x['event'] in ('refusal-sync-advanced','refusal-sync-unchanged','refusal-sync-failed') for x in timing))
  check('all four originals survive a controlled validator refusal',all(task(s,'const v=await hostSessionCase.group.snapshot(),h=await hostSessionCase.group.history({limit:1});return v.pending.length===0&&JSON.stringify(v.state.messages.slice(-4).map(m=>m.text))===JSON.stringify(params[0]);',[ordinaryBurst,actors[ordinaryWriter]]) for s in sessions))
  accepted=task('a','return hostSessionCase.group.snapshot();');base_height=accepted['height'];base_head=accepted['head']
  # A fresh ninth participant needs just one explicit seed, not every peer.
  start('i');actors['i']=task('i','return (await hostSessionCase.view.createIdentity("Late ordinary participant")).channel;');task('i','hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors['i']]);seed=next(s for s in 'efgh' if task(s,'return hostSessionCase.owner().stats().peerOrganization[0].neighbors<6;'));joined=connect('i',seed);bind('i',joined['i']);height('i',base_height)
  wait('i','const p=hostSessionCase.owner().stats().peerOrganization[0];return p.connected>0&&p.neighbors>=2;',seconds=90)
  check('a ninth native participant catches up from one ordinary seed and introduces its own extra peer',task('i','const p=hostSessionCase.owner().stats().peerOrganization[0],s=await hostSessionCase.group.snapshot();return s.head===params[0]&&!s.validator&&p.connected>0&&p.neighbors>=2&&p.neighbors<=6;',[base_head]))
  task('a','return hostSessionCase.group.queue("chat",{text:"New and existing peers continue after a late participant joins"});')
  for side in sessions:height(side,base_height+1)
  check('late join and existing members converge the next certified update together',all(task(s,'return (await hostSessionCase.group.snapshot()).state.messages.length===15;') for s in sessions))
  wait('i','return !hostSessionCase.node(arguments[0]).querySelector("[data-device-traffic]").disabled;',[windows['i']]);js('i','const select=hostSessionCase.node(arguments[0]).querySelector("[data-device-traffic]");select.value="fast";select.dispatchEvent(new Event("change",{bubbles:true}));',[windows['i']]);d.wait(lambda:task('i','return (await hostSessionCase.group.snapshot()).trafficProfile==="fast";'),15)
  check('one participant can select low latency while the same group stays low-data on other devices',all(task(s,'return (await hostSessionCase.group.snapshot()).trafficProfile==="limited";') for s in sessions if s!='i'))
  metrics('nineAfterJoin')
  r['iCleanup']=task('i','await hostSessionCase.closeAll();return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};');assert all(v==0 for k,v in r['iCleanup']['network'].items() if k!='closed');d.call('/session/'+sessions.pop('i'),method='DELETE')
  start('i');task('i','hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0].channel);return true;',[config]);check('a fresh Chrome process retains the same author, accepted floor and channel traffic preference',task('i','const s=await hostSessionCase.group.snapshot();return s.actor===params[0]&&s.height===params[1]&&s.trafficProfile==="fast";',[actors['i'],base_height+1]));task('i','await hostSessionCase.closeAll();return true;');d.call('/session/'+sessions.pop('i'),method='DELETE')
  task('a','return hostSessionCase.group.queue("chat",{text:"Remaining peers continue after a participant leaves"});')
  for side in sessions:height(side,base_height+2)
  check('participant departure preserves accepted history and the remaining bounded graph',all(task(s,'const p=hostSessionCase.owner().stats().peerOrganization[0],s=await hostSessionCase.group.snapshot();return s.height===params[0]&&s.state.messages.length===16&&p.neighbors<=6;',[base_height+2]) for s in sessions))
  metrics('eightAfterDeparture')
  r['fixtureSignaledRTCLinks']=r['actualRTCLinks'];seen=set()
  for side in sessions:seen.update(task(side,'return desktopNetwork.appContext().pool.list().filter(p=>desktopNetwork.appContext().pool.get(p.id).established).map(p=>p.connectionId);'))
  r['actualRTCLinks']=len(seen);r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,wakeTrace:hostSessionCase.wakeTrace,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:
    cleanup=task(side,'await hostSessionCase.closeAll();return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};');r[side+'Cleanup']=cleanup;assert cleanup['owner']['peerOrganization']==[];assert cleanup['owner']['tasks']==0 and cleanup['owner']['members']['tasks']==0 and cleanup['owner']['members']['responses']==0 and cleanup['owner']['scheduler']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0};assert all(v==0 for k,v in cleanup['network'].items() if k!='closed')
   except Exception as e:r.update(status='FAIL',cleanupSide=side,cleanupError=str(e))
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r[side+'BrowserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for profile in profiles.values():shutil.rmtree(profile)
  tmp.cleanup();r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists(),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--credits',action='store_true');p.add_argument('--production-cadence',action='store_true');p.add_argument('--trace-wakes',action='store_true');p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core,a.credits,a.production_cadence,a.trace_wakes);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
