#!/usr/bin/env python3
"""Actual desktop/Chrome/v86 regression for app API 2 view lifetimes.

Owned loopback fixture only; checks real Desktop.render and Close actions rather
than simulating them. Does not touch live services or user tabs.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('app_desktop_fixture',ROOT/'scripts/guest-client-browser-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
f.PAGE=(ROOT/'index.html').read_bytes()
call,wait=f.call,f.wait

def browser(fixture):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[]
    def js(script,args=[]):return call('/session/'+sid+'/execute/sync',{'script':script,'args':args})
    def check(label,value):assert value,label;checks.append(label)
    def mounted(id):wait(lambda:js('return !!document.querySelector("[data-window=\\\""+arguments[0]+"\\\"]")?.appView',[id]),30)
    try:
        call('/session/'+sid+'/url',{'url':fixture.origin+fixture.base+'/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&!!document.querySelector("[data-window=\\\"2\\\"]")?.appView'),150)
        js('window.d=[...surfaces.values()][0];window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;window.kept=terminalSessions.get(2);window.first=document.querySelector("[data-window=\\\"2\\\"]");window.originalView=first.appView;window.disposeCalls=0;const dispose=originalView.dispose;originalView.dispose=(...a)=>{disposeCalls++;return dispose(...a);};')
        js('d.switchWorkspace(1);d.switchWorkspace(0);const w=d.windows.find(w=>w.id===2);w.minimized=true;d.render();w.minimized=false;w.rolled=true;d.render();w.rolled=false;d.render();')
        check('real workspace/minimize/roll-up retain same view and PTY without disposal',js('return disposeCalls===0&&!originalView.signal.aborted&&first.appView===originalView&&terminalSessions.get(2)===kept'))
        ids={}
        for name in ['calculator','help','chat','rooms','text','files','terminal']:
            id=js('return d.launch(arguments[0]).id',[name]);mounted(id);ids[name]=id
        check('all seven migrated applications mount through API 2',True)
        js('const i=document.querySelector("[aria-label=\\\"Arithmetic expression\\\"]");i.value="(12+8)/4";i.form.requestSubmit();')
        check('bundled calculator still computes',js('return document.querySelector(".calculator-result").textContent==="5"'))
        js('sendTerminal(2,"export APP_SCOPE_KEEP=original; printf \\\"\\\\nAPP_SCOPE_ORIGINAL\\\\n\\\"\\r")')
        wait(lambda:js('return serialScreen.text().includes("\\nAPP_SCOPE_ORIGINAL\\n")'),20)
        second=ids['terminal']
        js('sendTerminal(arguments[0],"export APP_SCOPE_KEEP=second; printf \\\"\\\\nAPP_SCOPE_SECOND\\\\n\\\"\\r")',[second])
        wait(lambda:js('return terminalSessions.get(arguments[0]).screen.text().includes("\\nAPP_SCOPE_SECOND\\n")',[second]),20)
        js('first.querySelector("[aria-label=Close]").click();')
        check('actual Close disposes view once and closes only its PTY',js('return disposeCalls===1&&originalView.signal.aborted&&!first.isConnected&&!terminalSessions.has(2)&&terminalSessions.has(arguments[0])',[second]))
        js('sendTerminal(arguments[0],"printf \\\"\\\\nAPP_STILL=%s\\\\n\\\" \\\"$APP_SCOPE_KEEP\\\"\\r")',[second])
        wait(lambda:js('return terminalSessions.get(arguments[0]).screen.text().includes("\\nAPP_STILL=second\\n")',[second]),20)
        check('second independent shell and Linux/filesystem survive first terminal close',js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS'))
        editor=ids['text']
        js('window.editorWin=document.querySelector("[data-window=\\\""+arguments[0]+"\\\"]");window.editorView=editorWin.appView;d.windows.find(w=>w.id===arguments[0]).editor={path:"/Documents/Other.txt",text:"new model",loaded:true,dirty:false};d.render();',[editor])
        mounted(editor)
        check('real editor-model replacement disposes old view before new mount',js('return editorView.signal.aborted&&!editorWin.isConnected&&document.querySelector("[data-window=\\\""+arguments[0]+"\\\"] .guest-editor").value==="new model"',[editor]))
        js('window.ownerWin=document.querySelector("[data-window=\\\""+arguments[0]+"\\\"]");window.ownerView=ownerWin.appView;d.windows.find(w=>w.id===arguments[0]).ownerSub="unavailable-account";d.render();',[ids['calculator']])
        check('account-owned view removal disposes resources',js('return ownerView.signal.aborted&&!ownerWin.isConnected'))
        errors=call('/session/'+sid+'/log',{'type':'browser'})
        unexpected=[e for e in errors if e['level']=='SEVERE']
        check('no unexpected Chrome errors',not unexpected)
        return {'status':'PASS','checks':checks,'actualV86Linux':True,'actualDesktopRenderAndClose':True,'physicalPhoneTested':False,'liveChanged':False}
    finally:
        try:js('v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')

async def main():
    fixture=f.Fixture('/hidden')
    try:
        await fixture.start()
        return await asyncio.to_thread(browser,fixture)
    finally:await fixture.close()

if __name__=='__main__':
    result={'status':'FAIL'}
    try:result=asyncio.run(main())
    finally:
        names=['scripts/public-app-desktop-check.py','app.js','desktop-apps.js','terminal.js','assets/desktop/apps.mjs','assets/desktop/app-instance.mjs','assets/desktop/apps.json']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
        result['appSourcesSHA256']={p.parent.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT.parent/'served_apps_public').glob('*/index.mjs')}
        path=ROOT/'.build/checks/public-app-desktop-result.json'
        if path.exists():path.rename(path.with_name('public-app-desktop-before-'+str(time.time_ns())+'.json'))
        path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
