#!/usr/bin/env python3
"""Full desktop network adapter, account transitions and mixed-version boot.

Real local HTTP issuer, signed grants, private Unix QEMU workers and Chrome/v86.
This fixture does not install managed services or prove host kernel confinement.
"""
import asyncio
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('guest_browser_fixture',ROOT/'scripts/guest-client-browser-check.py')
fixture_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture_module)
call,wait=fixture_module.call,fixture_module.wait

class DesktopFixture(fixture_module.Fixture):
    def __init__(self,base,mode):super().__init__(base);self.mode=mode;self.sdk_gets=0;self.usage_temp=None;self.ledgers={}
    def worker_usage(self,role):return self.ledgers.get(role)
    async def start(self):
        if self.mode=='controlled':
            from guest_service.usage import Permissions,UsageLedger,initialize_usage,initialize_permissions
            self.usage_temp=tempfile.TemporaryDirectory(prefix='.codi-browser-network-usage-',dir=Path.home());root=Path(self.usage_temp.name)
            for name in ['policy','anonymous','registered']:(root/name).mkdir(mode=0o700)
            self.permissions_path=root/'policy/permissions.sqlite3';initialize_permissions(self.permissions_path,owner_uid=os.getuid())
            for role in ['anonymous','registered']:
                path=root/role/'usage.sqlite3';initialize_usage(path,role);self.ledgers[role]=UsageLedger(path,role,Permissions(self.permissions_path,owner_uid=os.getuid()))
        await super().start();original=self.issuer.config
        def config():
            value=original()
            if self.mode=='offline':value.pop('guestNetwork')
            elif self.mode=='legacy':value['guestNetwork'].pop('authorization')
            elif self.mode=='invalid':value['guestNetwork']['authorization']['clientPath']=self.base+'/unexpected.mjs'
            return value
        self.issuer.config=config
    async def close(self):
        try:await super().close()
        finally:
            if self.usage_temp:self.usage_temp.cleanup()
    async def proxy(self,request):
        if request.path==self.base+'/':
            self.cookie_gets+=1
            response=web.Response(body=(ROOT/'index.html').read_bytes(),content_type='text/html',headers={'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp'})
            response.set_cookie('codi_guest_relay',self.cookie,httponly=True,samesite='Strict',path=self.base+'/',max_age=3600)
            return response
        if request.path==self.base+'/guest-access/client.mjs':
            self.sdk_gets+=1
            if self.mode in ('offline','legacy'):raise web.HTTPNotFound()
        return await super().proxy(request)

