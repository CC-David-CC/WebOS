#!/usr/bin/env python3
"""Four local browsers test verified catch-up after 512 signed blocks.

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
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-neighbor-admission-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':4,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits}
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
  member=folder/'network/device-member-channel.mjs';raw=member.read_text();assert raw.count('const MEMBER_SEGMENT_BLOCKS=256;')==1;member.write_text(raw);r['fixtureCheckpointThreshold']=512;r['fixtureSegmentLimit']=256;r['fixtureMemberSHA256']=hashlib.sha256(member.read_bytes()).hexdigest()
  source=(ROOT/'networking.js').read_text();assert source.count('const disabled=true;')==1;(folder/'networking-fixture.js').write_text(source.replace('const disabled=true;','const disabled=false;'));fixture=(ROOT/'scripts/fixtures/device-session-page.mjs').read_text()
  if compiled:
   c=json.loads((compiled/'apps.json').read_bytes());app=c['apps'][0];assert len(c['apps'])==1;src=compiled/Path(app['path']).parent.relative_to('assets/desktop');raw=(src/'index.mjs').read_bytes();assert hashlib.sha256(raw).hexdigest()==app['sha256'];(assets/'device-history-host.mjs').write_bytes(raw);r['actualCompiledCoreSHA256']=app['sha256']
   for name in ['device-channel-session.mjs','channel-archive.mjs','channel-directory.mjs','storage-consent.mjs','channel-keys.mjs']:fixture=fixture.replace("'./assets/desktop/"+name+"'","'./assets/desktop/device-history-host.mjs'")
   for name in ['device-channel-state.mjs','device-replica.mjs','device-replica-round.mjs','device-member-channel.mjs','device-member-introductions.mjs','device-replica-exchange.mjs']:fixture=fixture.replace("'./network/"+name+"'","'./assets/desktop/device-history-host.mjs'")
  fixture+="\nimport {DeviceChannelDownloadCache} from './assets/desktop/channel-download-cache.mjs'; import {DevicePeerSync} from './network/device-peer-sync.mjs'; const timing=(proto,name,label)=>{const original=proto[name];if(typeof original!=='function')return;proto[name]=async function(...args){const start=performance.now();try{const result=await original.apply(this,args);if(hostSessionCase.measureCatchup&&label.startsWith('archive.')&&Number.isSafeInteger(result?.position?.height))hostSessionCase.measureLastHeight=Math.max(hostSessionCase.measureLastHeight||0,result.position.height);return result;}finally{if(hostSessionCase.measureCatchup){const m=hostSessionCase.timings[label]||={count:0,totalMs:0,maxMs:0};const elapsed=performance.now()-start;m.count++;m.totalMs+=elapsed;m.maxMs=Math.max(m.maxMs,elapsed);}}};}; for(const name of ['append','load','installCheckpoint'])timing(DeviceChannelArchive.prototype,name,'archive.'+name);for(const name of ['get','put','trim','getIndex','putIndex'])timing(DeviceChannelDownloadCache.prototype,name,'cache.'+name);for(const name of ['requestNode','requestHeadChain','requestBlockBundle'])timing(DevicePeerSync.prototype,name,'network.'+name);for(const name of ['installCheckpoint','prepareCheckpoint','inspectCheckpointIndex','inspectCheckpointAncestry','sync'])timing(DeviceMemberChannel.prototype,name,'member.'+name);timing(DeviceReplicaExchange.prototype,'call','network.memberCall');\n"
  fixture+='\nconst admissionMaintain=DeviceMemberIntroductions.prototype.maintain;DeviceMemberIntroductions.prototype.maintain=function(options){return hostSessionCase.pauseIntroductions?Promise.resolve():admissionMaintain.call(this,options);};hostSessionCase.pauseIntroductions=true;\n';
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){f.wireMeter.bytes+=new TextEncoder().encode(wire).length;f.wireMeter.frames++;return measuredSend.call(this,wire);};')
  fixture+='\nconst oldMemberMaintain=DeviceMemberChannel.prototype.maintain;DeviceMemberChannel.prototype.maintain=function(runtime,options){return hostSessionCase.pauseMemberRepair?Promise.resolve({nextMs:300000,retryMs:300000,active:false,phase:"fixture-paused",height:0,round:0,changed:false}):oldMemberMaintain.call(this,runtime,options);};\n'
  fixture+='\nconst realInstall=DeviceMemberChannel.prototype.installCheckpoint;DeviceMemberChannel.prototype.installCheckpoint=async function(...args){try{const result=await realInstall.apply(this,args);hostSessionCase.autoCheckpoint=result;return result;}catch(error){(hostSessionCase.autoErrors||=[]).push({message:error.message,code:error.code});throw error;}};const realSync=DeviceMemberChannel.prototype.sync;DeviceMemberChannel.prototype.sync=async function(peer,options){try{const result=await realSync.call(this,peer,options);(hostSessionCase.autoSync||=[]).push({prefer:!!options?.preferCheckpoint,result});return result;}catch(error){(hostSessionCase.autoErrors||=[]).push({sync:error.message});throw error;}};const realFill=DeviceMemberChannel.prototype.fillCheckpointGap;DeviceMemberChannel.prototype.fillCheckpointGap=function(...args){if(hostSessionCase.holdGapFill)throw Error("fixture history fill paused");return realFill.apply(this,args);};\n'
  fixture+='\nconst realInvoke=DeviceMemberChannel.prototype.invoke;DeviceMemberChannel.prototype.invoke=async function(method,value,options){if(method==="node"&&Array.isArray(value?.blobs)){hostSessionCase.bulkCalls=(hostSessionCase.bulkCalls||0)+1;const result=await realInvoke.call(this,method,value,options);hostSessionCase.bulkItems=(hostSessionCase.bulkItems||0)+result.bundles.length;return result;}return realInvoke.call(this,method,value,options);};\n'
  fixture+='\nconst oldScout=DeviceReplicaExchange.prototype.scout;DeviceReplicaExchange.prototype.scout=function(peer,pins,contact,options){hostSessionCase.savedBootstrap={exchange:this,peer,pins,contact};return oldScout.call(this,peer,pins,contact,options);};\n'
  (folder/'bootstrap.js').write_text((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text().replace('{sampleMs:1000,pendingMs:15000,backoffMs:1000}','{target:4,maxNeighbors:4,sampleMs:1000,pendingMs:15000,backoffMs:1000}').replace('windowMs:10000','windowMs:2000').replace('stepMs:12000','stepMs:60000'));(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',18786),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  saved=ROOT/'.build/test-fixtures/member-512-v1';metadata=json.loads((saved/'metadata.json').read_text());assert metadata['fixtureOnly'] and metadata['origin']==origin and metadata['providerHeight']==515 and metadata['readerHeight']==3
  r['reusedFixture']=True;r['fixtureMetadataSHA256']=hashlib.sha256((saved/'metadata.json').read_bytes()).hexdigest();config=metadata['config'];actors=metadata['actors']
  for side in 'abcd':
   profiles[side]=Path(tempfile.mkdtemp(prefix='codi-member-peers-restored-'+side+'-',dir=Path.home()/'snap/chromium/common'));shutil.copytree(saved/side,profiles[side],dirs_exist_ok=True)
   start(side);js(side,'hostSessionCase.pauseMemberRepair=true;');task(side,'hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0]);return true;',[config['channel']])
  check('reused provider and reader retain distinct signed history floors',task('a','return (await hostSessionCase.group.snapshot()).height===515;') and task('d','return (await hostSessionCase.group.snapshot()).height===3;'))
  extra=connect('d','a');bind('d',extra['d']);d.wait(lambda:task('d','return (await hostSessionCase.group.memberPeers()).some(p=>p.peerId===params[0]);',[extra['d']]),60)
  check('restored reader has a fresh fully admitted provider',task('d','return hostSessionCase.group.memberCheckpoint(params[0]).then(c=>!!c.checkpoint);',[extra['d']]))
  expected=task('a','return (await hostSessionCase.group.load()).position;')
  descriptor=task('d','return hostSessionCase.group.memberCheckpoint(params[0]);',[extra['d']])
  js('d','hostSessionCase.timings={};hostSessionCase.measureCatchup=true;hostSessionCase.measureLastHeight=3;hostSessionCase.measureStartWire={...hostSessionCase.wireMeter};')
  startedPhase=time.monotonic();ancestry=task('d','return hostSessionCase.group.memberInspectAncestry(params[0],params[1]);',[extra['d'],descriptor]);r['ancestrySeconds']=round(time.monotonic()-startedPhase,3);r['ancestry']=ancestry
  check('all 512 certificates prove ancestry without advancing the floor',ancestry['height']==515 and ancestry['certificates']==512 and task('d','return (await hostSessionCase.group.load()).position.height===3;'))
  print(json.dumps({'ancestrySeconds':r['ancestrySeconds'],'phase':'index'}),flush=True)
  startedPhase=time.monotonic();index=task('d','return hostSessionCase.group.memberInspectIndex(params[0],params[1]);',[extra['d'],descriptor]);r['indexSeconds']=round(time.monotonic()-startedPhase,3);r['index']=index
  check('complete index matches the signed checkpoint without advancing the floor',index['status']=='verified-unaccepted-index' and index['height']==515 and task('d','return (await hostSessionCase.group.load()).position.height===3;'))
  r['timings']=js('d','return hostSessionCase.timings;');r['wireEnd']=js('d','return hostSessionCase.wireMeter;')
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,autoSync:hostSessionCase.autoSync,autoErrors:hostSessionCase.autoErrors,autoCheckpoint:hostSessionCase.autoCheckpoint,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
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
