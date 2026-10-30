#!/usr/bin/env python3
"""Chrome/WebCrypto, actual gateway subprocess restart, private files and v86.

All accounts/state/services are disposable loopback fixtures. Does not modify
the live site or connect to actual user storage. Root and /hidden mounts tested.
"""
import asyncio
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server
from aiohttp import ClientSession,ClientTimeout,web,ClientError

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
WORKER_ROOT=ROOT
NATIVE_ROOT=None
from origin_service.lifecycle import Service
from origin_service.gateway_authority import GatewayAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from codiauth.service import Config
from gateway_service.auth import MAX_REQUEST_BYTES
from gateway_service.http import MAX_FILE_BYTES
spec=importlib.util.spec_from_file_location('gateway_staging',ROOT/'scripts/serve-connected.py');staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
spec=importlib.util.spec_from_file_location('gateway_chrome_helpers',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
call,wait=helpers.call,helpers.wait;CHECKS=ROOT/'.build/checks'

def free_port():
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));return probe.getsockname()[1]

class Fixture:
    def __init__(self,base_path):
        self.base=base_path;self.temp=tempfile.TemporaryDirectory(prefix='codi-gateway-browser-');self.root=Path(self.temp.name)
        self.origin='http://127.0.0.1:'+str(free_port());self.gateway_port=free_port()
        self.child=None;self.http_thread=None;self.runner=None;self.outgoing=None;self.native_child=None;self.native_log=None

    async def start(self):
        if NATIVE_ROOT is None:
            public=staging.stage(self.root/'public');fixture=self
            class Issuer(Service):
                def config(self):
                    value=super().config();value['gateway']={'version':'codi-user-files/1','basePath':fixture.base+'/gateway','fileBytes':MAX_FILE_BYTES};return value
            self.issuer=Issuer(Config(self.root/'issuer-state',public,origin=self.origin,rate_per_minute=1000),base_path=self.base)
            self.http=make_server('127.0.0.1',0,staging.HeadSupport(GatewayAuthority(self.issuer)),server_class=BoundedServer,handler_class=QuietHandler)
            self.http_thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.http_thread.start();self.issuer_port=self.http.server_port
            identity_policy=self.issuer.config()['identity']
        else:
            self.issuer_port=free_port();self.native_log=(self.root/'native.log').open('w')
            self.native_child=subprocess.Popen([sys.executable,'-I','-B',str(NATIVE_ROOT/'scripts/serve-connected.py'),'--port',str(self.issuer_port),'--origin',self.origin,'--base-path',self.base,'--runtime-dir',str(self.root/'native-runtime'),'--user-files'],stdout=self.native_log,stderr=self.native_log)
            async with ClientSession(timeout=ClientTimeout(total=2),trust_env=False) as session:
                for _ in range(200):
                    if self.native_child.poll() is not None:raise AssertionError('Native issuer exited; '+(self.root/'native.log').read_text()[-2000:])
                    try:
                        async with session.get('http://127.0.0.1:'+str(self.issuer_port)+'/config.json',headers={'Host':urlsplit(self.origin).netloc}) as response:
                            if response.status==200:
                                value=await response.json();identity_policy=value['identity'];assert value['gateway']['basePath']==self.base+'/gateway';break
                    except (OSError,ClientError):pass
                    await asyncio.sleep(.025)
                else:raise AssertionError('Native issuer readiness timeout')
        for name in ['gateway-state','gateway-files']:(self.root/name).mkdir(mode=0o700)
        policy=self.root/'issuer-policy.json';raw=json.dumps(identity_policy).encode();policy.write_bytes(raw);policy.chmod(0o600)
        self.command=[sys.executable,'-I','-B',str(WORKER_ROOT/'scripts/serve-user-files.py'),'serve','--state-root',str(self.root/'gateway-state'),'--data-root',str(self.root/'gateway-files'),'--issuer-policy',str(policy),'--issuer-policy-sha256',hashlib.sha256(raw).hexdigest(),'--port',str(self.gateway_port),'--base-path',self.base]
        init=self.command.copy();init[4]='initialize'
        initialized=await asyncio.to_thread(subprocess.run,init,capture_output=True,text=True,timeout=15)
        if initialized.returncode:raise AssertionError(initialized.stderr)
        self.log=(self.root/'gateway.log').open('w');await self.start_child()
        self.outgoing=ClientSession(timeout=ClientTimeout(total=150),trust_env=False,auto_decompress=False)
        app=web.Application(client_max_size=MAX_REQUEST_BYTES,handler_args={'auto_decompress':False})
        app.router.add_route('*','/{tail:.*}',self.proxy)
        self.runner=web.AppRunner(app,access_log=None);await self.runner.setup();await web.TCPSite(self.runner,'127.0.0.1',int(urlsplit(self.origin).port)).start()

    async def start_child(self):
        self.child=subprocess.Popen(self.command,stdout=self.log,stderr=self.log)
        async with ClientSession(timeout=ClientTimeout(total=2),trust_env=False) as session:
            for _ in range(150):
                if self.child.poll() is not None:raise AssertionError('Gateway child exited; '+(self.root/'gateway.log').read_text()[-2000:])
                try:
                    async with session.get('http://127.0.0.1:'+str(self.gateway_port)+'/healthz',headers={'Host':urlsplit(self.origin).netloc}) as response:
                        if response.status==200:return
                except (OSError,ClientError):pass
                await asyncio.sleep(.02)
        raise AssertionError('Gateway readiness timeout')

    async def restart(self):
        before=self.child.pid;self.child.kill();await asyncio.to_thread(self.child.wait,10);await self.start_child()
        return {'beforePID':before,'afterPID':self.child.pid,'actualProcessChanged':before!=self.child.pid}

    async def proxy(self,request):
        path=request.raw_path
        if self.base:
            if not path.startswith(self.base+'/'):raise web.HTTPNotFound()
            path=path[len(self.base):]
        target=('http://127.0.0.1:'+str(self.gateway_port) if path.startswith('/gateway/') else 'http://127.0.0.1:'+str(self.issuer_port))+path
        hop={'connection','keep-alive','transfer-encoding','upgrade','te','trailer'}
        headers={key:value for key,value in request.headers.items() if key.lower() not in hop}
        response=None
        try:
            async with self.outgoing.request(request.method,target,headers=headers,data=request.content if request.can_read_body else None,allow_redirects=False) as upstream:
                response=web.StreamResponse(status=upstream.status,headers={k:v for k,v in upstream.headers.items() if k.lower() not in hop});await response.prepare(request)
                async for chunk in upstream.content.iter_chunked(65536):await response.write(chunk)
                await response.write_eof();return response
        except (OSError,ClientError):
            if response is not None and response.prepared:
                if request.transport:request.transport.close()
                return response
            return web.json_response({'error':'Disposable fixture backend unavailable'},status=503)

    async def close(self):
        if self.runner:await self.runner.cleanup()
        if self.outgoing:await self.outgoing.close()
        if self.child and self.child.poll() is None:self.child.terminate();await asyncio.to_thread(self.child.wait,15)
        if self.http_thread:
            await asyncio.to_thread(self.http.shutdown);self.http_thread.join(2);self.http.server_close()
        if self.native_child and self.native_child.poll() is None:self.native_child.terminate();await asyncio.to_thread(self.native_child.wait,15)
        if self.native_log:self.native_log.close()
        if getattr(self,'log',None):self.log.close()
        self.temp.cleanup()

