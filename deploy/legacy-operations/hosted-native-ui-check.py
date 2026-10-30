#!/usr/bin/env python3
"""Actual retained native20/21 desktop menu/Rooms/IndexedDB/workspace workflow.

One owned Chrome/v86 desktop at fixture-pinned HTTPS, not public WAN, real
concurrent tabs, physical phone, P2P hosted delivery, chess or8k acceptance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import secrets
import shlex

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
driver=module('hosted_ui_driver',ROOT/'scripts/touch-preview-check.py');vm=module('hosted_ui_vm',ROOT/'scripts/upgrade-signin-native-vm.py')


def run(release):
    checks=[];sid=None;subject=None;username='vmhosted_'+secrets.token_hex(6);password=secrets.token_urlsafe(32)
    before=vm.runtime();pin=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();assert before['manifestSHA256']==pin
    result={'status':'FAIL','scope':__doc__,'checks':checks,'createdTestAccount':username,'productionChanged':False,'nativeManifestSHA256':pin,'actualBrowsers':1,'actualV86Desktops':1,'fixtureSPKIOnly':True,'publicWANTested':False,'actualConcurrentTabsTested':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        value=driver.call('/session/'+sid+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:e.stack}));','args':args});assert value['ok'],value;return value.get('value')
    def wait(fn):return driver.wait(fn,90)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def ready():wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready&&desktopNetwork.appContext().meshReady&&desktopNetwork.appContext().hostedRooms?.snapshot().ready;'))
    def snap(node=None):return js('return desktopNetwork.appContext().hostedRooms.snapshot(arguments[0]);',[node])
    def idle():wait(lambda:snap()['busy']==0)
    def open_rooms():
        ids=js('return [...surfaces.values()][0].windows.map(w=>w.id);')
        js('document.querySelector(".app-menu-button").click();const b=[...document.querySelectorAll(".menu-row")].find(b=>b.querySelector(".row-text")?.textContent==="Rooms");if(!b)throw Error("Rooms menu missing");b.click();')
        w=wait(lambda:js('return [...surfaces.values()][0].windows.find(w=>w.app==="rooms"&&!arguments[0].includes(w.id))?.id;',[ids]))
        wait(lambda:js('return !!document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-create]`);',[w]));return w
    def click(w,key):
        js('const b=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-${arguments[1]}]`);if(!b||b.disabled)throw Error("Hosted action disabled: "+arguments[1]);b.click();',[w,key])
    def text(w,key,value):js('const el=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-${arguments[1]}]`);el.value=arguments[2];el.dispatchEvent(new Event("input",{bubbles:true}));',[w,key,value])
    def close(w):js('document.querySelector(`[data-window="${arguments[0]}"] .window-controls button[title="Close"]`).click();',[w]);wait(lambda:js('return !document.querySelector(`[data-window="${arguments[0]}"]`);',[w]))
    def workspace(number):
        js('document.querySelector(".panel [aria-label=Workspaces]").click();document.querySelector(`[aria-label="Workspace ${arguments[0]}"]`).click();',[number])
        wait(lambda:js('return [...surfaces.values()][0].current===arguments[0]-1&&!document.querySelector(".status-popup");',[number]))
    try:
        installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'))
        sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':installed['publicOrigin']+'/'});ready()
        check('actual root Linux desktop initializes shared hosted client',js('return desktopNetwork.appContext().hostedMode&&currentSession.public.kind==="anonymous";'))
        js('window.firstHostedVM=v86Instance;window.firstHostedFS=v86Instance.fs9p;')
        task('await changeAccount("register",params[0],params[1]);return true;',[username,password]);ready();subject=js('return currentSession.public.sub;');result['subject']=subject
        check('account promotion preserves the same Linux guest and shared home',js('return v86Instance===firstHostedVM&&v86Instance.fs9p===firstHostedFS&&currentSession.public.kind==="registered";'))
        a=open_rooms();b=open_rooms();check('Applications menu opens two independent complete Rooms views',js('return [...surfaces.values()][0].windows.filter(w=>w.app==="rooms").length===2&&document.querySelectorAll("[data-hosted-rooms]").length===2;'))
        click(a,'create');idle();node=js('return [...surfaces.values()][0].windows.find(w=>w.id===arguments[0]).hostedRoomId;',[a]);assert node;result['ownedRoom']=node
        check('real Rooms pane creates and verifies a durable account-owned chat',snap(node)['selected']['count']==0 and snap(node)['selected']['joined'])
        text(b,'id',node);click(b,'open');idle();text(b,'draft','Workspace one independent draft');text(a,'draft','Native desktop saved chat message');click(a,'send');idle()
        check('two actual desktop windows share accepted messages and preserve separate drafts',snap(node)['selected']['count']==1 and js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-history]`).textContent.includes("Native desktop saved chat message")&&document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`).value==="Workspace one independent draft";',[b]))
        js('window.hostedDraftNode=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`);',[b]);workspace(2);c=open_rooms();text(c,'draft','Workspace two draft');workspace(1)
        check('workspace chooser restores original app DOM draft and independent selection',js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`)===hostedDraftNode&&hostedDraftNode.value==="Workspace one independent draft"&&[...surfaces.values()][0].windows.find(w=>w.id===arguments[1]).workspace===1;',[b,c]))
        js('document.querySelector(`[data-window="${arguments[0]}"] .window-controls button[title="Minimize"]`).click();const d=[...surfaces.values()][0];d.activateWindow(d.windows.find(w=>w.id===arguments[0]));',[b])
        check('minimize and restore preserve the hosted view and draft',js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`)===hostedDraftNode&&hostedDraftNode.value==="Workspace one independent draft";',[b]))
        js('document.querySelector(`[data-window="${arguments[0]}"] .window-controls button[title="Roll up"]`).click();document.querySelector(`[data-window="${arguments[0]}"] .window-controls button[title="Unroll"]`).click();',[b])
        check('roll-up preserves hosted content instead of remounting it',js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`)===hostedDraftNode;',[b]))
        baseline=task('return await desktopNetwork.stats();')
        for _ in range(12):w=open_rooms();close(w)
        after=task('return await desktopNetwork.stats();')
        check('twelve full Rooms reopen cycles release both mesh and hosted observers',baseline['hostedViews']==after['hostedViews'] and baseline['meshViews']==after['meshViews'] and baseline['budget']['metadataBytes']==after['budget']['metadataBytes'])
        workspace(2);check('other workspace draft remains independent after repeated app cycles',js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-draft]`).value==="Workspace two draft";',[c]));workspace(1)
        driver.call('/session/'+sid+'/refresh',{});ready();task('await changeAccount("signin",params[0],params[1]);return true;',[username,password]);ready()
        check('real page reload and fresh sign-in recover this account browser bookmark',js('return currentSession.public.sub===arguments[0]&&desktopNetwork.appContext().hostedRooms.snapshot().rooms.some(r=>r.id===arguments[1]);',[subject,node]))
        d=open_rooms();text(d,'id',node);click(d,'open');idle()
        check('installed client verifies the persisted position and saved history after reload',snap(node)['selected']['count']==1 and js('return document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-history]`).textContent.includes("Native desktop saved chat message");',[d]))
        click(d,'join');idle();text(d,'draft','Fresh session after native reload');click(d,'send');idle();check('reloaded account can continue in a distinct authorized shell-independent stream',snap(node)['selected']['count']==2)
        text(d,'draft','Unsent saved chat draft before sign-out')
        task('await changeAccount("anonymous");return true;');ready()
        check('identity change retires old hosted views and isolates anonymous bookmarks',not snap()['rooms'] and js('return [...document.querySelectorAll("[data-hosted-create]")].every(b=>b.disabled);'))
        check('sign-out retains the unsent saved-chat draft in the read-only identity archive',js('const root=document.querySelector(`[data-window="${arguments[0]}"] .window-content`);return root.textContent.includes("Previous identity")&&root.textContent.includes("Unsent draft")&&root.textContent.includes("Unsent saved chat draft before sign-out")&&!root.querySelector("[data-hosted-send]");',[d]))
        anon=open_rooms();text(anon,'id',node);click(anon,'open');idle();check('anonymous actual desktop can verify public chat without a server-file account',snap(node)['selected']['count']==2 and not snap()['registered'])
        driver.call('/session/'+sid+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
        wait(lambda:js('return document.querySelector(".desktop").classList.contains("compact-desktop");'))
        metrics=js('const root=document.querySelector(`[data-window="${arguments[0]}"] [data-hosted-rooms]`),box=root.getBoundingClientRect();return {viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,section:{left:box.left,right:box.right},controls:[...root.querySelectorAll(".mesh-field,button")].map(n=>{const r=n.getBoundingClientRect();return {label:n.ariaLabel||n.textContent,hidden:n.hidden,rects:n.getClientRects().length,left:r.left,right:r.right,width:r.width,height:r.height};})};',[anon])
        result['phoneLayout']=metrics
        visible=[control for control in metrics['controls'] if control['rects']]
        check('phone-sized hosted fields and visible touch controls remain contained',
              len(visible)>=10 and metrics['scrollWidth']<=metrics['viewport']
              and all(not c['hidden'] and c['width']>=44 and c['height']>=44
                      and c['left']>=metrics['section']['left']-1
                      and c['right']<=metrics['section']['right']+1 for c in visible)
              and all(not c['rects'] for c in metrics['controls'] if c['hidden']))
        result.update(status='PASS',actualPageReload=True,fullRoomsReopenCycles=12,workspaceDOMAndDraftsPreserved=True,acceptedRecordsInOwnedRoom=2,nativeRuntimeBefore=before)
    except Exception as error:
        import traceback;result.update(error=str(error),traceback=traceback.format_exc())
        if sid:
            try:result['diagnostics']={'body':js('return document.body.innerText.slice(-5000);'),'state':js('return {guest:desktopLab.guestState,kind:currentSession.public.kind,hostedError:desktopNetwork.appContext().hostedError};'),'logs':driver.call('/session/'+sid+'/log',{'type':'browser'})}
            except Exception as e:result['diagnosticsError']=str(e)
    finally:
        if sid:
            if not subject:
                try:
                    who=js('return currentSession.public;')
                    if who['name']==username:subject=who['sub'];result['subject']=subject
                except Exception:pass
            driver.call('/session/'+sid,method='DELETE');result['ownedBrowserContextsClosed']=1
        if subject:
            assert re.fullmatch('vmhosted_[a-f0-9]{12}',username)
            code='''import json,sys,os
from pathlib import Path
c=json.loads(Path('/etc/codi-native-fixture/managed.json').read_bytes());source=Path(c['release']);sys.path.insert(0,str(source));sys.path.insert(0,str(source/'codiserver-server-v0.3.0'))
from origin_service.lifecycle import connection,private_database,set_disabled
state=Path(c['stateRoot'])/'issuer/state';owner=state.stat();os.setgroups([]);os.setgid(owner.st_gid);os.setuid(owner.st_uid)
with connection(private_database(state)) as db:assert db.execute('SELECT subject FROM accounts WHERE username=?',(NAME,)).fetchone()==(SUBJECT,)
print(json.dumps(set_disabled(state,NAME,True)))
'''.replace('NAME',repr(username)).replace('SUBJECT',repr(subject))
            result['ownedAccountPolicy']=json.loads(vm.remote('/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)));assert result['ownedAccountPolicy']['disabled']
        assert vm.runtime()==before,'Browser UI tests changed native runtime'
    result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
