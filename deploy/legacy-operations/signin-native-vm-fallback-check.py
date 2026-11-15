#!/usr/bin/env python3
"""Managed disable must provide local Linux, never an anonymous relay fallback.

Private retained VM only. Restores its strict existing binding in finally;
no data restore, root/key regeneration or live webhost operation is performed.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
CONTROL='/etc/codi-native-fixture/managed.json'
EXPECTED='5fad3b77a5b3f982345c7bd959789509634076059c0b94403f2148146744fcb8'

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
vm=module('signin_fallback_vm','scripts/prepare-native-network-vm.py')
helpers=module('signin_fallback_browser','scripts/touch-preview-check.py');call,wait=helpers.call,helpers.wait

def remote(command,check=True):return subprocess.run([*vm.ssh_args(),command],check=check,capture_output=True,text=True,timeout=90)
def codi(action,*args):
    c=json.loads(remote('cat '+CONTROL).stdout)
    return remote(shlex.join([c['python'],'-I','-B',c['release']+'/scripts/manage-services.py',action,'--config',CONTROL,*args]))
def snap():return json.loads(remote('/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/signin-native-vm-migration-check.py --snapshot').stdout)

def browser(installed):
    sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]}}}})['sessionId'];checks=[]
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def check(label,value):assert value,label;checks.append(label)
    def command(shell):
        token='LOCAL_ONLY_'+str(time.time_ns());js('sendTerminal(2,arguments[0]);',[shell+'; local_only_rc=$?; printf "\\n'+token+'=%s\\n" "$local_only_rc"\r'])
        wait(lambda:js('return serialScreen.text().includes(arguments[0])',['\n'+token+'=']),25);return js('return serialScreen.text().includes(arguments[0])',['\n'+token+'=0\n'])
    try:
        call('/session/'+sid+'/url',{'url':installed['publicOrigin']+'/hidden/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready'),150)
        check('local Linux boots while managed Internet is disabled',js('return !identityConfig.guestNetwork&&!guestNetworkAdapter&&currentSession.public.kind==="anonymous"'))
        check('guest loopback works without relay',command('ping -c 1 -W 1 127.0.0.1 >/tmp/local-only-loopback 2>&1'))
        check('external guest ping cannot use a legacy relay',not command('ping -c 1 -W 1 1.1.1.2 >/tmp/local-only-public 2>&1'))
        result=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];fetch("config.json",{cache:"no-store"}).then(r=>r.json()).then(c=>done({noGuestNetwork:!c.guestNetwork,rtc:!!c.rtc}));','args':[]})
        check('fresh public config omits guest Internet but keeps browser RTC',result['noGuestNetwork'] and result['rtc'])
        # Fetch includes the actual HttpOnly host cookie from the index. The
        # endpoint body distinguishes explicit local-only mode from bad origin.
        result=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];fetch("guest-network",{credentials:"same-origin"}).then(async r=>done({status:r.status,text:await r.text()}));','args':[]})
        check('guest transport explicitly returns disabled, even with valid browser cookie',result['status']==403 and result['text']=='Guest networking is disabled')
        return checks
    finally:
        try:js('v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')

if __name__=='__main__':
    result={'status':'FAIL'};restore=None;checks=[]
    try:
        vm.status();before=snap();c=json.loads(remote('cat '+CONTROL).stdout);assert c['manifestSHA256']==EXPECTED and before['guestPolicyVersion']=='codi-guest-egress-policy/2'
        restore=c['guestNetwork'];installed=json.loads(remote('cat /srv/codi-network-fixture/installed-result.json').stdout)
        # Unsupported downgrade is refused before journaling or stopping units.
        args=[c['python'],'-I','-B',c['release']+'/scripts/manage-services.py','upgrade','--config',CONTROL,'--release','/srv/codi-network-fixture/candidate-8810761ee7e47e15','--python',c['python']]
        denied=remote(shlex.join(args),check=False);assert denied.returncode!=0 and 'cannot remove registered-only' in denied.stderr
        assert snap()['pids']==before['pids'];checks.append('code downgrade below strict-policy capability refused without stopping services')
        disabled=json.loads(codi('configure-guest-network','--disable').stdout);assert disabled['status']=='network-configured' and not disabled['enabled']
        middle=snap();assert middle['configVersion']=='codi-managed-instance/4' and middle['pids']['issuer']>0 and middle['pids']['guest']>0
        for role in ['steward','files','filesProxy']:assert middle['pids'][role]==before['pids'][role]
        checks+=browser(installed)
    finally:
        if restore:
            restored=json.loads(codi('configure-guest-network','--network-config',restore['configFile'],'--network-operator',restore['operatorRelease']).stdout);assert restored['status'] in ['network-configured','network-already-current']
            after=snap();assert after['guestPolicyVersion']=='codi-guest-egress-policy/2' and all(after['pids'].values())
            assert before['keysAccountDBCookieSHA256']==after['keysAccountDBCookieSHA256'] and before['fixturePrivateFilesSHA256']==after['fixturePrivateFilesSHA256'] and before['permissionsLogicalSHA256']==after['permissionsLogicalSHA256']
            for role in ['steward','files','filesProxy']:assert after['pids'][role]==before['pids'][role]
            checks.append('strict binding restored with keys accounts cookie permissions files and steward/file PIDs preserved')
            # A failed inner test remains failed, even if restoration succeeds.
            if len(checks)==7:result={'status':'PASS','checks':checks,'before':before,'after':after,'fixtureCertificatePinUsed':True,'liveWebhostChanged':False,'hostFirewallChanged':False}
        result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();p=ROOT/'.build/checks/signin-native-vm-fallback-result.json'
        if p.exists():p.rename(p.with_name('signin-native-vm-fallback-before-'+str(time.time_ns())+'.json'))
        p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
