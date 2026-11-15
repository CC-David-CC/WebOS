#!/usr/bin/env python3
"""Real public Chrome registered-only Linux Internet and private-file proof.

Only a newly registered qa_net_* account is used. Its generated file is removed
and account disabled afterward. No real user's sign-in or files are touched.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import time
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('public_role_helpers',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers);call,wait=helpers.call,helpers.wait
def reference():
    code="""import http.client,json,subprocess
route=json.loads(subprocess.check_output(['ip','-j','-4','route','show','default'],text=True))[0]['dev'];data=json.loads(subprocess.check_output(['ip','-j','-4','address','show','dev',route],text=True));address=next(a['local'] for n in data for a in n['addr_info'] if a['scope']=='global')
c=http.client.HTTPConnection(address,80,timeout=5);c.request('GET','/',headers={'Host':'ksu.codes','Connection':'close'});r=c.getresponse();assert r.status in (200,301,302,308);print(json.dumps({'lanIPv4':address,'directHostHTTPStatus':r.status}));c.close()
"""
    return json.loads(subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','python3','-c',shlex.quote(code)],check=True,capture_output=True,text=True,timeout=15).stdout)
def disable(name):
    assert re.fullmatch('qa_net_[a-f0-9]{12}',name)
    code="""import json,pathlib,subprocess
