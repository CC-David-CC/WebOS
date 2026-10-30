#!/usr/bin/env python3
"""Native same-profile tabs contend for durable device/channel allowances.

Real Chrome persistent storage, IndexedDB, native keys, additive v1->v2
migration and owned SIGKILL/reopen. This is not an RTC, WAN or throughput test.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,shutil,signal,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('durable_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(current,legacy):
 checks=[];r={'status':'FAIL','scope':__doc__,'checks':checks,'actualProfiles':1,'actualBrowserLaunches':0,'maximumConcurrentTabs':2,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'wholeGoalComplete':False};sid=None;tmp=tempfile.TemporaryDirectory(prefix='codi-durable-traffic-');folder=Path(tmp.name);profile=Path(tempfile.mkdtemp(prefix='codi-durable-traffic-',dir=Path.home()/'snap/chromium/common'));server=None;thread=None;started=time.monotonic()
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error?.stack||String(error)}));','args':args});assert v['ok'],v;return v.get('value')
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def switch(handle):d.call('/session/'+sid+'/window',{'handle':handle})
 def ready(legacy=False):
  d.call('/session/'+sid+'/url',{'url':origin+('/?legacy=1' if legacy else '/')});d.wait(lambda:js('return window.fixtureReady===true;'),20)
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  if not js('return window.storageReady===true;'):
   e=d.call('/session/'+sid+'/element',{'using':'css selector','value':'button'})['element-6066-11e4-a52e-4f735466cecf'];d.call('/session/'+sid+'/element/'+e+'/click',{})
  d.wait(lambda:js('return window.storageReady===true;'),20)
 def launch():
  nonlocal sid
  v=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}});sid=v['sessionId'];r['actualBrowserLaunches']+=1;d.call('/session/'+sid+'/timeouts',{'script':45000});pid=v['capabilities']['goog:processID'];r.setdefault('ownedBrowserProcesses',[]).append({'pid':pid,'startTicks':(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]});return pid
 try:
  for name,artifact in [('current-core',current),('old-core',legacy)]:
   catalog=json.loads((artifact/'apps.json').read_bytes());app=catalog['apps'][0];src=artifact/Path(app['path']).parent.relative_to('assets/desktop');target=folder/name;target.mkdir()
   for n,row in app['files'].items():
    b=(src/n).read_bytes();assert row=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()};(target/n).write_bytes(b)
   r['actualCompiledCoreSHA256' if name=='current-core' else 'legacyCompiledCoreSHA256']=app['sha256']
  fixture=ROOT/'scripts/fixtures/device-traffic-ledger-page.mjs';target=folder/'scripts/fixtures';target.mkdir(parents=True);shutil.copyfile(fixture,target/fixture.name);r['sourceSHA256']={str(fixture.relative_to(ROOT)):hashlib.sha256(fixture.read_bytes()).hexdigest()};r['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
  (folder/'index.html').write_text('<!doctype html><button disabled>Accept storage</button><script type="module" src="scripts/fixtures/device-traffic-ledger-page.mjs"></script>');server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  pid=launch();ready(True);oldtab=d.call('/session/'+sid+'/window',method='GET');before=task('return trafficCase.prepare();');configs=before['configs'];check('legacy code creates real native keys and bookmarks in the original three-store schema',before['raw']['version']==1 and len(before['raw']['tables'])==3 and len(before['raw']['rows'])==2)
  tab=d.call('/session/'+sid+'/window/new',{'type':'tab'})['handle'];switch(tab);ready();after=task('return trafficCase.prepare(params[0]);',[configs]);check('additive schema upgrade preserves every existing bookmark byte and native actor',after['raw']['version']==2 and len(after['raw']['tables'])==5 and after['raw']['rows']==before['raw']['rows'] and after['keys']==before['keys'])
  switch(oldtab);check('an actual old directory connection retires on the native versionchange event',task('try{await trafficCase.directory.get(params[0]);return false;}catch{return true;}',[configs[0]['channel']]))
  ready();task('return trafficCase.prepare(params[0]);',[configs]);check('a second live tab sees the same persistent global policy',task('return (await trafficCase.snapshot(0)).global.limits.uploadBytes===5000;'))
  js('window.firstWave=Promise.all(Array.from({length:6},(_,i)=>trafficCase.reserve(i%2,{upload:1000}).then(()=>true,()=>false)));');switch(tab);js('window.secondWave=Promise.all(Array.from({length:6},(_,i)=>trafficCase.reserve(i%2,{upload:1000}).then(()=>true,()=>false)));');second=task('return secondWave;');switch(oldtab);first=task('return firstWave;');snap=task('return trafficCase.snapshot(0);');r['concurrentReservation']={'first':first,'second':second,'global':snap['global']}
  check('twelve actual concurrent reservations across two tabs and channels cannot multiply the global allowance',sum(first+second)==5 and snap['global']['allocated']['upload']==5000)
  local=task('return [await trafficCase.snapshot(0),await trafficCase.snapshot(1)];');check('per-channel durable totals sum to the shared device total',sum(v['channel']['allocated']['upload'] for v in local)==5000)
  stale=snap['global']['version'];task('return trafficCase.setGlobal({uploadBytes:1000});');switch(tab);check('a stale tab reads current global limits and cannot reserve against its old policy',task('try{await trafficCase.reserve(1,{upload:1});return false;}catch{return (await trafficCase.snapshot(1)).global.allocated.upload===5000;}'))
  check('global limit edits require an exact version and preserve previously charged usage',task('try{await trafficCase.ledger.setGlobalLimits(trafficCase.globalLimits,{expected:params[0]});return false;}catch(e){return e.name==="DeviceTrafficPolicyConflict";}',[stale]));task('return trafficCase.setGlobal({uploadBytes:10000});')
  check('a failed combined upload and serving reservation commits neither counter',task('const before=await trafficCase.snapshot(0);try{await trafficCase.reserve(0,{upload:1,serve:3001});return false;}catch{const after=await trafficCase.snapshot(0);return after.global.allocated.upload===before.global.allocated.upload&&after.global.allocated.serve===0;}'))
  allocation=task('return Promise.all([trafficCase.reserve(0,{download:3072},{minDownload:512}),trafficCase.reserve(1,{download:3072},{minDownload:512})]);');check('concurrent download grants share the remaining allowance instead of overissuing credits',sorted(v['charged']['download'] for v in allocation)==[1024,3072] and task('return (await trafficCase.snapshot(0)).global.allocated.download===4096;'))
  task('const old=await trafficCase.directory.get(params[0]);return trafficCase.directory.setTrafficLimits(params[0],{...trafficCase.localLimits,uploadBytes:0},{expected:old.version});',[configs[0]['channel']]);switch(oldtab);check('fresh per-channel settings are checked in the same transaction even when another tab cached larger limits',task('try{await trafficCase.reserve(0,{upload:1},{fallback:{...trafficCase.localLimits,uploadBytes:100000}});return false;}catch{return (await trafficCase.snapshot(0)).channel.limits.uploadBytes===0;}'))
  saved=task('const old=await trafficCase.directory.get(params[0]);return trafficCase.directory.forget(params[0],{expected:old.version});',[configs[1]['channel']]);check('removing a shortcut cannot erase the channel or global reservation totals',saved and task('return (await trafficCase.snapshot(1)).global.allocated.upload===5000;'))
  task('const q=indexedDB.open("codi-device-channel-directory-v1");await new Promise((resolve,reject)=>{q.onerror=()=>reject(q.error);q.onsuccess=()=>{const db=q.result,tx=db.transaction(["trafficPolicy","trafficUsage"],"readwrite",{durability:"strict"}),st=tx.objectStore("trafficPolicy");trafficCase.hold=true;trafficCase.blockDone=new Promise(r=>tx.oncomplete=()=>{db.close();r();});const spin=()=>{const read=st.get("device");read.onsuccess=()=>{if(trafficCase.hold)spin();};};spin();resolve();};});const original=IDBDatabase.prototype.transaction;trafficCase.restoreTransaction=()=>IDBDatabase.prototype.transaction=original;IDBDatabase.prototype.transaction=function(names,mode,...rest){const tx=original.call(this,names,mode,...rest);if(mode==="readwrite"&&Array.from(names).includes("trafficUsage"))trafficCase.reservationQueued=true;return tx;};trafficCase.cancel=new AbortController();trafficCase.pending=trafficCase.reserve(1,{upload:1},{signal:trafficCase.cancel.signal}).then(()=>false,()=>true);return true;')
  d.wait(lambda:js('return trafficCase.reservationQueued===true;'),10);js('trafficCase.cancel.abort(Error("Owned cancellation"));trafficCase.hold=false;trafficCase.restoreTransaction();')
  check('cancelling a real queued strict transaction cannot mint or consume a reservation',task('await trafficCase.blockDone;return await trafficCase.pending&&(await trafficCase.snapshot(0)).global.allocated.upload===5000;'))
  check('shortening the accounting window does not erase active charged usage',task('const before=await trafficCase.snapshot(0);await trafficCase.setGlobal({windowMs:1000});const after=await trafficCase.snapshot(0);return after.global.allocated.upload===before.global.allocated.upload&&after.global.allocated.until>=before.global.allocated.until;'))
  check('switching local account scope shares the same device-wide budget rather than creating another allowance',task('const other=await new trafficCase.core.DeviceTrafficLedger({scope:"owned-other-account",limits:{...trafficCase.globalLimits,uploadBytes:1000000}}).open(trafficCase.permit);try{await other.reserve(trafficCase.configs[0].channel,trafficCase.configs[0].genesisHash,{upload:1000});return (await trafficCase.snapshot(0)).global.allocated.upload===6000;}finally{other.close();await other.idle();}'))
  before_crash=task('return trafficCase.snapshot(0);');proc=Path('/proc')/str(pid);args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').split();assert ('--user-data-dir='+str(profile)).encode() in args and not any(a.startswith(b'--type=') for a in args) and os.readlink(proc/'exe').endswith('/chrome') and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==r['ownedBrowserProcesses'][-1]['startTicks'];os.kill(pid,signal.SIGKILL);d.call('/session/'+sid,method='DELETE');sid=None;r['ownedCrashSignal']='SIGKILL';launch();ready();restored=task('return trafficCase.prepare(params[0]);',[configs]);snap=task('return trafficCase.snapshot(0);');check('a real browser process crash and reopen preserves device usage, limits and native signing actors',snap['global']['allocated']==before_crash['global']['allocated'] and snap['global']['limits']==before_crash['global']['limits'] and restored['keys']==before['keys'])
  check('already allocated download data cannot be granted again after restart',task('try{await trafficCase.reserve(1,{download:1});return false;}catch{return (await trafficCase.snapshot(1)).global.allocated.download===4096;}'))
  task('trafficCase.ledger.close();await trafficCase.ledger.idle();const q=indexedDB.open("codi-device-channel-directory-v1");await new Promise((resolve,reject)=>{q.onerror=()=>reject(q.error);q.onsuccess=()=>{const db=q.result,tx=db.transaction("trafficUsage","readwrite",{durability:"strict"});tx.objectStore("trafficUsage").delete(["device"]);tx.oncomplete=()=>{db.close();resolve();};tx.onabort=()=>reject(tx.error);};});return true;')
  check('missing durable global usage fails closed rather than silently minting a new allowance',task('try{await new trafficCase.core.DeviceTrafficLedger({scope:trafficCase.scope}).open(trafficCase.permit);return false;}catch{return (await trafficCase.raw()).rows.length===1;}'))
  r['status']='PASS'
 except Exception as e:r.update(error=str(e),traceback=traceback.format_exc())
 finally:
  if sid:
   try:
    for handle in d.call('/session/'+sid+'/window/handles',method='GET'):
     switch(handle);result=task('return window.trafficCase?.close();');assert not result or result['jobs']==0
    r['allLedgerJobsDrained']=True
   except Exception as e:r.update(status='FAIL',cleanupError=str(e))
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as e:r['browserCleanupError']=str(e)
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  shutil.rmtree(profile);tmp.cleanup();r.update(ownedProfileRemoved=not profile.exists(),fixtureRemoved=not folder.exists(),elapsedSeconds=round(time.monotonic()-started,3))
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--compiled-core',type=Path,required=True);p.add_argument('--legacy-core',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core,a.legacy_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error'),'cleanupError':r.get('cleanupError')}));raise SystemExit(r['status']!='PASS')
