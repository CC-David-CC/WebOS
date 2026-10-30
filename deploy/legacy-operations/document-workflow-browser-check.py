#!/usr/bin/env python3
"""Complete Files→Text→server word-count→Text workflow in real Chrome/v86."""
import argparse,base64,hashlib,importlib.util,json,secrets,shlex,subprocess,time,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=module('document_browser_helpers',ROOT/'scripts/touch-preview-check.py');call,wait=h.call,h.wait

def browser(origin,chrome_args,ledger,base='/hidden'):
 sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900',*chrome_args]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[]
 def js(s,args=[]):return call('/session/'+sid+'/execute/sync',{'script':s,'args':args})
 def task(s,args=[]):
  v=call('/session/'+sid+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+s+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':args});assert v['ok'],v;return v.get('value')
 def check(n,v):assert v,n;checks.append(n)
 def click(selector,label):assert js('const b=[...(document.querySelector(arguments[0])?.querySelectorAll("button")||[])].find(b=>b.textContent===arguments[1]);if(!b)return false;b.click();return true;',[selector,label]),(selector,label)
 def list_ready():wait(lambda:js('return document.querySelector("[data-server-file-list]")?.getAttribute("aria-busy")==="false"'),30)
 def editor_ready():wait(lambda:js('return !!document.querySelector("[data-server-editor] textarea:not(:disabled)")'),30)
 def fill(text):js('const f=document.querySelector("[data-server-editor] textarea");f.value=arguments[0];f.dispatchEvent(new Event("input",{bubbles:true}));',[text])
 def register(name):
  task('await changeAccount("register",params[0],wfPassword);return true;',[name]);ledger['subjects'][name]=js('return signedInSubject()')
 def close_editors():js('for(const w of [...wfDesktop.windows])if(w.app==="text")document.querySelector(`[data-window="${w.id}"] [aria-label="Close"]`)?.click();')
 try:
  call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':origin+base+'/'})
  wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),150)
  js('window.wfDesktop=[...surfaces.values()][0];window.wfPassword=crypto.randomUUID()+crypto.randomUUID();window.confirm=()=>true;')
  click('[data-window="4"]','My server files');check('anonymous Files offers sign-in and no server operation',js('return !document.querySelector("[data-server-file-list]")&&!document.body.innerText.includes("Word count on server")'))
  register(ledger['names'][0]);list_ready()
  task('window.wfOwner=signedInSubject();await (await serverFileContext()).files.write("workflow.txt","Before editing.");serverFilesChanged();return true;');list_ready()
  wait(lambda:js('return !!document.querySelector("[data-server-path=\\\"workflow.txt\\\"]")'),20)
  click('[data-server-path="workflow.txt"]','workflow.txt');editor_ready()
  check('Files opens selected authoritative document in Text with immutable context',js('const w=wfDesktop.windows.find(w=>w.editor?.storage==="server");return Object.isFrozen(w.launchContext)&&w.launchContext.path==="workflow.txt"&&w.editor.text==="Before editing."'))
  fill('Shared document\nEdited in Text.\n');click('[data-server-editor]','Save')
  wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent==="Saved on the server."'),30)
  check('Text save updates authoritative file bytes',task('window.wfSaved=await (await serverFileContext()).files.read("workflow.txt");return new TextDecoder().decode(wfSaved.data)==="Shared document\\nEdited in Text.\\n";'))
  wait(lambda:js('return document.querySelector("[data-server-path=\\\"workflow.txt\\\"] .file-size")?.textContent===wfSaved.data.length+" bytes"'),20)
  check('returning to Files shows updated result without refresh',True)
  close_editors();click('[data-server-path="workflow.txt"]','Word count on server')
  wait(lambda:js('return [...document.querySelectorAll("[data-server-editor] textarea")].some(n=>n.value.includes("Word-count report"))'),30)
  js('window.wfReportWindow=wfDesktop.windows.find(w=>w.editor?.text.includes("Word-count report"));window.wfReportPath=wfReportWindow.editor.path;')
  check('server saves report and Files composes its reopening in Text',js('return wfReportWindow.editor.text.includes("Words (whitespace separated): 5")&&wfReportWindow.editor.text.includes("Source SHA256: "+wfSaved.sha256)'))
  check('server retry returns the same durable operation and result',task('const c=await serverFileContext();window.wfReport=await c.files.wordCount("workflow.txt",wfSaved.sha256);return wfReport.path===wfReportPath&&(await c.files.wordCount("workflow.txt",wfSaved.sha256)).operationId===wfReport.operationId;'))
  close_editors();list_ready();wait(lambda:js('return !!document.querySelector(`[data-server-path="${wfReportPath}"]`)'),20);js('document.querySelector(`[data-server-path="${wfReportPath}"] .guest-file-name`).click()');editor_ready()
  check('closed result reopens from server storage',js('return document.querySelector("[data-server-editor] textarea").value.includes("Words (whitespace separated): 5")'))
  js('const p=document.querySelector("[aria-label=\\\"Server file path\\\"]");p.value="report-copy.txt";p.dispatchEvent(new Event("input",{bubbles:true}));');click('[data-server-editor]','Save')
  wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent==="Saved on the server."'),30)
  js('document.querySelector(`[data-server-path="${wfReportPath}"] .guest-file-name`).click();')
  wait(lambda:js('return wfDesktop.windows.some(w=>w.editor?.path===wfReportPath)&&wfDesktop.windows.some(w=>w.editor?.path==="report-copy.txt")'),20)
  check('Save As does not redirect a later original-document launch to the copy',True)
  # Hold the actual successful server response, then close its originating view.
  close_editors();task('await (await serverFileContext()).files.write("close-test.txt","one two three four");window.wfFetch=window.fetch;window.fetch=async(...args)=>{const r=await wfFetch(...args);if(args[1]?.body?.includes("\\\"operation\\\":\\\"word-count\\\"")&&args[1].body.includes("close-test.txt"))return new Promise(resolve=>{window.wfRelease=()=>resolve(r);});return r;};serverFilesChanged();return true;');list_ready();wait(lambda:js('return !!document.querySelector("[data-server-path=\\\"close-test.txt\\\"]")'),20)
  click('[data-server-path="close-test.txt"]','Word count on server');wait(lambda:js('return typeof wfRelease==="function"'),30)
  js('document.querySelector("[data-window=\\\"4\\\"] [aria-label=\\\"Close\\\"]").click();wfRelease();window.fetch=wfFetch;')
  task('await new Promise(r=>setTimeout(r,150));return true;');check('closed Files cannot open a stale result window',js('return !wfDesktop.windows.some(w=>w.app==="text")'))
  task('const w=wfDesktop.launch("files");w.storage="server";window.wfFilesId=w.id;wfDesktop.render();return true;');list_ready()
  check('accepted operation persists after originating Files closes',task('const f=(await serverFileContext()).files,entry=(await f.list()).entries.find(e=>e.name.startsWith("close-test.txt.word-count-"));return !!entry&&new TextDecoder().decode((await f.read(entry.name)).data).includes("Words (whitespace separated): 4");'))
  register(ledger['names'][1]);list_ready();check('second account sees none of the first account documents',js('return !document.querySelector("[data-server-path]")'))
  prior_errors=[e for e in call('/session/'+sid+'/log',{'type':'browser'}) if e['level']=='SEVERE'];check('no browser errors before deliberate authorization refusals',not prior_errors)
  check('server refuses another account report and source operation',task('const f=(await serverFileContext()).files;let denied=0;for(const operation of [()=>f.read(wfReportPath),()=>f.wordCount("workflow.txt",wfSaved.sha256)])try{await operation();}catch(e){if(e.status===404||e.status===403)denied++;}return denied===2;'))
  refusal_errors=[e for e in call('/session/'+sid+'/log',{'type':'browser'}) if e['level']=='SEVERE']
  (ROOT/'.build/checks/document-workflow-refusal-console.json').write_text(json.dumps(refusal_errors,indent=2)+'\n')
  check('negative-test console errors belong only to the two expected gateway denials',len(refusal_errors)<=2 and all(e.get('source')=='network' and base+'/gateway/use' in e['message'] and re.search(r'status of (?:403|404)\b',e['message']) for e in refusal_errors))
  task('await changeAccount("signin",params[0],wfPassword);return true;',[ledger['names'][0]]);list_ready()
  credentials=js('return {password:wfPassword,report:wfReportPath};')
  call('/session/'+sid+'/refresh',{});wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!desktopLab.lifecycle.blocked'),150)
  task('window.wfPassword=params[1];window.wfDesktop=[...surfaces.values()][0];window.confirm=()=>true;await changeAccount("signin",params[0],params[1]);return true;',[ledger['names'][0],credentials['password']]);click('[data-window="4"]','My server files');list_ready()
  js('document.querySelector(`[data-server-path="${arguments[0]}"] .guest-file-name`).click();',[credentials['report']]);editor_ready()
  check('browser reload and sign-in reopen persisted report with no prior window callback',js('return document.querySelector("[data-server-editor] textarea").value.includes("Words (whitespace separated): 5")'))
  for _ in range(5):
   close_editors();click('[data-server-path="workflow.txt"]','workflow.txt');editor_ready()
  check('repeated Text close and contextual reopen preserve file and working view',js('return wfDesktop.windows.filter(w=>w.app==="text").length===1&&document.querySelector("[data-server-editor] textarea").value==="Shared document\\nEdited in Text.\\n"'))
  close_editors();js('wfDesktop.activateWindow(wfDesktop.windows.find(w=>w.app==="files"));')
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
  wait(lambda:js('return document.querySelector(".desktop").classList.contains("compact-desktop")'),10)
  point=js('const b=[...document.querySelector("[data-server-path=\\\"workflow.txt\\\"]").querySelectorAll("button")].find(b=>b.textContent==="Word count on server");b.scrollIntoView({block:"center"});const r=b.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,width:r.width,height:r.height,left:r.left,right:r.right};')
  check('phone server-operation button fits viewport with a touch target',point['width']>=44 and point['height']>=44 and point['left']>=0 and point['right']<=390)
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchStart','touchPoints':[{'x':point['x'],'y':point['y']}]}})
  call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchEnd','touchPoints':[]}})
  editor_ready();check('trusted phone touch reopens persisted report through Files',js('return document.querySelector("[data-server-editor] textarea").value.includes("Words (whitespace separated): 5")'))
  errors=[e for e in call('/session/'+sid+'/log',{'type':'browser'}) if e['level']=='SEVERE'];(ROOT/'.build/checks/document-workflow-final-console.json').write_text(json.dumps(errors,indent=2)+'\n');check('no unexpected browser errors',not errors)
  screenshot=call('/session/'+sid+'/screenshot');(ROOT/'.build/checks/document-workflow.png').write_bytes(base64.b64decode(screenshot))
  return {'status':'PASS','checks':checks,'serverReport':js('return {path:arguments[0],persisted:true};',[credentials['report']]),'physicalPhoneTested':False,'realUserAccountUsed':False}
 except Exception:
  try:(ROOT/'.build/checks/document-workflow-diagnostics.json').write_text(json.dumps(js('return {text:document.body.innerText.slice(-4500),state:window.desktopLab?.guestState,windows:typeof wfDesktop!=="undefined"?wfDesktop.windows.map(w=>({id:w.id,app:w.app,title:w.title,editor:w.editor?.path})):[]};'),indent=2)+'\n')
  except Exception:pass
  raise
 finally:
  try:
   if ledger['subjects']:
    task('window.fetch=typeof wfFetch!=="undefined"?wfFetch:window.fetch;return true;')
    for name in ledger['subjects']:
     task('await changeAccount("signin",params[0],wfPassword);const f=(await serverFileContext()).files;for(const e of (await f.list()).entries){if(e.directory)throw Error("Unexpected QA directory");const r=await f.read(e.name);await f.remove(e.name,r.sha256);}return true;',[name])
    ledger['ownedFilesRemoved']=True
  finally:call('/session/'+sid,method='DELETE')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--public',action='store_true');a=p.parse_args();ledger={'names':['qa_doc_'+secrets.token_hex(6) for _ in range(2)],'subjects':{},'ownedFilesRemoved':False};result={'status':'FAIL','public':a.public}
 try:
  if a.public:origin='https://ksu.codes';args=[]
  else:
   vm=module('document_vm',ROOT/'scripts/upgrade-signin-native-vm.py');runtime=vm.runtime();installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));origin=installed['publicOrigin'];args=['--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]
  result.update(browser(origin,args,ledger),defaultPublicTLS=a.public)
  if not a.public:
   assert runtime==vm.runtime(),'Installed release changed during document workflow'
   result['installedRuntime']=runtime
 finally:
  ledger_path=ROOT/'.build/checks'/('document-public-fixtures.json' if a.public else 'document-vm-fixtures.json');ledger_path.write_text(json.dumps(ledger,indent=2)+'\n');result['fixtureLedger']=ledger_path.name;result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('document-workflow-public-result.json' if a.public else 'document-workflow-vm-result.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
