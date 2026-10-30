#!/usr/bin/env python3
"""Actual shared browser-file store and compiled Files/Text desktop composition.

Two sequential real Chrome launches reuse one owned profile. Actual IndexedDB,
Web Crypto, strict write abort, CAS, native persistence grant/denial and CDP site
clearing. No v86/server account/history/production changes. Desktop.open is the
exact method extracted from app.js; fixture supplies window rendering, identity
switches and guest placeholders, not a full desktop/real registered-login test.
"""
import argparse,functools,hashlib,http.server,importlib.util,json,shutil,tempfile,threading,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=module('browser_file_driver',ROOT/'scripts/touch-preview-check.py');builder=module('browser_file_builder',ROOT/'scripts/build-public-apps.py')
class Quiet(http.server.SimpleHTTPRequestHandler):
 writes=[]
 def log_message(self,*args):pass
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
 def do_POST(self):self.writes.append(self.path);self.send_error(405)
def run(shared_service=None):
 sid=None;server=None;thread=None;tmp=tempfile.TemporaryDirectory(prefix='codi-browser-files-');folder=Path(tmp.name);profile=Path(tempfile.mkdtemp(prefix='codi-browser-files-',dir=Path.home()/'snap/chromium/common'));checks=[];started=time.monotonic()
 result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserLaunches':0,'maximumConcurrentBrowsers':1,'actualV86Desktops':0,'actualPeerConnections':0,'productionChanged':False,'nativePermissionControl':'CDP persistent-storage permission'}
 payloads={n:(ROOT/n).read_bytes() for n in ['desktop-apps.js','app.js','assets/desktop/apps.mjs','assets/desktop/app-instance.mjs','assets/desktop/browser-files.mjs','network/strict-json.mjs','scripts/fixtures/browser-files-bootstrap.js','scripts/fixtures/browser-files-page.mjs']}
 result['sourceSHA256']={str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),**{n:hashlib.sha256(data).hexdigest() for n,data in payloads.items()}}
 def js(code,args=[]):return h.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  v=h.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
 def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
 def click(selector,label):
  eid=h.call('/session/'+sid+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];buttons=h.call('/session/'+sid+'/element/'+eid+'/elements',{'using':'css selector','value':'button'})
  for button in buttons:
   bid=button['element-6066-11e4-a52e-4f735466cecf']
   if h.call('/session/'+sid+'/element/'+bid+'/text',method='GET')==label:h.call('/session/'+sid+'/element/'+bid+'/click',{});return
  raise AssertionError((selector,label))
 def ready_files():h.wait(lambda:js('return document.querySelector("[data-browser-file-list]")?.getAttribute("aria-busy")==="false";'),15)
 def ready_editor():h.wait(lambda:js('return !!document.querySelector("[data-browser-editor] textarea:not(:disabled)");'),15)
 def start():
  nonlocal sid
  sid=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1400,1000','--user-data-dir='+str(profile)]}}}})['sessionId'];result['actualBrowserLaunches']+=1;h.call('/session/'+sid+'/timeouts',{'script':90000});h.call('/session/'+sid+'/url',{'url':origin+'/'});h.wait(lambda:js('return window.fixtureReady===true;'),15)
 def browse():
  js('window.filesWindow=browserFixture.desktop.launch("files");');h.wait(lambda:js('return !!document.querySelector("[aria-label=\\\"File storage\\\"]");'),15);click('[aria-label="File storage"]','This browser');ready_files()
 try:
  public=folder/'public';assets=public/'assets/desktop';assets.mkdir(parents=True);result['appBuild']=builder.build(ROOT.parent/'served_apps_public',assets,['files','text','calculator'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));result['builtApps']=json.loads((assets/'apps.json').read_bytes());result['appCatalogSHA256']=hashlib.sha256((assets/'apps.json').read_bytes()).hexdigest();result['sourceSHA256'].update({str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for app_id in ['files','text','calculator'] for p in sorted((ROOT.parent/'served_apps_public'/app_id).rglob('*')) if p.is_file() and p.suffix in ['.mjs','.js','.css','.json']})
  for n,data in payloads.items():
   if n=='app.js':continue
   target=public/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  if shared_service:
   manifest=json.loads((shared_service/'shared-service.json').read_bytes());assert manifest['name']=='browser-files' and manifest['sourceAlias']=='assets/desktop/browser-files.mjs';entry=shared_service/manifest['path'];data=entry.read_bytes();assert manifest['files']['index.mjs']=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()};(public/'assets/desktop/browser-files.mjs').write_bytes(data);result['actualCompiledServiceSHA256']=hashlib.sha256(data).hexdigest();result['compiledServiceManifestSHA256']=hashlib.sha256((shared_service/'shared-service.json').read_bytes()).hexdigest()
  app=payloads['app.js'].decode();start_at=app.index('  open(app,context){');end_at=app.index('\n  launch(app,title)',start_at);method=app[start_at:end_at].strip();(public/'desktop-open.js').write_text('window.exactDesktopOpen=({'+method+'}).open;\n');result['desktopOpenMethodSHA256']=hashlib.sha256(method.encode()).hexdigest()
  (public/'index.html').write_text('<!doctype html><title>Owned browser files workflow</title><main id="windows"></main><script src="scripts/fixtures/browser-files-bootstrap.js"></script><script src="desktop-apps.js"></script><script src="desktop-open.js"></script><script type="module" src="scripts/fixtures/browser-files-page.mjs"></script>')
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(public)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();origin='http://127.0.0.1:'+str(server.server_port);start()
  check('ordinary desktop load opens no browser file database before choosing that volume',task('return (await indexedDB.databases()).length===0;'))
  h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'denied','origin':origin}});browse()
  click('[data-browser-files]','Keep browser files');h.wait(lambda:js('return document.querySelector("[data-browser-files]").textContent.includes("did not grant storage protection");'),15)
  check('native persistence denial is reported honestly and does not block ordinary browser files',task('return !(await navigator.storage.persisted())&&!!document.querySelector("[data-browser-file-list]");'))
  js('document.querySelector("[aria-label=\\\"New browser item name\\\"]").value="notes.txt";');click('[data-browser-files]','New text file');ready_editor()
  check('Files opens the saved browser file through the real immutable document context',js('const w=browserFixture.desktop.windows.find(w=>w.editor?.storage==="browser");return Object.isFrozen(w.launchContext)&&w.launchContext.storage==="browser"&&w.browserOwner===browserFixture.scope();'))
  js('const a=document.querySelector("[data-browser-editor] textarea");a.value="My browser note\\nEdited in Text.\\n";a.dispatchEvent(new Event("input",{bubbles:true}));');click('[data-browser-editor]','Save');h.wait(lambda:js('return document.querySelector("[data-browser-editor] .app-status").textContent.includes("Saved in this browser.");'),15)
  check('Text save writes actual shared IndexedDB bytes without a server account',task('return await browserFixture.read("/notes.txt")==="My browser note\\nEdited in Text.\\n";'))
  h.wait(lambda:js('return document.querySelector("[data-browser-path=\\\"/notes.txt\\\"] .file-size")?.textContent==="32 bytes";'),15)
  check('Files updates the saved result after Text without replacing the editor draft',js('return document.querySelector("[data-browser-editor] textarea").value==="My browser note\\nEdited in Text.\\n";'))
  # Real compare-and-swap conflict: external same-account client updates the
  # saved version while Text retains its older loaded version and newer draft.
  task('const c=await browserFixture.context(),old=await c.files.read("/notes.txt");await c.files.write("/notes.txt","Another view won.",old.version);return true;')
  js('const a=document.querySelector("[data-browser-editor] textarea");a.value="Keep my conflicting draft";a.dispatchEvent(new Event("input",{bubbles:true}));');click('[data-browser-editor]','Save');h.wait(lambda:js('return document.querySelector("[data-browser-editor] .app-status").textContent.includes("changed in another view");'),15)
  check('stale editor save refuses overwrite and preserves both accepted bytes and local draft',task('return await browserFixture.read("/notes.txt")==="Another view won."&&document.querySelector("[data-browser-editor] textarea").value==="Keep my conflicting draft";'))
  click('[data-browser-editor]','Reload');h.wait(lambda:js('return document.querySelector("[data-browser-editor] textarea").value==="Another view won.";'),15)
  js('const a=document.querySelector("[data-browser-editor] textarea");a.value="Saved across a closed browser.";a.dispatchEvent(new Event("input",{bubbles:true}));');click('[data-browser-editor]','Save');h.wait(lambda:js('return document.querySelector("[data-browser-editor] .app-status").textContent.includes("Saved in this browser.");'),15)
  check('opaque versions prevent two native transactions from replacing the same saved version',task('const c=await browserFixture.context();await c.files.write("/race.txt","initial");const before=await c.files.read("/race.txt"),values=await Promise.allSettled([c.files.write("/race.txt","A",before.version),c.files.write("/race.txt","B",before.version)]);return values.filter(v=>v.status==="fulfilled").length===1&&values.filter(v=>v.status==="rejected"&&v.reason.name==="BrowserFileConflict").length===1;'))
  check('actual native write abort leaves old content and accounting unchanged',task('const c=await browserFixture.context(),before=await c.files.read("/notes.txt"),audit=await browserFixture.rawAudit(),put=IDBObjectStore.prototype.put;let aborted=false;IDBObjectStore.prototype.put=function(...args){const q=put.apply(this,args);if(this.name==="contents"&&!aborted){aborted=true;this.transaction.abort();}return q;};let failed=false;try{await c.files.write("/notes.txt","Aborted bytes",before.version);}catch{failed=true;}finally{IDBObjectStore.prototype.put=put;}return failed&&aborted&&(await c.files.read("/notes.txt")).version===before.version&&JSON.stringify(await browserFixture.rawAudit())===JSON.stringify(audit);'))
  check('a closed/account-changed browser context cannot read or write the next account',task('window.oldContext=await browserFixture.context();browserFixture.account("owned-b");const fresh=await browserFixture.context();let denied=0;try{await oldContext.files.read("/notes.txt");}catch{denied++;}try{await oldContext.files.write("/late.txt","stale");}catch{denied++;}return denied===2&&(await fresh.files.list("/")).entries.length===0;'))
  task('await (await browserFixture.context()).files.write("/private.txt","Only this on-device account");browserFixture.account(null);return true;');browse();check('returning anonymous browser scope retains its files separately from registered local scopes',task('const c=await browserFixture.context();return await browserFixture.read("/notes.txt")==="Saved across a closed browser."&&!(await c.files.list("/")).entries.some(e=>e.name==="private.txt");'))
  h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Browser.setPermission','params':{'permission':{'name':'persistent-storage'},'setting':'granted','origin':origin}});click('[data-browser-files]','Keep browser files');h.wait(lambda:js('return document.querySelector("[data-browser-files]").textContent.includes("storage protection granted");'),15);check('native persistent storage success is observed from the real browser API',task('return await navigator.storage.persisted()===true;'))
  task('browserFixture.closeAll();return true;');h.call('/session/'+sid,method='DELETE');sid=None;start();browse();click('[data-browser-path="/notes.txt"]','notes.txt');ready_editor()
  check('a genuinely new Chrome launch reopens the saved file without previous window or RAM state',js('return document.querySelector("[data-browser-editor] textarea").value==="Saved across a closed browser.";'))
  check('capacity refusal leaves existing files and another independent calculator usable',task('const {BrowserFileStore}=await import("/assets/desktop/browser-files.mjs"),small=new BrowserFileStore({fileBytes:1024,scopeBytes:1024});let failed=false;try{await small.write("owned-quota-scope","/too-large.txt",new Uint8Array(1024));}catch(e){failed=e.name==="BrowserFileCapacity";}finally{small.close();}return failed&&await browserFixture.read("/notes.txt")==="Saved across a closed browser.";'))
  js('browserFixture.desktop.launch("calculator");');h.wait(lambda:js('return !!document.querySelector(".calculator-result");'),15);js('const i=document.querySelector(".calculator-content input");i.value="6*7";i.form.requestSubmit();');check('independent browser app remains functional after storage refusal',js('return document.querySelector(".calculator-result").textContent==="42";'))
  check('browser folder operations refuse nonempty deletion and preserve nested data',task('const c=await browserFixture.context(),folder=await c.files.mkdir("/Projects");await c.files.write("/Projects/child.txt","nested browser file");let denied=false;try{await c.files.remove("/Projects",folder.version);}catch(e){denied=e.message.includes("must be empty");}const file=await c.files.read("/Projects/child.txt");await c.files.remove("/Projects/child.txt",file.version);await c.files.remove("/Projects",folder.version);return denied&&!(await c.files.list("/")).entries.some(e=>e.name==="Projects");'))
  check('browser document contexts cannot name another local account scope',task('let refused=false;try{browserFixture.desktop.open("text",Object.freeze({version:1,storage:"browser",path:"/notes.txt",owner:"other-account"}));}catch(e){refused=e.message.includes("browser document owner");}return refused;'))
  js('document.querySelector(arguments[0]).value=arguments[1];',['[aria-label="Browser file path"]','/copy.txt']);click('[data-browser-editor]','Save');h.wait(lambda:js('return browserFixture.desktop.windows.some(w=>w.editor?.path==="/copy.txt");'),15);click('[data-browser-path="/notes.txt"]','notes.txt');h.wait(lambda:js('return browserFixture.desktop.windows.filter(w=>w.editor?.storage==="browser").length===2;'),15)
  check('browser Save As does not redirect reopening the original document to its copy',task('return await browserFixture.read("/copy.txt")===await browserFixture.read("/notes.txt")&&browserFixture.desktop.windows.some(w=>w.editor?.path==="/copy.txt")&&browserFixture.desktop.windows.some(w=>w.editor?.path==="/notes.txt");'))
  js('for(const w of [...browserFixture.desktop.windows])if(w.app==="text")browserFixture.close(w.id);');click('[data-browser-path="/notes.txt"]','notes.txt');ready_editor()
  js('window.terminalSessions=new Map();desktopNetwork.appContext=()=>({disabled:true,views:new Map()});')
  js((ROOT/'scripts/fixtures/app-lifecycle-probe.js').read_text());baseline=js('return appLifecycleProbe.snapshot();')
  for i in range(30):
   wid=js('const w=browserFixture.desktop.launch("files");w.storage="browser";browserFixture.desktop.render();return w.id;');h.wait(lambda:js('return document.querySelector(`[data-window="${arguments[0]}"] [data-browser-file-list]`)?.getAttribute("aria-busy")==="false";',[wid]),15);js('browserFixture.close(arguments[0]);',[wid])
  after=js('return appLifecycleProbe.snapshot();');result['lifecycleSamples']={'warmBaseline':baseline,'after30Reopens':after};check('thirty Files reopens leave no new app timers, global listeners, workers or requests',baseline==after)
  check('serialized metadata and content sizes agree with stored quota accounting',task('const a=await browserFixture.rawAudit();return a.bytes===a.accounting.bytes&&a.entries===a.accounting.entries&&a.contents===a.entries;'))
  h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Storage.clearDataForOrigin','params':{'origin':origin,'storageTypes':'indexeddb,local_storage'}})
  js('const a=document.querySelector("[data-browser-editor] textarea");a.value="Unsaved draft after browser data clearing";a.dispatchEvent(new Event("input",{bubbles:true}));');click('[data-browser-editor]','Save');h.wait(lambda:js('return document.querySelector("[data-browser-editor] .app-status").textContent.includes("cleared");'),15)
  check('site-data clearing does not silently recreate a missing saved file from a stale draft',task('return (await (await browserFixture.context()).files.list("/")).entries.length===0&&document.querySelector("[data-browser-editor] textarea").value==="Unsaved draft after browser data clearing";'))
  check('no file contents or account operations were sent to an HTTP backend',not Quiet.writes)
  result['status']='PASS'
 except Exception as e:
  result.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:result['diagnostic']=js('return {text:document.body.innerText,windows:browserFixture.desktop.windows.map(w=>({id:w.id,app:w.app,storage:w.storage,editor:w.editor})),errors:window.fixtureError||null};')
   except Exception as d:result['diagnosticError']=str(d)
 finally:
  if sid:
   try:js('browserFixture.closeAll();')
   except Exception as e:result['cleanupError']=str(e)
   h.call('/session/'+sid,method='DELETE');result['ownedBrowserClosed']=True
  if server:server.shutdown();server.server_close()
  if thread:thread.join(timeout=3)
  tmp.cleanup();shutil.rmtree(profile);result.update(fixtureRemoved=not folder.exists(),ownedProfileRemoved=not profile.exists())
 result['elapsedSeconds']=round(time.monotonic()-started,3);return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--shared-service',type=Path);a=p.parse_args();assert not a.output.exists();r=run(a.shared_service.resolve() if a.shared_service else None);a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(0 if r['status']=='PASS' else 1)
