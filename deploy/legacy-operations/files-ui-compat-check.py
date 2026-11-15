#!/usr/bin/env python3
"""Real v86 browser compatibility for independently rolled-back UI assets."""
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('files_compat_fixture',ROOT/'scripts/gateway-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
call,wait=fixture.call,fixture.wait

def browser(url,old_app):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1200,900']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    def js(code):return call('/session/'+session+'/execute/sync',{'script':code,'args':[]})
    try:
        call('/session/'+session+'/url',{'url':url});wait(lambda:js('return window.desktopLab?.guestState==="ready"'),120)
        assert js('return ![...document.querySelectorAll("button")].some(b=>b.textContent==="My server files");')
        assert js('return (window.CODI_PRIVATE_FILES_UI===1)')== (not old_app)
        js('window.__compatVM=v86Instance;const d=[...surfaces.values()][0],w=d.launch("text");w.editor={path:"/Documents/compat.txt",text:"Compatible guest draft",loaded:true,dirty:true};d.render();window.__compatEditor=document.querySelector(".window.focused textarea");const save=[...document.querySelectorAll(".window.focused button")].find(b=>b.textContent==="Save");save.click();')
        wait(lambda:js('return document.querySelector(".window.focused .app-status")?.textContent.includes("in the guest")'),30)
        value=call('/session/'+session+'/execute/async',{'script':'const done=arguments[arguments.length-1];guestFiles.read("/Documents/compat.txt").then(data=>done(new TextDecoder().decode(data)),error=>done(error.message));','args':[]})
        assert value=='Compatible guest draft'
        js('const d=[...surfaces.values()][0];d.switchWorkspace(1);d.switchWorkspace(0);')
        assert js('return __compatVM===v86Instance&&__compatEditor.isConnected&&__compatEditor.value==="Compatible guest draft";')
        errors=[x for x in call('/session/'+session+'/log',{'type':'browser'}) if x['level']=='SEVERE'];assert not errors,errors
        return {'url':url,'oldAppNewDesktopApps':old_app,'newAppOldDesktopApps':not old_app,'serverFileControlsSuppressed':True,'realGuestSave':True,'vmAndEditorSurviveWorkspaceSwitch':True,'noBrowserErrors':True}
    finally:call('/session/'+session,method='DELETE')

async def main():
    results=[]
    old_sources={'app.js':ROOT/'.build/frontends/user-apps-r14/app.js','desktop-apps.js':ROOT/'.build/releases/connected-account-menu-r2/desktop-apps.js'}
    for old_app in [True,False]:
        f=fixture.Fixture('/hidden')
        try:
            await f.start();name='app.js' if old_app else 'desktop-apps.js'
            public=next((f.root/'native-runtime').glob('public-*')) if fixture.NATIVE_ROOT is not None else f.root/'public'
            shutil.copyfile(old_sources[name],public/name)
            results.append(await asyncio.to_thread(browser,f.origin+'/hidden/',old_app))
            print(json.dumps({'milestone':'mixed UI versions passed','legacyAsset':name}),flush=True)
        finally:await f.close()
    return results
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--worker-release',type=Path,required=True);p.add_argument('--issuer-release',type=Path);args=p.parse_args();fixture.WORKER_ROOT=args.worker_release.resolve()
    raw=(fixture.WORKER_ROOT/'files-service.json').read_bytes();metadata=json.loads(raw)
    for name,r in metadata['files'].items():assert r=={'bytes':(fixture.WORKER_ROOT/name).stat().st_size,'sha256':hashlib.sha256((fixture.WORKER_ROOT/name).read_bytes()).hexdigest()}
    report={'status':'FAIL','scope':'Actual local disposable Chrome/v86 mixed-version frontend rollback compatibility, not public deployment','workerManifestSHA256':hashlib.sha256(raw).hexdigest()}
    if args.issuer_release:
        from origin_service.release import verify
        fixture.NATIVE_ROOT=args.issuer_release.resolve();report['executedIssuerManifestSHA256']=verify(fixture.NATIVE_ROOT)['manifestSHA256']
    try:report.update(status='PASS',witnesses=asyncio.run(main()))
    finally:
        names=['app.js','desktop-apps.js','scripts/files-ui-compat-check.py','scripts/gateway-browser-check.py','.build/frontends/user-apps-r14/app.js','.build/releases/connected-account-menu-r2/desktop-apps.js']
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks/files-ui-compat-result.json'
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('files-ui-compat-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
