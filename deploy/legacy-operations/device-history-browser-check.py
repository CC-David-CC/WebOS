#!/usr/bin/env python3
"""Real Chrome persistence decisions, cancellable consent UI and signed IDB history.

Owned loopback origin/browser only, zero v86/production changes. CDP explicitly
sets browser storage permission for native grant/denial tests; no physical phone
permission-popup claim. Additional controlled failure branches are labeled.
The signed fixture is not the final channel consensus/authorization protocol.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,os,shutil,signal,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('history_driver',ROOT/'scripts/touch-preview-check.py');d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run():
 checks=[];sid=None;server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-device-history-');folder=Path(tmp.name)
 profile=Path(tempfile.mkdtemp(prefix='codi-device-history-',dir=Path.home()/'snap/chromium/common'))
 result={'status':'FAIL','scope':__doc__,'checks':checks,'productionChanged':False,'actualBrowsers':0,'maximumConcurrentBrowsers':1,'maximumConcurrentTabs':2,'actualV86Desktops':0,'permissionOverride':'CDP Browser.setPermission persistent-storage','fullChannelProtocolImplemented':False}
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def cdp(command,params):return d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':command,'params':params})
 def click(selector):
  element=d.call('/session/'+sid+'/element',{'using':'css selector','value':selector});d.call('/session/'+sid+'/element/'+element['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def rejected(code,name,args=[]):return task('try{'+code+';return false;}catch(e){return '+json.dumps(name)+'===e.name||'+json.dumps(name)+'===e.code||e.message.includes('+json.dumps(name)+');}',args)
 try:
  for name in ['storage-consent.mjs','channel-journal.mjs']:shutil.copyfile(ROOT/'assets/desktop'/name,folder/name)
  for name in ['crypto.mjs','strict-json.mjs']:shutil.copyfile(ROOT/'network'/name,folder/name)
  shutil.copyfile(ROOT/'scripts/device-history-page.mjs',folder/'fixture.mjs')
  (folder/'index.html').write_text('<!doctype html><title>Device history test</title><div id="gate"></div><div id="feature"></div><input aria-label="Independent editor"><script type="module" src="fixture.mjs"></script>')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(folder)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];result['actualBrowsers']+=1;d.call('/session/'+sid+'/timeouts',{'script':90000});d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.fixtureReady===true;'),15)
  cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'denied','origin':origin})
  task('await storageTest.init();return true;');js('storageTest.gate()');d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10)
  check('no storage prompt, marker, history database or feature activation before acceptance',task('return storageTest.starts===0&&localStorage.length===0&&(await indexedDB.databases()).length===0;'))
  click('.storage-consent button');d.wait(lambda:js('return document.querySelector("[role=status]").textContent.includes("did not grant");'),15)
  check('actual browser denial leaves feature disabled and no consent/history writes',task('return !(await navigator.storage.persisted())&&storageTest.starts===0&&localStorage.length===0&&(await indexedDB.databases()).length===0;'))
  js('storageTest.gate()');d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10)
  click('.storage-consent button:nth-of-type(2)')
  check('declining device storage never starts chat or opens history',task('return storageTest.starts===0&&localStorage.length===0&&(await indexedDB.databases()).length===0&&document.querySelector("[role=status]").textContent.includes("stays unavailable");'))
  js('storageTest.gate()');d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10)
  check('forged storage capability cannot open the journal',rejected('const j=new storageTest.DeviceChannelJournal({verify:storageTest.verify});await j.open({version:"codi-persistent-device-storage/1"});','consent-required'))
  cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin})
  check('an origin grant alone is insufficient without explicit application consent',rejected('await storageTest.policy.acquire();','consent-required'))
  click('.storage-consent button');d.wait(lambda:js('return storageTest.starts===1;'),15)
  check('trusted acceptance click receives real native browser persistence and enables once',task('return await navigator.storage.persisted()&&localStorage.getItem("codi-device-history-consent-v1")==="accepted-v1"&&storageTest.starts===1;'))
  task('storageTest.j=await storageTest.open();storageTest.wire1=await storageTest.packet();storageTest.saved=await storageTest.j.save("account-a",storageTest.channel,storageTest.wire1,{expected:null});return true;')
  check('complete signed content is stored durably under its device/account/channel scope',task('const v=await storageTest.j.load("account-a",storageTest.channel);return v.wire===storageTest.wire1&&v.floor.count===1&&await storageTest.j.load("account-b",storageTest.channel)===null;'))
  check('a signed packet for another account is rejected before storage',rejected('await storageTest.j.save("account-b",storageTest.channel,storageTest.wire1,{expected:null});','Wrong signed history scope'))
  check('signature or signed-content corruption is refused',rejected('const w=storageTest.wire1;const parts=w.split(".");parts[2]=(parts[2][0]==="A"?"B":"A")+parts[2].slice(1);await storageTest.j.save("account-a",storageTest.channel,parts.join("."),{expected:storageTest.saved.hash});','Signature verification failed'))
  task('storageTest.j2=await storageTest.open();storageTest.wire2=await storageTest.packet({count:2,text:"Next signed checkpoint",previous:storageTest.saved.hash});storageTest.wire3=await storageTest.packet({count:2,text:"Competing signed checkpoint",previous:storageTest.saved.hash});const results=await Promise.allSettled([storageTest.j.save("account-a",storageTest.channel,storageTest.wire2,{expected:storageTest.saved.hash}),storageTest.j2.save("account-a",storageTest.channel,storageTest.wire3,{expected:storageTest.saved.hash})]);storageTest.race={successes:results.filter(r=>r.status==="fulfilled").length,conflicts:results.filter(r=>r.status==="rejected"&&r.reason.name==="DeviceJournalConflict").length};return storageTest.race;')
  check('concurrent independent store connections atomically commit one head and reject the competing view',js('return storageTest.race.successes===1&&storageTest.race.conflicts===1;'))
  task('storageTest.winner=await storageTest.j.load("account-a",storageTest.channel);return true;')
  check('stale writes cannot roll back a newer device checkpoint',rejected('await storageTest.j.save("account-a",storageTest.channel,storageTest.wire1,{expected:storageTest.winner.hash});','DeviceJournalConflict'))
  check('retrying the identical accepted snapshot is idempotent',task('const r=await storageTest.j.save("account-a",storageTest.channel,storageTest.winner.wire,{expected:storageTest.saved.hash});return r.idempotent===true;'))
  task('storageTest.limited=await storageTest.open({channelBytes:4096,totalBytes:8192,maxChannels:2,maxScopeChannels:1});storageTest.otherChannel=await (await import("./crypto.mjs")).hash("another device channel");storageTest.second=await storageTest.packet({channel:storageTest.otherChannel});return true;')
  check('per-account channel limits reject only the extra write',rejected('await storageTest.limited.save("account-a",storageTest.otherChannel,storageTest.second,{expected:null});','DeviceJournalCapacity'))
  task('storageTest.accountB=await storageTest.packet({scope:"account-b"});storageTest.savedB=await storageTest.limited.save("account-b",storageTest.channel,storageTest.accountB,{expected:null});return true;')
  check('another account can save within the independent scope limit',task('return (await storageTest.limited.load("account-b",storageTest.channel)).wire===storageTest.accountB;'))
  check('total channel allowance refuses growth without deleting retained history',rejected('const wire=await storageTest.packet({scope:"account-c"});await storageTest.limited.save("account-c",storageTest.channel,wire,{expected:null});','DeviceJournalCapacity'))
  task('storageTest.byteLimited=await storageTest.open({channelBytes:4096,totalBytes:4096});storageTest.largeWire=await storageTest.packet({scope:"account-c",text:"x".repeat(1800)});return true;')
  check('aggregate byte accounting refuses a valid signed snapshot at the configured budget',rejected('await storageTest.byteLimited.save("account-c",storageTest.channel,storageTest.largeWire,{expected:null});','DeviceJournalCapacity'))
  task('storageTest.cancelLife=new AbortController();let resume;const verify=storageTest.verify;storageTest.cancelJournal=await storageTest.open({verify:async(...args)=>{await new Promise(r=>resume=r);return verify(...args);}});storageTest.cancelWire=await storageTest.packet({scope:"account-c"});storageTest.cancelDone=storageTest.cancelJournal.save("account-c",storageTest.channel,storageTest.cancelWire,{expected:null,signal:storageTest.cancelLife.signal}).then(()=>({saved:true}),e=>({saved:false,name:e.name}));storageTest.resumeVerify=()=>resume();return true;')
  d.wait(lambda:js('return typeof storageTest.resumeVerify==="function";'),5)
  js('storageTest.beforeCancel=performance.now();storageTest.cancelLife.abort(new DOMException("Account changed","AbortError"));storageTest.cancelJournal.close();')
  check('closing an account view during proof verification cannot commit its stale operation',task('const r=await storageTest.cancelDone;const elapsed=performance.now()-storageTest.beforeCancel;storageTest.resumeVerify();return !r.saved&&r.name==="AbortError"&&elapsed<1000&&await storageTest.j.load("account-c",storageTest.channel)===null;'))
  task('await storageTest.limited.remove("account-b",storageTest.channel,{expected:storageTest.savedB.hash});storageTest.limited.close();storageTest.byteLimited.close();return true;')
  retained=js('return {publicKey:storageTest.publicKey,channel:storageTest.channel,wire:storageTest.winner.wire,hash:storageTest.winner.hash};')
  js('storageTest.close()');d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.fixtureReady===true;'),15);js('storageTest.publicKey=arguments[0].publicKey;storageTest.channel=arguments[0].channel;storageTest.gate();',[retained]);d.wait(lambda:js('return storageTest.starts===1;'),15)
  check('full page reload retains explicit consent and opens history without re-prompting',task('storageTest.j=await storageTest.open();const r=await storageTest.j.load("account-a",storageTest.channel);return r.wire===params[0].wire&&r.hash===params[0].hash&&r.floor.count===2;',[retained]))
  # Kill only the exact owned browser process, retaining its test-only profile.
  # Strict IDB transaction completion preceded this browser-process crash.
  candidates=[]
  for proc in Path('/proc').glob('[0-9]*'):
   try:
    args=(proc/'cmdline').read_bytes().split(b'\0')
    if any(('--user-data-dir='+str(profile)).encode() in a for a in args) and not any(b'--type=' in a for a in args) and os.readlink(proc/'exe').endswith('/chrome'):candidates.append((int(proc.name),(proc/'stat').read_text().rsplit(')',1)[1].split()[19]))
   except (FileNotFoundError,ProcessLookupError,PermissionError):pass
  assert len(candidates)==1,candidates
  pid,ticks=candidates[0];assert (Path('/proc')/str(pid)/'stat').read_text().rsplit(')',1)[1].split()[19]==ticks
  os.kill(pid,signal.SIGKILL);d.call('/session/'+sid,method='DELETE');sid=None
  result['ownedBrowserCrash']={'pid':pid,'startTicks':ticks,'signal':'SIGKILL','profileOwned':True}
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--user-data-dir='+str(profile)]}}}})['sessionId'];result['actualBrowsers']+=1
  d.call('/session/'+sid+'/timeouts',{'script':90000});d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.fixtureReady===true;'),15);js('storageTest.publicKey=arguments[0].publicKey;storageTest.channel=arguments[0].channel;storageTest.gate();',[retained])
  post_crash=task('return await storageTest.policy.status();');result['postCrashNativeStorageStatus']=post_crash
  if post_crash['state']!='ready':
   check('fresh browser rechecks persistence instead of trusting a pre-crash permission override',js('return storageTest.starts===0;'))
   cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin})
   d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10);click('.storage-consent button')
  d.wait(lambda:js('return storageTest.starts===1;'),15)
  check('actual browser-process crash preserves committed signed content in the owned device profile',task('storageTest.j=await storageTest.open();const r=await storageTest.j.load("account-a",storageTest.channel);return r.hash===params[0].hash&&r.wire===params[0].wire;',[retained]))
  task('storageTest.j.close();await storageTest.raw((rows,meta,done)=>{const q=meta.get("totals");q.onsuccess=()=>{const r=q.result;r.bytes++;meta.put(r);done(true);};});return true;')
  check('corrupted aggregate accounting refuses reopen without resetting history',rejected('await storageTest.open();','accounting changed'))
  task('await storageTest.raw((rows,meta,done)=>{const q=meta.get("totals");q.onsuccess=()=>{const r=q.result;r.bytes--;meta.put(r);done(true);};});storageTest.j=await storageTest.open();return true;')
  check('stale explicit removal cannot erase a newer checkpoint',rejected('await storageTest.j.remove("account-a",storageTest.channel,{expected:"0".repeat(64)});','DeviceJournalConflict'))
  # Deliberate checksum corruption; schema/accounting remain valid. Proof reads
  # must refuse it rather than render text or silently replace retained state.
  task('await storageTest.raw((rows,meta,done)=>{const q=rows.get(["account-a",storageTest.channel]);q.onsuccess=()=>{const r=q.result;r.hash="0".repeat(64);rows.put(r);done(true);};});return true;')
  check('corrupted saved bytes/checksum fail closed on read',rejected('await storageTest.j.load("account-a",storageTest.channel);','checksum mismatch'))
  task('await storageTest.raw((rows,meta,done)=>{const q=rows.get(["account-a",storageTest.channel]);q.onsuccess=()=>{const r=q.result;r.hash=params[0].hash;rows.put(r);done(true);};});return true;',[retained])
  # Bound refusal preserves the accepted document and does not open a network.
  check('per-channel size refusal preserves the old snapshot',rejected('await storageTest.j.save("account-a",storageTest.channel,"x".repeat(8*1048576+1),{expected:params[0].hash});','too large',[retained]))
  original_window=d.call('/session/'+sid+'/window')
  other_window=d.call('/session/'+sid+'/window/new',{'type':'tab'})['handle'];d.call('/session/'+sid+'/window',{'handle':other_window});d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.fixtureReady===true;'),15);js('storageTest.policy.forget();storageTest.close();');d.call('/session/'+sid+'/window',None,'DELETE');d.call('/session/'+sid+'/window',{'handle':original_window})
  d.wait(lambda:js('return localStorage.getItem("codi-device-history-consent-v1")===null;'),10)
  check('consent withdrawal in another tab closes existing history capabilities',rejected('await storageTest.j.load("account-a",storageTest.channel);','closed'))
  js('storageTest.gate()');d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10);click('.storage-consent button');d.wait(lambda:js('return storageTest.starts===1;'),15)
  check('reconsent restores retained device history without silently erasing it',task('storageTest.j=await storageTest.open();return (await storageTest.j.load("account-a",storageTest.channel)).hash===params[0].hash;',[retained]))
  cdp('Browser.setPermission',{'permission':{'name':'persistent-storage'},'setting':'denied','origin':origin})
  check('permission revocation blocks an already-open history connection',rejected('await storageTest.j.load("account-a",storageTest.channel);','permission-required'))
  js('const n=document.querySelector("input");n.value="independent editor still works";n.dispatchEvent(new Event("input",{bubbles:true}));')
  check('storage refusal leaves unrelated editor usable',js('return document.querySelector("input").value==="independent editor still works";'))
  # Controlled asynchronous native-API adapters cover denial/unsupported,
  # detached-view and cross-tab consent races independently of CDP permissions.
  task('storageTest.policy.forget();const base={secure:true,consentStore:localStorage,eventTarget:window,userActivated:()=>true};let resolve;storageTest.delayed=new storageTest.PersistentDeviceStorage({...base,storage:{persist:()=>new Promise(r=>resolve=r),persisted:async()=>true}});storageTest.resolveGrant=()=>resolve(true);storageTest.gate({policy:storageTest.delayed});return true;')
  d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10);click('.storage-consent button');js('storageTest.life.abort("view closed");storageTest.view.dispose();storageTest.resolveGrant();')
  check('a delayed grant after closing the view writes no consent and starts no app',task('await new Promise(r=>setTimeout(r,30));return storageTest.starts===0&&localStorage.getItem("codi-device-history-consent-v1")===null;'))
  task('storageTest.delayed.close();storageTest.noAPI=new storageTest.PersistentDeviceStorage({secure:true,consentStore:localStorage,eventTarget:window,userActivated:()=>true,storage:{}});storageTest.gate({policy:storageTest.noAPI});return true;')
  d.wait(lambda:js('return document.querySelector("[role=status]").textContent.includes("cannot grant");'),10)
  check('unsupported storage stays unavailable without a fallback history database',js('return document.querySelector(".storage-consent button").disabled&&storageTest.starts===0;'))
  js('storageTest.close();storageTest.delayed?.close();storageTest.noAPI?.close();')
  cdp('Storage.clearDataForOrigin',{'origin':origin,'storageTypes':'local_storage,indexeddb'})
  check('explicit site-data clearing removes history and consent rather than silently recovering private content from the server',task('return localStorage.getItem("codi-device-history-consent-v1")===null&&(await indexedDB.databases()).length===0;'))
  result['status']='PASS'
 except Exception as e:
  result.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:result['failureBrowserState']=task('return {status:await storageTest.policy.status(),gate:document.querySelector("#gate").innerText,starts:storageTest.starts,databases:await indexedDB.databases()};')
   except Exception as diagnostic:result['diagnosticError']=str(diagnostic)

 finally:
  if sid:
   try:js('storageTest.close();storageTest.delayed?.close();storageTest.noAPI?.close();')
   except Exception as e:result['cleanupError']=str(e)
   d.call('/session/'+sid,method='DELETE');result['ownedBrowserClosed']=True
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  tmp.cleanup();result['fixtureRemoved']=not folder.exists()
  shutil.rmtree(profile);result['ownedProfileRemoved']=not profile.exists()
 result['sourceSHA256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/device-history-page.mjs',ROOT/'assets/desktop/storage-consent.mjs',ROOT/'assets/desktop/channel-journal.mjs']}
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(0 if r['status']=='PASS' else 1)
