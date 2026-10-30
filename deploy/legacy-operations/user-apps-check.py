#!/usr/bin/env python3
"""Real registered-only per-account template windows, catalogs, pins and drafts."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
spec=importlib.util.spec_from_file_location('touch_test',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
call,wait=helpers.call,helpers.wait

def run(url,names):
    results=[]
    for mobile in [False,True]:
        session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
        def js(code,args=[]):return call('/session/'+session+'/execute/sync',{'script':code,'args':args})
        def asyncjs(code,args=[]):
            result=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':args})
            assert result['ok'],result.get('error');return result.get('value')
        def cdp(command,params):return call('/session/'+session+'/goog/cdp/execute',{'cmd':command,'params':params})
        def click(selector):
            rect=js('const n=document.querySelector(arguments[0]);if(!n)throw Error("Missing "+arguments[0]);const r=n.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};',[selector])
            if mobile:
                cdp('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[rect]});time.sleep(.08);cdp('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            else:
                for event in ['mousePressed','mouseReleased']:cdp('Input.dispatchMouseEvent',{'type':event,**rect,'button':'left','clickCount':1})
            time.sleep(.1)
        def menu():click('.panel .app-menu-button')
        def open_app(name):
            menu();click('.menu-row[aria-label="YOUR APP HERE"]')
            assert js('return [...document.querySelectorAll(`.menu-pane[data-depth="1"] .menu-row`)].filter(n=>n.ariaLabel!=="‹ Back").map(n=>n.ariaLabel).join("|")==="Blank canvas|My notes|My dashboard"')
            click('.menu-row[aria-label='+json.dumps(name)+']')
            return js('return [...surfaces.values()][0].active')
        def fill(value):js('const f=document.querySelector(".window.focused .prototype-draft");f.value=arguments[0];f.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:arguments[0]}));',[value])
        first='apps_'+secrets.token_hex(6);second='apps_'+secrets.token_hex(6)
        password=secrets.token_urlsafe(30)
        try:
            if mobile:
                cdp('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True});cdp('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5})
            call('/session/'+session+'/url',{'url':url});wait(lambda:js('return window.desktopLab?.guestState==="ready"'),120)
            js('window.__appVM=v86Instance;window.__appD=[...surfaces.values()][0];')
            menu();assert js('return document.querySelector(".menu-row").ariaLabel==="Terminal"&&!document.querySelector(`.menu-row[aria-label="YOUR APP HERE"]`)');click('.panel .app-menu-button')
            names.append(first);asyncjs('await changeAccount("register",params[0],params[1]);return currentSession.public.kind;',[first,password])
            js('window.__appA=currentSession.public.sub;window.__appIds=[];')
            menu();assert js('const names=[...document.querySelectorAll(".menu-row")].map(n=>n.ariaLabel);return names[0]==="YOUR APP HERE"&&names[1]==="Terminal"');click('.panel .app-menu-button')
            for index,name in enumerate(['Blank canvas','My notes','My dashboard']):
                wid=open_app(name);js('__appIds.push(arguments[0]);',[wid]);fill('Account A draft '+str(index))
            assert js('return document.querySelector(".prototype-badge").textContent===arguments[0]+"’s app"&&document.querySelectorAll(".prototype-cards .prototype-card").length===3',[first])
            wid=open_app('My notes');js('__appIds.push(arguments[0]);',[wid]);fill('Account A second notes')
            assert js('return document.querySelector(`.task[aria-label="My notes windows"] .count`).textContent==="2"')
            click('.window.focused [aria-label=Minimize]')
            assert js('return document.querySelector(`.task[aria-label="My notes windows"]`).classList.contains("running")&&document.querySelector(`.task[aria-label="My notes windows"] .count`).textContent==="2"')
            click('.task[aria-label="My notes windows"]');click('.task-popup .pin')
            js('window.__appAPin=__appD.pins.find(isAccountApp);__appD.switchWorkspace(1);')
            assert js('return !document.querySelector(`.tasks [data-app^="user-app:"]`)')
            extra=open_app('Blank canvas');fill('Account A workspace two');js('__appIds.push(arguments[0]);__appD.switchWorkspace(0);',[extra])
            asyncjs('await changeAccount("anonymous");')
            assert js('return !document.querySelector(".prototype-app")&&!document.querySelector(`.tasks [data-app^="user-app:"]`)&&!__appD.pins.some(isAccountApp)&&__appD.launch(__appAPin)===null')
            menu();assert js('return document.querySelector(".menu-row").ariaLabel==="Terminal"');click('.panel .app-menu-button')
            names.append(second);asyncjs('await changeAccount("register",params[0],params[1]);',[second,password])
            assert js('return currentSession.public.sub!==__appA&&!document.querySelector(".prototype-app")&&!__appD.pins.some(isAccountApp)')
            open_app('My notes');assert js('return document.querySelector(".window.focused .prototype-draft").value===""&&document.querySelector(".window.focused .prototype-badge").textContent===arguments[0]+"’s app"',[second]);fill('Account B separate draft')
            click('.task[aria-label="My notes windows"]');click('.task-popup .pin')
            js('window.__appBPin=__appD.pins.find(isAccountApp);')
            assert js('return __appAPin!==__appBPin&&!__appD.pins.includes(__appAPin)&&document.querySelectorAll(".prototype-app").length===1')
            asyncjs('await changeAccount("anonymous");await changeAccount("signin",params[0],params[1]);',[first,password])
            assert js('return currentSession.public.sub===__appA&&__appD.pins.includes(__appAPin)&&!__appD.pins.includes(__appBPin)&&__appIds.every(id=>document.querySelector(`[data-window="${id}"] .prototype-app`))&&[...document.querySelectorAll(".prototype-draft")].every(n=>n.value.startsWith("Account A"))&&document.querySelectorAll(".prototype-app").length===5&&v86Instance===__appVM')
            js('window.__appExpiry=currentSession.trust.claims.exp;currentSession.trust.claims.exp=0;__appD.render();')
            assert js('return !document.querySelector(".prototype-app")&&accountApplications().length===0')
            js('currentSession.trust.claims.exp=__appExpiry;__appD.render();__appD.activateWindow(__appD.windows.find(w=>w.id===__appIds[0]));')
            assert js('return document.querySelector(".window.focused .prototype-draft").value==="Account A draft 0"')
            send='sendTerminal(2,"printf \'\\nUSER_APPS_VM_OK\\n\'\\r");';js(send);wait(lambda:js('return /(?:^|\\n)USER_APPS_VM_OK(?:\\n|$)/.test(serialScreen.text())'))
            screenshot=CHECKS/('user-apps-mobile.png' if mobile else 'user-apps-desktop.png');screenshot.write_bytes(base64.b64decode(call('/session/'+session+'/screenshot')))
            results.append({'mobile':mobile,'anonymousHasNoPersonalApps':True,'menuEntryAboveTerminal':True,'threeDistinctTemplates':True,'multipleInstances':True,'draftsCatalogPinsAndWindowsIsolatedByStableAccount':True,'workspaceIsolation':True,'minimizedCountsRetained':True,'sameAccountReloginRestoresDrafts':True,'expiredIdentityHidesApps':True,'linuxVmUnchanged':True,'serverPersistence':False})
        finally:call('/session/'+session,method='DELETE')
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--url');a=p.parse_args();server=None;temp=None;log=None;names=[]
    report={'status':'FAIL','scope':'Real issuer accounts and Chrome mouse/touch emulation; personal template UI is RAM-only, not a server authorization boundary'}
    try:
        if a.url:url=a.url
        else:
            temp=tempfile.TemporaryDirectory(prefix='codi-user-apps-')
            with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            url='http://127.0.0.1:'+str(port)+'/'
            log=(CHECKS/'user-apps-local.log').open('w')
            server=subprocess.Popen([sys.executable,'-B',str(ROOT/'scripts/serve-connected.py'),'--port',str(port),'--runtime-dir',temp.name],stdout=log,stderr=log)
            def ready():
                if server.poll() is not None:raise AssertionError('Fixture issuer exited')
                try:
                    with urllib.request.urlopen(url+'config.json',timeout=2) as response:return response.status==200
                except OSError:return False
            wait(ready,30)
        report.update(url=url,witnesses=run(url,names),status='PASS')
        report['servedAssetsSHA256']={}
        for name in ['app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz']:
            with urllib.request.urlopen(url+name,timeout=20) as response:report['servedAssetsSHA256'][name]=hashlib.sha256(response.read()).hexdigest()
            assert report['servedAssetsSHA256'][name]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    finally:
        if server:server.terminate();server.wait(timeout=15)
        if log:log.close()
        if temp:temp.cleanup()
        (CHECKS/'user-apps-fixture-names.json').write_text(json.dumps(names)+'\n')
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['app.js','style.css','scripts/user-apps-check.py']}
        output=CHECKS/('user-apps-public-result.json' if a.url else 'user-apps-result.json')
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
