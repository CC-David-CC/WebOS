#!/usr/bin/env python3
"""Real Chrome pending queue, full signed archive and compact sparse-tree checks.

One owned profile, two sequential real browser launches and actual SIGKILL.
Four logical keys/replicas share one browser; no actual RTC or v86. One archive
block uses the real durable replica engine. Later retention blocks use manual
fixture certificates; neither scale nor automatic network consensus is claimed.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,shutil,signal,tempfile,threading,time,traceback,subprocess,shlex,re,urllib.request,secrets
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('archive_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled_core=None):
 sid=None;browser=None;server=None;thread=None;driver_proc=None;tunnel=None;checks=[];tmp=tempfile.TemporaryDirectory(prefix='codi-archive-');folder=Path(tmp.name);profile=Path(subprocess.check_output(['ssh','-o','BatchMode=yes','maint@10.0.7.105','mktemp','-d','/tmp/codi-prefetch-XXXXXXXX'],text=True).strip());assert re.fullmatch(r'/tmp/codi-prefetch-[A-Za-z0-9]{8}',str(profile));pidfile='/tmp/codi-prefetch-driver-'+secrets.token_hex(8)+'.pid';started=time.monotonic()
 files=['network/device-content-node.mjs','network/device-replica.mjs','network/device-operation-tree.mjs','network/device-channel-state.mjs','network/device-operation-set.mjs','network/crypto.mjs','network/strict-json.mjs','network/chess-record.mjs','assets/vendor/chess/chess.mjs','assets/desktop/storage-consent.mjs','assets/desktop/device-key-database.mjs','assets/desktop/channel-keys.mjs','assets/desktop/controller-key-backup.mjs','assets/desktop/controller-backup-store.mjs','assets/desktop/experimental-recovery-archive-schema.mjs','assets/desktop/replica-journal.mjs','assets/desktop/replica-core.mjs','assets/desktop/channel-archive.mjs','scripts/fixtures/device-archive-page.mjs']
 payloads={n:(ROOT/n).read_bytes() for n in files};pins={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),**{n:hashlib.sha256(b).hexdigest() for n,b in payloads.items()}}
 source=payloads['assets/desktop/channel-archive.mjs'].decode();changes=[
 ('const current=await this.#current(s),block=blocks[0],wire=wires[0];','const __phase=globalThis.__archivePhases;let __t=performance.now();const current=await this.#current(s),block=blocks[0],wire=wires[0];if(__phase)__phase.load+=performance.now()-__t;'),
 ('const item=blocks[index];next=await protocol.acceptDeviceChannelBlock(next,item,{signal:s});','const item=blocks[index];__t=performance.now();next=await protocol.acceptDeviceChannelBlock(next,item,{signal:s});if(__phase)__phase.accept+=performance.now()-__t;'),
 ('const p=await protocol.readDeviceChannelProposal(r.proposal,this.#policy),added=await tree.insert(root,p.id,{signal:s});','__t=performance.now();const p=await protocol.readDeviceChannelProposal(r.proposal,this.#policy);if(__phase)__phase.proposal+=performance.now()-__t;__t=performance.now();const added=await tree.insert(root,p.id,{signal:s});if(__phase)__phase.tree+=performance.now()-__t;'),
 ('const answer=await this.#headTx(s,(st,done,fail)=>{','__t=performance.now();const answer=await this.#headTx(s,(st,done,fail)=>{'),
 ('// This exact checkpoint was just built from the already replayed, branded','if(__phase)__phase.commit+=performance.now()-__t;\n  // This exact checkpoint was just built from the already replayed, branded')]
 for old,new in changes:
  assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
 payloads['assets/desktop/channel-archive.mjs']=source.encode()
 baseline=os.environ.get('CODI_ARCHIVE_BASELINE');
 if baseline:payloads['assets/desktop/channel-archive.mjs']=Path(baseline).read_bytes()
 r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserLaunches':0,'maximumConcurrentBrowsers':1,'logicalReplicas':4,'actualPeerLinks':0,'actualV86Desktops':0,'productionChanged':False,'automaticTimeoutsTested':False,'permissionOverride':'CDP persistent-storage','instrumentedArchiveSHA256':hashlib.sha256(payloads['assets/desktop/channel-archive.mjs']).hexdigest()}
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def start():
  nonlocal sid,browser
  opened=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/usr/bin/chromium','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}});sid=opened['sessionId'];pid=opened['capabilities']['goog:processID'];browser=(pid,subprocess.check_output(['ssh','-o','BatchMode=yes','maint@10.0.7.105','cat','/proc/'+str(pid)+'/stat'],text=True).rsplit(')',1)[1].split()[19]);r['actualBrowserLaunches']+=1
  d.call('/session/'+sid+'/timeouts',{'script':600000});d.call('/session/'+sid+'/url',{'url':origin+'/'});d.wait(lambda:js('return window.fixtureReady===true;'),15)
 def accept_storage():
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  if js('return window.storageReady===true;'):return
  d.wait(lambda:js('return window.storageReady===true||!document.querySelector(".storage-consent button").disabled;'),10)
  if not js('return window.storageReady===true;'):
   e=d.call('/session/'+sid+'/element',{'using':'css selector','value':'.storage-consent button'});d.call('/session/'+sid+'/element/'+e['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
  d.wait(lambda:js('return window.storageReady===true;'),15)
 try:
  for n,data in payloads.items():
   if n=='assets/desktop/channel-archive.mjs' and os.environ.get('CODI_DISABLE_CANDIDATE_CACHE')=='1':
    old=b'this.#cacheVerifiedCheckpoint(checkpoint,next);return answer;';assert data.count(old)==1;data=data.replace(old,b'return answer;');r['servedArchiveMode']='without newly added cache'
   elif n=='assets/desktop/channel-archive.mjs':r['servedArchiveMode']='with newly added cache'
   q=folder/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
   if n=='assets/desktop/channel-archive.mjs':r['servedArchiveSHA256']=hashlib.sha256(data).hexdigest()
  if compiled_core:
   catalog=json.loads((compiled_core/'apps.json').read_bytes());assert len(catalog['apps'])==1;app=catalog['apps'][0];assert app['id']=='replica-core' and not app['styles'];source=compiled_core/Path(app['path']).parent.relative_to('assets/desktop');target=folder/'compiled-core';target.mkdir()
   for name,record in app['files'].items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts;data=(source/name).read_bytes();assert record=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
   fixture=folder/'scripts/fixtures/device-archive-page.mjs';text=fixture.read_text()
   for old in ['../../network/device-channel-state.mjs','../../network/device-replica.mjs','../../network/device-operation-tree.mjs','../../assets/desktop/channel-archive.mjs','../../assets/desktop/channel-keys.mjs','../../assets/desktop/storage-consent.mjs']:
    assert text.count("'"+old+"'")==1;text=text.replace("'"+old+"'","'../../compiled-core/index.mjs'")
   fixture.write_text(text);r.update(actualCompiledCoreSHA256=app['sha256'],compiledCatalogSHA256=hashlib.sha256((compiled_core/'apps.json').read_bytes()).hexdigest(),servedFixtureSHA256=hashlib.sha256(fixture.read_bytes()).hexdigest(),fixtureTransformation='Six protocol/archive/core/capability imports redirected together to the single verified compiled entry')
  fixture=folder/'scripts/fixtures/device-archive-page.mjs';text=fixture.read_text();marker=" archive.close();check('closed archive handles refuse further queue or history work'"
  test=""" let batchCursor=null,batchBlocks=[];do{const p=await archive.history({before:batchCursor,limit:9});batchBlocks.push(...p.entries.map(e=>e.block));batchCursor=p.next;}while(batchCursor);batchBlocks.reverse();
 const batchScope=scope+':batch-test',batchArchive=new DeviceChannelArchive({keys,scope:batchScope,...config});owned.add(batchArchive);await batchArchive.open(await policy.acquire());const firstPending=await batchArchive.enqueue(batchBlocks[0].operations[0].proposal),initial=await batchArchive.stats();
 const invalidBatch=structuredClone(batchBlocks.slice(0,2));invalidBatch[1].header.parent='A'.repeat(43);check('invalid later block aborts whole batch and preserves pending original',await refuses(()=>batchArchive.appendBatch(invalidBatch),'')&&(await batchArchive.load()).position.height===0&&(await batchArchive.pending())[0].id===firstPending.id&&JSON.stringify(await batchArchive.stats())===JSON.stringify(initial));
 const oldPutBatch=IDBObjectStore.prototype.put;let batchAborted=false;IDBObjectStore.prototype.put=function(value,...args){const q=oldPutBatch.call(this,value,...args);if(this.name==='heads'&&!batchAborted){batchAborted=true;this.transaction.abort();}return q;};try{check('interrupted batch commit fails',await refuses(()=>batchArchive.appendBatch(batchBlocks.slice(0,8)),''));}finally{IDBObjectStore.prototype.put=oldPutBatch;}check('interrupted batch leaves no nodes or acknowledgement',(await batchArchive.load()).position.height===0&&(await batchArchive.pending())[0].id===firstPending.id&&JSON.stringify(await batchArchive.stats())===JSON.stringify(initial)&&batchAborted);
 globalThis.__archivePhases={load:0,accept:0,proposal:0,tree:0,commit:0};const batchStarted=performance.now();for(let i=0;i<batchBlocks.length;i+=8)await batchArchive.appendBatch(batchBlocks.slice(i,i+8));window.archiveMetrics.batchApplyMs=Math.round(performance.now()-batchStarted);window.archiveMetrics.batchPhases=globalThis.__archivePhases;globalThis.__archivePhases=null;const batchFinal=await batchArchive.load();check('batched signed history reaches the identical verified head and acknowledges pending original',batchFinal.position.head===at.head&&batchFinal.position.height===at.height&&(await batchArchive.pending()).length===0);
 let batchCount=0,batchNext=null;do{const p=await batchArchive.history({before:batchNext,limit:9});batchCount+=p.entries.length;batchNext=p.next;}while(batchNext);check('batched signed history retains every block',batchCount===batchBlocks.length);
 const treeCount=await raw((tx,done)=>{let count=0;const q=tx.objectStore('nodes').index('domain').openCursor(IDBKeyRange.only([batchScope,config.channel]));q.onsuccess=()=>{const c=q.result;if(!c){done(count);return;}if(JSON.parse(c.value.wire).profile==='codi-operation-tree/1')count++;c.continue();};});check('batched commits prune obsolete tree nodes',treeCount===2*batchBlocks.length-1);batchArchive.close();