c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_text());script='import sys,json;sys.path.insert(0,sys.argv[1]);from origin_service.lifecycle import set_disabled;print(json.dumps(set_disabled(sys.argv[2],sys.argv[3],True)))'
r=subprocess.run(['runuser','-u','codi-issuer','--',c['python'],'-I','-B','-c',script,c['release'],str(pathlib.Path(c['stateRoot'])/'issuer/state'),NAME],check=True,capture_output=True,text=True,timeout=20);print(r.stdout)
""".replace('NAME',repr(name))
    value=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(code)],check=True,capture_output=True,text=True,timeout=30);return json.loads(value.stdout)['disabled']
def run(base=''):
    direct=reference();sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];registered=None;probes=[];checks=[];output={}
    def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code):
        v=call('/session/'+sid+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':[]});assert v['ok'],v;return v.get('value')
    def check(name,value):assert value,name;checks.append(name)
    def command(shell):
        wait(lambda:js('return !desktopLab.lifecycle.blocked'),45);token='PUBLIC_'+str(time.time_ns())
        text="printf '\\n"+token+"_BEGIN\\n'; { "+shell+"; } >/tmp/public-check-output 2>&1; public_rc=$?; printf '\\n"+token+"_RC=%s\\n' \"$public_rc\"; head -n 5 /tmp/public-check-output; printf '\\n"+token+"_END\\n'\r"
        js('sendTerminal(2,arguments[0])',[text]);wait(lambda:js('return serialScreen.text().includes(arguments[0])',['\n'+token+'_END\n']),30)
        tail=js('return serialScreen.text()');m=re.search(r'\n'+token+r'_RC=(\d+)\n(.*?)\n'+token+'_END\n',tail,re.S);assert m,tail[-2000:];rc=int(m[1]);assert rc in (0,1,124,137,143),(rc,m[2]);return rc,m[2]
    def ping(name,ip,allowed):
        rc,text=command('ping -c 1 -W 2 '+ip);check(name,(rc==0)==allowed);probes.append({'name':name,'expectedAllowed':allowed,'exitCode':rc})
    def http(name,ip,allowed):
        request=r'GET / HTTP/1.0\r\nHost: ksu.codes\r\nConnection: close\r\n\r\n'
        rc,text=command('timeout 5 sh -c '+shlex.quote('printf '+shlex.quote(request)+' | nc -w 4 '+ip+' 80'))
        match=re.search(r'HTTP/1\.[01] ([12345][0-9]{2})',text);received=bool(match);status=int(match[1]) if match else None;check(name,received==allowed)
        if allowed:check(name+' returns the expected public website response',status in (200,301,302,303,307,308))
        probes.append({'name':name,'expectedAllowed':allowed,'httpResponseReceived':received,'httpStatus':status,'exitCode':rc})
    try:
        call('/session/'+sid+'/timeouts',{'script':120000});call('/session/'+sid+'/url',{'url':'https://ksu.codes'+base+'/'})
        wait(lambda:js('return window.desktopLab?.guestState==="ready"&&guestNetworkAdapter?.mode==="anonymous"&&!desktopLab.lifecycle?.blocked'),150)
        js('window.keepVM=v86Instance;window.keepFS=v86Instance.fs9p;window.qaName="qa_net_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.qaPass=crypto.randomUUID()+crypto.randomUUID()')
        check('actual configured public guest SDK is active',js('return guestNetworkAdapter.controlled&&identityConfig.guestNetwork.durableAccountLimits'))
        command('export PUBLIC_KEEP=retained_shell; printf retained_file > /home/guest/public-role-keep.txt')
        ping('anonymous external public ping denied','1.1.1.1',False);ping('anonymous own public ping denied','104.180.210.33',False);http('anonymous own public web denied','104.180.210.33',False)
        http('anonymous real host LAN web denied',direct['lanIPv4'],False);http('anonymous external HTTP denied','1.1.1.1',False)
        check('anonymous Network menu explains sign-in required',js('const p=document.createElement("div");[...surfaces.values()][0].appendNetworkInfo(p);return p.textContent.includes("Sign in using Anon to enable Linux Internet");'))
        rc,text=command('timeout 6 nslookup example.com 10.86.0.3');check('anonymous public DNS denied',rc!=0)
        task('await changeAccount("register",qaName,qaPass);return true;');registered=js('return currentSession.public.name');assert re.fullmatch('qa_net_[a-f0-9]{12}',registered)
        wait(lambda:js('return guestNetworkAdapter.mode==="registered"'),30)
        ping('registered external public ping works','1.1.1.1',True)
        rc,text=command('timeout 6 nslookup example.com 10.86.0.3');check('registered public DNS works',rc==0)
        ping('registered own public ping works','104.180.210.33',True);http('registered own public web works','104.180.210.33',True);http('registered real host LAN web denied',direct['lanIPv4'],False)
        task('const c=await serverFileContext();await c.files.write("network-role-test.txt","Private QA saved data");return true;')
        check('registered private file write/read works alongside guest policy',task('return new TextDecoder().decode((await (await serverFileContext()).files.read("network-role-test.txt")).data)==="Private QA saved data";'))
        task('await changeAccount("anonymous");return true;');wait(lambda:js('return guestNetworkAdapter.mode==="anonymous"'),30);ping('logout withdraws own-address ping access','104.180.210.33',False);ping('logout withdraws all public ping access','1.1.1.1',False)
        task('await changeAccount("signin",qaName,qaPass);return true;');wait(lambda:js('return guestNetworkAdapter.mode==="registered"'),30)
        check('private saved file survives logout and sign-in',task('return new TextDecoder().decode((await (await serverFileContext()).files.read("network-role-test.txt")).data)==="Private QA saved data";'))
        check('same browser Linux and shared filesystem retained across identities',js('return v86Instance===keepVM&&v86Instance.fs9p===keepFS'))
        rc,text=command('printf "KEPT=%s:" "$PUBLIC_KEEP"; cat /home/guest/public-role-keep.txt');check('independent guest shell and file retained',rc==0 and 'KEPT=retained_shell:retained_file' in text)
        output.update(status='PASS',scope=__doc__,checks=checks,probes=probes,defaultCertificateTrust=True,certificateExceptionUsed=False,unfilteredHostLANReference=direct,liveRegisteredOwnWANAndAnonymousDenyVerified=True,allAnonymousGuestInternetDenied=True,privateServerFilesVerified=True,realUserAccountUsed=False,physicalAndroidVerified=False,independentWANVerified=False)
        return output
    except Exception:
        try:(ROOT/'.build/checks/public-signin-account-diagnostics.json').write_text(json.dumps(js('return {lifecycle:window.desktopLab?.lifecycle,network:guestNetworkAdapter?.mode,terminal:serialScreen.text().slice(-2800)}'),indent=2)+'\n')
        except Exception:pass
        raise
    finally:
        if registered:
            try:
                if js('return currentSession?.public.name')!=registered:task('await changeAccount("signin",qaName,qaPass);return true;')
                task('const c=await serverFileContext();try{const f=await c.files.read("network-role-test.txt");await c.files.remove("network-role-test.txt",f.sha256);}catch(e){if(e.status!==404)throw e;}return true;');output['generatedPrivateFileRemoved']=True
            finally:output['generatedAccountDisabled']=disable(registered)
        try:js('desktopLifecycle?.stop();guestNetworkAdapter?.destroy();v86Instance?.destroy();')
        finally:call('/session/'+sid,method='DELETE')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--release-dir',type=Path,default=ROOT/'.build/releases/connected-root-cache-r2');parser.add_argument('--base-path',default='');parser.add_argument('--output',type=Path);args=parser.parse_args();release=args.release_dir.resolve();assert args.base_path in ('','/hidden')
    result={'status':'FAIL','scope':__doc__}
    try:
        with urllib.request.urlopen('https://ksu.codes'+args.base_path+'/index.html',timeout=20) as response:assert response.read()==(release/'index.html').read_bytes()
        result['nativeManifestSHA256']=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest()
        with urllib.request.urlopen('https://ksu.codes'+args.base_path+'/gateway/client.mjs',timeout=20) as response:result['observedPublicFileClientSHA256']=hashlib.sha256(response.read()).hexdigest()
        result.update(run(args.base_path),basePath=args.base_path)
    finally:
        result['sha256']={'scripts/public-signin-account-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'executed-entry':hashlib.sha256((release/'index.html').read_bytes()).hexdigest(),'guest-SDK':hashlib.sha256((release/'guest_service/client.mjs').read_bytes()).hexdigest()};file=args.output or ROOT/'.build/checks/public-signin-account-result.json'
        if file.exists():file.rename(file.with_name('public-signin-account-before-'+str(time.time_ns())+'.json'))
        file.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
