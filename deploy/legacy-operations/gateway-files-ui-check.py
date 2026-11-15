#!/usr/bin/env python3
"""Real Chrome Files/editor operations with disposable signed accounts and worker.

Uses root and /hidden same-origin fixtures. No real account, tab or deployment
is changed. The worker is the sealed artifact, not an in-process test double.
"""
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('file_ui_fixture',ROOT/'scripts/gateway-browser-check.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
call,wait=fixture.call,fixture.wait

def browser(url):
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
        call('/session/'+session+'/url',{'url':url});wait(guest_ready,120)
        task('window.__uiDesktop=[...surfaces.values()][0];window.__uiVM=v86Instance;window.__uiName="files_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.__uiPass=crypto.randomUUID()+crypto.randomUUID();window.confirm=()=>true;await guestFiles.write("/Documents/temporary.txt","Temporary Linux content");const w=__uiDesktop.launch("text");w.editor={path:"/Documents/draft.txt",text:"keep this guest draft",loaded:true,dirty:true};__uiDesktop.render();window.__uiGuestEditor=document.querySelector("[data-window=\\\""+w.id+"\\\"] textarea");return true;')
        click('[data-window="4"]','My server files')
        assert js('return document.querySelector("[data-window=\\\"4\\\"]").textContent.includes("Sign in using Anon")&&!document.querySelector("[data-server-file-list]");')
        task('await changeAccount("register",__uiName,__uiPass);window.__uiOwner=signedInSubject();return true;')
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
        # Pause an actual successful response before SDK delivery, switch account,
        # then release it. The old model and DOM must not receive its contents.
        task('await __uiContext.files.write("late.txt","private delayed response");window.__uiFetch=window.fetch;window.fetch=async(...args)=>{const response=await __uiFetch(...args);if(String(args[0]).endsWith("/gateway/use")&&args[1]?.body?.includes("\\\"path\\\":\\\"late.txt\\\"")&&args[1].body.includes("\\\"operation\\\":\\\"read\\\""))return new Promise(resolve=>{window.__releaseFileResponse=()=>resolve(response);});return response;};openServerEditor(__uiDesktop,__uiOwner,"late.txt");window.__uiLate=__uiDesktop.windows.at(-1);return true;')
        wait(lambda:js('return typeof __releaseFileResponse==="function"'),30)
        task('await changeAccount("register","files_"+crypto.randomUUID().replaceAll("-","").slice(0,12),__uiPass);__releaseFileResponse();window.fetch=__uiFetch;return true;')
        wait(lambda:js('return !document.querySelector("[data-server-editor]")'),30)
        assert js('return __uiLate.editor.text===""&&!__uiLate.editor.loaded&&__uiGuestEditor.isConnected&&__uiGuestEditor.value==="keep this guest draft";')
        click('[data-window="4"]','My server files');ready_list()
        assert js('return !document.querySelector("[data-server-path]")&&!document.querySelector("[data-server-editor]")&&v86Instance===__uiVM;')
        task('await changeAccount("signin",__uiName,__uiPass);return true;');ready_list()
        wait(lambda:js('return !!document.querySelector("[data-server-editor] textarea:not(:disabled)")'),30)
        assert js('return __uiDesktop.windows.some(w=>w.editor?.storage==="server"&&w.editor.path==="Saved/note.txt"&&w.editor.text==="Changed in another session");')
        account=js('return {name:__uiName,password:__uiPass};')
        call('/session/'+session+'/refresh',{});wait(guest_ready,120)
        task('await changeAccount("signin",params[0].name,params[0].password);return true;',[account])
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
        return {'url':url,'anonymousInstructionsWithoutHome':True,'actualEditorSaveAndRead':True,'versionConflictPreservesDraft':True,'serverToGuestExplicitCopy':True,'guestCopyRefusesOverwrite':True,'guestToServerExplicitSave':True,'accountSwitchKeepsGuestVMAndDraft':True,'otherAccountUIIsolation':True,'lateResponseCannotPopulateOtherAccount':True,'sameAccountDraftRestoration':True,'serverFileSurvivesBrowserReload':True,'mobileViewportAndTrustedTouchSave':True}
    except BaseException:
        failures=[]
        for entry in call('/session/'+session+'/log',{'type':'performance'}):
            message=json.loads(entry['message'])['message']
            if message['method']=='Network.responseReceived':
                response=message['params']['response']
                if response['status']>=400:failures.append({'url':response['url'],'status':response['status']})
        print(json.dumps({'browserFailureHTTP':failures,'guestMessage':js('return typeof guestMessage==="undefined"?null:guestMessage')}),flush=True)
        raise
    finally:call('/session/'+session,method='DELETE')

async def main():
    result=[]
    for base in ['', '/hidden']:
        f=fixture.Fixture(base)
        try:
            await f.start();result.append(await asyncio.to_thread(browser,f.origin+base+'/'))
            print(json.dumps({'milestone':'Files UI passed','basePath':base}),flush=True)
        finally:await f.close()
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker-release',type=Path,required=True);parser.add_argument('--issuer-release',type=Path);args=parser.parse_args()
    fixture.WORKER_ROOT=args.worker_release.resolve();raw=(fixture.WORKER_ROOT/'files-service.json').read_bytes();metadata=json.loads(raw)
    assert metadata['version']=='codi-private-file-service/1'
    for name,record in metadata['files'].items():
        assert record=={'bytes':(fixture.WORKER_ROOT/name).stat().st_size,'sha256':hashlib.sha256((fixture.WORKER_ROOT/name).read_bytes()).hexdigest()}
        assert (ROOT/name).read_bytes()==(fixture.WORKER_ROOT/name).read_bytes()
    report={'status':'FAIL','scope':'Local actual Chrome Files/editor with real issuer, sealed worker process, SQLite/disk and v86; not installed on live preview','workerManifestSHA256':hashlib.sha256(raw).hexdigest()}
    if args.issuer_release:
        from origin_service.release import verify
        fixture.NATIVE_ROOT=args.issuer_release.resolve();report['executedIssuerManifestSHA256']=verify(fixture.NATIVE_ROOT)['manifestSHA256']
    try:report.update(status='PASS',witnesses=asyncio.run(main()))
    finally:
        names=['app.js','style.css','desktop-apps.js','scripts/gateway-files-ui-check.py','scripts/gateway-browser-check.py']
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
        output=ROOT/'.build/checks/gateway-files-ui-result.json'
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('gateway-files-ui-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
