#!/usr/bin/env python3
"""Actual optional account menu in fresh mobile/desktop Chrome and real issuer."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'scripts'))
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location('touch_helpers', ROOT/'scripts/touch-preview-check.py')
helpers = module_from_spec(spec);spec.loader.exec_module(helpers)
call, wait = helpers.call, helpers.wait
CHECKS = ROOT/'.build/checks'

def run(url):
    observations = [];names = []
    try:
        for mobile in [False, True]:
            session = call('/session', {'capabilities': {'alwaysMatch': {'browserName': 'chrome', 'goog:chromeOptions': {'binary': '/snap/chromium/current/usr/lib/chromium-browser/chrome', 'args': ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--window-size=1366,900']}, 'goog:loggingPrefs': {'browser': 'ALL'}}}})['sessionId']
            def js(code, args=[]):return call('/session/'+session+'/execute/sync', {'script': code, 'args': args})
            def cdp(command, params):return call('/session/'+session+'/goog/cdp/execute', {'cmd': command, 'params': params})
            def click(selector):
                rect = js('const r=document.querySelector(arguments[0]).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};', [selector])
                if mobile:
                    cdp('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[rect]});time.sleep(.08)
                    cdp('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
                else:
                    for event in ['mousePressed','mouseReleased']:cdp('Input.dispatchMouseEvent', {'type':event,**rect,'button':'left','clickCount':1})
                time.sleep(.15)
            def field(name, value):
                js('const f=document.querySelector(".account-form [name="+arguments[0]+"]");f.value=arguments[1];f.dispatchEvent(new InputEvent("input",{bubbles:true,inputType:"insertText",data:arguments[1]}));', [name,value])
            def form(mode):click('.panel .account');click('[data-account-action="'+mode+'"]')
            def submit():click('.account-form button[type=submit]')
            name = 'menu_'+secrets.token_hex(6);password = secrets.token_urlsafe(30)
            try:
                if mobile:
                    cdp('Emulation.setDeviceMetricsOverride', {'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
                    cdp('Emulation.setTouchEmulationEnabled', {'enabled':True,'maxTouchPoints':5})
                call('/session/'+session+'/url', {'url':url})
                wait(lambda:js('return window.desktopLab?.guestState==="ready"'), 120)
                assert js('return currentSession.public.kind==="anonymous"&&document.querySelector(".account-label").textContent==="Anon"&&!document.querySelector(".account-form")')
                assert js('const r=document.querySelector(".panel .account").getBoundingClientRect();return r.right<=innerWidth&&r.right>=innerWidth-12&&r.width>=44')
                js('window.__accountVM=v86Instance;window.__accountAnon=currentSession;window.__accountTerminal=document.querySelector(".terminal-input");const d=[...surfaces.values()][0];window.__accountEditor=d.launch("text");window.__accountEditorDOM=document.querySelector(".guest-editor");__accountEditorDOM.value="Editor stays open";__accountEditorDOM.dispatchEvent(new Event("input",{bubbles:true}));d.launch("chat");document.querySelector("[data-chat-history]").textContent="Synthetic retained transcript";sendTerminal(2,"export ACCOUNT_KEEP=shell_stays; printf file_stays > /home/guest/account-keep.txt\\r");')
                form('signin')
                if mobile:
                    assert js('const r=document.querySelector(".account-popup").getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.bottom<=visualViewport.height&&[...document.querySelectorAll(".account-form input")].every(n=>n.getBoundingClientRect().height>=44)')
                    (CHECKS/'account-signin-mobile.png').write_bytes(base64.b64decode(call('/session/'+session+'/screenshot')))
                    click('.account-form [aria-label=Keyboard]')
                    assert js('return document.activeElement.name==="username"&&document.documentElement.dataset.keyboardMode==="typing"')
                field('username',name);field('password',password);submit()
                wait(lambda:js('return document.querySelector(".account-error")?.textContent.includes("Unable")'))
                assert js('return currentSession===__accountAnon&&v86Instance===__accountVM')
                click('.account-form [aria-label=Cancel]')
                form('register');field('username',name);field('password',password);field('confirmation',password+'different');submit()
                assert js('return document.querySelector(".account-error").textContent==="Passwords do not match."&&currentSession===__accountAnon')
                field('confirmation',password);submit()
                wait(lambda:js('return currentSession.public.kind==="registered"&&!accountTransition'))
                names.append(name)
                assert js('return currentSession.public.name===arguments[0]&&document.querySelector(".account-label").textContent===arguments[0]&&currentSession.trust.level==="test-server"', [name])
                assert js('return v86Instance===__accountVM&&document.querySelector(".terminal-input")===__accountTerminal&&document.querySelector(".guest-editor")===__accountEditorDOM&&__accountEditorDOM.value==="Editor stays open"&&__accountEditor.editor.dirty')
                assert js('return [...document.querySelectorAll(".account-archive")].some(n=>n.textContent.includes("Signed peer chat"))&&!document.querySelector("[data-chat-content]")')
                js('window.__registeredSubject=currentSession.public.sub;sendTerminal(2,"printf \'\\nACCOUNT_PRESERVED=%s:\' \\"$ACCOUNT_KEEP\\"; cat /home/guest/account-keep.txt; printf \'\\n\'\\r");')
                wait(lambda:js('return /(?:^|\\n)ACCOUNT_PRESERVED=shell_stays:file_stays(?:\\n|$)/.test(serialScreen.text())'))
                click('.panel .account');click('.status-popup [aria-label="Sign out"]')
                wait(lambda:js('return currentSession.public.kind==="anonymous"&&!accountTransition'))
                form('register');field('username',name);field('password',password);field('confirmation',password);submit()
                wait(lambda:js('return document.querySelector(".account-error")?.textContent.includes("Username unavailable")'))
                assert js('return currentSession.public.kind==="anonymous"&&v86Instance===__accountVM')
                click('.account-form [aria-label=Cancel]')
                form('signin');field('username',name);field('password','wrong password entirely');submit()
                wait(lambda:js('return document.querySelector(".account-error")?.textContent.includes("Unable")'))
                field('password',password);submit()
                wait(lambda:js('return currentSession.public.kind==="registered"&&!accountTransition'))
                assert js('return currentSession.public.sub===__registeredSubject&&v86Instance===__accountVM')
                # A second device/tab still starts anonymous; no local identity restore.
                call('/session/'+session+'/refresh', {})
                wait(lambda:js('return window.desktopLab?.guestState==="ready"'))
                assert js('return currentSession.public.kind==="anonymous"&&document.querySelector(".account-label").textContent==="Anon"')
                click('.panel .account')
                assert js('return ["Register","Sign in","Network","Test server validated"].every(s=>document.querySelector(".status-popup").textContent.includes(s))')
                picture = CHECKS/('account-menu-mobile.png' if mobile else 'account-menu-desktop.png')
                picture.write_bytes(base64.b64decode(call('/session/'+session+'/screenshot')))
                observations.append({'mobile':mobile,'anonymousDefault':True,'registerAndSigninDistinct':True,'failedSigninKeepsAnonymous':True,'registeredSubjectReused':True,'guestShellFilesAndEditorPreserved':True,'previousNetworkViewRetained':True,'refreshStartsAnonymous':True,'screenshot':str(picture)})
            finally:
                call('/session/'+session, method='DELETE')
        return observations
    finally:
        # Only account names are retained for explicit disposable-account cleanup.
        (CHECKS/'account-menu-fixture-names.json').write_text(json.dumps(names)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--url');parser.add_argument('--release',type=Path);args=parser.parse_args()
    server=None;temp=None;log=None
    report={'status':'FAIL','scope':'Actual Chrome UI, signed issuer crypto, SQLite and v86; touch is emulated, not a physical phone keyboard test'}
    try:
        if args.url:url=args.url
        else:
            temp=tempfile.TemporaryDirectory(prefix='codi-account-menu-')
            with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
            url='http://127.0.0.1:'+str(port)+'/'
            log=(CHECKS/'account-menu-local.log').open('w')
            execution=args.release.resolve() if args.release else ROOT
            server=subprocess.Popen([sys.executable,'-B',str(execution/'scripts/serve-connected.py'),'--port',str(port),'--runtime-dir',temp.name],stdout=log,stderr=log)
            if args.release:report['executedReleaseManifestSHA256']=hashlib.sha256((execution/'connected-release.json').read_bytes()).hexdigest()
            def ready():
                if server.poll() is not None:raise AssertionError('Fixture issuer exited; inspect local log')
                try:
                    with urllib.request.urlopen(url+'config.json',timeout=2) as response:return response.status==200
                except OSError:return False
            wait(ready,30)
        report.update(url=url,observations=run(url),status='PASS')
        report['servedAssetsSHA256']={}
        for name in ['app.js','style.css','networking.js','terminal.js','assets/terminal-initramfs.cpio.gz']:
            with urllib.request.urlopen(url+name,timeout=20) as response:report['servedAssetsSHA256'][name]=hashlib.sha256(response.read()).hexdigest()
            assert report['servedAssetsSHA256'][name]==hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),name
    finally:
        if server:
            server.terminate();server.wait(timeout=15)
        if log:log.close()
        if temp:temp.cleanup()
        report['sourceSHA256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['app.js','style.css','networking.js','origin_service/lifecycle.py','scripts/account-menu-check.py']}
        output=CHECKS/('account-menu-public-result.json' if args.url else 'account-menu-result.json')
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
