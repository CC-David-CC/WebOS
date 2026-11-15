#!/usr/bin/env python3
"""Eight native browsers enforce shared admission for explicit member and validator bindings.

Local-development identities, real Storage API/IDB/crypto/RTC and packaged apps;
explicit signaling, no v86/live activation/large-mesh or joint-membership claim.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,signal,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=mod('member_driver',ROOT/'scripts/touch-preview-check.py');builder=mod('member_apps',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled=None,credits=True):
 sessions={};profiles={};processes={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-neighbor-admission-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':8,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-member-peers-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];pid=v['capabilities']['goog:processID'];processes[side]=(pid,(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&peers=1&inline=1&data=1'+('&manualpeers=1' if side!='h' else '')+('&credits=1' if credits else '')});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
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
  fixture+='\nconst admissionMaintain=DeviceMemberIntroductions.prototype.maintain;DeviceMemberIntroductions.prototype.maintain=function(options){return hostSessionCase.pauseIntroductions?Promise.resolve():admissionMaintain.call(this,options);};hostSessionCase.pauseIntroductions=true;\n';
  fixture=fixture.replace('const f=window.hostSessionCase;','const f=window.hostSessionCase;f.wireMeter={bytes:0,frames:0,kinds:{}};const measuredSend=RTCDataChannel.prototype.send;RTCDataChannel.prototype.send=function(wire){const bytes=new TextEncoder().encode(wire).length;f.wireMeter.bytes+=bytes;f.wireMeter.frames++;let kind="unclassified";try{const payload=JSON.parse(atob(wire.split(".")[1].replaceAll("-","+").replaceAll("_","/")));const inner=payload.kind==="application"?JSON.parse(payload.text):null;kind=inner?[inner.mode,inner.body?.op,inner.body?.method].filter(Boolean).join(":"):payload.kind;}catch{}const row=f.wireMeter.kinds[kind]??={bytes:0,frames:0};row.bytes+=bytes;row.frames++;return measuredSend.call(this,wire);};')
  fixture+='\nconst actualMemberMaintain=DeviceMemberChannel.prototype.maintain;DeviceMemberChannel.prototype.maintain=function(runtime,options){return hostSessionCase.pauseMemberRepair?Promise.resolve({nextMs:300000,retryMs:300000,active:false,phase:"fixture-paused",height:0,round:0,changed:false}):actualMemberMaintain.call(this,runtime,options);};\n'
  fixture+="\nhostSessionCase.failSecondNode=actor=>{const previous=DeviceMemberChannel.prototype.invoke;let seen=0;hostSessionCase.nodeFaults=0;hostSessionCase.bootstrapNodeIds=[];DeviceMemberChannel.prototype.invoke=async function(method,...args){const out=await previous.call(this,method,...args);if(method==='node'&&args[0]?.cid&&args[1]?.actor===actor)hostSessionCase.bootstrapNodeIds.push(args[0].cid);if(method==='node'&&args[0]?.cid&&args[1]?.actor===actor&&++seen===2){hostSessionCase.nodeFaults++;throw Error('Fixture interruption after a retained chunk');}return out;};};\n"
  (folder/'bootstrap.js').write_text((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_text().replace('windowMs:10000','windowMs:2000').replace('downloadBytes:8388608','downloadBytes:8388608'));(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcdefgh':start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Admission actor "+params[0])).channel;',[side])
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Manual full-seed recovery; deterministic shared admission",controller:params[0],validators:params[1],publicRead:false,publicWrite:false});return (await hostSessionCase.view.channels())[0];',[actors['a'],[actors[s] for s in 'abcd']])
  for side in 'bcdefgh':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  for i,a in enumerate('abcd'):
   for b in 'abcd'[i+1:]:
    link=connect(a,b,True);bind(a,link[a]);bind(b,link[b])
  check('three validator neighbors share three slots with their authenticated member bindings',task('a','const p=hostSessionCase.owner().stats().peerOrganization[0];return p.admissions===3&&p.admissionRefs===6&&p.neighbors===3;'))
  for height_value,side in enumerate('efgh',1):permission(actors[side],True,False,height_value)
  links={}
  for side in 'efg':links[side]=connect(side,'a');bind(side,links[side][side])
  d.wait(lambda:task('a','const p=hostSessionCase.owner().stats().peerOrganization[0];return p.admissions===6&&p.admissionRefs===9&&p.neighbors===6;'),30)
  check('three ordinary seed connections fill the same six-slot budget',task('a','const p=hostSessionCase.owner().stats().peerOrganization[0];return p.admissions===6&&p.admissionRefs===9&&p.neighbors===6;'))
  extra=connect('h','a');before=task('a','return hostSessionCase.owner().stats().peerOrganization[0];')
  js('h','hostSessionCase.pauseIntroductions=false;')
  check('new private reader is locally at genesis despite accepted provider grant',task('h','const s=await hostSessionCase.group.snapshot();return s.height===0&&!s.readable;') and task('a','return (await hostSessionCase.group.snapshot()).height===4;'))
  js('a','hostSessionCase.failSecondNode(arguments[0]);',[actors['h']])
  result=task('h','try{await hostSessionCase.group.bindMember(params[0]);return false;}catch(e){return e.code==="unavailable";}',[extra['h']])
  scratch=task('h','return await hostSessionCase.scratchStats();')
  first=js('a','return hostSessionCase.bootstrapNodeIds.slice();')
  check('interrupted quorum transfer retains verified unaccepted chunks',result and len(first)>=2 and scratch and any(j['nodeCount']>0 for j in scratch['jobs']))
  pid,ticks=processes['h'];proc=Path('/proc')/str(pid);args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').split();assert ('--user-data-dir='+str(profiles['h'])).encode() in args and not any(v.startswith(b'--type=') for v in args) and os.readlink(proc/'exe').endswith('/chrome') and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==ticks
  os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop('h'),method='DELETE');r['ownedReaderCrash']={'pid':pid,'startTicks':ticks,'signal':'SIGKILL','afterVerifiedScratch':True}
  js('a','desktopNetwork.appContext().pool.closeEntry(arguments[0],"fixture crash cleanup");',[extra['a']])
  start('h')
  task('h','hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors['h']])
  after=task('h','return await hostSessionCase.scratchStats();')
  check('browser crash restart retains partial verified download and same channel actor',after and any(j['nodeCount']>0 for j in after['jobs']) and task('h','return (await hostSessionCase.group.snapshot()).actor===params[0];',[actors['h']]))
  extra=connect('h','a');js('h','hostSessionCase.pauseIntroductions=false;')
  result=task('h','try{return await hostSessionCase.group.bindMember(params[0]);}catch(e){return {error:String(e.message||e)};}',[extra['h']])
  check('restarted reader verifies the accepted grant',task('h','const s=await hostSessionCase.group.snapshot();return s.height===4&&s.readable;'))
  ids=js('a','return hostSessionCase.bootstrapNodeIds.slice();')
  check('crash restart resumes without requesting retained first node again',ids.count(first[0])==1)
  check('completed transfer clears scratch job',task('h','const s=await hostSessionCase.scratchStats();return !s||s.jobs.length===0;'))
  js('h','hostSessionCase.pauseMemberRepair=true;')
  permission(actors['e'],True,True,5);permission(actors['e'],True,False,6);height('e',6)
  full=connect('h','e');bind('h',full['h'])
  check('reader retains its older floor while four validators advance',task('h','return (await hostSessionCase.group.snapshot()).height===4;') and all(task(side,'const s=await hostSessionCase.group.snapshot();return s.height===6&&s.quorum===3;',[]) for side in 'abcd'))
  def checkpoint():
   def attempt():
    value=task('h','try{return {value:await hostSessionCase.group.memberCheckpoint(params[0])};}catch(e){if(e.code==="unavailable"||e.code==="rate-limited")return {retry:true};throw e;}',[full['h']]);return value.get('value') or False
   return d.wait(attempt,45)
  descriptor=checkpoint()
  invalid=dict(descriptor);packet=json.loads(invalid['checkpoint']);packet['commit']=packet['commit'][:2];invalid['checkpoint']=json.dumps(packet,separators=(',',':'))
  refused=task('h','try{await hostSessionCase.group.memberInstallCheckpoint(params[0],params[1]);return false;}catch(e){return true;}',[full['h'],invalid])
  check('checkpoint without the three-validator quorum cannot advance the reader',refused and task('h','return (await hostSessionCase.group.snapshot()).height===4;'))
  def install():
   value=task('h','try{return {value:await hostSessionCase.group.memberInstallCheckpoint(params[0],params[1])};}catch(e){const s=await hostSessionCase.group.snapshot();if((e.code==="rate-limited"||e.code==="unavailable"||e.message.includes("finishing earlier durable work"))&&s.height===4)return {retry:true,delay:e.retryAfterMs||1000};throw e;}',[full['h'],descriptor])
   if value.get('retry'):time.sleep(min(5,max(.1,value.get('delay',1000)/1000)));return False
   return value['value']
  result=d.wait(install,180);r['quorumCheckpoint']={k:v for k,v in result.items() if k!='prior'}
  check('reader installs peer checkpoint certified by three of four actual validators',result['height']==6 and result['prior']['height']==4 and result['scratchCleaned'] and task('h','const s=await hostSessionCase.group.snapshot(),h=await hostSessionCase.group.history({limit:8});return s.height===6&&s.quorum===3&&s.historical&&h.incomplete;',[]))
  pid,ticks=processes['h'];proc=Path('/proc')/str(pid);args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').split();assert ('--user-data-dir='+str(profiles['h'])).encode() in args and not any(v.startswith(b'--type=') for v in args) and os.readlink(proc/'exe').endswith('/chrome') and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==ticks
  os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop('h'),method='DELETE');r['checkpointReaderCrash']={'pid':pid,'startTicks':ticks,'signal':'SIGKILL','afterCheckpointCommit':True}
  start('h');js('h','hostSessionCase.pauseMemberRepair=true;');task('h','hostSessionCase.group=await hostSessionCase.view.restoreChannel(params[0]);return true;',[config['channel']])
  check('reader browser crash retains the three-validator checkpoint and older boundary',task('h','const s=await hostSessionCase.group.snapshot(),a=await hostSessionCase.group.load(),h=await hostSessionCase.group.history({limit:8});return s.height===6&&s.quorum===3&&s.historical&&a.prior.height===4&&h.incomplete;'))
  full=connect('h','e');bind('h',full['h']);permission(actors['e'],True,True,7);height('e',7)
  def pull():
   value=task('h','try{return {value:await hostSessionCase.group.pullMember(params[0])};}catch(e){if(e.code==="rate-limited"||e.message.includes("finishing earlier durable work"))return {retry:true,delay:e.retryAfterMs||1000};throw e;}',[full['h']])
   if value.get('retry'):time.sleep(min(5,max(.1,value.get('delay',1000)/1000)));return False
   return value['value']
  nextBlock=d.wait(pull,120)
  check('three-validator peer replay continues after checkpoint without hiding the gap',nextBlock['height']==7 and task('h','const s=await hostSessionCase.group.snapshot(),a=await hostSessionCase.group.load(),h=await hostSessionCase.group.history({limit:8});return s.height===7&&s.quorum===3&&a.prior.height===4&&h.incomplete;'))
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {owner:hostSessionCase.owner().stats(),wireMeter:structuredClone(hostSessionCase.wireMeter),text:document.body.innerText,memberTrace:hostSessionCase.memberTrace,topologyFailures:hostSessionCase.topologyFailures,memberAuth:hostSessionCase.memberAuth,introductions:hostSessionCase.introductions.map(p=>({answered:p.answered,entryId:p.entry.id})),stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,history:hostSessionCase.linkStateHistory.get(l)};})};')
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