def browser(fixture,mobile):
    url=fixture.origin+fixture.base+'/'
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    def js(source,args=[]):return call('/session/'+session+'/execute/sync',{'script':source,'args':args})
    def task(source,args=[]):
        value=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args})
        assert value['ok'],value;return value.get('value')
    def network(mode):wait(lambda:js('return guestNetworkAdapter?.mode===arguments[0]',[mode]),30)
    def command(id,text,expected):
        js('sendTerminal(arguments[0],arguments[1]);',[id,text]);wait(lambda:js('return terminalSessions.get(arguments[0])?.screen.text().includes(arguments[1])',[id,expected]),30)
    def click(selector):
        rect=js('const r=document.querySelector(arguments[0]).getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};',[selector])
        if mobile:
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchStart','touchPoints':[rect]}})
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Input.dispatchTouchEvent','params':{'type':'touchEnd','touchPoints':[]}})
        else:
            for event in ['mousePressed','mouseReleased']:call('/session/'+session+'/goog/cdp/execute',{'cmd':'Input.dispatchMouseEvent','params':{'type':event,**rect,'button':'left','clickCount':1}})
    def account_form(mode):
        click('.panel .account');click('[data-account-action="'+mode+'"]')
        js('for(const [key,value] of Object.entries({username:qaName,password:qaPassword,confirmation:qaPassword})){const f=document.querySelector(".account-form [name="+key+"]");if(f){f.value=value;f.dispatchEvent(new Event("input",{bubbles:true}));}}')
        assert js('const f=document.querySelector(".account-form [name=username]");const keep=f.value;f.value="invalid/name";const rejects=!f.checkValidity();f.value=keep;return rejects&&f.checkValidity();')
        click('.account-form button[type=submit]')
        wait(lambda:js('return currentSession.public.kind==="registered"&&!accountTransition'),30)
    def preserved():
        assert js('return v86Instance===qaVM&&v86Instance.fs9p===qaFS&&document.querySelector(".guest-editor")===qaEditor&&qaEditor.value==="Retained editor draft"&&surfaces.values().next().value.windows.length===qaWindows&&surfaces.values().next().value.windows.some(w=>w.id===qaOtherTerminal&&w.workspace===1)')
        command(2,'printf "\\nDESKTOP_KEEP=%s:" "$DESKTOP_KEEP"; cat /home/guest/desktop-network.txt\r','\nDESKTOP_KEEP=first_shell:shared_file')
        command(js('return qaSecondTerminal'),'printf "\\nSECOND_KEEP=%s\\n" "$DESKTOP_KEEP"\r','\nSECOND_KEEP=second_shell\n')
    try:
        call('/session/'+session+'/timeouts',{'script':60000})
        if mobile:
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
        call('/session/'+session+'/url',{'url':url})
        wait(lambda:js('return ["ready","error"].includes(window.desktopLab?.guestState)'),120)
        if fixture.mode=='invalid':
            assert js('return guestState==="error"&&v86Instance===null&&guestNetworkAdapter===null&&guestMessage.includes("Pinned guest authorization metadata")')
            assert all(not worker.processes for worker in fixture.workers.values())
            return {'mode':fixture.mode,'mobile':mobile,'invalidMetadataFailsClosed':True,'legacyFallbackNotAttempted':True,'failedVMStopped':True}
        assert js('return guestState==="ready"&&currentSession.public.kind==="anonymous"')
        controlled=fixture.mode=='controlled'
        if controlled:network('anonymous')
        else:assert js('return guestNetworkAdapter===null')
        js('window.qaVM=v86Instance;window.qaFS=v86Instance.fs9p;window.qaName="desk-"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.qaPassword=crypto.randomUUID()+crypto.randomUUID();const d=surfaces.values().next().value;window.qaSecondTerminal=d.launch("terminal").id;d.switchWorkspace(1);window.qaOtherTerminal=d.launch("terminal").id;d.switchWorkspace(0);d.launch("text");window.qaEditor=document.querySelector(".guest-editor");qaEditor.value="Retained editor draft";qaEditor.dispatchEvent(new Event("input",{bubbles:true}));window.qaWindows=d.windows.length;')
        command(2,'export DESKTOP_KEEP=first_shell; printf shared_file > /home/guest/desktop-network.txt; printf "\\nINITIAL_READY\\n"\r','\nINITIAL_READY\n')
        command(js('return qaSecondTerminal'),'export DESKTOP_KEEP=second_shell; printf "\\nSECOND_READY\\n"\r','\nSECOND_READY\n')
        if controlled:js('window.qaSocket=guestNetworkAdapter.socket')
        account_form('register')
        if controlled:
            network('registered');assert js('return guestNetworkAdapter.socket===qaSocket&&currentSession.trust.level==="test-server"')
        preserved()
        click('.panel .account');click('.status-popup [aria-label="Sign out"]')
        wait(lambda:js('return currentSession.public.kind==="anonymous"&&!accountTransition'))
        if controlled:network('anonymous')
        preserved();account_form('signin')
        if controlled:
            network('registered');assert js('return guestNetworkAdapter.socket===qaSocket')
            call('/session/'+session+'/cookie/codi_guest_relay',method='DELETE')
            js('guestNetworkAdapter.socket.close()')
            wait(lambda:js('return guestNetworkAdapter.socket&&guestNetworkAdapter.socket!==qaSocket&&guestNetworkAdapter.socket.readyState===WebSocket.OPEN'),30)
            network('registered');preserved()
            # Exercise the current desktop against a real durable quota denial.
            # The policy and ledger here belong only to this local fixture.
            from dataclasses import replace
            from guest_service.usage import set_permission,Allowance
            subject=js('return currentSession.public.sub')
            with sqlite3.connect(fixture.ledgers['registered'].path) as db:used=db.execute('SELECT bytes FROM usage WHERE subject=?',(subject,)).fetchone()[0]
            set_permission(fixture.permissions_path,subject,enabled=True,allowance=replace(Allowance(),window_bytes=used+1),owner_uid=os.getuid())
            js('window.quotaSocket=guestNetworkAdapter.socket;guestNetworkAdapter.reset();guestNetworkAdapter.nextAuth=0;guestNetworkAdapter.syncSession();')
            wait(lambda:js('return guestNetworkAdapter.mode==="anonymous"&&!guestNetworkAdapter.authRequested&&guestNetworkAdapter.nextAuth>Date.now()'),30)
            assert js('return currentSession.public.kind==="registered"&&currentSession.trust.level==="test-server"&&guestNetworkAdapter.socket===quotaSocket')
            preserved()
            set_permission(fixture.permissions_path,subject,enabled=True,owner_uid=os.getuid())
            js('guestNetworkAdapter.nextAuth=0;guestNetworkAdapter.syncSession()');network('registered');preserved()
        assert js('return document.querySelector("#voice-control")!==null&&document.documentElement.dataset.keyboardMode==="voice"')
        errors=[entry for entry in call('/session/'+session+'/log',{'type':'browser'}) if entry['level']=='SEVERE'];assert not errors,errors
        return {'mode':fixture.mode,'mobile':mobile,'actualDesktopLinuxReady':True,'actualAccountMenu':True,'sameVMAndFilesystem':True,'independentShellsPreserved':True,'workspaceAndEditorPreserved':True,'sameNetworkSocketAcrossAccounts':controlled,'registeredCookieReconnect':controlled,'durableUsageEnabled':controlled,'quotaDenialKeepsIdentityAndVM':controlled,'quotaRestorationResumesRegisteredWire':controlled,'legacySDKNotRequested':not controlled,'browserErrors':errors}
    finally:
        try:task('guestNetworkAdapter?.destroy();await v86Instance?.destroy();return true;')
        except Exception:pass
        call('/session/'+session,method='DELETE')

async def main():
    witnesses=[]
    for base,mode,mobile in [('', 'controlled',False),('/hidden','controlled',True),('','legacy',False),('/hidden','offline',True),('/hidden','invalid',False)]:
        fixture=DesktopFixture(base,mode)
        try:
            await fixture.start();value=await asyncio.to_thread(browser,fixture,mobile);value['basePath']=base;value['sdkRequests']=fixture.sdk_gets
            assert fixture.sdk_gets==(1 if mode in ('controlled','invalid') else 0)
            witnesses.append(value);print(json.dumps({'phase':'full desktop passed','mode':mode,'basePath':base}),flush=True)
        finally:await fixture.close()
    return witnesses

if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(status='PASS',witnesses=asyncio.run(main()))
    finally:
        names=['app.js','desktop-apps.js','networking.js','terminal.js','guest_service/client.mjs','guest_service/coordinator.py','guest_service/worker.py','guest_service/usage.py','guest_service/egress.py','guest_service/frames.py','origin_service/guest_authority.py','scripts/guest-client-browser-check.py','scripts/guest-desktop-browser-check.py']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
        output=ROOT/'.build/checks/guest-desktop-browser-result.json'
        if output.exists():output.rename(output.with_name('guest-desktop-browser-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