def chrome(url,commands,responses,loop):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage','--window-size=1200,900']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    def js(code,args=[]):return call('/session/'+session+'/execute/sync',{'script':code,'args':args})
    def asyncjs(code,args=[]):
        value=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message,status:error.status}));','args':args})
        if not value['ok']:raise AssertionError(value)
        return value.get('value')
    try:
        call('/session/'+session+'/timeouts',{'script':120000})
        call('/session/'+session+'/url',{'url':url});wait(lambda:js('return window.desktopLab?.guestState==="ready"'),120)
        asyncjs('window.__fileModule=await import(identityConfig.gateway.basePath+"/client.mjs");window.__fileVM=v86Instance;window.__fileName="file_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.__filePassword=crypto.randomUUID()+crypto.randomUUID();let rejected=false;try{const f=new __fileModule.UserFiles(identityConfig,currentSession);await f.list();}catch{rejected=true;}if(!rejected)throw Error("Anonymous SDK allowed files");await changeAccount("register",__fileName,__filePassword);window.__fileA=currentSession;window.__files=new __fileModule.UserFiles(identityConfig,__fileA,{sessionValid:()=>currentSession===__fileA});await __files.mkdir("Documents");window.__fileSaved=await __files.write("Documents/note.txt","A private server note");const loaded=await __files.read("Documents/note.txt");return new TextDecoder().decode(loaded.data)==="A private server note";')
        assert asyncjs('let conflict=false;try{await __files.write("Documents/note.txt","stale edit","0".repeat(64));}catch(error){conflict=error.status===409;}return conflict;')
        assert asyncjs('const original=Date.now;Date.now=()=>original()+10000;try{return (await __files.list("Documents")).entries.length===1;}finally{Date.now=original;}')
        large=asyncjs('window.__fileBinary=new Uint8Array(8*1024*1024);for(let i=0;i<__fileBinary.length;i++)__fileBinary[i]=i%251;window.__fileBig=await __files.write("Documents/binary.bin",__fileBinary);window.__fileRead=await __files.read("Documents/binary.bin");await guestFiles.write("/Documents/from-server.bin",__fileRead.data);return {bytes:__fileRead.data.length,sha256:__fileRead.sha256,sameVM:v86Instance===__fileVM};')
        assert large['bytes']==8*1024*1024 and large['sameVM']
        command='sha256sum /home/guest/Documents/from-server.bin; echo FILE_GATEWAY_VM_OK\r'
        js('sendTerminal(2,arguments[0]);',[command]);wait(lambda:js('return serialScreen.text().includes(arguments[0])&&serialScreen.text().includes("\\nFILE_GATEWAY_VM_OK\\n")',[large['sha256']]),120)
        loop.call_soon_threadsafe(commands.put_nowait,'restart')
        restarted=responses.result(timeout=30);assert restarted['actualProcessChanged']
        assert asyncjs('const value=await __files.read("Documents/note.txt");return new TextDecoder().decode(value.data)==="A private server note";')
        assert asyncjs('window.__fileBName="file_"+crypto.randomUUID().replaceAll("-","").slice(0,12);await changeAccount("register",__fileBName,__filePassword);window.__fileB=currentSession;window.__filesB=new __fileModule.UserFiles(identityConfig,__fileB,{sessionValid:()=>currentSession===__fileB});let isolated=false;try{await __filesB.read("Documents/note.txt");}catch(error){isolated=error.status===404;}let oldStopped=false;try{await __files.list();}catch{oldStopped=true;}return isolated&&oldStopped;')
        assert asyncjs('try{await identityModule.logoutSession(identityConfig,__fileA);}catch{}const stale=new __fileModule.UserFiles(identityConfig,__fileA);let refused=false;try{await stale.list();}catch(error){refused=error.status===401;}return refused;')
        assert asyncjs('await changeAccount("signin",__fileName,__filePassword);window.__filesFresh=new __fileModule.UserFiles(identityConfig,currentSession);const value=await __filesFresh.read("Documents/note.txt");return new TextDecoder().decode(value.data)==="A private server note"&&v86Instance===__fileVM;')
        # A full browser reload discards its VM/RAM but not authenticated server files.
        account=js('return {name:__fileName,password:__filePassword};')
        call('/session/'+session+'/refresh',{});wait(lambda:js('return window.desktopLab?.guestState==="ready"'),120)
        assert asyncjs('if(currentSession.public.kind!=="anonymous")throw Error("Reload did not start anonymous");await changeAccount("signin",params[0].name,params[0].password);const module=await import(identityConfig.gateway.basePath+"/client.mjs"),files=new module.UserFiles(identityConfig,currentSession);const value=await files.read("Documents/note.txt");return new TextDecoder().decode(value.data)==="A private server note";',[account])
        return {'url':url,'webCryptoProofs':True,'anonymousRefused':True,'deviceClockTenSecondsAheadSupported':True,'real8MiBBinaryRoundtrip':large['bytes'],'guestReadsRestoredServerFile':True,'actualGatewayProcessRestart':restarted,'anotherAccountCannotReadFile':True,'staleSessionClientStopped':True,'serverRejectsLoggedOutToken':True,'fileVersionConflict':True,'serverFilesSurviveBrowserReload':True,'loginAfterBootPreservesVM':True}
    finally:call('/session/'+session,method='DELETE')

