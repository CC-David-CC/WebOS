#!/usr/bin/env python3
"""Fresh trusted root Chrome/v86, browser files across two process launches.

Uses one owned browser profile and anonymous identity. It never clears an
existing visitor's storage or sends local documents to the file backend. Phone
coverage is Chrome viewport/touch emulation, not a physical phone test.
"""
import argparse,hashlib,importlib.util,json,secrets,shutil,tempfile,time,traceback,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('browser_files_live_driver',ROOT/'scripts/touch-preview-check.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

def run(release):
 checks=[];sid=None;profile=Path(tempfile.mkdtemp(prefix='codi-browser-files-live-',dir=Path.home()/'snap/chromium/common'));started=time.monotonic()
 result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserLaunches':0,'actualV86Desktops':0,'defaultPublicTLS':True,'outsideWAN':False,'physicalPhoneTested':False,'ownedProfileRemoved':False,'wholeGoalComplete':False}
 name='browser-note-'+secrets.token_hex(5)+'.txt';text='A saved browser document.\nThis survives a browser restart.\n'
 def js(code,args=[]):return h.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  r=h.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert r['ok'],r;return r.get('value')
 def check(label,ok):assert ok,label;checks.append(label);print(json.dumps({'check':label}),flush=True)
 def click(selector,label):
  found=js('return [...document.querySelector(arguments[0]).querySelectorAll("button")].findIndex(b=>b.textContent===arguments[1]);',[selector,label]);assert found>=0,(selector,label)
  e=h.call('/session/'+sid+'/element',{'using':'css selector','value':selector})['element-6066-11e4-a52e-4f735466cecf'];buttons=h.call('/session/'+sid+'/element/'+e+'/elements',{'using':'css selector','value':'button'});bid=buttons[found]['element-6066-11e4-a52e-4f735466cecf'];h.call('/session/'+sid+'/element/'+bid+'/click',{})
 def ready_files():h.wait(lambda:js('return document.querySelector("[data-browser-file-list]")?.getAttribute("aria-busy")==="false"'),25)
 def ready_editor():h.wait(lambda:js('return !!document.querySelector("[data-browser-editor] textarea:not(:disabled)")'),25)
 def start():
  nonlocal sid
  sid=h.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1400,1000','--user-data-dir='+str(profile)]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];result['actualBrowserLaunches']+=1
  h.call('/session/'+sid+'/timeouts',{'script':120000});h.call('/session/'+sid+'/url',{'url':'https://ksu.codes/'})
  h.wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),180);result['actualV86Desktops']+=1
  js('window.bfDesktop=[...surfaces.values()][0];window.confirm=()=>true;')
 def browse():
  js('window.bfFiles=bfDesktop.windows.find(w=>w.app==="files")||bfDesktop.launch("files");bfDesktop.activateWindow(bfFiles);');h.wait(lambda:js('return !!document.querySelector(`[data-window="${bfFiles.id}"] [aria-label="File storage"]`)'),25)
  click('[data-window="'+str(js('return bfFiles.id'))+'"] [aria-label="File storage"]','This browser');ready_files()
 try:
  expected=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();result['candidateManifestSHA256']=expected
  for n in ['index.html','assets/desktop/network-release.json','assets/desktop/shared-services.json']:
   with urllib.request.urlopen('https://ksu.codes/'+n,timeout=25) as response:assert response.status==200 and response.read()==(release/n).read_bytes(),n
  check('trusted root assets match the exact sealed browser-files candidate',True)
  start();check('anonymous desktop boots real v86 with xterm',js('return !signedInSubject()&&!!document.querySelector(".xterm")&&guestFiles.ready'))
  browse();js('document.querySelector(arguments[0]).value=arguments[1]',['[aria-label="New browser item name"]',name]);click('[data-browser-files]','New text file');ready_editor()
  check('actual Files launches Text with immutable on-device document context',js('const w=bfDesktop.windows.find(w=>w.editor?.storage==="browser");return Object.isFrozen(w.launchContext)&&w.launchContext.storage==="browser"&&w.browserOwner===browserFilesScope()'))
  js('const a=document.querySelector("[data-browser-editor] textarea");a.value=arguments[0];a.dispatchEvent(new Event("input",{bubbles:true}))',[text]);click('[data-browser-editor]','Save')
  h.wait(lambda:js('return document.querySelector("[data-browser-editor] .app-status")?.textContent.includes("Saved in this browser.")'),25)
  check('Text saved bytes can be read through the shared native browser volume',task('return new TextDecoder().decode((await (await browserFileContext()).files.read(params[0])).data)===params[1];',['/'+name,text]))
  ready_files();check('Files observes Text save size without reloading the page',js('return document.querySelector(`[data-browser-path="/${arguments[0]}"] .file-size`)?.textContent===arguments[1]+" bytes"',[name,len(text.encode())]))
  # User selects Copy to Linux from Files. It is an explicit, independent RAM copy.
  js('bfDesktop.activateWindow(bfFiles)');click('[data-browser-path="/'+name+'"]','Copy to Linux')
  h.wait(lambda:js('return document.querySelector("[data-browser-files] .app-status")?.textContent.startsWith("Copied to temporary Linux Downloads")'),25)
  check('explicit Copy to Linux writes the actual shared v86 filesystem',task('return new TextDecoder().decode(await guestFiles.read("/Downloads/"+params[0]))===params[1];',[name,text]))
  js('window.bfTerm=bfDesktop.windows.find(w=>w.app==="terminal");sendTerminal(bfTerm.id,"cat /home/guest/Downloads/"+arguments[0]+"\\r")',[name])
  h.wait(lambda:js('return terminalSessions.get(bfTerm.id).screen.text().includes("This survives a browser restart.")'),25);check('the real Linux shell reads the browser file copy through 9p',True)
  # Keep a separate unsaved Linux draft; only the explicit save-copy persists it.
  task('await guestFiles.write("/Documents/temporary-browser-copy.txt","Temporary Linux draft");return true;')
  js('openGuestEditor(bfDesktop,"/Documents/temporary-browser-copy.txt")');h.wait(lambda:js('return [...document.querySelectorAll(".guest-editor")].some(a=>a.value==="Temporary Linux draft")'),25)
  js('window.bfGuestEditor=bfDesktop.windows.find(w=>w.editor?.storage!=="browser"&&w.editor?.path==="/Documents/temporary-browser-copy.txt");window.prompt=()=>"/from-linux.txt";')
  click('[data-window="'+str(js('return bfGuestEditor.id'))+'"]','Save browser copy…');h.wait(lambda:js('return [...document.querySelectorAll("[data-browser-editor] textarea")].some(a=>a.value==="Temporary Linux draft")'),25)
  check('Save browser copy preserves the actual Linux document separately',task('return new TextDecoder().decode((await (await browserFileContext()).files.read("/from-linux.txt")).data)==="Temporary Linux draft";'))
  js('bfDesktop.switchWorkspace(1);window.bfOther=bfDesktop.launch("calculator");')
  h.wait(lambda:js('return !!document.querySelector(".calculator-result")'),25);js('const i=document.querySelector(".calculator-content input");i.value="6*7";i.form.requestSubmit()')
  check('browser save leaves another workspace and calculator usable',js('return document.querySelector(".calculator-result").textContent==="42"'))
  h.call('/session/'+sid,method='DELETE');sid=None;start();browse();click('[data-browser-path="/'+name+'"]',name);ready_editor()
  check('a new Chrome process and new Linux boot reopen the saved Text document',js('return document.querySelector("[data-browser-editor] textarea").value===arguments[0]',[text]))
  check('temporary Linux copy disappeared while browser files survived',task('let missing=false;try{await guestFiles.read("/Downloads/"+params[0]);}catch{missing=true;}return missing&&new TextDecoder().decode((await (await browserFileContext()).files.read("/from-linux.txt")).data)==="Temporary Linux draft";',[name]))
  h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
  h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
  h.wait(lambda:js('return bfDesktop.mobile'),20);js('bfDesktop.activateWindow(bfFiles)')
  point=js('const b=[...document.querySelector(arguments[0]).querySelectorAll("button")].find(b=>b.textContent===arguments[1]);b.scrollIntoView({block:"center"});const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,width:r.width,height:r.height,left:r.left,right:r.right};',['[data-browser-path="/'+name+'"]',name])
  check('phone browser file button has a contained44px touch target',point['width']>=44 and point['height']>=44 and point['left']>=0 and point['right']<=390)
  for kind in ['touchStart','touchEnd']:h.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':kind,'touchPoints':[{'x':point['x'],'y':point['y']}] if kind=='touchStart' else []}})
  h.wait(lambda:js('return document.querySelector(".window.focused [data-browser-editor] textarea")?.value===arguments[0]',[text]),25)
  check('trusted phone touch opens the persisted document in Text',True)
  check('voice mode preserves editable browser fields without requesting the keyboard',js('const a=document.querySelector(".window.focused [data-browser-editor] textarea");return a.inputMode==="none"&&!a.readOnly&&!a.disabled&&!!document.querySelector("#voice-control")'))
  stats=task('return await desktopNetwork.stats();');check('chat remains paused with no pool or saved-chat backend allocation',stats.get('peers')==[] and stats.get('hosted') is None and not stats.get('budget'))
  check('browser files never send document requests to the gateway or chat backend',js('return !performance.getEntriesByType("resource").some(r=>{const p=new URL(r.name).pathname;return p.startsWith("/gateway/")||p.startsWith("/rooms/")||p==="/rendezvous";})'))
  logs=h.call('/session/'+sid+'/log',{'type':'browser'});result['severeConsole']=[v for v in logs if v['level']=='SEVERE'];check('no unexpected browser console errors',not result['severeConsole'])
  result['status']='PASS'
 except Exception as e:
  result.update(error=str(e),traceback=traceback.format_exc())
  if sid:
   try:result['diagnostic']=js('return {text:document.body.innerText.slice(-7000),guest:window.desktopLab?.guestState,windows:typeof bfDesktop!=="undefined"?bfDesktop.windows.map(w=>({id:w.id,app:w.app,path:w.editor?.path,storage:w.storage,workspace:w.workspace})):[]};')
   except Exception as diagnostic:result['diagnosticError']=str(diagnostic)
 finally:
  if sid:h.call('/session/'+sid,method='DELETE')
  shutil.rmtree(profile);result['ownedProfileRemoved']=not profile.exists();result['elapsedSeconds']=round(time.monotonic()-started,3);result['scriptSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run(a.release.resolve());a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks']),'error':r.get('error')}));raise SystemExit(r['status']!='PASS')
