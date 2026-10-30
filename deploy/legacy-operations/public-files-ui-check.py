#!/usr/bin/env python3
"""Default-trusted public Files UI tests using only two generated QA accounts.

No user tabs or real account files are inspected. Passwords stay only in the
owned disposable Chrome context; the ledger retains public names/subjects.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('public_files_helpers',ROOT/'scripts/gateway-files-ui-check.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
call,wait=helpers.call,helpers.wait
LEDGER=ROOT/'.build/checks/public-files-fixtures.json'
def persist(value):
    LEDGER.write_text(json.dumps(value,indent=2)+'\n')

def browser(url, names, ledger):
    transfer_dir=Path(tempfile.mkdtemp(prefix='owned-file-transfer-',dir=ROOT/'.build/checks'))
    upload_file=transfer_dir/'imported.bin';upload_bytes=bytes(range(256))*16;upload_file.write_bytes(upload_bytes)
    downloads=transfer_dir/'downloads';downloads.mkdir()
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1200,900']},'goog:loggingPrefs':{'browser':'ALL','performance':'ALL'}}}})['sessionId']
    def js(source,args=[]):return call('/session/'+session+'/execute/sync',{'script':source,'args':args})
    def task(source,args=[]):
        value=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':args})
        assert value['ok'],value
        return value.get('value')
    def ready_list():wait(lambda:js('return document.querySelector("[data-server-file-list]")?.getAttribute("aria-busy")==="false"'),30)
    def click(selector,label):
        assert js('const root=document.querySelector(arguments[0]),b=[...(root?.querySelectorAll("button")||[])].find(n=>n.textContent===arguments[1]);if(!b)return false;b.click();return true;',[selector,label]),(selector,label)
    def fill(selector,text):js('const field=document.querySelector(arguments[0]);if(!field)throw Error("Missing "+arguments[0]);field.value=arguments[1];field.dispatchEvent(new Event("input",{bubbles:true}));',[selector,text])
    def guest_ready():
        if js('return window.desktopLab?.guestState==="error"'):raise AssertionError(js('return guestMessage'))
        return js('return window.desktopLab?.guestState==="ready"')
    try:
        call('/session/'+session+'/timeouts',{'script':120000})
        call('/session/'+session+'/goog/cdp/execute',{'cmd':'Browser.setDownloadBehavior','params':{'behavior':'allow','downloadPath':str(downloads)}})
        call('/session/'+session+'/url',{'url':url});wait(guest_ready,120)
        task('window.__uiDesktop=[...surfaces.values()][0];window.__uiVM=v86Instance;window.__uiName=params[0];window.__uiPass=crypto.randomUUID()+crypto.randomUUID();window.confirm=()=>true;await guestFiles.write("/Documents/temporary.txt","Temporary Linux content");const w=__uiDesktop.launch("text");w.editor={path:"/Documents/draft.txt",text:"keep this guest draft",loaded:true,dirty:true};__uiDesktop.render();window.__uiGuestEditor=document.querySelector("[data-window=\\\""+w.id+"\\\"] textarea");return true;',[names[0]])
        click('[data-window="4"]','My server files')
        assert js('return document.querySelector("[data-window=\\\"4\\\"]").textContent.includes("Sign in using Anon")&&!document.querySelector("[data-server-file-list]");')
        task('await changeAccount("register",__uiName,__uiPass);window.__uiOwner=signedInSubject();return true;')
        ledger["subjects"][names[0]]=js("return signedInSubject()")
        persist(ledger)
        ready_list()
        assert js('return __uiGuestEditor.isConnected&&__uiGuestEditor.value==="keep this guest draft"&&v86Instance===__uiVM;')
        fill('[aria-label="New server item name"]','Saved');click('[data-window="4"]','New folder')
        wait(lambda:js('return !!document.querySelector("[data-server-path=Saved]")'),30)
        click('[data-server-path="Saved"]','▸ Saved');ready_list()
        fill('[aria-label="New server item name"]','note.txt');click('[data-window="4"]','New text file')
        wait(lambda:js('return !!document.querySelector("[data-server-editor] textarea:not(:disabled)")'),30)
        fill('[aria-label="Server text document"]','Saved through the real editor')
        click('[data-server-editor]','Save')
        wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent==="Saved on the server."'),30)
        task('window.__uiContext=await serverFileContext();window.__uiVersion=await __uiContext.files.read("Saved/note.txt");if(new TextDecoder().decode(__uiVersion.data)!=="Saved through the real editor")throw Error("UI save missing");await __uiContext.files.write("Saved/note.txt","Changed in another session",__uiVersion.sha256);return true;')
        fill('[aria-label="Server text document"]','unsaved conflicting draft');click('[data-server-editor]','Save')
        wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent.includes("File changed")'),30)
        assert js('return document.querySelector("[aria-label=\\\"Server text document\\\"]").value==="unsaved conflicting draft";')
        click('[data-server-editor]','Reload')
        wait(lambda:js('return document.querySelector("[aria-label=\\\"Server text document\\\"]")?.value==="Changed in another session"'),30)
        ready_list();click('[data-server-path="Saved/note.txt"]','Copy to guest')
        wait(lambda:task('try{return new TextDecoder().decode(await guestFiles.read("/Downloads/note.txt"))==="Changed in another session";}catch{return false;}'),30)
        # A second click refuses to overwrite independently edited guest data.
        task('await guestFiles.write("/Downloads/note.txt","my temporary Linux edit");return true;')
        click('[data-server-path="Saved/note.txt"]','Copy to guest')
        wait(lambda:js('return document.querySelector("[data-window=\\\"4\\\"] .app-status")?.textContent.includes("already in guest Downloads")'),30)
        assert task('return new TextDecoder().decode(await guestFiles.read("/Downloads/note.txt"))==="my temporary Linux edit";')
        click('[data-window="4"]','Temporary files');click('[data-window="4"]','Home')
        click('[data-path="/Documents"]','▸ Documents')
        js('window.prompt=()=>"from-guest.txt";')
        click('[data-path="/Documents/temporary.txt"]','Save to server…')
        wait(lambda:task('try{return new TextDecoder().decode((await __uiContext.files.read("from-guest.txt")).data)==="Temporary Linux content";}catch{return false;}'),30)
        click('[data-window="4"]','My server files');ready_list();click('[data-window="4"]','Home');ready_list()
        upload_element=call('/session/'+session+'/element',{'using':'css selector','value':'[aria-label="Import server files"]'})['element-6066-11e4-a52e-4f735466cecf']
        call('/session/'+session+'/element/'+upload_element+'/value',{'text':str(upload_file)})
        wait(lambda:js('return !!document.querySelector("[data-server-path=\\\"imported.bin\\\"]")'),30)
        click('[data-server-path="imported.bin"]','Download')
        wait(lambda:(downloads/'imported.bin').exists(),30)
        assert (downloads/'imported.bin').read_bytes()==upload_bytes
        ledger['actualImportAndDownloadSHA256']=hashlib.sha256(upload_bytes).hexdigest();persist(ledger)
        binary=task('const f=(await serverFileContext()).files,b=new Uint8Array(8*1024*1024);for(let i=0;i<b.length;i++)b[i]=(i*17+9)%251;window.__uiBinary=await f.write("maximum.bin",b);const r=await f.read("maximum.bin");if(r.data.length!==b.length||r.data.some((v,i)=>v!==b[i]))throw Error("Maximum binary transfer mismatch");return {bytes:r.data.length,sha256:r.sha256};')
        ledger['maximumBinaryTransfer']=binary;persist(ledger)
        # Pause an actual successful response before SDK delivery, switch account,
        # then release it. The old model and DOM must not receive its contents.
        task('await __uiContext.files.write("late.txt","private delayed response");window.__uiFetch=window.fetch;window.fetch=async(...args)=>{const response=await __uiFetch(...args);if(String(args[0]).endsWith("/gateway/use")&&args[1]?.body?.includes("\\\"path\\\":\\\"late.txt\\\"")&&args[1].body.includes("\\\"operation\\\":\\\"read\\\""))return new Promise(resolve=>{window.__releaseFileResponse=()=>resolve(response);});return response;};openServerEditor(__uiDesktop,__uiOwner,"late.txt");window.__uiLate=__uiDesktop.windows.at(-1);return true;')
        wait(lambda:js('return typeof __releaseFileResponse==="function"'),30)
        task('await changeAccount("register",params[0],__uiPass);__releaseFileResponse();window.fetch=__uiFetch;return true;',[names[1]])
        ledger["subjects"][names[1]]=js("return signedInSubject()")
        persist(ledger)
        wait(lambda:js('return !document.querySelector("[data-server-editor]")'),30)
        assert js('return __uiLate.editor.text===""&&!__uiLate.editor.loaded&&__uiGuestEditor.isConnected&&__uiGuestEditor.value==="keep this guest draft";')
        click('[data-window="4"]','My server files');ready_list()
        assert js('return !document.querySelector("[data-server-path]")&&!document.querySelector("[data-server-editor]")&&v86Instance===__uiVM;')
        task('await changeAccount("signin",__uiName,__uiPass);return true;');ready_list()
        wait(lambda:js('return !!document.querySelector("[data-server-editor] textarea:not(:disabled)")'),30)
        assert js('return __uiDesktop.windows.some(w=>w.editor?.storage==="server"&&w.editor.path==="Saved/note.txt"&&w.editor.text==="Changed in another session");')
        account=js('return {name:__uiName,password:__uiPass};')
        call('/session/'+session+'/refresh',{});wait(guest_ready,120)
        task('await changeAccount("signin",params[0].name,params[0].password);window.__uiName=params[0].name;window.__uiPass=params[0].password;window.__uiOwner=signedInSubject();return true;',[account])
        click('[data-window="4"]','My server files');ready_list();click('[data-server-path="Saved"]','▸ Saved');ready_list();click('[data-server-path="Saved/note.txt"]','note.txt')
        wait(lambda:js('return document.querySelector("[aria-label=\\\"Server text document\\\"]")?.value==="Changed in another session"'),30)
        call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
        call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
        wait(lambda:js('return document.querySelector(".desktop").classList.contains("compact-desktop")'),10)
        fill('[aria-label="Server text document"]','Saved with phone touch')
        point=js('const b=[...document.querySelectorAll("[data-server-editor] button")].find(b=>b.textContent==="Save"),r=b.getBoundingClientRect();if(r.width<44||r.height<44||r.right>innerWidth||r.left<0)throw Error("Phone save control outside viewport");return {x:r.x+r.width/2,y:r.y+r.height/2};')
        call('/session/'+session+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchStart','touchPoints':[point]}})
        call('/session/'+session+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchEnd','touchPoints':[]}})
        wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent==="Saved on the server."'),30)
        assert task('return new TextDecoder().decode((await (await serverFileContext()).files.read("Saved/note.txt")).data)==="Saved with phone touch";')
        return {'url':url,'anonymousInstructionsWithoutHome':True,'actualEditorSaveAndRead':True,'versionConflictPreservesDraft':True,'serverToGuestExplicitCopy':True,'guestCopyRefusesOverwrite':True,'guestToServerExplicitSave':True,'accountSwitchKeepsGuestVMAndDraft':True,'otherAccountUIIsolation':True,'lateResponseCannotPopulateOtherAccount':True,'sameAccountDraftRestoration':True,'serverFileSurvivesBrowserReload':True,'mobileViewportAndTrustedTouchSave':True,'actualBrowserFileImport':True,'actualDownloadedFileMatches':True}
    except BaseException:
        failures=[]
        for entry in call('/session/'+session+'/log',{'type':'performance'}):
            message=json.loads(entry['message'])['message']
            if message['method']=='Network.responseReceived':
                response=message['params']['response']
                if response['status']>=400:failures.append({'url':response['url'],'status':response['status']})
        print(json.dumps({'browserFailureHTTP':failures,'guestMessage':js('return typeof guestMessage==="undefined"?null:guestMessage')}),flush=True)
        raise
    finally:
        try:
            if js('return typeof __uiOwner!=="undefined"&&typeof __uiName!=="undefined"'):
                task('if(signedInSubject()!==__uiOwner)await changeAccount("signin",__uiName,__uiPass);const f=(await serverFileContext()).files;async function clean(path){for(const entry of (await f.list(path)).entries){const p=path?path+"/"+entry.name:entry.name;if(entry.directory){await clean(p);await f.remove(p,null);}else{const value=await f.read(p);await f.remove(p,value.sha256);}}}await clean("");return true;')
                ledger['ownedFilesRemoved']=True
                persist(ledger)
        finally:
            call('/session/'+session,method='DELETE')
            shutil.rmtree(transfer_dir)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='https://ksu.codes/hidden/')
    args=parser.parse_args()
    assert args.url=='https://ksu.codes/hidden/'
    if LEDGER.exists():
        old=json.loads(LEDGER.read_text())
        assert old.get('accountsDisabled') is True,'Clean up prior owned QA accounts before another run'
        LEDGER.rename(LEDGER.with_name('public-files-fixtures-before-'+str(time.time_ns())+'.json'))
    names=['fqa_'+secrets.token_hex(6) for _ in range(2)]
    ledger={'version':1,'names':names,'subjects':{},'accountsDisabled':False,'ownedFilesRemoved':False}
    persist(ledger)
    report={'status':'FAIL','scope':'Actual public HTTPS with default trust, disposable QA accounts only; touch emulated, not independent WAN','url':args.url,'defaultCertificateTrust':True}
    try:
        report['witness']=browser(args.url,names,ledger)
        report['status']='PASS'
        report['servedAssetsSHA256']={}
        for name in ['app.js','style.css','desktop-apps.js','terminal.js','assets/terminal-initramfs.cpio.gz','gateway/client.mjs']:
            with urllib.request.urlopen(args.url+name,timeout=20) as response:
                report['servedAssetsSHA256'][name]=hashlib.sha256(response.read()).hexdigest()
        report['maximumBinaryTransfer']=ledger['maximumBinaryTransfer']
        report['actualImportAndDownloadSHA256']=ledger['actualImportAndDownloadSHA256']
    finally:
        report['fixtureLedger']=str(LEDGER.relative_to(ROOT))
        report['testFilesRemoved']=ledger['ownedFilesRemoved']
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/public-files-ui-check.py','scripts/gateway-files-ui-check.py']}
        output=ROOT/'.build/checks/public-files-ui-result.json'
        if output.exists():output.rename(output.with_name('public-files-ui-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
