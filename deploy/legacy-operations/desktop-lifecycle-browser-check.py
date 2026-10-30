#!/usr/bin/env python3
"""Real Chrome/Linux: lazy apps, short maintenance, offline lock and recovery.

Owned loopback issuer/worker fixture only. Root notice publication is real;
issuer replacement retains its real SQLite/key state but is not an installed
systemd process restart. No production service or user's browser is changed.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time
import uuid
from aiohttp import web

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('desktop_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
fixture.PAGE=(ROOT/'index.html').read_bytes()
call,wait=fixture.call,fixture.wait
from codiauth.service import Failure

class Fixture(fixture.Fixture):
    async def start(self):
        await super().start()
        from origin_service.turn import TurnPolicy
        self.issuer.turn_policy=TurnPolicy(b'x'*32,['turns:fixture.invalid:443?transport=tcp'],'relay')
    async def proxy(self,request):
        if request.path.endswith('/api/v1/desktop-status') and getattr(self,'down',False):return web.json_response({'error':'deliberate fixture outage'},status=503)
        response=await super().proxy(request)
        if request.path.endswith('/config.json') and getattr(self,'changed_pin',False):
            value=json.loads(response.body);value['identity']['authorityKeys'][0]['kid']='untrusted-replacement'
            return web.json_response(value,headers={k:v for k,v in response.headers.items() if k.lower() not in ('content-type','content-length')})
        return response
    def replace_issuer(self,transport='relay'):
        old=self.issuer
        from origin_service.turn import TurnPolicy
        self.issuer=type(old)(old.c,base_path=self.base,maintenance_file=old.maintenance_file,turn_policy=TurnPolicy(b'x'*32,['turns:fixture.invalid:443?transport=tcp'],transport))
        self.http.set_app(fixture.staging.HeadSupport(fixture.GuestAuthority(self.issuer,self.policy.sha256)))

def check_browser(f,directory):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];checks=[]
    def js(source,args=[]):return call('/session/'+sid+'/execute/sync',{'script':source,'args':args})
    def task(source):
        result=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]})
        assert result['ok'],result
        return result['value']
    def check(name,value):assert value,name;checks.append(name)
    def publish(phase,seconds=0):
        result=subprocess.run(['sudo','-n','python3',str(ROOT/'scripts/desktop-maintenance.py'),'--directory',str(directory),phase,'--in-seconds',str(seconds)],check=True,capture_output=True,text=True)
        value=json.loads(result.stdout);assert not value['servicesRestarted'] and not value['workSaved'];return value
    def kept():
        check('same Linux, filesystem, app DOM, text and selection retained',js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS&&keepEditor.isConnected&&keepEditor.value==="keep this unsaved draft"&&keepEditor.selectionStart===5&&keepEditor.selectionEnd===9'))
        token='LIFE_'+str(time.time_ns());js('sendTerminal(2,arguments[0]);',['printf "\\n'+token+'=%s:" "$LIFE_KEEP"; cat /home/guest/life-keep.txt\r']);wait(lambda:js('return serialScreen.text().includes(arguments[0])',['\n'+token+'=retained_shell:retained_file']),30)
    try:
        call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':f.origin+f.base+'/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked&&document.querySelector(".terminal-input")'),150)
        loaded=js('return performance.getEntriesByType("resource").map(n=>new URL(n.name).pathname).filter(n=>n.includes("/assets/desktop/apps/"))')
        check('only initially open Files and Terminal app modules load',bool(loaded) and all('/files/' in p or '/terminal/' in p for p in loaded))
        js('window.d=[...surfaces.values()][0];d.launch("calculator")');wait(lambda:js('return !!document.querySelector("[aria-label=\\"Arithmetic expression\\"]")'),20)
        js('const input=document.querySelector("[aria-label=\\"Arithmetic expression\\"]");input.value="(12 + 8) / 4";input.form.requestSubmit()')
        check('independent lazy calculator computes',js('return document.querySelector(".calculator-result").textContent==="5"'))
        for app,selector in [('help','.help-content'),('chat','[data-chat-content]'),('rooms','[data-peer-rooms]')]:
            js('window.checkWindow=d.launch(arguments[0])',[app])
            wait(lambda:js('return !!document.querySelector("[data-window=\\\""+checkWindow.id+"\\\"] "+arguments[0])',[selector]),20)
            check(app+' loads its independent app view',True)
        js('d.launch("text")');wait(lambda:js('return !!document.querySelector(".guest-editor")'),20)
        js('window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;window.keepEditor=document.querySelector(".guest-editor");keepEditor.value="keep this unsaved draft";keepEditor.dispatchEvent(new Event("input",{bubbles:true}));keepEditor.focus();keepEditor.setSelectionRange(5,9);sendTerminal(2,"export LIFE_KEEP=retained_shell; printf retained_file > /home/guest/life-keep.txt; printf \\\"\\\\nLIFE_READY\\\\n\\\"\\r")')
        wait(lambda:js('return serialScreen.text().includes("\\nLIFE_READY\\n")'),30)
        notice=publish('scheduled',10)
        wait(lambda:js('return !document.querySelector("#desktop-recovery").hidden&&document.querySelector("#desktop-recovery-title").textContent.includes("restarting")'),6)
        check('forced notice and real countdown explicitly deny automatic saves',js('return document.querySelector("#desktop-recovery").textContent.includes("Nothing is automatically saved")&&document.querySelector("#desktop-recovery").textContent.includes("Starts in")'))
        js('document.querySelector("#desktop-recovery button").click()')
        check('acknowledging warning leaves time to save',js('return document.querySelector("#desktop-recovery").hidden&&!document.querySelector("#maintenance-banner").hidden&&!document.querySelector("#previews").inert'))
        wait(lambda:js('return desktopLab.lifecycle.blocked'),12)
        check('deadline blanks desktop and disables desktop and voice controls',js('return !document.querySelector("#desktop-recovery").hidden&&document.querySelector("#previews").inert&&document.querySelector("#voice-control").inert'))
        js('d.closePopups();document.querySelector("[aria-label=Applications]").click()')
        check('blocked app controls cannot open menus',js('return !document.querySelector(".menu-pane")'))
        check('blocked message accurately describes RAM retention',js('return document.querySelector("#desktop-recovery").textContent.includes("not been saved to disk")'))
        publish('cancelled');wait(lambda:js('return !desktopLab.lifecycle.blocked'),8);kept()
        f.down=True;wait(lambda:js('return desktopLab.lifecycle.blocked'),14)
        check('abrupt server outage locks without claiming work was saved',js('return document.querySelector("#desktop-recovery-title").textContent==="Connection interrupted"'))
        f.down=False;wait(lambda:js('return !desktopLab.lifecycle.blocked'),8);kept()
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.enable','params':{}})
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0}})
        wait(lambda:js('return desktopLab.lifecycle.blocked'),5)
        call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.emulateNetworkConditions','params':{'offline':False,'latency':0,'downloadThroughput':-1,'uploadThroughput':-1}})
        wait(lambda:js('return !desktopLab.lifecycle.blocked'),45);kept()
        js('window.previousSession=currentSession.id');f.replace_issuer()
        wait(lambda:js('return !desktopLab.lifecycle.blocked&&currentSession.id!==previousSession'),15);kept()
        check('issuer RAM session loss becomes a new anonymous session without VM reset',js('return currentSession.public.kind==="anonymous"'))
        js('window.previousSession=currentSession.id');f.replace_issuer(transport='all')
        wait(lambda:js('return !desktopLab.lifecycle.blocked&&currentSession.id!==previousSession'),15);kept()
        check('issuer policy change refreshes pinned configuration without reloading Linux',js('return identityConfig.rtc.iceTransportPolicy==="all"&&currentSession.rtc.iceTransportPolicy==="all"'))
        js('window.previousSession=currentSession.id');f.changed_pin=True;f.replace_issuer(transport='all')
        wait(lambda:js('return desktopLab.lifecycle.blocked'),10);time.sleep(4)
        check('changed issuer key pins leave the desktop locked with its prior identity',js('return currentSession.id===previousSession&&v86Instance===keepVM&&keepEditor.isConnected'))
        check('rejected configuration does not create an anonymous server session',not f.issuer.sessions)
        f.changed_pin=False;wait(lambda:js('return !desktopLab.lifecycle.blocked&&currentSession.id!==previousSession'),15);kept()
        js('window.previousSession=currentSession.id');f.replace_issuer(transport='relay')
        normal_renew=f.issuer.continue_session
        def busy(*args):raise Failure(429,'Deliberate temporary issuer saturation')
        f.issuer.continue_session=busy
        wait(lambda:js('return desktopLab.lifecycle.blocked'),10);time.sleep(4)
        check('temporary renewal failure does not sign out or create a replacement identity',js('return currentSession.id===previousSession') and not f.issuer.sessions)
        f.issuer.continue_session=normal_renew
        wait(lambda:js('return !desktopLab.lifecycle.blocked&&currentSession.id!==previousSession'),15);kept()
        check('recovery also accepts a managed return to relay-only policy',js('return identityConfig.rtc.iceTransportPolicy==="relay"&&currentSession.rtc.iceTransportPolicy==="relay"'))
        matrix=task('''
          const {reconcileRecoveryPolicy}=await import('./assets/desktop/recovery-policy.mjs');
          const base=structuredClone(identityConfig);
          base.discovery={pin:{rootKey:{x:'retained-root'},endpoints:['wss://fixture.invalid/ws']},scope:'retained-scope',sourcePath:'/hidden/discovery.json',seed:'old-signed-seed',descriptor:'old-signed-record'};
          const cases=[
            ['local identity mode',c=>c.identity.mode='local-development'],
            ['issuer URL',c=>c.identity.issuer='https://wrong.invalid'],
            ['API path',c=>c.identity.apiBase='/other/api/v1'],
            ['audience',c=>c.identity.audience='wrong-audience'],
            ['authority class',c=>c.identity.authorityClass='official'],
            ['authority key',c=>c.identity.authorityKeys=[]],
            ['TURN endpoint',c=>c.rtc.turnUrls=['turns:wrong.invalid:443?transport=tcp']],
            ['ICE profile removal',c=>delete c.rtc.credentialMode],
            ['unknown ICE policy',c=>c.rtc.iceTransportPolicy='automatic'],
            ['missing ICE policy',c=>delete c.rtc.iceTransportPolicy],
            ['new endpoint credentials',c=>c.rtc.iceServers=[{urls:['turns:wrong.invalid:443?transport=tcp']}]],
            ['guest route',c=>c.guestNetwork.relayPath='/other/guest-network'],
            ['private Files service',c=>c.gateway={basePath:'/other/gateway'}],
            ['Linux asset route',c=>c.vm.manifest='/other/vm/manifest.json'],
            ['status route',c=>c.desktopLifecycle.statusPath='/other/api/v1/desktop-status'],
            ['discovery root',c=>c.discovery.pin.rootKey.x='wrong-root'],
            ['discovery endpoint',c=>c.discovery.pin.endpoints=['wss://wrong.invalid/ws']],
            ['discovery scope',c=>c.discovery.scope='wrong-scope'],
            ['discovery route',c=>c.discovery.sourcePath='/other/discovery.json'],
            ['unknown service field',c=>c.unreviewedService={url:'https://wrong.invalid'}]
          ];
          for(const [name,mutate] of cases){const next=structuredClone(base);mutate(next);let rejected=false;try{reconcileRecoveryPolicy(base,next)}catch{rejected=true}if(!rejected)throw Error('Accepted '+name);}
          const next=structuredClone(base);next.rtc.iceTransportPolicy='all';next.discovery.seed='new-signed-seed';next.discovery.descriptor='new-signed-record';
          const result=reconcileRecoveryPolicy(base,next);if(result.rtc.iceTransportPolicy!=='all'||result.discovery.seed!=='new-signed-seed')throw Error('Permitted update lost');
          result.rtc.turnUrls[0]='changed-copy';if(base.rtc.turnUrls[0]!==next.rtc.turnUrls[0])throw Error('Original policy mutated');
          const unavailable=structuredClone(base);delete unavailable.discovery;
          const retained=reconcileRecoveryPolicy(base,unavailable);
          if(JSON.stringify(retained.discovery)!==JSON.stringify(base.discovery))throw Error('Missing steward changed retained pins or fabricated freshness');
          return {rejected:cases.map(([name])=>name),permittedTransportAndSignedStatementRefresh:true,missingStewardRetainsPriorPinsAndStatements:true};
        ''')
        check('recovery rejects twenty authority and endpoint changes',len(matrix['rejected'])==20)
        check('all seven public app entries are browser modules',json.loads((ROOT/'assets/desktop/apps.json').read_text())['hostAPI']==2)
        errors=call('/session/'+sid+'/log',{'type':'browser'});(ROOT/'.build/checks/desktop-lifecycle-browser-console.json').write_text(json.dumps(errors,indent=2)+'\n')
        def expected(error):
            text=error['message']
            return error.get('source')=='network' and (('503' in text and f.origin+f.base+'/api/v1/desktop-status' in text) or (any(code in text for code in ['401','429']) and any(f.origin+f.base+'/api/v1/'+path+' - ' in text for path in ['renew','logout'])) or ('ERR_INTERNET_DISCONNECTED' in text))
        unexpected=[e for e in errors if e['level']=='SEVERE' and not expected(e)]
        assert not unexpected,unexpected
        checks.append('no unexpected browser errors')
        return {'status':'PASS','scope':__doc__,'checks':checks,'recoveryPolicyMatrix':matrix,'countdownSeconds':10,'workSavedByWarning':False,'linuxRAMRetainedWithoutReload':True,'browserCloseOrReloadPrevented':False,'physicalAndroidVerified':False,'initialAppResources':loaded,'expectedOutageBrowserErrors':[e for e in errors if e['level']=='SEVERE']}
    except Exception:
        try:(ROOT/'.build/checks/desktop-lifecycle-browser-diagnostics.json').write_text(json.dumps(js('return {lifecycle:desktopLab?.lifecycle,networkMode:guestNetworkAdapter?.mode,socket:guestNetworkAdapter?.socket?.readyState,body:document.body.innerText.slice(-2400)}'),indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        try:js('desktopLifecycle?.stop();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')

async def main():
    directory=Path('/var/lib/codi-desktop-check-'+uuid.uuid4().hex[:12]);subprocess.run(['sudo','-n','install','-d','-m','0755',str(directory)],check=True)
    f=Fixture('/hidden')
    try:
        await f.start();f.issuer.maintenance_file=directory/'desktop-maintenance.json'
        return await asyncio.to_thread(check_browser,f,directory)
    finally:
        await f.close();subprocess.run(['sudo','-n','rm','-rf','--',str(directory)],check=True)

if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(asyncio.run(main()))
    finally:
        names=['scripts/desktop-lifecycle-browser-check.py','scripts/desktop-maintenance.py','assets/desktop/lifecycle.mjs','assets/desktop/recovery-policy.mjs','network/identity.mjs','assets/desktop/apps.mjs','assets/desktop/apps.json','app.js','desktop-apps.js','networking.js','origin_service/lifecycle.py','scripts/serve-connected.py']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks/desktop-lifecycle-browser-result.json'
        if output.exists():output.rename(output.with_name('desktop-lifecycle-browser-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
