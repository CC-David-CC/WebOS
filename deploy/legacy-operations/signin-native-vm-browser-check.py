#!/usr/bin/env python3
"""Real Chrome/v86 through installed registered-only native15, sealed workers and kernel.

Uses a fixture-specific certificate pin, not a public TLS/WAN proof. All ping,
DNS and HTTP destinations are controlled addresses on the disposable VM. No
host firewall, live webhost, user tab or real user account is changed.
"""
import hashlib
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parent.parent
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
vm=module('installed_browser_vm','scripts/prepare-native-network-vm.py');helpers=module('installed_browser_helpers','scripts/touch-preview-check.py');call,wait=helpers.call,helpers.wait
candidate=module('installed_browser_runtime','scripts/upgrade-signin-native-vm.py')
def remote(command):return subprocess.run([*vm.ssh_args(),command],check=True,capture_output=True,text=True,timeout=90).stdout

def browser(installed,mobile=False,check_ui=False,base='/hidden',ledger=None):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1366,900','--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    checks=[];probes=[]
    def check(name,value):assert value,name;checks.append(name)
    def js(source,args=[]):return call('/session/'+session+'/execute/sync',{'script':source,'args':args})
    def task(source,args=[]):
        value=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
    def mode(kind):wait(lambda:js('return guestNetworkAdapter?.mode===arguments[0]',[kind]),30)
    def network_text():return js('const p=document.createElement("div");[...surfaces.values()][0].appendNetworkInfo(p);return p.textContent;')
    def command(id,text,expected):
        wait(lambda:js('return !window.desktopLab?.lifecycle?.blocked'),45)
        js('sendTerminal(arguments[0],arguments[1]);',[id,text]);wait(lambda:js('return terminalSessions.get(arguments[0])?.screen.text().includes(arguments[1])',[id,expected]),30)
    def probe(name,shell,allowed):
        token='VMNET_'+str(len(probes))+'_'+str(time.time_ns())
        command(2,"printf '\\n"+token+"_START\\n'; "+shell+" >/tmp/vm-net-output 2>&1; vm_rc=$?; printf '\\n"+token+"_RC=%s\\n' \"$vm_rc\"; cat /tmp/vm-net-output; printf '\\n"+token+"_DONE\\n'\r",'\n'+token+'_DONE\n')
        text=js('return terminalSessions.get(2).screen.text()');match=re.search(r'(?:^|\n)'+token+r'_RC=([0-9]+)(?:\n|$)',text);assert match,(name,text[-2000:]);rc=int(match[1]);assert rc in (0,1,124,137,143),(name,'Unexpected guest command failure',rc,text[-2000:]);check(name,(rc==0)==allowed);probes.append({'name':name,'exitCode':rc,'allowed':allowed})
    def click(selector,label=None):
        if label is None:script='const n=document.querySelector(arguments[0]);if(!n)throw Error("Missing "+arguments[0]);n.click();'
        else:script='const n=[...(document.querySelector(arguments[0])?.querySelectorAll("button")||[])].find(n=>n.textContent===arguments[1]);if(!n)throw Error("Missing button "+arguments[1]);n.click();'
        js(script,[selector,label])
    def fill(selector,value):js('const f=document.querySelector(arguments[0]);if(!f)throw Error("Missing "+arguments[0]);f.value=arguments[1];f.dispatchEvent(new Event("input",{bubbles:true}));',[selector,value])
    def account(kind):
        click('.panel .account');click('[data-account-action="'+kind+'"]')
        js('for(const [key,value] of Object.entries({username:qaName,password:qaPass,confirmation:qaPass})){const f=document.querySelector(".account-form [name="+key+"]");if(f){f.value=value;f.dispatchEvent(new Event("input",{bubbles:true}));}}')
        click('.account-form button[type=submit]');wait(lambda:js('return currentSession.public.kind==="registered"&&!accountTransition'),30);mode('registered')
    def preserved():
        check('same Linux VM, 9p, editor and other workspace retained',js('return v86Instance===qaVM&&v86Instance.fs9p===qaFS&&qaEditor.isConnected&&qaEditor.value==="Retained VM integration draft"&&qaDesktop.windows.some(w=>w.id===qaOtherTerminal&&w.workspace===1)'))
        command(2,'printf "\\nVM_FIRST=%s:" "$VM_SESSION_KEEP"; cat /home/guest/vm-network-keep.txt\r','\nVM_FIRST=first_shell:retained_file')
        command(js('return qaSecondTerminal'),'printf "\\nVM_SECOND=%s\\n" "$VM_SESSION_KEEP"\r','\nVM_SECOND=second_shell\n')
    try:
        call('/session/'+session+'/timeouts',{'script':120000})
        if mobile:
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setDeviceMetricsOverride','params':{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True}})
            call('/session/'+session+'/goog/cdp/execute',{'cmd':'Emulation.setTouchEmulationEnabled','params':{'enabled':True,'maxTouchPoints':5}})
        call('/session/'+session+'/url',{'url':installed['publicOrigin']+base+'/'})
        def ready():
            if js('return window.desktopLab?.guestState==="error"'):raise AssertionError(js('return guestMessage'))
            return js('return window.desktopLab?.guestState==="ready"&&guestFiles.ready')
        wait(ready,150);mode('anonymous');check('secure fixture origin and configured network adapter',js('return isSecureContext&&identityConfig.guestNetwork.durableAccountLimits&&currentSession.public.kind==="anonymous"'))
        if check_ui:
            check('anonymous Network menu explains all Linux Internet requires sign-in', 'Sign in using Anon to enable Linux Internet: ping, DNS and web access.' in network_text())
            check('Network distinguishes browser chat and chess from guest Internet', 'browser chat/chess remain available without signing in' in network_text())
            check('guest README explains sign-in before suggesting ping',task('return new TextDecoder().decode(await guestFiles.read("/Documents/README.txt")).includes("Sign in using Anon before using Linux Internet");'))
        js('window.qaVM=v86Instance;window.qaFS=v86Instance.fs9p;window.qaDesktop=[...surfaces.values()][0];window.qaName="vmnet_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.qaPass=crypto.randomUUID()+crypto.randomUUID();window.qaSocket=guestNetworkAdapter.socket;window.qaSecondTerminal=qaDesktop.launch("terminal").id;qaDesktop.switchWorkspace(1);window.qaOtherTerminal=qaDesktop.launch("terminal").id;qaDesktop.switchWorkspace(0);window.qaTextWindow=qaDesktop.launch("text");')
        if ledger is not None:ledger['names'].append(js('return qaName;'))
        wait(lambda:js('return !!document.querySelector("[data-window=\\\""+qaTextWindow.id+"\\\"] textarea")'),20)
        js('window.qaEditor=document.querySelector("[data-window=\\\""+qaTextWindow.id+"\\\"] textarea");qaEditor.value="Retained VM integration draft";qaEditor.dispatchEvent(new Event("input",{bubbles:true}));')
        command(2,'export VM_SESSION_KEEP=first_shell; printf retained_file > /home/guest/vm-network-keep.txt; printf "\\nVM_INITIAL_READY\\n"\r','\nVM_INITIAL_READY\n')
        command(js('return qaSecondTerminal'),'export VM_SESSION_KEEP=second_shell; printf "\\nVM_SECOND_READY\\n"\r','\nVM_SECOND_READY\n')
        for name,shell,allowed in [('anonymous own public ping denied','ping -c 1 -W 1 1.1.1.1',False),('anonymous own public HTTP denied','timeout 4 wget -O /tmp/vm-http http://1.1.1.1/probe',False),('anonymous other public ping denied','ping -c 1 -W 1 1.1.1.2',False),('anonymous other public HTTP denied','timeout 4 wget -O /tmp/vm-http http://1.1.1.2/probe',False),('anonymous controlled DNS denied','timeout 4 nslookup codi-fixture.test 10.86.0.3',False),('anonymous private LAN denied','timeout 4 wget -O /tmp/vm-http http://10.222.0.1/probe',False),('anonymous metadata denied','timeout 4 wget -O /tmp/vm-http http://169.254.169.254/probe',False)]:probe(name,shell,allowed)
        probe('anonymous guest loopback remains usable','ping -c 1 -W 1 127.0.0.1',True)
        click('[data-window="4"]','My server files');check('anonymous file view offers sign-in without server folder',js('return document.querySelector("[data-window=\\\"4\\\"]").textContent.includes("Sign in using Anon")&&!document.querySelector("[data-server-file-list]")'))
        account('register')
        if ledger is not None:ledger['subjects'][js('return qaName;')]=js('return signedInSubject();')
        check('account promotion opens authorized wire or retains an existing public socket',js('return guestNetworkAdapter.socket?.readyState===WebSocket.OPEN&&(qaSocket===null||guestNetworkAdapter.socket===qaSocket)'));preserved()
        if check_ui:check('signed-in Network menu reports account Internet enabled', 'Linux Internet is enabled for signed-in accounts' in network_text())
        for name,shell,allowed in [('registered own public ping works','ping -c 1 -W 1 1.1.1.1',True),('registered own public HTTP works','timeout 4 wget -O /tmp/vm-http http://1.1.1.1/probe',True),('registered other public HTTP works','timeout 4 wget -O /tmp/vm-http http://1.1.1.2/probe',True),('registered controlled DNS works','timeout 4 nslookup codi-fixture.test 10.86.0.3',True),('registered private 10 network denied','timeout 4 wget -O /tmp/vm-http http://10.222.0.1/probe',False),('registered private 172 network denied','timeout 4 wget -O /tmp/vm-http http://172.22.0.1/probe',False),('registered private 192 network denied','timeout 4 wget -O /tmp/vm-http http://192.168.222.1/probe',False),('registered metadata denied','timeout 4 wget -O /tmp/vm-http http://169.254.169.254/probe',False)]:probe(name,shell,allowed)
        wait(lambda:js('return document.querySelector("[data-server-file-list]")?.getAttribute("aria-busy")==="false"'),30)
        fill('[aria-label="New server item name"]','network-saved.txt');click('[data-window="4"]','New text file');wait(lambda:js('return !!document.querySelector("[data-server-editor] textarea:not(:disabled)")'),30)
        fill('[aria-label="Server text document"]','Saved alongside the isolated network');click('[data-server-editor]','Save');wait(lambda:js('return document.querySelector("[data-server-editor] .app-status")?.textContent==="Saved on the server."'),30)
        check('real private Files GUI write and authenticated read work with new networking',task('return new TextDecoder().decode((await (await serverFileContext()).files.read("network-saved.txt")).data)==="Saved alongside the isolated network";'))
        call('/session/'+session+'/cookie/codi_guest_relay',method='DELETE');js('window.qaOldSocket=guestNetworkAdapter.socket;guestNetworkAdapter.socket.close();')
        wait(lambda:js('return guestNetworkAdapter.socket&&guestNetworkAdapter.socket!==qaOldSocket&&guestNetworkAdapter.socket.readyState===WebSocket.OPEN'),30);mode('registered');preserved();probe('registered own access survives cookie renewal without VM restart','ping -c 1 -W 1 1.1.1.1',True)
        task('await changeAccount("anonymous");return true;');mode('anonymous');preserved();probe('logout withdraws all guest Internet on same Linux instance','ping -c 1 -W 1 1.1.1.1',False)
        if check_ui:check('logout restores sign-in-required Network message', 'Sign in using Anon to enable Linux Internet' in network_text())
        probe('logout withdraws other public Internet too','ping -c 1 -W 1 1.1.1.2',False)
        account('signin');preserved();check('private saved file survives logout and sign-in',task('return new TextDecoder().decode((await (await serverFileContext()).files.read("network-saved.txt")).data)==="Saved alongside the isolated network";'))
        check('voice overlay and keyboard mode preserved',js('return !!document.querySelector("#voice-control")&&document.documentElement.dataset.keyboardMode==="voice"'))
        errors=[item for item in call('/session/'+session+'/log',{'type':'browser'}) if item['level']=='SEVERE'];check('no severe browser errors',not errors)
        if ledger is not None:
            ledger['subjects'][js('return qaName;')]=js('return signedInSubject();')
            task('const c=await serverFileContext(),f=await c.files.read("network-saved.txt");await c.files.remove("network-saved.txt",f.sha256);return true;')
            ledger['ownedFilesRemoved']=True
        return {'status':'PASS','checks':checks,'probes':probes,'mobileViewport':mobile,'accountSubject':js('return signedInSubject()'),'realPrivateFilesGUI':True,'actualBrowserWorkerKernelChain':True,'fixtureCertificatePinUsed':True,'publicDefaultTLSVerified':False,'independentWANVerified':False,'browserErrors':errors}
    except Exception:
        try:
            diagnostics={'guestState':js('return window.desktopLab?.guestState'),'guestMessage':js('return typeof guestMessage==="undefined"?null:guestMessage'),'networkMode':js('return typeof guestNetworkAdapter==="undefined"?null:guestNetworkAdapter?.mode'),'terminalTail':js('return typeof terminalSessions==="undefined"?null:terminalSessions.get(2)?.screen.text().slice(-4000)')}
            (ROOT/'.build/checks/signin-native-vm-browser-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        try:task('guestNetworkAdapter?.destroy();await v86Instance?.destroy();return true;')
        except Exception:pass
        call('/session/'+session,method='DELETE')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mobile',action='store_true');parser.add_argument('--release-dir',type=Path,default=ROOT/'.build/releases/connected-signin-r6');parser.add_argument('--check-ui',action='store_true');args=parser.parse_args()
    report={'status':'FAIL','scope':__doc__,'hostFirewallChanged':False,'liveWebhostChanged':False}
    try:
        vm.status();executed=candidate.runtime();release=args.release_dir.resolve();assert executed['manifestSHA256']==hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest() and executed['appSHA256']==hashlib.sha256((release/'app.js').read_bytes()).hexdigest();installed=json.loads(remote('cat /srv/codi-network-fixture/installed-result.json'));report.update(browser(installed,args.mobile,args.check_ui));report['installed']=installed;report['executedRuntime']=executed
    finally:
        names=['scripts/prepare-native-network-vm.py','scripts/upgrade-signin-native-vm.py','scripts/setup-native-network-vm.py','scripts/native-network-vm-services.py','scripts/signin-native-vm-browser-check.py',str(args.release_dir.resolve().relative_to(ROOT))+'/guest_service/client.mjs',str(args.release_dir.resolve().relative_to(ROOT))+'/app.js']
        prefix=('signin-native-vm-mobile' if args.mobile else 'signin-native-vm-browser')+('-ui' if args.check_ui else '');report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks'/(prefix+'-result.json')
        if output.exists():output.rename(output.with_name(prefix+'-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
