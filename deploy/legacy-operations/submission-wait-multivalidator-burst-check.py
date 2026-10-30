#!/usr/bin/env python3
"""Actual native-browser ordinary members, accepted ACLs and independent voters.

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
def run(compiled=None,credits=False):
 sessions={};profiles={};windows={};server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-members-');folder=Path(tmp.name);checks=[];started=time.monotonic();r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':6,'actualBrowserLaunches':0,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False,'byteCreditsEnabled':credits}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=45):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(side,selector):
  e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-members-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side+'&automatic=1&peers=1&manualpeers=1'+('&inline=1&data=1&credits=1' if credits else '')});wait(side,'return window.fixtureReady===true;');d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});w=js(side,'return hostSessionCase.open("chat");');windows[side]=w
  wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels],.storage-consent button:first-of-type:not(:disabled)");',[w])
  if not js(side,'return !!hostSessionCase.node(arguments[0]).querySelector("[data-device-channels]");',[w]):click(side,'[data-window="'+str(w)+'"] .storage-consent button')
  wait(side,'return !!hostSessionCase.node(arguments[0])?.querySelector("[data-device-channels]");',[w]);js(side,'hostSessionCase.view=hostSessionCase.facades.get(arguments[0]);',[w])
 def connect(a,b,validator=False,delay_signaling=False):
  offer=task(a,'return hostSessionCase.view.offer();');answer=task(b,'return hostSessionCase.view.answer(params[0]);',[offer['token']])
  if delay_signaling:js(a,'const link=desktopNetwork.appContext().pool.get(arguments[0]).link,rtc=link.rtc.bind(link),state=link.state.bind(link);hostSessionCase.handshakeStates=[];link.state=(name,detail)=>{hostSessionCase.handshakeStates.push({name,at:performance.now(),caller:new Error().stack});return state(name,detail);};link.rtc=async(method,...args)=>{const value=await rtc(method,...args);if(method==="setRemoteDescription"){const until=performance.now()+10000;while(!(link.sentHello&&link.receivedHello)&&performance.now()<until)await new Promise(r=>setTimeout(r,10));hostSessionCase.delayedSignalingSawHello=link.sentHello&&link.receivedHello;}return value;};',[offer['peerId']])
  task(a,'return hostSessionCase.view.accept(params[0],params[1]);',[offer['peerId'],answer['token']]);wait(a,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[offer['peerId']]);wait(b,'return desktopNetwork.appContext().pool.get(arguments[0])?.link.deviceMemberReady;',[answer['peerId']]);r['actualRTCLinks']+=1
  if validator:task(a,'return hostSessionCase.group.bindValidator(params[0]);',[offer['peerId']])
  return {a:offer['peerId'],b:answer['peerId']}
 def height(side,n):return d.wait(lambda:task(side,'return (await hostSessionCase.group.snapshot()).height===params[0];',[n]),75)
 def bind_authorized_member(side,peer):
  # A native read grant is already accepted at this provider before each
  # positive probe. Retry only this bounded idempotent binding after busy refusal,
  # never the signed permission operation. Negative authorization probes below
  # remain single requests and must still be refused.
  def attempt():
   v=task(side,'try{await hostSessionCase.group.bindMember(params[0]);return {bound:true};}catch(error){if(error.code!=="unavailable")throw error;return {bound:false};}',[peer])
   if not v['bound']:r['transientRebindRefusals']=r.get('transientRebindRefusals',0)+1
   return v['bound']
  return d.wait(attempt,30)
 def permission(actor,read,write,n):
  # Exercise the same public host API that the permission controls call.
  task('a','return hostSessionCase.view.setChannelMemberAccess(hostSessionCase.group.channel,params[0],{read:params[1],write:params[2]});',[actor,read,write])
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
  (folder/'bootstrap.js').write_bytes((ROOT/'scripts/fixtures/device-session-bootstrap.js').read_bytes());(folder/'fixture.mjs').write_text(fixture);(folder/'index.html').write_text('<!doctype html><title>Owned member integration</title><main id="windows"></main><script src="bootstrap.js"></script><script src="networking-fixture.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);actors={}
  for side in 'abcdef':start(side);actors[side]=task(side,'return (await hostSessionCase.view.createIdentity("Membership actor "+params[0])).channel;',[side])
  # Slot11/round0 selects validator index2. Make that exact actor the
  # controller we later close, so recovery never depends on random key order.
  offlineLeader=sorted('abcd',key=lambda side:actors[side])[2]
  if offlineLeader!='a':
   for table in [sessions,profiles,windows,actors]:table['a'],table[offlineLeader]=table[offlineLeader],table['a']
  config=task('a','hostSessionCase.group=await hostSessionCase.view.createChannel({label:"Private member channel",controller:params[0],validators:params[1],publicRead:false,publicWrite:false});return (await hostSessionCase.view.channels())[0];',[actors['a'],[actors[s] for s in 'abcd']])
  for side in 'bcdef':task(side,'hostSessionCase.group=await hostSessionCase.view.openChannel(params[0],params[1]);return true;',[config,actors[side]])
  for i,a in enumerate('abcd'):
   for b in 'abcd'[i+1:]:connect(a,b,True)
  links={s:connect(s,'a',delay_signaling=s=='e') for s in 'ef'}
  check('late signaling completion cannot overwrite an already authenticated peer ready state',js('e','return hostSessionCase.delayedSignalingSawHello===true;'))
  check('ordinary identities have no validator state and cannot bind a voting route',all(task(s,'try{await hostSessionCase.group.bindValidator(params[0]);return false;}catch{return !(await hostSessionCase.group.snapshot()).validator;}',[links[s][s]]) for s in 'ef'))
  check('a private channel rejects an ungranted durable actor before exposing its head',task('e','try{await hostSessionCase.group.bindMember(params[0]);return false;}catch{return (await hostSessionCase.group.snapshot()).height===0;}',[links['e']['e']]))
  permission(actors['e'],True,True,1);permission(actors['f'],True,True,2)
  # Existing bookmarked reader binds using the host API.
  bind_authorized_member('e',links['e']['e']);height('e',2)
  bind_authorized_member('f',links['f']['f']);height('f',2)
  check('bookmarked member binds with its saved actor',task('e','return (await hostSessionCase.group.snapshot()).actor===params[0];',[actors['e']]))
  texts=['multivalidator burst '+side for side in 'aef'];sendAt=int(time.time()*1000)+3000
  for side,text in zip('aef',texts):
   js(side,'window.burstResult={scheduled:arguments[1]};const text=arguments[0],at=arguments[1];setTimeout(()=>{burstResult.started=Date.now();hostSessionCase.group.queue("chat",{text}).then(()=>burstResult.queued=Date.now(),e=>burstResult.error=e.message);},Math.max(0,at-Date.now()));',[text,sendAt])
  arrivals={};deadline=time.monotonic()+120
  while time.monotonic()<deadline and len(arrivals)<6:
   for side in 'abcdef':
    if side in arrivals:continue
    value=task(side,'const s=await hostSessionCase.group.snapshot();return {head:s.head,counts:params[0].map(t=>s.state.messages.filter(x=>x.text===t).length)};',[texts])
    if value['counts']==[1,1,1]:arrivals[side]={'at':round(time.time()*1000),'head':value['head']}
   time.sleep(.2)
  r['burst']={'scheduledAt':sendAt,'arrivals':arrivals,'senders':{side:js(side,'return burstResult;') for side in 'aef'},'scope':'Local six browsers, four validators with quorum three; three senders; real RTC.'}
  check('all three concurrent originals arrive exactly once on six browsers',len(arrivals)==6)
  check('all validators and observers agree on the same verified head',len({v['head'] for v in arrivals.values()})==1)
  check('all three senders queued their originals',all('queued' in v and 'error' not in v for v in r['burst']['senders'].values()))
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,syncFailures:hostSessionCase.syncFailures,scratch:await hostSessionCase.scratchStats(),memberTrace:hostSessionCase.memberTrace,memberAuth:hostSessionCase.memberAuth,stats:await hostSessionCase.stats(),channel:await hostSessionCase.group?.snapshot(),delayedSignaling:hostSessionCase.delayedSignalingSawHello,handshakeStates:hostSessionCase.handshakeStates,links:desktopNetwork.appContext().pool.list().map(p=>{const l=desktopNetwork.appContext().pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,active:l.activeOperations};})};')
   except Exception as x:r[side+'DiagnosticError']=str(x)
 finally:
  for side,sid in sessions.items():
   try:
    cleanup=task(side,'await hostSessionCase.closeAll();return {owner:hostSessionCase.owner().stats(),network:(await hostSessionCase.stats()).network.budget};');r[side+'Cleanup']=cleanup;assert cleanup['owner']['tasks']==0 and cleanup['owner']['members']['tasks']==0 and cleanup['owner']['members']['responses']==0 and cleanup['owner']['scheduler']=={'closed':True,'channels':0,'timers':0,'deadlines':0,'jobs':0};assert all(v==0 for k,v in cleanup['network'].items() if k!='closed')
   except Exception as e:r.update(status='FAIL',cleanupSide=side,cleanupError=str(e))
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r[side+'BrowserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for profile in profiles.values():shutil.rmtree(profile)
  tmp.cleanup();r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists(),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--credits',action='store_true');p.add_argument('--output',required=True,type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core,a.credits);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
