#!/usr/bin/env python3
"""Actual desktop-apps.js/catalog/bundler/API2 with consent-gated signed IDB.

One owned real Chrome,0v86 and0actual peer links. Identity and network-start
hooks are controlled fixtures; test Chat/Rooms apps exercise the real shared
storage API. The independent Calculator is the actual application source.
No live deployment or chat enablement; no new consensus/8k proof.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=mod('history_host_driver',ROOT/'scripts/touch-preview-check.py');builder=mod('history_host_builder',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
def run(shared_service=None,desktop_source=None):
 sid=None;server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-device-host-');folder=Path(tmp.name);checks=[]
 r={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':1,'actualV86Desktops':0,'actualPeerConnections':0,'productionChanged':False}
 def js(code,args=[]):return d.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=d.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def click(selector):
  e=d.call('/session/'+sid+'/element',{'using':'css selector','value':selector});d.call('/session/'+sid+'/element/'+e['element-6066-11e4-a52e-4f735466cecf']+'/click',{})
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def ready(w):d.wait(lambda:js('return !!hostFixture.node(arguments[0])?.querySelector("[data-history-ready]");',[w]),20)
 try:
  source=folder/'source';public=folder/'public';assets=public/'assets/desktop';assets.mkdir(parents=True)
  for app in ['chat','rooms']:shutil.copytree(ROOT/'scripts/fixtures/device-history-app',source/app)
  shutil.copytree(ROOT.parent/'served_apps_public/calculator',source/'calculator')
  r['appBuild']=builder.build(source,assets,['chat','rooms','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'))
  for name in ['device-history-host.mjs','storage-consent.mjs','channel-journal.mjs','channel-keys.mjs','device-key-database.mjs','device-channel-session.mjs','channel-directory.mjs','channel-archive.mjs','channel-download-cache.mjs','replica-journal.mjs','apps.mjs','app-instance.mjs']:shutil.copyfile(ROOT/'assets/desktop'/name,assets/name)
  if shared_service:
   manifest=json.loads((shared_service/'shared-service.json').read_bytes());assert manifest['version']=='codi-shared-service/1' and manifest['name']=='device-history'
   entry=shared_service/manifest['path'];expected=manifest['files']['index.mjs'];assert expected=={'bytes':entry.stat().st_size,'sha256':hashlib.sha256(entry.read_bytes()).hexdigest()}
   shutil.copyfile(entry,assets/'device-history-host.mjs');r['actualCompiledServiceSHA256']=expected['sha256']
   for name,desc in manifest['files'].items():
    if name=='index.mjs':continue
    source=entry.parent/name;assert not source.is_symlink() and {'bytes':source.stat().st_size,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}==desc
    target=assets/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)

  (public/'network').mkdir()
  for name in ['crypto.mjs','strict-json.mjs']:shutil.copyfile(ROOT/'network'/name,public/'network'/name)
  chosen_desktop=desktop_source or ROOT/'desktop-apps.js';shutil.copyfile(chosen_desktop,public/'desktop-apps.js');r['testedDesktopSourceSHA256']=hashlib.sha256(chosen_desktop.read_bytes()).hexdigest()
  # Real network initialization is exercised separately with ONLY the explicit
  # operator-pause constant changed in this owned fixture, never in production.
  shutil.rmtree(public/'network');shutil.copytree(ROOT/'network',public/'network')
  vendor=public/'assets/vendor/chess';vendor.mkdir(parents=True);shutil.copyfile(ROOT/'assets/vendor/chess/chess.mjs',vendor/'chess.mjs')
  raw=(ROOT/'networking.js').read_text();assert raw.count('const disabled=true;')==1
  (public/'networking-fixture.js').write_text(raw.replace('const disabled=true;','const disabled=false;').replace('const legacyEnabled=false;','const legacyEnabled=true;'))
  bootstrap=(ROOT/'scripts/fixtures/device-history-host-bootstrap.js').read_text();(public/'network-bootstrap.js').write_text(bootstrap[:bootstrap.index('const desktopNetwork=')])
  shutil.copyfile(ROOT/'scripts/fixtures/device-history-network-case.mjs',public/'network-case.mjs');shutil.copyfile(ROOT/'config.json',public/'config.json')
  (public/'network-case.html').write_text('<!doctype html><title>Consented real network resources</title><script src="network-bootstrap.js"></script><script src="desktop-apps.js"></script><script src="networking-fixture.js"></script><script type="module" src="network-case.mjs"></script>')

  shutil.copyfile(ROOT/'scripts/fixtures/device-history-host-bootstrap.js',public/'bootstrap.js');shutil.copyfile(ROOT/'scripts/fixtures/device-history-host-page.mjs',public/'fixture.mjs')
  (public/'index.html').write_text('<!doctype html><title>Shared device history host</title><main id="windows"></main><script src="bootstrap.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(public)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port)
  sid=d.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];d.call('/session/'+sid+'/timeouts',{'script':90000});d.call('/session/'+sid+'/url',{'url':origin+'/'})
  d.wait(lambda:js('return window.fixtureReady===true;'),15)
  js((ROOT/'scripts/fixtures/app-lifecycle-probe.js').read_text())
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'denied','origin':origin}})
  paused=js('hostFixture.disabled=true;return hostFixture.open("chat");');d.wait(lambda:js('return !!hostFixture.node(arguments[0])?.querySelector("[data-chat-disabled]");',[paused]),15)
  check('the operator pause bypasses both storage prompts and network activation',task('return hostFixture.networkStarts===0&&hostFixture.mounts===0&&localStorage.length===0&&(await indexedDB.databases()).length===0;'))
  js('hostFixture.close(arguments[0]);hostFixture.disabled=false;',[paused])
  w=js('return hostFixture.open("rooms");');d.wait(lambda:js('return !!hostFixture.node(arguments[0])?.querySelector("[data-storage-consent]");',[w]),15)
  d.wait(lambda:js('return !hostFixture.node(arguments[0]).querySelector("button").disabled;',[w]),10)
  check('real loader mounts the storage prerequisite before the app/network/database',task('return hostFixture.mounts===0&&hostFixture.networkStarts===0&&(await indexedDB.databases()).length===0;'))
  check('desktop-owned room extensions cannot bypass the pending consent gate',js('return hostFixture.routedMounts===0&&!document.querySelector(".fixture-routed");'))
  calc=js('return hostFixture.open("calculator");');d.wait(lambda:js('return !!hostFixture.node(arguments[0])?.querySelector(".calculator-result");',[calc]),15)
  js('const n=hostFixture.node(arguments[0]).querySelector("input");n.value="6*7";n.form.requestSubmit();',[calc])
  check('unrelated genuine Calculator works while a chat window awaits storage',js('return hostFixture.node(arguments[0]).querySelector(".calculator-result").textContent==="42";',[calc]))
  click('[data-window="'+str(w)+'"] .storage-consent button');d.wait(lambda:js('return hostFixture.node(arguments[0]).textContent.includes("did not grant");',[w]),15)
  check('native denial never mounts the gated app or starts its network hook',task('return hostFixture.mounts===0&&hostFixture.networkStarts===0&&(await indexedDB.databases()).length===0;'))
  d.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}})
  click('[data-window="'+str(w)+'"] .storage-consent button');ready(w)
  check('explicit native grant mounts app through the same API2 and opens exactly one scoped journal',task('const s=await hostFixture.stats();return s.views===1&&s.journals===1&&s.active===1&&hostFixture.networkStarts===1;'))
  check('room extension mounts only inside the approved app view',js('return hostFixture.routedMounts===1&&!!hostFixture.node(arguments[0]).querySelector("[data-history-app] .fixture-routed");',[w]))
  click('[data-window="'+str(w)+'"] [data-history-app] button');d.wait(lambda:js('return hostFixture.node(arguments[0]).textContent.includes("Saved note: Note 1");',[w]),15)
  check('consented app opens a scope-bound key facade and signs without exposing its private key',task('window.firstKeys=hostFixture.keyFacades.at(-1);window.savedKey=await firstKeys.create({label:"Stable shared channel"});const wire=await firstKeys.sign(savedKey.channel,"operation",{text:"From actual host facade"});const {verifyDeviceChannelProof}=await import("./assets/desktop/channel-keys.mjs");return (await verifyDeviceChannelProof(wire,{channel:savedKey.channel})).body.text==="From actual host facade"&&(await hostFixture.stats()).keyStores===1&&!("privateKey" in savedKey);'))
  js('window.keepHistoryNode=hostFixture.node(arguments[0]).querySelector("[data-history-app]");hostFixture.node(arguments[0]).hidden=true;hostFixture.windows.find(w=>w.id===arguments[0]).workspace=2;hostFixture.node(arguments[0]).hidden=false;',[w])
  check('workspace/minimize visibility changes retain the same live history app and connection',task('const s=await hostFixture.stats();return keepHistoryNode.isConnected&&s.views===1&&s.journals===1&&s.active===1&&hostFixture.mounts===1;'))
  js('hostFixture.close(arguments[0]);',[w])
  check('closing the view releases child resources and its native history connection',task('const s=await hostFixture.stats();return s.views===0&&s.journals===0&&s.active===0;'))
  check('disposed app key facade refuses further signing and releases its native key connection',task('let refused=false;try{await firstKeys.sign(savedKey.channel,"operation",{});}catch{refused=true;}return refused&&(await hostFixture.stats()).keyStores===0;'))
  w=js('return hostFixture.open("rooms");');ready(w)
  check('another existing app restores the same account/channel saved result',js('return hostFixture.node(arguments[0]).textContent.includes("Saved note: Note 1");',[w]))
  check('another app in the same account restores the identical persistent channel key',task('return (await hostFixture.keyFacades.at(-1).get(savedKey.channel)).genesisHash===savedKey.genesisHash;'))
  js('hostFixture.account("registered-b")');b=js('return hostFixture.open("chat");');ready(b)
  check('account change disposes old apps and gives the new account an empty independent history scope',js('return hostFixture.active===1&&hostFixture.node(arguments[0]).textContent.includes("No saved device note.")&&new Set(hostFixture.liveScopes).size===2;',[b]))
  check('account-bound key facade cannot select another account scope or use its private key',task('const keys=hostFixture.keyFacades.at(-1);let refused=false;try{await keys.sign(savedKey.channel,"operation",{});}catch{refused=true;}return refused&&(await keys.list()).length===0&&await keys.get(savedKey.channel)===null;'))
  js('hostFixture.account("registered-a")');a=js('return hostFixture.open("chat");');ready(a)
  check('returning with a fresh session restores the original stable account scope',js('return hostFixture.node(arguments[0]).textContent.includes("Saved note: Note 1");',[a]))
  check('fresh login session for the same subject retains channel key continuity',task('return (await hostFixture.keyFacades.at(-1).get(savedKey.channel)).genesisHash===savedKey.genesisHash;'))
  js('hostFixture.close(arguments[0]);hostFixture.holdNetwork=true;hostFixture.finishNetwork=null;',[a]);before=js('return hostFixture.mounts;');late=js('return hostFixture.open("rooms");');d.wait(lambda:js('return typeof hostFixture.finishNetwork==="function";'),15)
  js('hostFixture.close(arguments[0]);hostFixture.holdNetwork=false;hostFixture.finishNetwork();',[late])
  check('closing during an asynchronous network-start hook prevents a late app mount and releases the gate',task('await new Promise(r=>setTimeout(r,30));const s=await hostFixture.stats();return hostFixture.mounts===params[0]&&s.views===0&&s.journals===0&&s.active===0;',[before]))
  js('hostFixture.decoratorFail=true');failed=js('return hostFixture.open("rooms");')
  d.wait(lambda:js('return hostFixture.node(arguments[0]).textContent.includes("Room extension temporarily unavailable");',[failed]),15)
  check('failed room decoration disposes the partially mounted app and its pending history work',task('const s=await hostFixture.stats();return s.active===0&&s.journals===0&&s.views===1;'))
  js('hostFixture.decoratorFail=false');click('[data-window="'+str(failed)+'"] .storage-consent button');ready(failed)
  check('retry after preparation failure mounts exactly one new app and journal',task('const s=await hostFixture.stats();return s.active===1&&s.journals===1&&s.views===1;'))
  js('hostFixture.close(arguments[0]);',[failed])
  resource_baseline=js('return appLifecycleProbe.snapshot();')
  for i in range(30):
   w=js('return hostFixture.open(arguments[0]);',['chat' if i%2 else 'rooms']);ready(w);js('hostFixture.close(arguments[0]);',[w])
  check('30 gated app reopens leave no app timers, views, history or key connections',task('const s=await hostFixture.stats();const before=hostFixture.inputEvents;window.dispatchEvent(new Event("fixture-history-event"));return s.views===0&&s.journals===0&&s.keyStores===0&&s.active===0&&hostFixture.inputEvents===before;'))
  resource_after=js('return appLifecycleProbe.snapshot();');r['resourceSamples']={'warmBaseline':resource_baseline,'after30Reopens':resource_after}
  check('native timer/listener/worker/request observations return to the warm baseline',resource_after==resource_baseline)
  js('hostFixture.account(null)');anon=js('return hostFixture.open("chat");');ready(anon)
  check('anonymous device history is separate from registered account content',js('return hostFixture.node(arguments[0]).textContent.includes("No saved device note.");',[anon]))
  # Revocation must redact live content and close app/session-owned resources.
  task('const history=await desktopHistoryServices();await history.status();history.close();return true;')
  check('closing shared storage service retires mounted apps and all history/key handles',task('const s=await hostFixture.stats();return s.closed&&s.views===0&&s.journals===0&&s.keyStores===0&&hostFixture.active===0&&!document.querySelector("[data-history-app]");'))
  # This page runs actual PeerPool/PublicRooms/budget classes with a real
  # browser-generated local identity, no peer links and no issuer traffic.
  js('localStorage.removeItem("codi-device-history-consent-v1")');d.call('/session/'+sid+'/url',{'url':origin+'/network-case.html'})
  d.wait(lambda:js('return window.networkCaseReady===true;'),20)
  check('real network initialization stays dormant without explicit device consent',task('const started=await desktopNetwork.initialize(currentSession,identityConfig);const s=await desktopNetwork.stats();return started===false&&!s.budget&&s.peers.length===0&&!performance.getEntriesByType("resource").some(r=>r.name.includes("/network/peer-pool.mjs"));'))
  js('networkCase.prepare()');d.wait(lambda:js('return !document.querySelector(".storage-consent button").disabled;'),10);click('.storage-consent button');d.wait(lambda:js('return networkCase.approved;'),15)
  check('after native consent actual shared network resources initialize with no fabricated peer links',task('const started=await desktopNetwork.initialize(currentSession,identityConfig);const s=await desktopNetwork.stats();networkCase.initialBudget=s.budget;return started===true&&s.budget.metadataBytes>=4*1048576&&s.peers.length===0&&!s.budget.closed;'))
  check('repeated app initialization reuses the same session resources',task('const again=await desktopNetwork.initialize(currentSession,identityConfig);const s=await desktopNetwork.stats();return again===true&&JSON.stringify(s.budget)===JSON.stringify(networkCase.initialBudget);'))
  js('networkCase.view.dispose();networkCase.policy.close()')
  check('closing one approval view leaves the consented shared pool available to other apps',task('return !(await desktopNetwork.stats()).budget.closed;'))
  task('(await desktopHistoryServices()).forget();return true;')
  check('withdrawn shared consent closes real session resources and releases every tracked allowance',task('const s=await desktopNetwork.stats();return s.budget.closed&&Object.entries(s.budget).every(([k,v])=>k==="closed"||v===0)&&s.peers.length===0;'))
  js('desktopNetwork.close()')
  r['status']='PASS'
 except Exception as e:
  r.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:r['diagnostics']=task('return {text:document.body.innerText,stats:await hostFixture.stats(),networkStarts:hostFixture.networkStarts,mounts:hostFixture.mounts};')
   except Exception as diag:r['diagnosticError']=str(diag)
 finally:
  if sid:
   try:task('if(window.networkCase){desktopNetwork.close();networkCase.view?.dispose();networkCase.policy?.close();(await desktopHistoryServices()).close();}else await hostFixture.closeAll();return true;')
   except Exception as e:r['cleanupError']=str(e)
   d.call('/session/'+sid,method='DELETE');r['ownedBrowserClosed']=True
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  tmp.cleanup();r['fixtureRemoved']=not folder.exists()
 r['sourceSHA256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'desktop-apps.js',ROOT/'networking.js',ROOT/'assets/desktop/device-history-host.mjs',ROOT/'assets/desktop/storage-consent.mjs',ROOT/'assets/desktop/channel-journal.mjs',ROOT/'assets/desktop/channel-keys.mjs',ROOT/'assets/desktop/device-key-database.mjs',ROOT/'assets/desktop/apps.mjs',ROOT/'assets/desktop/app-instance.mjs',*sorted((ROOT/'scripts/fixtures/device-history-app').glob('*')),ROOT/'scripts/fixtures/device-history-host-bootstrap.js',ROOT/'scripts/fixtures/device-history-host-page.mjs',ROOT/'scripts/fixtures/app-lifecycle-probe.js',ROOT/'scripts/fixtures/device-history-network-case.mjs']}
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--shared-service',type=Path);p.add_argument('--desktop-source',type=Path);a=p.parse_args();assert not a.output.exists();v=run(a.shared_service.resolve() if a.shared_service else None,a.desktop_source.resolve() if a.desktop_source else None);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
