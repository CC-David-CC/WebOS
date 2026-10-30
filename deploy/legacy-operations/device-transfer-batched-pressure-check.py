#!/usr/bin/env python3
"""Two isolated real Chromes, authenticated PeerPool RTC, resumable signed history.

Native device storage and browser SIGKILL, real Web Crypto identities and channel
signatures. Solo channel validator has zero Byzantine fault tolerance. Provider
remains alive while reader restarts. Loopback static HTTP serves fixture code;
manual out-of-band offer/answer through WebDriver, no history/identity backend,
no live changes, no outside WAN/TURN/v86/8k or multi-replica liveness claim.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,re,shutil,signal,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('peer_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(compiled=None):
 started=time.monotonic();sessions={};processes={};profiles={};server=None;thread=None;checks=[];tmp=tempfile.TemporaryDirectory(prefix='codi-device-peer-');folder=Path(tmp.name)
 result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserLaunches':0,'maximumConcurrentBrowsers':2,'actualRTCLinks':0,'actualV86Desktops':0,'productionChanged':False,'permissionOverride':'CDP persistent-storage','outOfBandSignaling':'WebDriver passes actual signed offer/answer between isolated browsers'}
 fixture='scripts/fixtures/device-peer-transfer-page.mjs';files=set()
 def include(name):
  if name in files:return
  path=ROOT/name;assert path.is_file(),name;files.add(name)
  if path.suffix=='.mjs':
   for specifier in re.findall(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]",path.read_text()):
    if specifier.startswith('.'):
     target=(path.parent/specifier).resolve();assert target.is_relative_to(ROOT);include(str(target.relative_to(ROOT)))
 include(fixture);payloads={n:(ROOT/n).read_bytes() for n in sorted(files)};pins={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),**{n:hashlib.sha256(b).hexdigest() for n,b in payloads.items()}}
 fixtureSource=payloads[fixture].decode();marker='window.fixtureReady=true;';assert fixtureSource.count(marker)==1;fixtureSource=fixtureSource.replace(marker,'const originalTrim=DeviceChannelDownloadCache.prototype.trim;DeviceChannelDownloadCache.prototype.trim=function(...args){window.trimCount=(window.trimCount||0)+1;return originalTrim.apply(this,args);};const originalRequest=DevicePeerSync.prototype.requestNode;DevicePeerSync.prototype.requestNode=async function(...args){if(window.throttleBulk)await new Promise(r=>setTimeout(r,80));return originalRequest.apply(this,args);};'+marker);payloads[fixture]=fixtureSource.encode();result['instrumentedFixtureSHA256']=hashlib.sha256(payloads[fixture]).hexdigest()
 candidate=ROOT/'.build/candidates/transfer-batched-trim/network/device-channel-transfer.mjs';payloads['network/device-channel-transfer.mjs']=candidate.read_bytes();result['candidateSHA256']=hashlib.sha256(payloads['network/device-channel-transfer.mjs']).hexdigest();result['candidateScope']='Only transfer implementation substituted; shipped source unchanged'
 def js(side,code,args=[]):return d.call('/session/'+sessions[side]+'/execute/sync',{'script':code,'args':args})
 def task(side,code,args=[]):
  v=d.call('/session/'+sessions[side]+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def start(side):
  if side not in profiles:profiles[side]=Path(tempfile.mkdtemp(prefix='codi-device-peer-'+side+'-',dir=Path.home()/'snap/chromium/common'))
  opened=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profiles[side])]}}}});sessions[side]=opened['sessionId'];pid=opened['capabilities']['goog:processID'];processes[side]=(pid,(Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]);result['actualBrowserLaunches']+=1
  d.call('/session/'+sessions[side]+'/timeouts',{'script':180000});d.call('/session/'+sessions[side]+'/url',{'url':origin+'/?side='+side});d.wait(lambda:js(side,'return window.fixtureReady===true;'),15)
 def consent(side):
  d.call('/session/'+sessions[side]+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  d.wait(lambda:js(side,'return window.storageReady===true||!document.querySelector(".storage-consent button").disabled;'),10)
  if not js(side,'return window.storageReady===true;'):
   e=d.call('/session/'+sessions[side]+'/element',{'using':'css selector','value':'.storage-consent button'});d.call('/session/'+sessions[side]+'/element/'+e['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
  d.wait(lambda:js(side,'return window.storageReady===true;'),15)
 def connect():
  offer=task('provider','const r=await peerFixture.pool.offer();return {id:r.entry.id,token:r.token};');answer=task('reader','const r=await peerFixture.pool.answer(params[0]);return {id:r.entry.id,token:r.token};',[offer['token']]);task('provider','return peerFixture.pool.accept(params[0],params[1]);',[offer['id'],answer['token']])
  for side in ['provider','reader']:
   d.wait(lambda:js(side,'return !!peerFixture.pool.firstReady()?.link.deviceApplicationReady;'),20);js(side,'peerFixture.instrument(arguments[0]);',[offer['id'] if side=='provider' else answer['id']])
  result['actualRTCLinks']+=1;return offer['id'],answer['id']
 def download(offer,options={}):return task('reader','return peerFixture.startDownload(params[0],params[1]);',[offer,options])
 try:
  for n,b in payloads.items():p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  if compiled:
   catalog=json.loads((compiled/'apps.json').read_bytes());assert len(catalog['apps'])==1;app=catalog['apps'][0];assert app['id']=='replica-core';source=compiled/Path(app['path']).parent.relative_to('assets/desktop');target=folder/'compiled-core';target.mkdir()
   for name,record in app['files'].items():
    data=(source/name).read_bytes();assert Path(name).name==name and record=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};(target/name).write_bytes(data)
   text=(folder/fixture).read_text()
   imports=re.findall(r"from '([^']+)'",text)
   for old in imports:
    if old.endswith('/crypto.mjs') or old.endswith('/device-peer-external-pool.mjs'):continue
    assert text.count("'"+old+"'")==1;text=text.replace("'"+old+"'","'../../compiled-core/index.mjs'")
   (folder/fixture).write_text(text);result.update(actualCompiledCoreSHA256=app['sha256'],compiledCatalogSHA256=hashlib.sha256((compiled/'apps.json').read_bytes()).hexdigest(),servedFixtureSHA256=hashlib.sha256(text.encode()).hexdigest())
  (folder/'index.html').write_text('<!doctype html><title>Owned peer history transfer</title><main id="gate"></main><script type="module" src="scripts/fixtures/device-peer-transfer-page.mjs"></script>')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  for side in ['provider','reader']:start(side);check(side+' opens no history/key/cache database before native storage acceptance',task(side,'return (await indexedDB.databases()).length===0;'));consent(side)
  provider=task('provider','return peerFixture.setup();');reader=task('reader','return peerFixture.setup();');task('reader','return peerFixture.configure(params[0]);',[provider['config']]);offer=task('provider','return peerFixture.produce(3);');old_p,old_r=connect()
  check('isolated browser sessions use distinct authenticated peer keys',provider['public']['key']!=reader['public']['key'])
  check('content requests require a current read grant even on a ready authenticated RTC link',task('reader',"try{await peerFixture.sync.requestNode(peerFixture.pool.firstReady(),params[0].channel,params[0].genesisHash,params[0].history);return false;}catch(e){return e.message.includes('current read grant');}",[offer]))
  grant=task('provider','return peerFixture.grant(params[0]);',[reader['public']['key']]);foreign=task('provider','return peerFixture.grant(params[0]);',[provider['public']['key']]);expired=task('provider','return peerFixture.expiredGrant(params[0]);',[reader['public']['key']])
  for token in [foreign,expired]:
   rid=os.urandom(16).hex();task('reader','return peerFixture.pool.firstReady().link.sendDeviceApplication({op:"open",channel:params[0].channel,genesisHash:params[0].genesisHash,grant:params[1],request_id:params[2]});',[offer,token,rid]);d.wait(lambda:js('reader','return inbound.some(e=>e.op==="error"&&e.request===arguments[0]);',[rid]),10)
  rid=os.urandom(16).hex();task('reader','return peerFixture.pool.firstReady().link.sendDeviceApplication({op:"get",channel:params[0].channel,genesisHash:params[0].genesisHash,node:params[0].history,request_id:params[1]});',[offer,rid]);d.wait(lambda:js('reader','return inbound.some(e=>e.op==="error"&&e.request===arguments[0]);',[rid]),10)
  check('provider rejects wrong-peer and expired grants plus ungranted raw RTC reads before touching content',js('provider','return nodeReadCount===0&&peerFixture.sync.stats().inboundGrants===0&&peerFixture.sync.stats().rejected>=3;'))
  checks.extend(task('reader','return peerFixture.negative(params[0],params[1]);',[grant,foreign]))
  interrupted=download(offer,{'abortAfter':6});first_requested=js('reader','return requested;')
  check('partial chunks commit durably while acceptance remains at the original floor',not interrupted['ok'] and interrupted['cache']['nodes']==6 and interrupted['floor']['height']==0 and interrupted['cache']['status']=='incomplete-unaccepted-cache')
  retained={'actor':reader['actor']};pid,ticks=processes['reader'];proc=Path('/proc')/str(pid);args=(proc/'cmdline').read_bytes().replace(b'\0',b' ').split();assert ('--user-data-dir='+str(profiles['reader'])).encode() in args and not any(a.startswith(b'--type=') for a in args) and os.readlink(proc/'exe').endswith('/chrome') and (proc/'stat').read_text().rsplit(')',1)[1].split()[19]==ticks
  os.kill(pid,signal.SIGKILL);d.call('/session/'+sessions.pop('reader'),method='DELETE');result['ownedReaderCrash']={'pid':pid,'startTicks':ticks,'signal':'SIGKILL','afterUnacceptedChunkCommits':True};js('provider','peerFixture.pool.closeEntry(arguments[0],"Owned departed reader cleanup");',[old_p]);start('reader');result['postCrashStorageStatus']=task('reader','return peerFixture.policy.status();');consent('reader');reader2=task('reader','return peerFixture.setup(params[0]);',[retained]);task('reader','return peerFixture.configure(params[0]);',[provider['config']]);connect()
  check('a read grant cannot be replayed by a new browser transport key',task('reader',"try{await peerFixture.sync.open(peerFixture.pool.firstReady(),params[0],params[1]);return false;}catch(e){return e.message.includes('wrong-peer');}",[grant,provider['config']]))
  grant2=task('provider','return peerFixture.grant(params[0]);',[reader2['public']['key']]);task('reader','return peerFixture.sync.open(peerFixture.pool.firstReady(),params[0],params[1]);',[grant2,provider['config']]);resumed=download(offer);new_requested=js('reader','return requested;')
  check('fresh Chrome and a new authenticated connection resume the exact durable partial graph',resumed['ok'] and resumed['result']['position']['head']==offer['head'] and resumed['stats']['cachedNodes']>=6)
  check('resume requests only missing nodes instead of retransmitting retained chunks',not set(first_requested)&set(new_requested) and len(new_requested)>0)
  counts=task('reader','return peerFixture.downloadCounts();');check('accepted transfer removes all unaccepted scratch nodes and job accounting',counts['nodes']==counts['jobs']==counts['totals']['bytes']==counts['totals']['nodes']==0)
  offer4=task('provider','return peerFixture.produce(1);');bad=task('provider','return peerFixture.invalidOffer();');invalid=download(bad)
  check('correctly hashed malicious block chunks cannot bypass signed authorization replay',not invalid['ok'] and invalid['floor']['height']==3 and 'author authorization' in invalid['error'])
  task('reader','return peerFixture.cache.trim([],{removeJob:true});');js('provider','window.fault={poison:true};');poisoned=download(offer4)
  check('a bad response hash is rejected before durable chunk storage or floor advancement',not poisoned['ok'] and poisoned['floor']['height']==3 and poisoned['cache']['nodes']==0)
  js('provider','window.fault=null;');repaired=download(offer4);check('a subsequent valid peer response repairs the interrupted transfer',repaired['ok'] and repaired['result']['position']['height']==4)
  offer5=task('provider','return peerFixture.produce(1);');capped=download(offer5,{'maxNodes':1})
  check('scratch capacity refusal preserves the accepted floor and honest partial cache',not capped['ok'] and capped['name']=='DeviceDownloadCapacity' and capped['floor']['height']==4 and capped['cache']['nodes']==1)
  task('provider',"return peerFixture.pool.firstReady().link.send('independent peer message while history is capped');");d.wait(lambda:js('reader',"return window.independentMessage==='independent peer message while history is capped';"),10);check('capacity refusal leaves the shared peer connection usable',True)
  repaired=download(offer5);check('raising the per-download allowance resumes the same retained target',repaired['ok'] and repaired['result']['position']['height']==5)
  offer6=task('provider','return peerFixture.produce(1);');js('provider','window.fault={drop:true};');timed=download(offer6)
  check('a missing response times out and releases request slots without advancing acceptance',not timed['ok'] and 'timed out' in timed['error'] and timed['floor']['height']==5 and js('reader','return peerFixture.sync.stats().pending===0&&peerFixture.budget().repairJobs===0;'))
  js('provider','window.fault=null;');fixed=download(offer6);check('retry after timeout repairs the same offered history',fixed['ok'] and fixed['result']['position']['height']==6)
  offer7=task('provider','return peerFixture.produce(1);');js('provider','window.fault={hold:true};');js('reader','window.longDownload=null;peerFixture.startDownload(arguments[0]).then(v=>window.longDownload=v);',[offer7]);d.wait(lambda:js('provider','return window.fault.held===true;'),10);js('reader','peerFixture.transfer.close();');closed=d.wait(lambda:js('reader','return window.longDownload;'),10)
  check('closing a transfer cancels pending work while keeping the shared peer service alive',not closed['ok'] and closed['floor']['height']==6 and js('reader','return !peerFixture.sync.stats().closed&&peerFixture.sync.stats().pending===0&&peerFixture.pool.firstReady().link.deviceApplicationReady;'))
  js('provider','window.fault.release();window.fault=null;');d.wait(lambda:js('provider','return peerFixture.sync.stats().serving===0;'),10)
  check('late verified bytes from a closed transfer cannot advance the archive',task('reader','return (await peerFixture.archive.load()).position.height===6;'))
  fixed=download(offer7);check('a new transfer over the same shared connection recovers after view closure',fixed['ok'] and fixed['result']['position']['height']==7)
  offer8=task('provider','return peerFixture.produce(1);');js('provider','window.fault={hold:true};');js('reader','window.longDownload=null;peerFixture.startDownload(arguments[0]).then(v=>window.longDownload=v);',[offer8]);d.wait(lambda:js('provider','return window.fault.held===true;'),10);sourceEntry=js('provider','return peerFixture.pool.firstReady().id;');readerEntry=js('reader','return peerFixture.pool.firstReady().id;');js('reader','peerFixture.pool.closeEntry(arguments[0],"Owned link loss while requesting content");',[readerEntry]);disconnected=d.wait(lambda:js('reader','return window.longDownload;'),10)
  check('link loss promptly rejects pending reads and preserves the retained accepted floor',not disconnected['ok'] and disconnected['floor']['height']==7 and js('reader','return peerFixture.sync.stats().pending===0;'))
  js('provider','peerFixture.pool.closeEntry(arguments[0],"Owned disconnected link cleanup");window.fault.release();window.fault=null;',[sourceEntry]);d.wait(lambda:js('provider','return peerFixture.sync.stats().serving===0;'),10);connect();task('reader','return peerFixture.sync.open(peerFixture.pool.firstReady(),params[0],params[1]);',[grant2,provider['config']]);fixed=download(offer8)
  check('a fresh authenticated RTC path repairs the same incomplete target after disconnection',fixed['ok'] and fixed['result']['position']['height']==8)
  legacy=task('provider','return peerFixture.legacyOffer();');legacyAnswer=task('reader','const v=await peerFixture.pool.answer(params[0]);return {id:v.entry.id,token:v.token};',[legacy['token']]);task('provider','return peerFixture.legacyPool.accept(params[0],params[1]);',[legacy['id'],legacyAnswer['token']]);d.wait(lambda:js('reader','return peerFixture.pool.get(arguments[0]).state==="ready";',[legacyAnswer['id']]),20);result['actualRTCLinks']+=1
  check('a legacy peer negotiates its ordinary connection without implicitly enabling device history',task('reader','const e=peerFixture.pool.get(params[0]);try{await e.link.sendDeviceApplication({op:"get"});return false;}catch(e){return e.message.includes("not negotiated");}',[legacyAnswer['id']]))
  task('provider','return peerFixture.legacyPool.firstReady().link.send("ordinary legacy peer remains usable");');d.wait(lambda:js('reader','return window.independentMessage==="ordinary legacy peer remains usable";'),10);js('reader','peerFixture.pool.closeEntry(arguments[0],"Owned legacy compatibility test finished");',[legacyAnswer['id']]);legacyBudget=task('provider','return peerFixture.closeLegacy();')
  check('closing the legacy test preserves the existing content link and releases its separate budget',all(v==0 for k,v in legacyBudget.items() if k!='closed') and js('reader','return peerFixture.pool.firstReady().link.deviceApplicationReady&&peerFixture.budget().connections===1;'))
  check('thirty peer content service reopens return shared metadata accounting to the warm baseline',task('reader','return peerFixture.serviceReopens();'))
  check('an independently imported pool and budget receive the actual transfer service resource charges',task('reader','return peerFixture.externalPoolBudget();'))
  offer9=task('provider','return peerFixture.produce(1);');js('reader','window.fault={outgoingHold:true};window.longDownload=null;peerFixture.startDownload(arguments[0]).then(v=>window.longDownload=v);',[offer9]);d.wait(lambda:js('reader','return window.fault.held===true;'),10);heldTimeout=d.wait(lambda:js('reader','return window.longDownload;'),10)
  check('request timeout remains effective while the underlying send is still pending',not heldTimeout['ok'] and 'timed out' in heldTimeout['error'] and heldTimeout['floor']['height']==8 and js('reader','return peerFixture.sync.stats().pending===0&&peerFixture.budget().repairJobs===0;'))
  js('reader','window.fault.release();window.fault=null;');d.wait(lambda:js('provider','return peerFixture.sync.stats().serving===0;'),10);fixed=download(offer9);check('late outbound work is isolated by request nonce and a fresh retry still converges',fixed['ok'] and fixed['result']['position']['height']==9)
  result['reader']=task('reader','return peerFixture.finalChecks(params[0]);',[offer9]);checks.extend(result['reader']['checks']);result['provider']=task('provider','return {service:peerFixture.sync.stats(),budget:peerFixture.budget(),wireMax:Math.max(0,...sentFrames)};')
  check('every signed RTC wire frame respects the existing 32768-byte bound',result['reader']['wireMax']<=32768 and result['provider']['wireMax']<=32768)
  js('reader','window.throttleBulk=true;');bulk=task('provider','return peerFixture.produce(12);');js('reader','window.trimCount=0;');batch=download(bulk);result['bulkResult']=batch;result['bulkTrimCalls']=js('reader','return window.trimCount;')
  check('twelve-block catch-up batches scratch cleanup',batch['ok'] and batch['result']['position']['height']==21 and js('reader','return window.trimCount;')==3)
  limited=task('provider','return peerFixture.produce(12);');js('reader','window.trimCount=0;');recovered=download(limited,{'maxNodes':20});result['pressureResult']=recovered;result['pressureTrimCalls']=js('reader','return window.trimCount;')
  check('scratch pressure trims and resumes without losing verified history',recovered['ok'] and recovered['result']['position']['height']==33 and js('reader','return window.trimCount>3;'))
  result['status']='PASS'
 except Exception as e:
  result.update(error=str(e),traceback=traceback.format_exc())
  for side in sessions:
   try:result[side+'Failure']=js(side,'return {checks:peerFixture?.checks,gate:document.querySelector("#gate").innerText,progress:progress.slice(-4),fault:fault&&{held:fault.held},inbound:inbound.slice(-4)};')
   except Exception as diagnostic:result[side+'DiagnosticError']=str(diagnostic)
 finally:
  for side,sid in list(sessions.items()):
   try:result[side+'Cleanup']=task(side,'return peerFixture.close();')
   except Exception as e:result[side+'CleanupError']=str(e)
   if side+'Cleanup' in result:
    cleanup=result[side+'Cleanup']
    if not all(v==0 for k,v in cleanup['network'].items() if k!='closed') or cleanup['sync']['pending'] or cleanup['sync']['serving']:
     result.update(status='FAIL',error='Owned shared network resources remain charged after cleanup',cleanupSide=side)
   try:d.call('/session/'+sid,method='DELETE')
   except Exception as cleanup_error:result.update(status='FAIL',error='Owned browser cleanup failed',cleanupError=str(cleanup_error))
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  for p in profiles.values():shutil.rmtree(p)
  tmp.cleanup();result.update(ownedBrowsersClosed=True,ownedProfilesRemoved=all(not p.exists() for p in profiles.values()),fixtureRemoved=not folder.exists())
 result.update(elapsedSeconds=round(time.monotonic()-started,3),sourceSHA256=pins,sourceUnchangedThroughoutRun=all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==pin for n,pin in pins.items()))
 if not result['sourceUnchangedThroughoutRun']:result.update(status='FAIL',error='Source changed during run; receipt binds its actual served snapshot')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiled-core',type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.compiled_core);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(0 if r['status']=='PASS' else 1)