async def main():
    import concurrent.futures
    results=[]
    for prefix in ['', '/hidden']:
        fixture=Fixture(prefix);commands=asyncio.Queue();response=concurrent.futures.Future()
        try:
            await fixture.start();loop=asyncio.get_running_loop()
            job=asyncio.create_task(asyncio.to_thread(chrome,fixture.origin+prefix+'/',commands,response,loop))
            async def control():
                while not job.done():
                    get=asyncio.create_task(commands.get());done,_=await asyncio.wait([job,get],return_when=asyncio.FIRST_COMPLETED)
                    if get not in done:get.cancel();break
                    if get.result()=='restart':response.set_result(await fixture.restart())
            controller=asyncio.create_task(control())
            result=await job;await controller;results.append(result)
            print(json.dumps({'milestone':'browser private files passed','basePath':prefix}),flush=True)
        finally:await fixture.close()
    return results

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--worker-release',type=Path);parser.add_argument('--issuer-release',type=Path);args=parser.parse_args()
    report={'status':'FAIL','scope':'Disposable actual Chrome/WebCrypto, running v86, real issuer/file HTTP and gateway process crash/restart; local root/hidden mounts, not live deployment'}
    if args.worker_release:
        WORKER_ROOT=args.worker_release.resolve();raw=(WORKER_ROOT/'files-service.json').read_bytes();metadata=json.loads(raw)
        assert metadata['version']=='codi-private-file-service/1'
        for name,record in metadata['files'].items():
            assert record=={'bytes':(WORKER_ROOT/name).stat().st_size,'sha256':hashlib.sha256((WORKER_ROOT/name).read_bytes()).hexdigest()}
            assert (ROOT/name).read_bytes()==(WORKER_ROOT/name).read_bytes()
        report['executedWorkerManifestSHA256']=hashlib.sha256(raw).hexdigest()
    if args.issuer_release:
        from origin_service.release import verify
        NATIVE_ROOT=args.issuer_release.resolve();report['executedIssuerManifestSHA256']=verify(NATIVE_ROOT)['manifestSHA256']
    try:report.update(status='PASS',witnesses=asyncio.run(main()))
    finally:
        names=['gateway_service/http.py','gateway_service/auth.py','gateway_service/transfers.py','gateway_service/user_store.py','gateway_service/client.mjs','origin_service/gateway_authority.py','scripts/serve-user-files.py','scripts/gateway-browser-check.py']
        report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names}
        output=CHECKS/'gateway-browser-result.json'
        if output.exists() and json.loads(output.read_text()).get('status')=='FAIL':output.rename(output.with_name('gateway-browser-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
