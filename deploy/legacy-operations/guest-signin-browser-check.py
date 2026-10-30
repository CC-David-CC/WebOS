#!/usr/bin/env python3
"""Real Chrome/Linux role promotion under the registered-only policy.

Owned loopback issuer/coordinator/QEMU fixture. Sends one registered ping and
HTTP request to public 1.1.1.1; anonymous attempts are rejected before QEMU.
This does not install the managed UID guard or change live services.
"""
import asyncio,hashlib,importlib.util,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('signin_browser_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from guest_service.signin_policy import SigninPolicy
call,wait=fixture.call,fixture.wait
class Fixture(fixture.Fixture):
    def __init__(self,base):super().__init__(base);self.policy=SigninPolicy(('1.1.1.1',),('1.1.1.3',))
def browser(f):
    s=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];checks=[]
    def js(code,args=[]):return call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(code):
        r=call('/session/'+s+'/execute/async',{'script':'const done=arguments[0];(async()=>{'+code+'})().then(v=>done({ok:true,value:v}),e=>done({ok:false,error:e.message}));','args':[]});assert r['ok'],r;return r.get('value')
    def check(name,value):assert value,name;checks.append(name)
    def command(shell):
        marker='SIGNIN_'+str(time.time_ns())
        text=shell+'; signin_test_rc=$?; printf "\\n'+marker+'=%s\\n" "$signin_test_rc"\r'
        js('command(arguments[0])',[text]);wait(lambda:js('return shellText.includes(arguments[0])',['\n'+marker+'=']),20)
        output=js('return shellText');match=re.search(r'\n'+marker+r'=(\d+)\n',output);assert match,output[-1600:];return int(match[1]),output
    def kept():
        check('same browser Linux and filesystem',js('return fixtureVM===savedVM&&fixtureVM.fs9p===savedFS'))
        rc,out=command('printf "KEEP=%s:" "$SIGNIN_KEEP"; cat /home/guest/signin-keep.txt');check('same shell variable and guest file',rc==0 and 'KEEP=shell_kept:file_kept' in out)
    try:
        call('/session/'+s+'/timeouts',{'script':120000});call('/session/'+s+'/url',{'url':f.origin+f.base+'/'})
        wait(lambda:js('return fixtureReady&&guestFiles.ready&&shellText.includes("$")&&adapter.mode==="anonymous"'),150)
        js('window.savedVM=fixtureVM;window.savedFS=fixtureVM.fs9p;window.testName="signin_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.testPass=crypto.randomUUID()+crypto.randomUUID()')
        command('export SIGNIN_KEEP=shell_kept; printf file_kept > /home/guest/signin-keep.txt')
        before=f.workers['anonymous'].blocked
        rc,_=command('ping -c 1 -W 1 1.1.1.1 >/tmp/signin-anon-ping 2>&1');check('anonymous Linux public ping denied',rc!=0)
        rc,_=command('timeout 3 nslookup example.com 10.86.0.3 >/tmp/signin-anon-dns 2>&1');check('anonymous Linux DNS denied',rc!=0)
        rc,_=command('timeout 3 sh -c '+"'printf x | nc -w 2 1.1.1.1 80'"+' >/tmp/signin-anon-web 2>&1');check('anonymous Linux web connection denied',rc!=0)
        check('anonymous Internet packets rejected before QEMU',f.workers['anonymous'].blocked>=before+3)
        task('return await account("auth",testName,testPass)');wait(lambda:js('return adapter.mode==="registered"'),30);kept()
        rc,_=command('ping -c 1 -W 2 1.1.1.1 >/tmp/signin-reg-ping 2>&1');check('registered Linux public ping works',rc==0)
        request="printf 'GET / HTTP/1.0\\r\\nHost: one.one.one.one\\r\\nConnection: close\\r\\n\\r\\n' | nc -w 4 1.1.1.1 80 > /tmp/signin-reg-web; head -n 1 /tmp/signin-reg-web"
        rc,out=command(request);check('registered Linux receives public HTTP response',bool(re.search(r'HTTP/1\.[01] [12345][0-9]{2}',out)))
        task('return await account("anonymous")');wait(lambda:js('return adapter.mode==="anonymous"'),30);kept()
        before=f.workers['anonymous'].blocked;rc,_=command('ping -c 1 -W 1 1.1.1.1 >/tmp/signin-logout-ping 2>&1')
        check('logout withdraws Internet access immediately',rc!=0 and f.workers['anonymous'].blocked>before)
        return {'status':'PASS','scope':__doc__,'checks':checks,'realAnonymousPingDNSWebDenied':True,'realRegisteredPublicPingAndHTTP':True,'logoutWithdrawsAccess':True,'sameLinuxShellAndFilesystem':True,'publicRollout':False,'managedKernelConfinementClaimed':False,'realUserAccountUsed':False}
    finally:
        try:task('adapter?.destroy();await fixtureVM?.destroy();return true')
        finally:call('/session/'+s,method='DELETE')
async def main():
    f=Fixture('/hidden')
    try:await f.start();return await asyncio.to_thread(browser,f)
    finally:await f.close()
if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(asyncio.run(main()))
    finally:
        result['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['guest_service/signin_policy.py','guest_service/frames.py','scripts/guest-signin-browser-check.py']};p=ROOT/'.build/checks/guest-signin-browser-result.json'
        if p.exists():p.rename(p.with_name(p.stem+'-before-'+str(time.time_ns())+'.json'))
        p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
