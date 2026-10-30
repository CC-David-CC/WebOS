#!/usr/bin/env python3
"""Short allocation windows retain independent useful credits on delayed signed RTC paths.

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
def run(compiled=None):
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-byte-credit-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':6,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-byte-credit-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&inline=1&data=1&credits=1'});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
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
  if a=='never':js(a,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,send=link.channel.send.bind(link.channel);link.channel.send=wire=>{const parts=wire.split("."),body=parts.length===3?JSON.parse(atob(parts[1].replaceAll("-","+").replaceAll("_","/"))):null;if(!hostSessionCase.droppedHello&&body?.kind==="hello"){hostSessionCase.droppedHello=true;return;}return send(wire);};',[offer['peerId']])
  answer=task(b,'return hostSessionCase.view.answer(params[0]);',[offer['token']])
  if delay_signaling:js(a,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,rtc=link.rtc.bind(link);link.rtc=async(method,...args)=>{const value=await rtc(method,...args);if(method==="setRemoteDescription"){const until=performance.now()+10000;while(!(link.sentHello&&link.receivedHello)&&performance.now()<until)await new Promise(r=>setTimeout(r,10));hostSessionCase.delayedSignalingSawHello=link.sentHello&&link.receivedHello;}return value;};',[offer['peerId']])
  task(a,'return hostSessionCase.view.accept(params[0],params[1]);',[offer['peerId'],answer['token']]);wait(a,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[offer['peerId']]);wait(b,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[answer['peerId']]);r['actualRTCLinks']+=1
  if validator:bind(a,offer['peerId'],'bindValidator')
  return {a:offer['peerId'],b:answer['peerId']}
 def height(side,n):return d.wait(lambda:task(side,'return (await hostSessionCase.group.snapshot()).height===params[0];',[n]),75)
 def metrics(label):
  result={}
  for side in sessions:
   data=task(side,'const stats=await hostSessionCase.stats();return {wire:hostSessionCase.wireMeter,budget:stats.network.budget,peers:stats.network.peers.length,scheduler:hostSessionCase.owner().stats().scheduler,organization:hostSessionCase.owner().stats().peerOrganization[0]};');data['rendererHeap']=d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}});result[side]=data
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
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){f.wireMeter.bytes+=new TextEncoder().encode(wire).length;f.wireMeter.frames++;return measuredSend.call(this,wire);};')
  (folder/'bootstrap.js').write_text((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text().replace('windowMs:10000','windowMs:3000'));(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcdef':start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Byte credit actor "+params[0])).channel;',[side])
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Mixed device budgets",controller:params[0],validators:params[1],publicRead:true,publicWrite:true});return (await hostSessionCase.view.channels())[0];',[actors['a'],[actors[s] for s in 'abcd']])
  for side in 'bcdef':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  for i,side in enumerate('abcd'):
   for other in 'abcd'[i+1:]:connect(side,other,True)
  slow=connect('e','b');bind('e',slow['e']);fast=connect('f','c');bind('f',fast['f'])
  check('every real peer negotiates receiver-issued credits within the eight-capability limit',all(js(s,'return desktopNetwork.appContext().pool.list().filter(e=>e.established).every(e=>{const l=desktopNetwork.appContext().pool.get(e.id).link;return l.deviceCreditReady&&l.applications.length<=8;});') for s in sessions))
  task('a','return hostSessionCase.group.queue("chat",{text:"Initial certified budget message"});')
  for side in sessions:height(side,1)
  check('six native histories converge using real signed receive-credit controls',all(task(s,'return hostSessionCase.owner().stats().traffic.creditsIssued>0&&hostSessionCase.owner().stats().traffic.receivedBytes>0;') for s in sessions))
  def limits(side,**overrides):
   saved=task(side,'return hostSessionCase.view.savedChannel(params[0].channel);',[config]);base={'windowMs':3000,'uploadBytes':8388608,'downloadBytes':8388608,'serveBytes':8388608,'controlBytes':1048576};base.update(overrides);return task(side,'return hostSessionCase.group.setTrafficLimits(params[0],params[1]);',[base,saved['version']])
  # No clock injection or fake budget counters. Let an actual short window end.
  denied_before_pause=task('e','return hostSessionCase.owner().stats().traffic.creditsDenied;')
  limits('e',downloadBytes=0);time.sleep(10.4);before=task('e','return hostSessionCase.owner().stats().traffic.receivedBytes;')
  task('a','return hostSessionCase.group.queue("chat",{text:"Fast readers continue while one receiver is paused"});')
  for side in 'abcdf':height(side,2)
  check('zero download allowance leaves the slow reader at its prior native accepted floor',task('e','return (await hostSessionCase.group.snapshot()).height===1&&hostSessionCase.owner().stats().traffic.receivedBytes===params[0];',[before]))
  check('the paused receiver issues explicit zero-byte grants instead of downloading then dropping content',task('e','return hostSessionCase.owner().stats().traffic.creditsDenied>params[0];',[denied_before_pause]))
  # Delay application writes at the transport boundary, retaining genuine RTC,
  # signatures and native archives. This is injected delay, not WAN/3G proof.
  for side in ['e','b']:
   peer=slow[side];js(side,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,send=link.sendPacket.bind(link);link.sendPacket=async(...args)=>{await new Promise(r=>setTimeout(r,150));return send(...args);};',[peer])
  limits('e',downloadBytes=131072)
  task('a','return hostSessionCase.group.queue("chat",{text:"The fast path continues beside a delayed receiver"});')
  for side in 'abcdf':height(side,3)
  height('e',3)
  check('window refill repairs the delayed reader to the same certified head without replaying originals',task('e','const s=await hostSessionCase.group.snapshot();return s.state.messages.length===3&&new Set(s.state.messages.map(m=>m.id)).size===3&&s.pending.length===0;'))
  eSnap=task('e','return hostSessionCase.group.snapshot();');r['limitedReceiver']=eSnap['traffic'];check('allocated receive credits remain within the configured window allowance',eSnap['traffic']['allocated']['download']<=131072)
  ordinary=connect('f','e');bind('f',ordinary['f']);limits('e',serveBytes=0)
  check('serving can be paused without changing accepted membership or breaking local reads',task('f','const peer=desktopNetwork.appContext().pool.get(params[0]);try{await hostSessionCase.memberExchange.call(peer,params[1],"head",{});return false;}catch{return true;}',[ordinary['f'],config]) and task('e','return (await hostSessionCase.group.snapshot()).height===3;'))
  # A foreign transport cannot use another peer's valid grant. Capture a real
  # credit from f->e, then send it in a correctly signed b->e request.
  limits('e',serveBytes=8388608);js('f','const link=desktopNetwork.appContext().pool.get(arguments[0]).link,send=link.sendPacket.bind(link);link.sendPacket=(kind,text,...rest)=>{try{const a=JSON.parse(text);if(a.credit)hostSessionCase.capturedCredit=a.credit;}catch{}return send(kind,text,...rest);};',[ordinary['f']])
  d.wait(lambda:task('f','const peer=desktopNetwork.appContext().pool.get(params[0]);try{await hostSessionCase.memberExchange.call(peer,params[1],"head",{});return true;}catch{return false;}',[ordinary['f'],config]),15);foreign=js('f','return hostSessionCase.capturedCredit;');assert foreign
  js('b','const link=desktopNetwork.appContext().pool.get(arguments[0]).link,send=link.sendPacket.bind(link);link.sendPacket=(kind,text,...rest)=>{try{const a=JSON.parse(text);if(a.credit){a.credit=arguments[1];text=JSON.stringify(a);}}catch{}return send(kind,text,...rest);};',[slow['b'],foreign])
  task('b','const peer=desktopNetwork.appContext().pool.get(params[0]);try{await hostSessionCase.memberExchange.call(peer,params[1],"head",{});}catch{}return true;',[slow['b'],config]);wait('e','return desktopNetwork.appContext().pool.get(arguments[0]).link.closed;',[slow['e']])
  check('a correctly signed cross-link credit replay is rejected without advancing the native floor',task('e','return (await hostSessionCase.group.snapshot()).height===3&&hostSessionCase.owner().stats().traffic.rejected>0;'))
  # Apply actual allowance inputs and native CAS, then reopen this Chrome
  # profile to prove the limits (not session usage counters) remain saved.
  wait('f','return !hostSessionCase.node(arguments[0]).querySelector("[data-device-apply-allowance]").disabled;',[windows['f']]);js('f','const n=hostSessionCase.node(arguments[0]);n.querySelector("[data-device-allowance]").closest("details").open=true;for(const [key,value] of Object.entries({uploadBytes:2048,downloadBytes:4096,serveBytes:1024})){const f=n.querySelector("[data-device-quota="+key+"]");f.value=String(value);f.dispatchEvent(new Event("input",{bubbles:true}));}',[windows['f']]);click('f','[data-window="'+str(windows['f'])+'"] [data-device-apply-allowance]');d.wait(lambda:task('f','return (await hostSessionCase.view.savedChannel(params[0].channel)).trafficLimits?.downloadBytes===4194304;',[config]),15)
  check('the actual allowance form persists exact validated KiB values through native directory CAS',task('f','const s=await hostSessionCase.group.snapshot();return s.traffic.limits.uploadBytes===2097152&&s.traffic.limits.serveBytes===1048576;'))
  ownerActor=actors['f'];task('f','await hostSessionCase.closeAll();return true;');d.call('/session/'+sessions.pop('f'),method='DELETE');start('f');task('f','hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0].channel);return true;',[config]);check('fresh Chrome retains the author, accepted history and configured allowances',task('f','const s=await hostSessionCase.group.snapshot();return s.actor===params[0]&&s.height===3&&s.traffic.limits.downloadBytes===4194304&&s.traffic.allocated.download===0;',[ownerActor]))
  check('held scheduler work isolates other owners, preserves per-owner order and releases every lease',task('f','const {TrafficScheduler}=await import("./network/traffic-scheduler.mjs"),{sessionBudget}=await import("./network/resource-budget.mjs"),session={},scheduler=new TrafficScheduler(session),slow={},fast={},order=[];scheduler.register(slow);scheduler.register(fast);let release;const held=scheduler.submit(slow,"bulk",1000,()=>new Promise(r=>release=r)),queued=scheduler.submit(slow,"bulk",1000,()=>order.push("queued"));queued.catch(()=>{});const quick=scheduler.submit(fast,"interactive",1000,()=>order.push("fast"));await quick;const isolated=order.join() ==="fast"&&scheduler.stats().activeOwners===1&&sessionBudget(session).snapshot().queuedBytes===2000;scheduler.unregister(slow);const cancelled=await queued.then(()=>false,()=>true),retained=sessionBudget(session).snapshot().queuedBytes===1000;release();await held;scheduler.unregister(fast);await new Promise(r=>setTimeout(r,0));const budget=sessionBudget(session).snapshot();return isolated&&cancelled&&retained&&scheduler.stats().pendingJobs===0&&Object.entries(budget).every(([k,v])=>k==="closed"||v===0);'))
  check('credit controller isolates foreign nonces, disconnects control abuse and releases metadata (unit scope)',task('f','const {DeviceChannelBandwidth}=await import("./assets/desktop/device-history-host.mjs"),{sessionBudget}=await import("./network/resource-budget.mjs"),session={},resourceBudget=sessionBudget(session),pool={resourceBudget,attachDeviceTraffic(){},detachDeviceTraffic(){}},owner=new DeviceChannelBandwidth(pool),sent=[],link={closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async body=>sent.push(body)},good={id:"unit-good",link},bad={id:"unit-bad",link:{...link,close(){this.closed=true;}}},pins=params[0],limits={windowMs:60000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536};owner.register(pins.channel,pins.genesisHash,()=>limits);const job=owner.beforeSend(good,"device-channel-member/1",{op:"call",channel:pins.channel,genesisHash:pins.genesisHash},1024);job.catch(()=>{});while(!sent.length)await new Promise(r=>setTimeout(r,0));const grant={op:"grant",channel:pins.channel,genesisHash:pins.genesisHash,request_id:sent[0].request_id,credit:crypto.randomUUID().replaceAll("-",""),bytes:4096,validForMs:60000,retryAfterMs:60000};await owner.control(bad,grant,512);const isolated=owner.stats().pending===1;await owner.control(good,grant,512);const result=await job;for(let i=0;i<140&&!bad.link.closed;i++)await owner.control(bad,{...grant,request_id:crypto.randomUUID().replaceAll("-","")},512);const disconnected=bad.link.closed;owner.close();await owner.idle();return isolated&&disconnected&&result===grant.credit&&Object.entries(resourceBudget.snapshot()).every(([k,v])=>k==="closed"||v===0);',[config]))
  check('a grant expiring while its control send finishes refreshes once instead of reusing a settled wait (unit scope)',task('f','const {DeviceChannelBandwidth}=await import("./assets/desktop/device-history-host.mjs"),{sessionBudget}=await import("./network/resource-budget.mjs"),resourceBudget=sessionBudget({}),pool={resourceBudget,attachDeviceTraffic(){},detachDeviceTraffic(){}},pins=params[0];let clock=0,requests=0,owner;const peer={id:"unit-expiry",link:{closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async body=>{requests++;await owner.control(peer,{op:"grant",channel:pins.channel,genesisHash:pins.genesisHash,request_id:body.request_id,credit:String(requests).padStart(32,"0"),bytes:4096,validForMs:requests===1?2000:10000,retryAfterMs:1000},512);if(requests===1)clock=3000;}}};owner=new DeviceChannelBandwidth(pool,{clock:()=>clock});owner.register(pins.channel,pins.genesisHash,()=>({windowMs:60000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536}));const credit=await owner.beforeSend(peer,"device-channel-member/1",{op:"call",channel:pins.channel,genesisHash:pins.genesisHash},1024);owner.close();await owner.idle();return requests===2&&credit===String(2).padStart(32,"0")&&Object.entries(resourceBudget.snapshot()).every(([k,v])=>k==="closed"||v===0);',[config]))
  check('a receiver credit issued at a window boundary has a useful independent lease (unit scope)',task('f','const {DeviceChannelBandwidth}=await import("./assets/desktop/device-history-host.mjs"),{sessionBudget}=await import("./network/resource-budget.mjs"),resourceBudget=sessionBudget({}),pool={resourceBudget,attachDeviceTraffic(){},detachDeviceTraffic(){}},pins=params[0],sent=[];let clock=0;const peer={id:"unit-boundary",link:{closed:false,deviceCreditReady:true,deviceCreditCost:()=>512,sendDeviceCredit:async body=>sent.push(body)}},owner=new DeviceChannelBandwidth(pool,{clock:()=>clock,creditLifetimeMs:6000});owner.register(pins.channel,pins.genesisHash,()=>({windowMs:10000,uploadBytes:1048576,downloadBytes:1048576,serveBytes:1048576,controlBytes:65536}));owner.snapshot(pins.channel);clock=9999;await owner.control(peer,{op:"request",channel:pins.channel,genesisHash:pins.genesisHash,request_id:crypto.randomUUID().replaceAll("-",""),minBytes:1024,wantBytes:16384},512);const grant=sent[0],oldAllocation=owner.snapshot(pins.channel).allocated.download;clock=10001;const accepted=owner.receive(peer,"device-channel-member/1",{op:"call",channel:pins.channel,genesisHash:pins.genesisHash},grant.credit,1024),current=owner.snapshot(pins.channel).allocated.download;owner.close();await owner.idle();return grant.validForMs===6000&&oldAllocation===16384&&current===0&&accepted&&Object.entries(resourceBudget.snapshot()).every(([k,v])=>k==="closed"||v===0);',[config]))
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:
    cleanup=task(side,'await hostSessionCase.closeAll();return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};');r[side+'Cleanup']=cleanup;assert cleanup['owner']['traffic']['channels']==cleanup['owner']['traffic']['grants']==cleanup['owner']['traffic']['peers']==cleanup['owner']['traffic']['pending']==0;assert cleanup['owner']['peerOrganization']==[];assert cleanup['owner']['tasks']==0 and cleanup['owner']['members']['tasks']==0 and cleanup['owner']['members']['responses']==0 and cleanup['owner']['scheduler']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0};assert all(v==0 for k,v in cleanup['network'].items() if k!='closed')
   except Exception as e:r.update(status='FAIL',cleanupSide=side,cleanupError=str(e))
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r[side+'BrowserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for profile in profiles.values():shutil.rmtree(profile)
  tmp.cleanup();r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists(),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
