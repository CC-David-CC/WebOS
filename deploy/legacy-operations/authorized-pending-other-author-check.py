#!/usr/bin/env python3
"""Verify automatic unconfirmed peer gossip across real browser RTC links and restart.

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
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-member-peers-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':3,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits,'productionRoundCadence':production_cadence,'traceWakes':trace_wakes}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-member-peers-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&inline=1&data=1'+('&credits=1' if credits else '')});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
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
  assets=folder/'assets/desktop';assets.mkdir(parents=True);r['appBuild']=builder.build(ROOT/'served_apps_public',assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['appCatalogSHA256']=hashlib.sha256((assets/'apps.json').read_bytes()).hexdigest();files={str(p.relative_to(ROOT)) for p in (ROOT/'assets/desktop').glob('*.mjs')};files.update(str(p.relative_to(ROOT)) for p in (ROOT/'network').glob('*.mjs'));files.update(['networking.js','desktop-apps.js','assets/vendor/chess/chess.mjs','scripts/fixtures/device-session-page.mjs','scripts/fixtures/device-session-bootstrap.js']);r['sourceSHA256']={}
  for n in sorted(files):
   data=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(data).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  source=(ROOT/'networking.js').read_text();assert source.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(source.replace('const disabled=true;','const disabled=false;'));fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text().replace("['notice','head']","['notice','head','relay-submit']").replace("['notice','node','head']","['notice','node','head','relay-submit']")
  if compiled:
   c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];assert len(c['apps'])==1;src=compiled/Path(app['path']).parent.relative_to('assets/desktop');raw=(src/'index.mjs').read_bytes();assert hashlib.sha256(raw).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(raw);r['actualCompiledCoreSHA256']=app['sha256']
   if (src/'chunks').exists():shutil.copytree(src/'chunks',assets/'chunks')
   for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
   for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  fixture+='\nconst profiledCall=DeviceReplicaExchange.prototype.call;hostSessionCase.rpcProfile={};DeviceReplicaExchange.prototype.call=function(entry,pins,method,value,options){const role=this.stats().profile,key=[role,method,method===\"status\"?(value?.brief===true?\"brief\":\"full\"):null].filter(Boolean).join(\"/\"),rows=hostSessionCase.rpcProfile,bounded=Object.hasOwn(rows,key)||Object.keys(rows).length<64?key:\"other\",row=rows[bounded]??={calls:0,success:0,failed:0,inputBytes:0,outputBytes:0};row.calls++;row.inputBytes+=new TextEncoder().encode(JSON.stringify(value)).length;const task=profiledCall.call(this,entry,pins,method,value,options);task.then(result=>{row.success++;row.outputBytes+=new TextEncoder().encode(JSON.stringify(result)).length;},()=>row.failed++);return task;};\n';
  if trace_wakes:
   fixture=fixture.replace('const f=window.hostSessionCase;',"const f=window.hostSessionCase;f.wakeTrace=[];const {DeviceReplicaScheduler}=await import('./assets/desktop/device-history-host.mjs');f.coreTrace=[];const maintain=DeviceReplicaRound.prototype.maintain;DeviceReplicaRound.prototype.maintain=async function(runtime,...args){f.lastRuntime=runtime;const before={at:Math.round(performance.now()),version:runtime.version,next:runtime.next,phase:runtime.phase};try{const result=await maintain.call(this,runtime,...args);f.coreTrace.push({...before,ended:Math.round(performance.now()),versionAfter:runtime.version,result});if(f.coreTrace.length>64)f.coreTrace.shift();return result;}catch(e){throw e;}};const observedWake=DeviceReplicaScheduler.prototype.wake;DeviceReplicaScheduler.prototype.wake=function(channel,...args){f.lastScheduler=this;f.wakeTrace.push({channel,at:Math.round(performance.now()),stack:new Error().stack.slice(0,2200)});if(f.wakeTrace.length>64)f.wakeTrace.shift();return observedWake.call(this,channel,...args);};")
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0,categories:{}};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){const bytes=new TextEncoder().encode(wire).length;f.wireMeter.bytes+=bytes;f.wireMeter.frames++;let key="unparsed";try{const payload=JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(wire.split(".")[1].replaceAll("-","+").replaceAll("_","/")),c=>c.charCodeAt(0)))),body=payload.kind==="application"?JSON.parse(payload.text):null;key=[payload.kind,body?.mode,body?.body?.op,body?.body?.method].filter(Boolean).join("/").slice(0,160);}catch{}if(!Object.hasOwn(f.wireMeter.categories,key)&&Object.keys(f.wireMeter.categories).length>=64)key="other";const row=f.wireMeter.categories[key]??={bytes:0,frames:0};row.bytes+=bytes;row.frames++;return measuredSend.call(this,wire);};')
  bootstrap=(ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text().replace('maxChannels:1,','maxChannels:1,experimentalPendingSharing:true,')
  if production_cadence:
   accelerated='{tickMs:200,idleMs:30000,viewMs:2000,maxViewMs:16000,rpcMs:750,stepMs:12000}';assert bootstrap.count(accelerated)==1;bootstrap=bootstrap.replace(accelerated,'{}');r['roundCadenceScope']='Default production scheduler settings (tick1000ms/step60000ms); other fixture topology/10s byte windows/6s credits remain explicit QA settings.'
  (folder/'bootstrap.js').write_text(bootstrap);(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abc':start(side)
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Offline author proof",publicRead:true,publicWrite:true});return (await hostSessionCase.view.channels())[0];')
  for side in 'bc':task(side,'const actor=(await hostSessionCase.view.createIdentity("Offline actor")).channel;hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],actor);return true;',[config])
  ab=connect('a','b');bind('b',ab['b']);bc=connect('b','c');bind('c',bc['c'])
  author=js('c','return hostSessionCase.group.actor;');owner=js('a','return hostSessionCase.group.actor;')
  task('a','return hostSessionCase.closeAll();');d.call('/session/'+sessions.pop('a'),method='DELETE')
  record=task('c','''const saved=await hostSessionCase.group.queue("chat",{text:"Author gone before validator"}),pending=(await hostSessionCase.group.pending()).find(x=>x.id===saved.id),permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),A=await import("./assets/desktop/channel-archive.mjs"),vault=await new K.DeviceChannelKeys().open(permit),keys={get:(c,o)=>vault.get(scope,c,o),sign:(c,p,b,o)=>vault.sign(scope,c,p,b,o)},archive=await new A.DeviceChannelArchive({...params[0],keys,scope,actor}).open(permit);try{return await archive.record(pending.wire);}finally{archive.close();vault.close();}''',[config])
  check('author signs a complete record before going offline',bool(record.get('authorization') and record.get('proposal')))
  task('b','''const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),A=await import("./assets/desktop/channel-archive.mjs"),S=await import("./assets/desktop/authorized-pending-store.mjs"),M=await import("./network/device-member-channel.mjs");window.recordVault=await new K.DeviceChannelKeys().open(permit);const keys={get:(c,o)=>recordVault.get(scope,c,o),sign:(c,p,b,o)=>recordVault.sign(scope,c,p,b,o)};window.recordArchive=await new A.DeviceChannelArchive({...params[0],keys,scope,actor}).open(permit);window.recordStore=await new S.AuthorizedPendingStore({archive:recordArchive,scope,viewer:actor}).open(permit);const old=M.DeviceMemberChannel.prototype.invoke;M.DeviceMemberChannel.prototype.invoke=async function(method,value,options){if(method==="relay-submit"&&value.path.length===1)return recordStore.put(value.record,{signal:options.signal});return old.call(this,method,value,options);};return true;''',[config])
  check('forged authorization is rejected before storage',task('b','const E=await import("./network/experimental-authorized-pending.mjs"),r=structuredClone(params[0]),p=r.authorization.split(".");p[2]=(p[2][0]==="A"?"B":"A")+p[2].slice(1);r.authorization=p.join(".");try{await E.verifyAuthorizedPending(r,{archive:recordArchive,viewer:hostSessionCase.group.actor});return false;}catch{return true;}',[record]))
  stored=task('c','return hostSessionCase.memberExchange.call(desktopNetwork.appContext().pool.get(params[0]),params[1],"relay-submit",{record:params[2],path:[hostSessionCase.group.actor]});',[bc['c'],config,record]);check('reader stores the signed record received over actual RTC',stored['status']=='stored-unconfirmed')
  duplicate=task('c','return hostSessionCase.memberExchange.call(desktopNetwork.appContext().pool.get(params[0]),params[1],"relay-submit",{record:params[2],path:[hostSessionCase.group.actor]});',[bc['c'],config,record]);check('duplicate record delivery is idempotent',duplicate['status']=='already-stored')
  alternate=task('c','''const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),vault=await new K.DeviceChannelKeys().open(permit);try{const proof=await K.verifyDeviceChannelProof(params[0].authorization,{channel:actor,purpose:"operation"}),authorization=await vault.sign(scope,actor,"operation",proof.body);return {...params[0],authorization};}finally{vault.close();}''',[record])
  check('equivalent authorizations have distinct signatures',alternate['authorization']!=record['authorization'])
  check('equivalent signatures do not consume another inbox slot',task('b','const r=await recordStore.put(params[0]);return r.status==="already-stored"&&(await recordStore.list()).entries.length===1;',[alternate]))
  variants=task('c','''const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),vault=await new K.DeviceChannelKeys().open(permit);try{const proof=await K.verifyDeviceChannelProof(params[0].authorization,{channel:actor,purpose:"operation"}),out=[];for(const delta of [1,2])out.push({...params[0],authorization:await vault.sign(scope,actor,"operation",{...proof.body,permissionRevision:proof.body.permissionRevision+delta})});return out;}finally{vault.close();}''',[record])
  capacity=task('b','''const S=await import("./assets/desktop/authorized-pending-store.mjs"),C=await import("./network/crypto.mjs"),permit=await hostSessionCase.history.permit(),limited=await new S.AuthorizedPendingStore({archive:recordArchive,scope:hostSessionCase.owner().scope,viewer:hostSessionCase.group.actor,maxChannel:2}).open(permit);try{const outcomes=await Promise.allSettled(params[0].map(v=>limited.put(v))),good=outcomes.map((x,i)=>({x,i})).filter(v=>v.x.status==="fulfilled"),bad=outcomes.filter(x=>x.status==="rejected");if(good.length!==1||bad.length!==1)return false;const wire=params[0][good[0].i].authorization,parts=wire.split("."),auth=await C.hash(JSON.stringify(["codi-device-channel/1","signed-content",parts[0],parts[1]]));await limited.remove({id:good[0].x.value.id,authorization:auth});return (await limited.list()).entries.length===1;}finally{limited.close();}''',[variants])
  check('concurrent inserts respect capacity without losing the original',capacity)
  check('other device scope cannot see the record',task('b','const S=await import("./assets/desktop/authorized-pending-store.mjs"),permit=await hostSessionCase.history.permit(),other=await new S.AuthorizedPendingStore({archive:recordArchive,scope:hostSessionCase.owner().scope+"-other",viewer:hostSessionCase.group.actor}).open(permit);try{return (await other.list()).entries.length===0;}finally{other.close();}'))
  task('c','return hostSessionCase.closeAll();');d.call('/session/'+sessions.pop('c'),method='DELETE')
  task('b','recordStore.close();recordArchive.close();recordVault.close();return hostSessionCase.closeAll();');d.call('/session/'+sessions.pop('b'),method='DELETE')
  start('b');task('b','hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0]);return true;',[config['channel']])
  saved=task('b','''const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),A=await import("./assets/desktop/channel-archive.mjs"),S=await import("./assets/desktop/authorized-pending-store.mjs"),vault=await new K.DeviceChannelKeys().open(permit),keys={get:(c,o)=>vault.get(scope,c,o),sign:(c,p,b,o)=>vault.sign(scope,c,p,b,o)},archive=await new A.DeviceChannelArchive({...params[0],keys,scope,actor}).open(permit),store=await new S.AuthorizedPendingStore({archive,scope,viewer:actor}).open(permit);try{return (await store.list()).entries[0]?.record;}finally{store.close();archive.close();vault.close();}''',[config])
  check('reader retains the signed authorization across browser restart',saved==record)
  start('a');task('a','hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0]);return true;',[config['channel']]);check('owner returns with original validator identity',js('a','return hostSessionCase.group.actor===arguments[0];',[owner]))
  ab2=connect('a','b');bind('b',ab2['b'])
  task('a','await hostSessionCase.group.queue("chat",{text:"another author wrote first"});return true;')
  d.wait(lambda:task('b','return (await hostSessionCase.group.snapshot()).state.messages.some(v=>v.text==="another author wrote first");'),60)
  check('another author advances accepted history before the offline original',True)
  receipt=task('b','''const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import("./assets/desktop/channel-keys.mjs"),A=await import("./assets/desktop/channel-archive.mjs"),E=await import("./network/experimental-authorized-pending.mjs"),vault=await new K.DeviceChannelKeys().open(permit),keys={get:(c,o)=>vault.get(scope,c,o),sign:(c,p,b,o)=>vault.sign(scope,c,p,b,o)},archive=await new A.DeviceChannelArchive({...params[0],keys,scope,actor}).open(permit);try{const pool=desktopNetwork.appContext().pool;return await E.forwardAuthorizedPending(params[1],{archive,viewer:actor,exchange:hostSessionCase.memberExchange,pool,peer:pool.get(params[2])});}finally{archive.close();vault.close();}''',[config,saved,ab2['b']])
  check('reader verifies a validator receipt without the author online',receipt['status']=='verified-receipt')
  for side in 'ab':d.wait(lambda:task(side,'return (await hostSessionCase.group.snapshot()).state.messages.filter(v=>v.text==="Author gone before validator").length===1;'),60)
  check('validator rebases the unsigned witness and accepts the offline author exactly once',True)
  check('accepted record is pruned without removing accepted history',task('b',"""const permit=await hostSessionCase.history.permit(),scope=hostSessionCase.owner().scope,actor=hostSessionCase.group.actor,K=await import('./assets/desktop/channel-keys.mjs'),A=await import('./assets/desktop/channel-archive.mjs'),S=await import('./assets/desktop/authorized-pending-store.mjs'),vault=await new K.DeviceChannelKeys().open(permit),keys={get:(c,o)=>vault.get(scope,c,o),sign:(c,p,b,o)=>vault.sign(scope,c,p,b,o)},archive=await new A.DeviceChannelArchive({...params[0],keys,scope,actor}).open(permit),store=await new S.AuthorizedPendingStore({archive,scope,viewer:actor}).open(permit);try{return (await store.list()).entries.length===0&&(await hostSessionCase.group.snapshot()).state.messages.some(v=>v.text==='Author gone before validator');}finally{store.close();archive.close();vault.close();}""",[config]))
  r['fixtureSignaledRTCLinks']=r['actualRTCLinks'];seen=set()
  for side in sessions:seen.update(task(side,'return desktopNetwork.appContext().pool.list().filter(p=>desktopNetwork.appContext().pool.get(p.id).established).map(p=>p.connectionId);'))
  r['actualRTCLinks']=len(seen);r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'BrowserLog']=d.call('/session/'+sessions[side]+'/log',{'type':'browser'})
   except Exception:pass
  if 'a' in sessions:
   try:js('a','window.releaseNetworkHold?.();window.releasePermissionHold?.();')
   except Exception:pass
  if 'c' in sessions:
   try:js('c','window.releaseRelayRace?.();window.releaseNetworkHold?.();')
   except Exception:pass
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,wakeTrace:hostSessionCase.wakeTrace,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:js(side,'window.recordStore?.close();window.recordArchive?.close();window.recordVault?.close();')
   except Exception:pass
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