""";assert text.count(marker)==1;fixture.write_text(text.replace(marker,test+marker));r['fixtureTransformation']=r.get('fixtureTransformation','source modules')+'; tests atomic batches against signed archive history';r['servedFixtureSHA256']=hashlib.sha256(fixture.read_bytes()).hexdigest()
  (folder/'index.html').write_text('<!doctype html><title>Durable channel archive test</title><main id="gate"></main><script type="module" src="scripts/fixtures/device-archive-page.mjs"></script>')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  driver_proc=subprocess.Popen(['ssh','-o','BatchMode=yes','maint@10.0.7.105','umask 077; echo $$ > '+shlex.quote(pidfile)+'; exec /usr/bin/chromedriver --port=19557 --allowed-ips=127.0.0.1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  tunnel=subprocess.Popen(['ssh','-o','BatchMode=yes','-o','ExitOnForwardFailure=yes','-N','-L','127.0.0.1:19557:127.0.0.1:19557','-R','127.0.0.1:19559:127.0.0.1:'+str(server.server_port),'maint@10.0.7.105'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);d.DRIVER='http://127.0.0.1:19557'
  def ready():
   if driver_proc.poll() is not None or tunnel.poll() is not None:raise RuntimeError('Remote browser tunnel stopped')
   try:
    with urllib.request.urlopen(d.DRIVER+'/status',timeout=1) as response:return json.load(response)['value']['ready']
   except OSError:return False
  d.wait(ready,25);origin='http://127.0.0.1:19559';start()
  assert task('return (await indexedDB.databases()).length===0;');checks.append('no key/history database opens before explicit device storage acceptance');accept_storage()
  js('archiveFixture.begin().catch(e=>window.beginError=e.stack);')
  def held():
   error=js('return window.beginError||null;');assert not error,error;return js('return window.pendingPhase==="durable-original";')
  d.wait(held,30);retained=js('return window.crashPublic;');checks.append('pending original is strictly committed before actual browser termination')
  pid,ticks=browser;kill_code='import os,sys; from pathlib import Path; p=Path("/proc")/sys.argv[1]; args=(p/"cmdline").read_bytes().replace(bytes([0]),b" ").split(); assert ("--user-data-dir="+sys.argv[3]).encode() in args and not any(x.startswith(b"--type=") for x in args) and (p/"stat").read_text().rsplit(")",1)[1].split()[19]==sys.argv[2]; os.kill(int(sys.argv[1]),9)'
  subprocess.run(['ssh','-o','BatchMode=yes','maint@10.0.7.105','python3','-c',shlex.quote(kill_code),str(pid),str(ticks),shlex.quote(str(profile))],check=True,timeout=15);d.call('/session/'+sid,method='DELETE');sid=None;r['ownedBrowserCrash']={'pid':pid,'startTicks':ticks,'signal':'SIGKILL','afterStrictPendingCommit':True};start()
  r['postCrashStorageStatus']=task('return archiveFixture.policy.status();');accept_storage()
  js('archiveFixture.finish(arguments[0]).then(()=>window.runResult={ok:true},e=>window.runResult={ok:false,error:e.stack});',[retained]);seen=0
  def done():
   nonlocal seen
   names=js('return archiveFixture.checks;')
   for name in names[seen:]:print(json.dumps({'check':name}),flush=True)
   seen=len(names);return js('return window.runResult;')
  value=d.wait(done,600);checks.extend(js('return archiveFixture.checks;'));assert value['ok'],value;r.update(status='PASS',archiveMetrics=js('return window.archiveMetrics;'))
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:r['browserFailure']=js('return {result:window.runResult,beginError:window.beginError,checks:window.archiveFixture?.checks,gate:document.querySelector("#gate").innerText};')
   except Exception as diagnostic:r['diagnosticError']=str(diagnostic)
 finally:
  if sid:
   try:js('archiveFixture.close();')
   except Exception as e:r['cleanupError']=str(e)
   d.call('/session/'+sid,method='DELETE');r['ownedBrowserClosed']=True
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  tmp.cleanup()
  for child in (tunnel,driver_proc):
   if child:
    child.terminate()
    try:child.wait(5)
    except subprocess.TimeoutExpired:child.kill();child.wait()
  cleanup='import os,re,shutil,signal,sys; from pathlib import Path; p=Path(sys.argv[1]); f=Path(sys.argv[2]); assert re.fullmatch(r"/tmp/codi-prefetch-[A-Za-z0-9]{8}",str(p)) and re.fullmatch(r"/tmp/codi-prefetch-driver-[0-9a-f]{16}[.]pid",str(f)); pid=int(f.read_text()) if f.exists() else 0; cmd=Path("/proc")/str(pid)/"cmdline"; os.kill(pid,signal.SIGTERM) if pid and cmd.exists() and b"chromedriver" in cmd.read_bytes() else None; f.unlink(missing_ok=True); shutil.rmtree(p) if p.exists() else None'
  subprocess.run(['ssh','-o','BatchMode=yes','maint@10.0.7.105','python3','-c',shlex.quote(cleanup),shlex.quote(str(profile)),shlex.quote(pidfile)],check=True,timeout=30);r.update(fixtureRemoved=not folder.exists(),ownedProfileRemoved=True)
 r.update(elapsedSeconds=round(time.monotonic()-started,3),sourceSHA256=pins,sourceUnchangedThroughoutRun=all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==pin for n,pin in pins.items()))
 if not r['sourceUnchangedThroughoutRun']:r.update(status='FAIL',error='Source changed during the run; receipt binds its served snapshot.')
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiled-core',type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(0 if r['status']=='PASS' else 1)
