#!/usr/bin/env python3
"""An already-open Chrome/v86 survives actual policy off/on without page reload.

Private VM only; the real native controller changes services and kernel state.
Fixture TLS pin only. The finalizer restores enabled policy before closing the
owned browser. No live webhost, existing tab or real user account is touched.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
vm=module('reconnect_vm','scripts/prepare-native-network-vm.py');helpers=module('reconnect_helpers','scripts/touch-preview-check.py');call,wait=helpers.call,helpers.wait
candidate=module('reconnect_runtime','scripts/upgrade-native-network-vm.py')
def remote(command):return subprocess.run([*vm.ssh_args(),command],check=True,capture_output=True,text=True,timeout=180).stdout
def configure(enabled):
    return json.loads(remote('/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/native/scripts/manage-services.py configure-guest-network --config /etc/codi-native-fixture/managed.json '+('--network-config /etc/codi-guest-network/fixture/managed.json --network-operator /srv/codi-network-fixture/guest-operator' if enabled else '--disable')))

def browser(installed):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]}}}})['sessionId'];disabled=False;checks=[]
    def js(source,args=[]):return call('/session/'+session+'/execute/sync',{'script':source,'args':args})
    def command(text,end):js('sendTerminal(2,arguments[0]);',[text]);wait(lambda:js('return terminalSessions.get(2)?.screen.text().includes(arguments[0])',[end]),30)
    def ping(label):
        token='RECONNECT_'+str(time.time_ns());command('ping -c 1 -W 1 1.1.1.2 >/dev/null 2>&1; printf "\\n'+token+'=%s\\n" "$?"\r','\n'+token+'=')
        assert js('return terminalSessions.get(2).screen.text().includes(arguments[0])',['\n'+token+'=0\n']),(label,js('return guestNetworkAdapter?.mode'),js('return terminalSessions.get(2).screen.text().slice(-1600)'))
        checks.append(label)
    def kept():
        assert js('return v86Instance===savedVM&&v86Instance.fs9p===savedFS&&guestNetworkAdapter===savedAdapter&&guestState==="ready"')
        command('printf "\\nKEPT=%s:" "$RECONNECT_KEEP"; cat /home/guest/reconnect-keep.txt\r','\nKEPT=retained_shell:retained_file');checks.append('same VM/filesystem/adapter and Linux shell/file retained')
    try:
        call('/session/'+session+'/timeouts',{'script':120000});call('/session/'+session+'/url',{'url':installed['publicOrigin']+'/hidden/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestNetworkAdapter?.mode==="anonymous"'),150)
        js('window.savedVM=v86Instance;window.savedFS=v86Instance.fs9p;window.savedAdapter=guestNetworkAdapter;window.savedSocket=guestNetworkAdapter.socket')
        command('export RECONNECT_KEEP=retained_shell; printf retained_file > /home/guest/reconnect-keep.txt; printf "\\nRECONNECT_READY\\n"\r','\nRECONNECT_READY\n');ping('configured worker path initially works')
        assert configure(False)['status']=='network-configured';disabled=True
        # Give the existing adapter its ordinary reconnect attempt. A fresh tab
        # would hide a cached-capability regression and is deliberately not used.
        wait(lambda:js('return guestNetworkAdapter.socket&&guestNetworkAdapter.socket!==savedSocket&&guestNetworkAdapter.socket.readyState===WebSocket.OPEN'),40)
        time.sleep(2);ping('cached adapter uses explicitly disabled binary relay');kept()
        assert configure(True)['status']=='network-configured';disabled=False
        wait(lambda:js('return guestNetworkAdapter.socket?.readyState===WebSocket.OPEN&&guestNetworkAdapter.mode==="anonymous"'),40);ping('cached adapter returns to configured anonymous worker');kept()
        command('ping -c 1 -W 1 1.1.1.1 >/dev/null 2>&1; printf "\\nPROTECTED_RC=%s\\n" "$?"\r','\nPROTECTED_RC=');assert js('return !terminalSessions.get(2).screen.text().includes("\\nPROTECTED_RC=0\\n")');checks.append('restored policy still blocks protected own address for anonymous guest')
        return {'status':'PASS','checks':checks,'actualNativePolicyOffOn':True,'sameBrowserAndLinuxInstance':True,'registeredPrivilegeNotAssumed':True,'liveWebhostChanged':False,'hostFirewallChanged':False}
    except Exception:
        try:
            value={'networkMode':js('return typeof guestNetworkAdapter==="undefined"?null:guestNetworkAdapter?.mode'),'socketState':js('return typeof guestNetworkAdapter==="undefined"?null:guestNetworkAdapter?.socket?.readyState'),'terminalTail':js('return typeof terminalSessions==="undefined"?null:terminalSessions.get(2)?.screen.text().slice(-2500)')}
            (ROOT/'.build/checks/native-network-vm-reconnect-diagnostics.json').write_text(json.dumps(value,indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        if disabled:configure(True)
        try:js('guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        except Exception:pass
        call('/session/'+session,method='DELETE')
if __name__=='__main__':
    value={'status':'FAIL','scope':__doc__}
    try:
        vm.status();executed=candidate.runtime();assert executed['clientSHA256']==hashlib.sha256((ROOT/'guest_service/client.mjs').read_bytes()).hexdigest();installed=json.loads(remote('cat /srv/codi-network-fixture/installed-result.json'));value.update(browser(installed));value['executedRuntime']=executed
    finally:
        value['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['guest_service/client.mjs','scripts/native-network-vm-reconnect-check.py']};out=ROOT/'.build/checks/native-network-vm-reconnect-result.json'
        if out.exists():out.rename(out.with_name('native-network-vm-reconnect-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
