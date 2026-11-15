#!/usr/bin/env python3
"""Eight native browsers enforce shared admission for explicit member and validator bindings.

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
def run(compiled=None,credits=True):
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-neighbor-admission-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':8,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-member-peers-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&peers=1&inline=1&data=1'+('&manualpeers=1' if side!='d' else '')+('&credits=1' if credits else '')});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
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
   data=task(side,'const stats=await hostSessionCase.stats();return {wire:hostSessionCase.wireMeter,budget:stats.network.budget,peers:stats.network.peers.length,scheduler:hostSessionCase.owner().stats().scheduler,organization:hostSessionCase.owner().stats().peerOrganization[0]};');data['rendererHeap']=d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}});result[side]=data
  r.setdefault('measurements',{})[label]={'elapsedSeconds':round(time.monotonic()-started,3),'participants':result,'scope':'Exact signed RTCDataChannel sent payload bytes/frames since startup; native renderer heap via CDP without forced GC; shared policy accounting. Excludes ICE/TURN/UDP/browser-process RAM and v86.'}
 def permission(actor,read,write,n):
  # Actual first-party controller buttons create the pending permission operation.
  js('a','const n=hostSessionCase.node(arguments[0]);n.querySelector("[data-device-connection-in]").closest("details").open=true;n.querySelector("[data-device-member-subject]").value=arguments[1];',[windows['a'],actor]);selector='[data-device-allow-write]' if write else '[data-device-allow-read]' if read else '[data-device-remove-access]';wait('a','return !hostSessionCase.node(arguments[0]).querySelector(arguments[1]).disabled;',[windows['a'],selector]);click('a','[data-window="'+str(windows['a'])+'"] '+selector)
  height('a',n)
 try:
  assets=folder/'assets/desktop';assets.mkdir(parents=True);r['appBuild']=builder.build(ROOT.parent/'served_apps_public',assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();r['appCatalogSHA256']=hashlib.sha256((assets/'apps.json').read_bytes()).hexdigest();files={str(p.relative_to(ROOT)) for p in (ROOT/'assets/desktop').glob('*.mjs')};files.update(str(p.relative_to(ROOT)) for p in (ROOT/'network').glob('*.mjs'));files.update(['networking.js','desktop-apps.js','assets/vendor/chess/chess.mjs','scripts/fixtures/device-session-page.mjs','scripts/fixtures/device-session-bootstrap.js']);r['sourceSHA256']={}
  for n in sorted(files):
   data=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(data).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  candidate=(ROOT/'network/device-member-channel.mjs').read_text();assert candidate.count('const MEMBER_SEGMENT_BLOCKS=256;')==1;candidate=candidate.replace('const MEMBER_SEGMENT_BLOCKS=256;','const MEMBER_SEGMENT_BLOCKS=4;');(folder/'network/device-member-channel.mjs').write_text(candidate);r['candidateMemberSHA256']=hashlib.sha256(candidate.encode()).hexdigest();r['candidateScope']='Retained segment target candidate; fixture uses four-block segment limit'
  source=(ROOT/'networking.js').read_text();assert source.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(source.replace('const disabled=true;','const disabled=false;'));fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text()
  if compiled:
   c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];assert len(c['apps'])==1;src=compiled/Path(app['path']).parent.relative_to('assets/desktop');raw=(src/'index.mjs').read_bytes();assert hashlib.sha256(raw).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(raw);r['actualCompiledCoreSHA256']=app['sha256']
   for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
   for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  fixture+='\nconst admissionMaintain=DeviceMemberIntroductions.prototype.maintain;DeviceMemberIntroductions.prototype.maintain=function(options){return hostSessionCase.pauseIntroductions?Promise.resolve():admissionMaintain.call(this,options);};hostSessionCase.pauseIntroductions=true;\n';
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){f.wireMeter.bytes+=new TextEncoder().encode(wire).length;f.wireMeter.frames++;return measuredSend.call(this,wire);};')
  fixture+='\nconst oldMemberMaintain=DeviceMemberChannel.prototype.maintain;DeviceMemberChannel.prototype.maintain=function(runtime,options){return hostSessionCase.pauseMemberRepair?Promise.resolve({nextMs:300000,retryMs:300000,active:false,phase:"fixture-paused",height:0,round:0,changed:false}):oldMemberMaintain.call(this,runtime,options);};\n'
  fixture+='\nconst savedAppend=DeviceChannelArchive.prototype.append;DeviceChannelArchive.prototype.append=async function(...args){const result=await savedAppend.apply(this,args);if(hostSessionCase.interruptSegments>0){hostSessionCase.interruptSegments--;throw Error("fixture interruption after durable block");}return result;};\n'
  fixture+='\nconst oldScout=DeviceReplicaExchange.prototype.scout;DeviceReplicaExchange.prototype.scout=function(peer,pins,contact,options){hostSessionCase.savedBootstrap={exchange:this,peer,pins,contact};return oldScout.call(this,peer,pins,contact,options);};\n'
  fixture+='\nconst realAncestryCall=DeviceReplicaExchange.prototype.call;DeviceReplicaExchange.prototype.call=async function(peer,pins,method,value,options){const result=await realAncestryCall.call(this,peer,pins,method,value,options);if(method==="ancestry"&&hostSessionCase.poisonRestoration){hostSessionCase.poisonRestoration=false;const bad=structuredClone(result);bad.entries[0].commit[0]="x";return bad;}return result;};\n'
  (folder/'bootstrap.js').write_text((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text().replace('{sampleMs:1000,pendingMs:15000,backoffMs:1000}','{target:2,maxNeighbors:2,sampleMs:1000,pendingMs:15000,backoffMs:1000}').replace('windowMs:10000','windowMs:2000'));(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcd':start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Admission actor "+params[0])).channel;',[side])
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Manual full-seed recovery; deterministic shared admission",controller:params[0],validators:[params[0]],publicRead:false,publicWrite:false});return (await hostSessionCase.view.channels())[0];',[actors['a'],[actors[s] for s in 'abcd']])
  for side in 'bcd':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  for height_value,side in enumerate('bc',1):permission(actors[side],True,False,height_value)
  links={}
  for side in 'bc':links[side]=connect(side,'a');bind(side,links[side][side])
  d.wait(lambda:task('a','const p=hostSessionCase.owner().stats().peerOrganization[0];return p.admissions===2&&p.neighbors===2;'),30)
  check('private seed is full with two admitted readers',True)
  extra=connect('d','a');js('d','hostSessionCase.pauseIntroductions=false;')
  check('newly granted reader has not downloaded the accepted grant',task('d','const s=await hostSessionCase.group.snapshot();return s.height===0&&!s.readable;'))
  refused=task('d','try{await hostSessionCase.group.bindMember(params[0]);return false;}catch(e){return true;} ',[extra['d']])
  check('ungranted reader is refused without receiving private history',refused and task('d','const s=await hostSessionCase.group.snapshot();return s.height===0&&!s.readable;'))
  permission(actors['d'],True,False,3)
  task('d','try{await hostSessionCase.group.bindMember(params[0]);}catch(e){if(e.code!=="unavailable")throw e;}return true;',[extra['d']])
  check('read-only bootstrap verifies and installs the accepted grant from the full seed',task('d','const s=await hostSessionCase.group.snapshot();return s.height===3&&s.readable&&!s.writable;'))
  page=task('d','return await hostSessionCase.group.memberAncestry(params[0],{before:null,limit:2});',[extra['d']])
  check('authorized reader receives a bounded newest-first certificate page',len(page['entries'])==2 and page['next'] is not None and all(set(x)=={'header','prepare','commit'} for x in page['entries']) and page['entries'][0]['header']['height']==3)
  page2=task('d','return await hostSessionCase.group.memberAncestry(params[0],{before:params[1],limit:2});',[extra['d'],page['next']])
  check('opaque cursor continues to genesis without operation bodies',len(page2['entries'])==1 and page2['next'] is None and page2['entries'][0]['header']['height']==1 and all(set(x)=={'header','prepare','commit'} for x in page2['entries']))
  desc=task('d','return await hostSessionCase.group.memberCheckpoint(params[0]);',[extra['d']])
  check('authorized reader receives pinned checkpoint and operation-tree descriptor',set(desc)=={'profile','channel','genesisHash','checkpoint','tree','history'} and desc['profile']=='codi-device-checkpoint-transfer/1' and desc['tree'] is not None)
  check('independent checkpoint verifier agrees with the retained local head',task('d','const p=await import("./network/device-channel-state.mjs"),v=await p.readDeviceChannelCheckpoint(params[0].checkpoint,{channel:params[0].channel,genesisHash:params[0].genesisHash});return v.head===(await hostSessionCase.group.snapshot()).head;',[desc]))
  index=task('d','const p=await import("./network/device-channel-state.mjs"),t=await import("./network/device-operation-tree.mjs"),v=await p.readDeviceChannelCheckpoint(params[0].checkpoint,{channel:params[0].channel,genesisHash:params[0].genesisHash});let requests=0;const tree=new t.DeviceOperationTree({get:async(cid,{link})=>{requests++;return (await hostSessionCase.group.memberIndexNode(params[1],link)).wire;},put:async()=>{throw Error("read-only");}}),walk=new t.DeviceOperationTreeVerifier({tree,root:params[0].tree,expectedRoot:p.deviceChannelState(v).acceptedRoot});let status;do{status=await walk.step({limit:2});}while(!status.complete);walk.close();return {status,requests};',[desc,extra['d']])
  check('peer index nodes verify incrementally against the signed checkpoint',index['status']['complete'] and index['requests']>=3 and index['status']['checked']==index['requests'])
  beforeIndex=task('d','return (await hostSessionCase.group.snapshot()).head;')
  def inspect_ancestry(descriptor):
   def attempt():
    value=task('d','try{return {result:await hostSessionCase.group.memberInspectAncestry(params[0],params[1])};}catch(e){if(e.message.includes("finishing earlier durable work"))return {busy:true};throw e;}',[extra['d'],descriptor]);return value.get('result') or False
   return d.wait(attempt,45)
  ancestry=inspect_ancestry(desc)
  check('peer ancestry inspection preserves an already matching accepted floor',ancestry['status']=='verified-unaccepted-ancestry' and ancestry['head']==beforeIndex and ancestry['certificates']==0 and task('d','return (await hostSessionCase.group.snapshot()).head;')==beforeIndex)
  def inspect():
   value=task('d','try{return {result:await hostSessionCase.group.memberInspectIndex(params[0],params[1])};}catch(e){if(e.message.includes("finishing earlier durable work"))return {busy:true};throw e;}',[extra['d'],desc]);return value.get('result') or False
  firstIndex=d.wait(inspect,45);secondIndex=d.wait(inspect,45)
  check('peer index downloads into unaccepted scratch and verifies to the signed root',firstIndex['status']=='verified-unaccepted-index' and firstIndex['fetched']>=3 and firstIndex['head']==beforeIndex)
  check('repeat verification reuses retained index nodes without fetching them again',secondIndex['checked']==firstIndex['checked'] and secondIndex['fetched']==0 and secondIndex['reused']==firstIndex['checked'] and task('d','return (await hostSessionCase.group.snapshot()).head;')==beforeIndex)

  forged=task('d','const link=structuredClone(params[1]);link.hash=(link.hash[0]==="A"?"B":"A")+link.hash.slice(1);try{await hostSessionCase.group.memberIndexNode(params[0],link);return false;}catch(e){return e.code==="unavailable";}',[extra['d'],desc['tree']])
  wait('a','return hostSessionCase.owner().stats().members.failures.some(f=>f.method==="index-node"&&f.message.includes("link differs"));',[],30)
  check('provider refuses a forged operation-index link',forged)




  d.wait(lambda:task('d','return hostSessionCase.owner().stats().peerOrganization[0].neighbors>0;'),60)
  check('new private reader binds an alternative after verifying the first grant',task('d','return hostSessionCase.owner().stats().peerOrganization[0].neighbors>0;'))
  check('provisional capability cannot invoke writes, introductions or wake hints',task('d','const {exchange,peer,pins}=hostSessionCase.savedBootstrap;for(const method of ["submit","peers","introduce","notice"]){try{await exchange.call(peer,pins,method,{});return false;}catch(e){if(!e.message.includes("read-only"))return false;}}return true;'))
  task('d','const {peer,pins}=hostSessionCase.savedBootstrap,m=await import("./network/device-replica-values.mjs"),value=await m.encodeDeviceReplicaInline({}, {channel:pins.channel,genesisHash:pins.genesisHash,purpose:"request:submit"});await peer.link.sendDeviceMember({op:"call",...pins,request_id:crypto.randomUUID().replaceAll("-",""),method:"submit",value});return true;')
  wait('a','return hostSessionCase.owner().stats().members.failures.some(f=>f.method==="submit"&&f.message.includes("read-only"));',[],30)
  check('provider rejects a forged write frame even if the local check is bypassed',True)
  js('d','hostSessionCase.pauseMemberRepair=true;')
  js('a','hostSessionCase.pauseMemberRepair=true;')
  task('a','for(let i=0;i<18;i++){let done=false;for(let attempt=0;attempt<40&&!done;attempt++){try{const row=await hostSessionCase.group.queue("chat",{text:"Stale peer history "+i});await hostSessionCase.group.settleSolo(row.id);done=true;}catch(e){if(!e.message.includes("already processing")&&!e.message.includes("finishing earlier"))throw e;await new Promise(r=>setTimeout(r,100));}}if(!done)throw Error("fixture could not settle");}return true;')
  check('reader remains at its previous floor while provider advances 18 blocks',task('d','return (await hostSessionCase.group.snapshot()).height===3;') and task('a','return (await hostSessionCase.group.snapshot()).height===21;'))
  later=task('d','return hostSessionCase.group.memberCheckpoint(params[0]);',[extra['d']])
  task('a','const row=await hostSessionCase.group.queue("chat",{text:"Provider advanced during checkpoint inspection"});await hostSessionCase.group.settleSolo(row.id);return true;')
  check('provider advances after checkpoint offer',task('a','return (await hostSessionCase.group.snapshot()).height===22;'))
  inspected=inspect_ancestry(later)
  check('stale reader verifies multiple newest-first pages over actual RTC without advancing its floor',inspected['status']=='verified-unaccepted-ancestry' and inspected['height']==21 and inspected['pages']>=2 and inspected['certificates']==18 and task('d','return (await hostSessionCase.group.snapshot()).height===3;'))
  check('offered checkpoint remains verifiable after provider advances',inspected['height']==21 and task('a','return (await hostSessionCase.group.snapshot()).height===22;'))
  newer=task('d','return hostSessionCase.group.memberCheckpoint(params[0]);',[extra['d']])
  mismatch=dict(later);mismatch['history']=newer['history']
  rejected=task('d','try{await hostSessionCase.group.memberInspectAncestry(params[0],params[1]);return "accepted";}catch(e){return e.message;}',[extra['d'],mismatch])
  check('mismatched checkpoint and history locator are rejected',('does not descend' in rejected or 'does not match' in rejected) and task('d','return (await hostSessionCase.group.snapshot()).height===3;'))
  baseline_jobs=task('d','const db=await new Promise((ok,no)=>{const q=indexedDB.open("codi-device-download-cache-v1",1);q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error);});try{return await new Promise((ok,no)=>{const tx=db.transaction("jobs"),q=tx.objectStore("jobs").count();q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error);});}finally{db.close();}')
  js('d','hostSessionCase.interruptSegments=6;')
  for expected in range(4,10):
   def interrupt_attempt():
    row=task('d','try{await hostSessionCase.group.pullMember(params[0]);return {bad:true};}catch(e){if(e.message.includes("finishing earlier durable work"))return {busy:true};return {error:e.message};}',[extra['d']]);return row if not row.get('busy') else False
   row=d.wait(interrupt_attempt,45)
   check('interrupted segment retains exact accepted block '+str(expected),'fixture interruption after durable block' in row.get('error','') and task('d','return (await hostSessionCase.group.snapshot()).height;')==expected)
   count=task('d','const db=await new Promise((ok,no)=>{const q=indexedDB.open("codi-device-download-cache-v1",1);q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error);});try{return await new Promise((ok,no)=>{const tx=db.transaction("jobs"),q=tx.objectStore("jobs").count();q.onsuccess=()=>ok(q.result);q.onerror=()=>no(q.error);});}finally{db.close();}')
   check('retries retain at most one unfinished segment job '+str(expected),count<=baseline_jobs+2)
   if expected==4:
    task('d','const m=await import("./assets/desktop/channel-download-cache.mjs"),p=await hostSessionCase.history.permit(),opts={scope:hostSessionCase.owner().scope,channel:params[0].channel,genesisHash:params[0].genesisHash},offers=await m.listDeviceChannelDownloadOffers(opts,p),old=offers.find(x=>x.height===7);if(!old)throw Error("missing interrupted target");const c=await new m.DeviceChannelDownloadCache(opts).open(p,old);await c.trim([],{removeJob:true});c.close();const forged={...old,height:6,head:"A".repeat(43),history:"B".repeat(42)+"A"};const f=await new m.DeviceChannelDownloadCache(opts).open(p,forged);f.close();return true;',[config])
    task('d','await hostSessionCase.closeAll();return true;');js('a','desktopNetwork.appContext().pool.closeEntry(arguments[0],"fixture reload cleanup");',[extra['a']])
    d.call('/session/'+sessions['d']+'/refresh',{});wait('d','return window.fixtureReady===true;');js('d','hostSessionCase.pauseMemberRepair=true;')
    task('a','const row=await hostSessionCase.group.queue("chat",{text:"Provider advanced while reader reloaded"});await hostSessionCase.group.settleSolo(row.id);return true;')
    check('provider advances while reader is reloading',task('a','return (await hostSessionCase.group.snapshot()).height===23;'))
    windows['d']=js('d','return hostSessionCase.open("chat");');wait('d','return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]");',[windows['d']]);js('d','hostSessionCase.view=hostSessionCase.facades.get(arguments[0]);',[windows['d']]);task('d','hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors['d']]);extra=connect('d','a');js('d','hostSessionCase.pauseIntroductions=false;hostSessionCase.interruptSegments=5;')
    task('d','try{await hostSessionCase.group.bindMember(params[0]);}catch(e){if(e.code!=="unavailable")throw e;}return true;',[extra['d']]);check('reload retains accepted floor before segment discovery',task('d','return (await hostSessionCase.group.snapshot()).height===4;'))
    js('d','hostSessionCase.poisonRestoration=true;')
    def poison_attempt():
     row=task('d','try{await hostSessionCase.group.pullMember(params[0]);return {accepted:true};}catch(e){if(e.message.includes("finishing earlier durable work"))return {busy:true};return {error:e.message};}',[extra['d']]);return row if not row.get('busy') else False
    bad=d.wait(poison_attempt,45)
    check('invalid restoration certificate cannot advance the retained floor',bool(bad.get('error')) and task('d','return (await hostSessionCase.group.snapshot()).height===4;'))
  while task('d','return (await hostSessionCase.group.snapshot()).height;')<23:
   def resume_attempt():
    row=task('d','try{return {result:await hostSessionCase.group.pullMember(params[0])};}catch(e){if(e.message.includes("finishing earlier durable work"))return {busy:true};throw e;}',[extra['d']]);return row.get('result') or False
   d.wait(resume_attempt,45)
  check('unrelated retained branch never changes the accepted chain',task('d','const s=await hostSessionCase.group.snapshot();return s.height===23&&s.head!=="A".repeat(43);'))
  check('repeated interruption resumes through the original offered head',task('d','const s=await hostSessionCase.group.snapshot();return s.height===23&&s.state.messages.length===20;'))
  js('a','hostSessionCase.pauseMemberRepair=false;')
  permission(actors['d'],False,False,24)
  before_denials=js('a','return hostSessionCase.memberAuth.filter(v=>v.actor===arguments[0]&&v.error.includes("not a reader")).length;',[actors['d']])
  denied=task('d','try{await hostSessionCase.group.memberAncestry(params[0],{before:null,limit:2});return false;}catch(e){return true;} ',[extra['d']])
  wait('a','return hostSessionCase.memberAuth.filter(v=>v.actor===arguments[0]&&v.error.includes("not a reader")).length>arguments[1];',[actors['d'],before_denials],30)
  check('revocation prevents further ancestry page disclosure',denied)
  check('revocation prevents further checkpoint disclosure',task('d','try{await hostSessionCase.group.memberCheckpoint(params[0]);return false;}catch(e){return true;} ',[extra['d']]))
  check('revocation prevents further index-node disclosure',task('d','try{await hostSessionCase.group.memberIndexNode(params[0],params[1]);return false;}catch(e){return true;} ',[extra['d'],desc['tree']]))

  check('revoked reader cannot start a new bootstrap from the full seed',task('d','try{await hostSessionCase.group.bindMember(params[0]);return false;}catch(e){return true;} ',[extra['d']]))
  check('bootstrap does not exceed the full seed neighbor limit',task('a','return hostSessionCase.owner().stats().peerOrganization[0].admissions===2;'))
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
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
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--credits',action='store_true');p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core,True);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
