#!/usr/bin/env python3
"""Activity delivery hints suppress echoes without granting acceptance or losing wakeups.

Four native Chrome/IDB/ECDSA/RTC profiles; explicit pulses and leader cut.
No automatic topology, v86, byte-credit shaper or WAN claim.

Owned local-development identities and native storage; no v86/server account/
history backend/live mutation. Manual out-of-band signaling and explicit round
actions, not automatic mesh/election or an8k/WAN/liveness claim.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,re,shutil,signal,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('replica_net_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled=None):
 sessions={};profiles={};processes={};server=None;thread=None;checks=[];tmp=tempfile.TemporaryDirectory(prefix='codi-compact-status-');folder=Path(tmp.name);started=time.monotonic()
 r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserLaunches':0,'maximumConcurrentBrowsers':4,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'identity':'Local / not server validated','nativeStoragePermissionControl':'CDP with actual Storage API/IDB','wholeGoalComplete':False}
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def wait(side,code,args=[],seconds=30):return d.wait(lambda:js(side,code,args),seconds)
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-replica-net-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]},'goog:loggingPrefs':{'browser':'ALL'}}}});sessions[side]=v['sessionId'];pid=v['capabilities']['goog:processID'];processes[side]=(pid,(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);r['actualBrowserLaunches']+=1;d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side});wait(side,'return window.fixtureReady===true;')
 def approve(side):
  d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});wait(side,'return window.storageReady===true||!document.querySelector(".storage-consent button").disabled;')
  if not js(side,'return window.storageReady===true;'):
   e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':'.storage-consent button'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sessions[side]+'/element/'+e+'/click',{})
  wait(side,'return window.storageReady===true;')
 def connect(a,b):
  offer=task(a,'const v=await replicaNetwork.pool.offer();return {id:v.entry.id,token:v.token};');answer=task(b,'const v=await replicaNetwork.pool.answer(params[0]);return {id:v.entry.id,token:v.token};',[offer['token']]);task(a,'return replicaNetwork.pool.accept(params[0],params[1]);',[offer['id'],answer['token']])
  for side,pid in [(a,offer['id']),(b,answer['id'])]:wait(side,'return !!replicaNetwork.pool.get(arguments[0])?.link.deviceReplicaReady;',[pid]);js(side,'replicaNetwork.instrument(arguments[0]);',[pid])
  r['actualRTCLinks']+=1;return {a:offer['id'],b:answer['id']}
 def bind(a,b,links):return task(a,'return replicaNetwork.exchange.bind(replicaNetwork.pool.get(params[0]),replicaNetwork.config);',[links[a]])
 def statuses():return {side:task(side,'return replicaNetwork.status();') for side in sessions}
 try:
  files=set();fixture='scripts/fixtures/device-replica-network-page.mjs'
  def include(name):
   if name in files:return
   p=ROOT/name;assert p.is_file(),name;files.add(name)
   for specifier in re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]",p.read_text()):
    if specifier.startswith('.'):
     path=(p.parent/specifier).resolve();assert path.is_relative_to(ROOT);include(str(path.relative_to(ROOT)))
  include(fixture);r['sourceSHA256']={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
  for n in sorted(files):
   data=(ROOT/n).read_bytes();r['sourceSHA256'][n]=hashlib.sha256(data).hexdigest();p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
  page=folder/fixture;text=page.read_text();assert text.count('deviceInlineValues:false')==1;text=text.replace('deviceInlineValues:false','deviceInlineValues:true')
  original='round=new DeviceReplicaRound({actor,policy,replica,archive,exchange,pool});';replacement='window.activityWakeups=0;window.activityWakeAttempts=0;window.activityRuntime={maxViewMs:600000,clearHint(){this.hint=null;}};round=new DeviceReplicaRound({actor,policy,replica,archive,exchange,pool,onActivity:value=>{activityWakeAttempts++;if(window.failNextActivityWake){window.failNextActivityWake=false;throw Error("Owned activity hint resource refusal");}activityRuntime.hint=value;activityWakeups++;}});';assert text.count(original)==1;text=text.replace(original,replacement);page.write_text(text);r['inlineValuesEnabled']=True;r['activityPulseScope']='Manual native round pulses with a ten-minute view timer; current leader transport cut, native voting/acceptance only after explicit view change.'
  if compiled:
   catalog=json.loads((compiled/'apps.json').read_bytes());app=catalog['apps'][0];assert len(catalog['apps'])==1 and app['id']=='replica-core';target=folder/'compiled-core';target.mkdir();src=compiled/Path(app['path']).parent.relative_to('assets/desktop')
   for n,record in app['files'].items():
    data=(src/n).read_bytes();assert Path(n).name==n and record=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};(target/n).write_bytes(data)
   p=folder/fixture;text=p.read_text()
   for old in re.findall(r"from '([^']+)'",text):
    if old.endswith('/crypto.mjs'):continue
    text=text.replace("'"+old+"'","'../../compiled-core/index.mjs'")
   p.write_text(text);r['actualCompiledCoreSHA256']=app['sha256']
  (folder/'index.html').write_text('<!doctype html><title>Owned remote replica quorum</title><main id="gate"></main><script type="module" src="scripts/fixtures/device-replica-network-page.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  actors={}
  for side in 'abcd':start(side);check(side+' starts no signing or channel database before consent',task(side,'return (await indexedDB.databases()).length===0;'));approve(side);actors[side]=task(side,'return replicaNetwork.setup();')['actor']
  config=task('a','return replicaNetwork.create(params[0]);',[list(actors.values())]);policies=[task(side,'return replicaNetwork.configure(params[0]);',[config]) for side in 'abcd'];check('four isolated native validator keys share one pinned3of4 policy',len(set(actors.values()))==4 and all(p=={'quorum':3,'faults':1} for p in policies))
  links={}
  for i,a in enumerate('abcd'):
   for b in 'abcd'[i+1:]:links[a+b]=connect(a,b)
  check('six actual RTC links separately negotiate the replica protocol',all(js(side,'return replicaNetwork.pool.list().filter(e=>e.state==="ready").length===3;') for side in 'abcd'))
  check('ordinary authenticated transport is insufficient without durable validator binding',task('a','try{await replicaNetwork.exchange.call(replicaNetwork.pool.get(params[0]),replicaNetwork.config,"status",{});return false;}catch(e){return e.message.includes("fresh validator binding");}',[links['ab']['a']]))
  for pair,ids in links.items():bind(pair[0],pair[1],ids)
  check('reciprocal link-bound proofs map each peer to distinct configured durable actors',all(task(side,'return replicaNetwork.exchange.members(params[0].channel,params[0].genesisHash).length===3;',[config]) for side in 'abcd'))
  check('the actual status benchmark negotiates the inline-value transport used by the application',all(js(side,'return replicaNetwork.pool.list().every(p=>replicaNetwork.pool.get(p.id).link.deviceInlineValuesReady);') for side in sessions))
  ordered=sorted(actors,key=lambda side:actors[side]);offline=ordered[0];source=ordered[-1];others=[p for p in ordered if p not in [offline,source]];left,right=others
  for pair,ids in links.items():
   if offline in pair:
    for side,pid in ids.items():js(side,'replicaNetwork.pool.closeEntry(arguments[0]);',[pid])
  def path(a,b):return links[''.join(sorted([a,b]))][a]
  def pulse(side,batch_ms=0):return task(side,'return replicaNetwork.round.maintain(activityRuntime,{signal:new AbortController().signal,viewMs:600000,rpcMs:5000,batchLimit:16,publishAfter:performance.now()+params[0],withDeadline:(parent,_ms,job)=>job(parent)});',[batch_ms])
  def counts():return {p:js(p,'return {activity:replicaInvokes.activity||0,wakeups:activityWakeups,attempts:activityWakeAttempts};') for p in [source,left,right]}
  def activity_count():return sum(p['activity'] for p in counts().values())
  records=task(source,'window.activityRecords=await replicaNetwork.records(Array.from({length:8},(_,i)=>"Deduplicated original "+i));return activityRecords;')
  def traffic():return {p:js(p,'return {status:replicaInvokes.status||0,activity:replicaInvokes.activity||0,bytes:replicaFrames.reduce((a,b)=>a+b,0)};') for p in [source,left,right]}
  before=traffic();batch_pulses=[pulse(source,10000) for _ in range(3)];after=traffic();r['localBatching']={'before':before,'after':after,'pulses':batch_pulses}
  check('a held local batch stays pending without polling status or sending activity',before==after and all(p['phase']=='batching-on-device' and p['height']==0 for p in batch_pulses) and task(source,'return (await replicaNetwork.archive.pending({limit:16})).length===8;'))
  poisoned=json.loads(json.dumps(records));parts=poisoned[0]['authorization'].split('.');parts[2]=('A' if parts[2][0]!='A' else 'B')+parts[2][1:];poisoned[0]['authorization']='.'.join(parts)
  negative=task(source,'try{await replicaNetwork.exchange.call(replicaNetwork.pool.get(params[0]),replicaNetwork.config,"activity",{records:params[1]});return false;}catch(error){return error.code==="unavailable";}',[path(source,left),poisoned])
  check('a correctly transported batch with an invalid author authorization cannot wake a voter or advance its native state',negative and js(left,'return activityWakeups===0;') and task(left,'return (await replicaNetwork.status()).height===0;'))
  before=activity_count();pulse(source);check('the original source wakes both surviving voters while the designated leader is disconnected',activity_count()==before+2 and all(js(p,'return activityWakeups===1&&activityRuntime.hint.records.length===8;') for p in others))
  incoming_before=traffic();pulse(left,10000);incoming_after=traffic();r['incomingActivityWhileBatching']={'before':incoming_before,'after':incoming_after}
  check('validated incoming activity reconciles immediately even with a future local publish time',sum(v['status'] for v in incoming_after.values())>sum(v['status'] for v in incoming_before.values()))
  pulse(left);pulse(right);r['initialActivityDelivery']=counts();r['initialValidActivityCalls']=activity_count()-before
  check('validated source and successful receipt knowledge avoid echoing the same full batch across every directed edge',r['initialValidActivityCalls']==3)
  r['beforeRepeatedPulses']=activity_count()
  for p in [source,left,right,source,left,right]:pulse(p)
  check('new authorization signatures for the same ordered originals do not rebroadcast or repeatedly wake the same batch',activity_count()==r['beforeRepeatedPulses'] and all(js(p,'return activityWakeups===1;') for p in others))
  task(source,'return replicaNetwork.records(["A ninth original keeps the first eight IDs"]);');pulse(source);pulse(left);pulse(right)
  check('growing a batch with the same first original still delivers the newly added original',all(js(p,'return activityRuntime.hint.records.length===9&&activityWakeups===2;') for p in others))
  pair=''.join(sorted([source,left]));old_path=links[pair]
  for p,pid in old_path.items():js(p,'replicaNetwork.pool.closeEntry(arguments[0]);',[pid])
  links[pair]=connect(pair[0],pair[1]);bind(pair[0],pair[1],links[pair]);before=counts();pulse(source);after=counts();r['afterFreshConnection']=after
  check('a new authenticated transport is told the batch again without duplicating the receiver wakeup',after[left]['activity']==before[left]['activity']+1 and after[right]['activity']==before[right]['activity'] and after[left]['wakeups']==2)
  task(source,'return replicaNetwork.records(["A tenth original exercises refusal and acknowledgement retry"]);');js(left,'window.failNextActivityWake=true;');before=counts();pulse(source);after=counts();r['wakeRefusal']=after
  check('a receiver hint-capacity refusal is not remembered as a completed wakeup or acceptance',after[left]['attempts']==before[left]['attempts']+1 and after[left]['wakeups']==before[left]['wakeups'] and task(left,'return (await replicaNetwork.status()).height===0;'))
  started=time.monotonic();before=activity_count();pulse(source);elapsed=time.monotonic()-started;r['immediateRetryMs']=round(elapsed*1000,3)
  check('an immediately repeated native pulse respects bounded activity-delivery backoff',elapsed<.9 and activity_count()==before)
  time.sleep(1.2);js(left,'const node=replicaNetwork.node,invoke=node.invoke;window.corruptNextActivityReceipt=true;node.invoke=async(method,value,options)=>{const result=await invoke(method,value,options);if(method==="activity"&&corruptNextActivityReceipt){corruptNextActivityReceipt=false;return {...result,head:"invalid"};}return result;};');before=counts();pulse(source);after=counts()
  check('retrying after capacity becomes available installs the original full hint exactly once',after[left]['activity']==before[left]['activity']+1 and after[left]['wakeups']==before[left]['wakeups']+1 and js(left,'return activityRuntime.hint.records.length===10;'))
  time.sleep(2.2);before=counts();pulse(source);after=counts()
  check('a malformed receipt cannot suppress a later valid activity delivery',after[left]['activity']==before[left]['activity']+1 and after[left]['wakeups']==before[left]['wakeups'])
  before=activity_count();pulse(source);check('a successful reported receipt suppresses further redundant delivery on that exact connection',activity_count()==before)
  check('delivery receipts and wakeups alone never create an accepted block or vote',all(task(p,'const s=await replicaNetwork.status();return s.height===0&&!s.prepareVote&&!s.commitVote;') for p in [source,left,right]))
  expected=task(source,'return (await replicaNetwork.archive.pending({limit:16,order:"queued"})).map(p=>p.id);');r['expectedOriginalIds']=expected
  for p in [source,left,right]:task(p,'return replicaNetwork.round.advance(1);')
  before=counts();pulse(source);after=counts();state=statuses();r['nativeAfterNewView']=state
  check('a new native view renews activity delivery and the surviving real quorum accepts every original once',all(after[p]['activity']>before[p]['activity'] for p in others) and all(state[p]['height']==1 and state[p]['count']==10 and [m['id'] for m in state[p]['messages']]==expected for p in [source,left,right]) and len({state[p]['head'] for p in [source,left,right]})==1)
  check('the disconnected validator remains at its old accepted floor rather than being counted as a voter',state[offline]['height']==0 and state[offline]['count']==0)
  for p in sessions:wait(p,'const s=replicaNetwork.exchange.stats();return s.pending===0&&s.jobs===0&&s.responses===0&&s.valueBytes===0;')
  check('activity retries and native consensus leave bounded wires and no retained reply/value leases',all(js(p,'return replicaFrames.length>0&&Math.max(...replicaFrames)<=32768;') for p in sessions))
  r['status']='PASS'
 except Exception as error:
  r.update(error=str(error),traceback=traceback.format_exc())
  for side in sessions:
   try:r[side+'Diagnostic']=task(side,'return {text:document.body.innerText,status:typeof replicaNetwork!=="undefined"?await replicaNetwork.status():null,peers:typeof replicaNetwork!=="undefined"?replicaNetwork.pool.list().map(p=>{const l=replicaNetwork.pool.get(p.id).link;return {...p,status:l.status,pc:l.pc?.connectionState,channel:l.channel?.readyState,sentHello:l.sentHello,receivedHello:l.receivedHello,tx:l.tx,rx:l.rx,pendingSend:l.pendingSend,pendingReceive:l.pendingReceive,active:l.activeOperations};}):null};')
   except Exception as e:r[side+'DiagnosticError']=str(e)
 finally:
  for side,sid in sessions.items():
   try:
    r[side+'Cleanup']=task(side,'return replicaNetwork.close();')
    if any(value!=0 for key,value in r[side+'Cleanup']['network'].items() if key!='closed'):r.update(status='FAIL',error='Owned replica network cleanup retained resource charges',cleanupSide=side)
   except Exception as e:r[side+'CleanupError']=str(e)
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r[side+'BrowserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for profile in profiles.values():shutil.rmtree(profile)
  tmp.cleanup();r.update(ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists())
 r['elapsedSeconds']=round(time.monotonic()-started,3);return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
