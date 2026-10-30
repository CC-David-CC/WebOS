#!/usr/bin/env python3
"""Compact/full validator status reads over genuine signed RTC, including legacy fallback.

Wire-size comparison uses the same prepared state and explicit rounds; no
automatic topology, byte-credit shaper or WAN claim.

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
  page=folder/fixture;text=page.read_text();assert text.count('deviceInlineValues:false')==1;page.write_text(text.replace('deviceInlineValues:false','deviceInlineValues:true'));r['inlineValuesEnabled']=True
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
  ordered=sorted(actors,key=lambda side:actors[side]);leader=ordered[0];reader=ordered[-1];pair=''.join(sorted([leader,reader]));path=links[pair][reader]
  prepared=task(leader,'return replicaNetwork.stageWithheldPrepared("A retained value survives compact reconciliation hints");');r['preparedHead']=prepared['head']
  def settled():
   for side in sessions:wait(side,'const s=replicaNetwork.exchange.stats();return s.pending===0&&s.jobs===0&&s.responses===0&&s.valueBytes===0;')
  def wire_total():return sum(js(side,'return replicaFrames.reduce((n,v)=>n+v,0);') for side in sessions)
  def read_status(value):
   settled();before=wire_total();reply=task(reader,'return replicaNetwork.exchange.call(replicaNetwork.pool.get(params[0]),replicaNetwork.config,"status",params[1]);',[path,value]);settled();return reply,wire_total()-before
  full,full_bytes=read_status({});brief,brief_bytes=read_status({'brief':True});r['statusBytes']={'full':full_bytes,'brief':brief_bytes,'fullJSON':len(json.dumps(full,separators=(',',':')).encode()),'briefJSON':len(json.dumps(brief,separators=(',',':')).encode()),'scope':'Total signed RTC application bytes for each settled read across the same4profiles/prepared state; negotiated inline values enabled, no IP/RTC overhead.'}
  check('brief status retains actor, accepted position, round and view promise from the same prepared state',all(brief[k]==full[k] for k in ['actor','position','round','viewChange']) and brief['profile']=='codi-device-replica-status-hint/1')
  check('full status keeps its retained certificate and votes while the brief read omits those duplicates',bool(full['prepareVote']) and bool(full['commitVote']) and bool(full['prepared']) and not any(k in brief for k in ['prepareVote','commitVote','prepared']))
  check('actual settled brief read uses less than half the signed wire bytes of the full prepared-state read',0<brief_bytes<full_bytes/2)
  # Real legacy-shape provider: authenticated requests still traverse the real
  # exchange and native bindings; only the optional argument is refused.
  js(leader,'const node=replicaNetwork.node,invoke=node.invoke;window.statusReadCounts={brief:0,full:0};window.statusLegacy=true;node.invoke=(method,value,options)=>{if(method==="status"){if(value.brief===true){statusReadCounts.brief++;if(statusLegacy)throw Error("Owned legacy status accepts only empty arguments");}else statusReadCounts.full++;}return invoke(method,value,options);};')
  def pulse():return task(reader,'return replicaNetwork.round.maintain({maxViewMs:600000,clearHint(){}},{signal:new AbortController().signal,viewMs:600000,rpcMs:5000,withDeadline:(_parent,_ms,job)=>job(_parent)});')
  pulse();pulse();counts=js(leader,'return statusReadCounts;');r['legacyReadCounts']=counts
  check('automatic reconciliation probes a legacy transport once and then uses only the unchanged full read',counts=={'brief':1,'full':2} and task(reader,'return (await replicaNetwork.replica.status()).round===0;'))
  # After exact transport renewal, optional read support is discovered again.
  js(leader,'statusLegacy=false;')
  for side in pair:js(side,'replicaNetwork.pool.closeEntry(arguments[0]);',[links[pair][side]])
  links[pair]=connect(pair[0],pair[1]);bind(pair[0],pair[1],links[pair]);path=links[pair][reader];pulse();new_counts=js(leader,'return statusReadCounts;');r['renewedReadCounts']=new_counts
  check('a new authenticated transport probes brief support again without retaining a legacy downgrade by session name',new_counts['brief']==2 and new_counts['full']==2)
  liar=next(side for side in ordered if side not in [leader,reader]);js(liar,'const node=replicaNetwork.node,invoke=node.invoke;window.invalidBriefCalls=0;window.unexpectedFullCalls=0;node.invoke=async(method,value,options)=>{if(method==="status"){if(value.brief===true){invalidBriefCalls++;return {profile:"codi-device-replica-status-hint/1",actor:replicaNetwork.actor,position:{height:900,head:"A".repeat(43),count:900},round:900,viewChange:null};}unexpectedFullCalls++;}return invoke(method,value,options);};')
  pulse();check('a correctly signed high compact hint without native acceptance or view promises cannot advance the local floor or round',task(reader,'const s=await replicaNetwork.status();return s.height===0&&s.round===0;') and js(liar,'return invalidBriefCalls===1&&unexpectedFullCalls===0;'))
  js(liar,'const node=replicaNetwork.node,invoke=node.invoke;node.invoke=(method,value,options)=>method==="status"&&value.brief===true?Promise.resolve({profile:"wrong"}):invoke(method,value,options);');pulse()
  check('malformed compact hints are rejected without falling back to a larger full-state read',task(reader,'const s=await replicaNetwork.status();return s.height===0&&s.round===0;') and js(liar,'return unexpectedFullCalls===0;'))
  # Compact reads still carry genuine prepared view promises when present.
  task(leader,'return replicaNetwork.round.advance(1);');full,unused=read_status({});brief,unused=read_status({'brief':True})
  check('the brief read retains the exact signed prepared-view promise needed for recovery',bool(brief['viewChange']) and brief['viewChange']==full['viewChange'] and brief['round']==1)
  for side in sessions:
   if side!=leader:task(side,'return replicaNetwork.round.advance(1);')
  result=task(ordered[1],'return replicaNetwork.recover(1);');state=statuses();r['recovered']=result
  check('real retained-value and quorum recovery still accepts the original exactly once after compact reads',all(s['height']==1 and s['count']==1 and len(s['messages'])==1 for s in state.values()) and len({s['head'] for s in state.values()})==1)
  settled();check('every signed status/consensus wire stays bounded and transient reply/value leases drain',all(js(side,'return replicaFrames.length>0&&Math.max(...replicaFrames)<=32768;') and task(side,'return replicaNetwork.exchange.stats().values===0;') for side in sessions))
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
