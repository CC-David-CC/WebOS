#!/usr/bin/env python3
"""Ten-second notice and actual installed native restart with one retained v86.

Private VM only, fixture-specific TLS pin. Actual systemd issuer/steward/guest
stop/start, root-owned notice, authenticated private file service and installed
network workers/kernel. No public service or real user's browser is changed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import time

ROOT=Path(__file__).resolve().parent.parent
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
candidate=module('maintenance_vm','scripts/upgrade-native-network-vm.py');helpers=module('maintenance_browser','scripts/touch-preview-check.py');call,wait=helpers.call,helpers.wait

def run(policy_change=False):
    candidate.vm.status();before=candidate.runtime();release=before['release'];assert before['appSHA256']==hashlib.sha256((ROOT/'app.js').read_bytes()).hexdigest()
    installed=json.loads(candidate.remote('cat /srv/codi-network-fixture/installed-result.json'));python='/srv/codi-network-fixture/venv/bin/python';config='/etc/codi-native-fixture/managed.json'
    def manage(action):return json.loads(candidate.remote(python+' -I -B '+release+'/scripts/manage-services.py '+action+' --config '+config))
    def turn_policy(transport):
        code='''import json,os,pathlib,subprocess
P=pathlib.Path;assert P('/var/lib/codi-fixture-ready').is_file()
c=json.loads(P('/etc/codi-native-fixture/managed.json').read_text());directory=P('/etc/codi-fixture-turn');secret=directory/'turn.secret'
assert c.get('turn') is None or c['turn']['secretFile']==str(secret),'Refuse to replace another relay fixture'
directory.mkdir(mode=0o700,exist_ok=True);assert directory.stat().st_uid==0 and directory.stat().st_mode&0o777==0o700 and not directory.is_symlink()
if not secret.exists():
 fd=os.open(secret,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:f.write(__import__('secrets').token_urlsafe(32))
args=[c['python'],'-I','-B',c['release']+'/scripts/manage-services.py','configure-turn','--config','/etc/codi-native-fixture/managed.json','--turn-secret-file',str(secret),'--turn-url','turns:fixture.invalid:443?transport=tcp','--turn-transport-policy',TRANSPORT]
r=subprocess.run(args,capture_output=True,text=True,check=True);value=json.loads(r.stdout);assert value['status'] in ('turn-configured','turn-already-current');print(json.dumps(value))
'''.replace('TRANSPORT',repr(transport))
        return json.loads(candidate.remote('/usr/bin/python3 -I -B -c '+shlex.quote(code)))
    if policy_change:turn_policy('relay');before=candidate.runtime()
    def notice(phase,seconds=0):return json.loads(candidate.remote(python+' -I -B '+release+'/scripts/desktop-maintenance.py --directory /var/lib/codi-native-fixture/public '+phase+' --in-seconds '+str(seconds)))
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]}}}})['sessionId'];stopped=False;checks=[]
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code):
        value=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]});assert value['ok'],value;return value.get('value')
    def check(name,value):assert value,name;checks.append(name)
    def command(shell,expected):js('sendTerminal(2,arguments[0])',[shell]);wait(lambda:js('return serialScreen.text().includes(arguments[0])',[expected]),30)
    def kept():
        check('same VM, 9p, editor, cursor and unsaved text survive',js('return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&savedEditor.isConnected&&savedEditor.value==="unsaved maintenance draft"&&savedEditor.selectionStart===3&&savedEditor.selectionEnd===7'))
        token='MAINT_'+str(time.time_ns());command('printf "\\n'+token+'=%s:" "$MAINT_KEEP"; cat /home/guest/maint-keep.txt\r','\n'+token+'=shell_alive:file_alive')
    try:
        call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':installed['publicOrigin']+'/hidden/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&desktopLab.lifecycle?.epoch&&!desktopLab.lifecycle.blocked'),150)
        js('window.d=[...surfaces.values()][0];window.qaName="maint_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.qaPass=crypto.randomUUID()+crypto.randomUUID()')
        task('await changeAccount("register",qaName,qaPass);return true;');wait(lambda:js('return guestNetworkAdapter.mode==="registered"'),20)
        js('d.launch("text")');wait(lambda:js('return !!document.querySelector(".guest-editor")'),20)
        js('window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.savedEditor=document.querySelector(".guest-editor");savedEditor.value="unsaved maintenance draft";savedEditor.dispatchEvent(new Event("input",{bubbles:true}));savedEditor.focus();savedEditor.setSelectionRange(3,7)')
        command('export MAINT_KEEP=shell_alive; printf file_alive > /home/guest/maint-keep.txt; printf "\\nMAINT_INITIAL_READY\\n"\r','\nMAINT_INITIAL_READY\n')
        announced=notice('scheduled',10);check('root operator announces ten seconds without claiming a save',not announced['servicesRestarted'] and not announced['workSaved'])
        wait(lambda:js('return !document.querySelector("#desktop-recovery").hidden&&document.querySelector("#desktop-recovery-title").textContent.includes("restarting")'),6)
        js('document.querySelector("#desktop-recovery button").click()')
        task('const context=await serverFileContext();await context.files.write("last-saved.txt",new TextEncoder().encode("explicitly saved before maintenance"));return true;')
        wait(lambda:js('return desktopLab.lifecycle.blocked'),12);check('real deadline locks desktop and voice controls',js('return document.querySelector("#previews").inert&&document.querySelector("#voice-control").inert'))
        notice('active');manage('stop');stopped=True
        stopped_state=manage('status');check('actual installed native services stop',all(int(v['MainPID'])==0 for v in stopped_state['units'].values()))
        check('browser preserves VM while all native services are stopped',js('return desktopLab.lifecycle.blocked&&v86Instance===savedVM&&savedEditor.isConnected'))
        if policy_change:turn_policy('all')
        manage('start');stopped=False;after=candidate.runtime()
        check('all actual native process IDs change',all(before['nativePIDs'][role]!=after['nativePIDs'][role] for role in ['issuer','steward','guest']))
        wait(lambda:js('return currentSession?.public.kind==="anonymous"&&guestNetworkAdapter?.socket?.readyState===WebSocket.OPEN'),45)
        check('active maintenance keeps controls locked even after services return',js('return desktopLab.lifecycle.blocked'))
        notice('cancelled');wait(lambda:js('return !desktopLab.lifecycle.blocked'),12);kept()
        check('registered session is not falsely restored after issuer restart',js('return currentSession.public.kind==="anonymous"&&guestNetworkAdapter.mode==="anonymous"'))
        if policy_change:check('changed managed ICE preference recovers without a page reload',js('return identityConfig.rtc.iceTransportPolicy==="all"&&currentSession.rtc.iceTransportPolicy==="all"'))
        task('await changeAccount("signin",qaName,qaPass);return true;');wait(lambda:js('return guestNetworkAdapter.mode==="registered"'),20);kept()
        check('explicitly saved private file survives actual service restart',task('const context=await serverFileContext();return new TextDecoder().decode((await context.files.read("last-saved.txt")).data)==="explicitly saved before maintenance";'))
        return {'status':'PASS','scope':__doc__,'checks':checks,'managedICEPolicyChanged':policy_change,'fixtureTurnEndpointOnly':'turns:fixture.invalid:443?transport=tcp' if policy_change else None,'turnConnectivityTested':False,'countdownSeconds':10,'executedRuntime':before,'runtimeAfterActualRestart':after,'actualInstalledProcessRestart':True,'sameBrowserAndLinuxInstance':True,'explicitServerSaveRetained':True,'warningAutomaticallySavedWork':False,'browserCloseOrCrashRecoveryProven':False,'liveWebhostChanged':False,'hostFirewallChanged':False,'publicDefaultTLSVerified':False,'physicalAndroidVerified':False}
    except Exception:
        try:(ROOT/'.build/checks/native-network-vm-maintenance-diagnostics.json').write_text(json.dumps(js('return {state:window.desktopLab?.lifecycle,network:guestNetworkAdapter?.mode,text:document.body.innerText.slice(-2200)}'),indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        if stopped:manage('start')
        notice('cancelled')
        try:js('desktopLifecycle?.stop();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--policy-change',action='store_true');args=parser.parse_args()
    value={'status':'FAIL','scope':__doc__}
    try:value.update(run(args.policy_change))
    finally:
        names=['scripts/native-network-vm-maintenance-check.py','scripts/upgrade-native-network-vm.py','app.js','assets/desktop/lifecycle.mjs','assets/desktop/recovery-policy.mjs','network/identity.mjs','scripts/desktop-maintenance.py']
        value['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks/native-network-vm-maintenance-result.json'
        if output.exists():output.rename(output.with_name('native-network-vm-maintenance-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
