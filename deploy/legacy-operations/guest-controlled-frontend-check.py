#!/usr/bin/env python3
"""Actual issuer launcher and controlled Relay HTTP/Chrome integration.

Disposable loopback issuer processes, Unix workers and real QEMU/v86. Covers
the public config/SDK gate and existing desktop account transitions. This does
not install managed frontend credentials, activate nftables or deploy a site.
"""
import asyncio
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import socket
import sys
import tempfile
import time
from urllib.parse import urlsplit
from aiohttp import ClientError,ClientSession,ClientTimeout,CookieJar,WSMsgType,web

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value
desktop=module('controlled_desktop_fixture','scripts/guest-desktop-browser-check.py')
relay_module=module('controlled_real_relay','guest-relay/server.py')
from guest_service.frontend import ControlledFrontend
from guest_service.runtime import VERSION,metadata,validate
from guest_service.usage import Permissions,UsageLedger,initialize_usage,initialize_permissions
from guest_service.worker import WireWorker
from gateway_service.auth import CHALLENGE as FILE_CHALLENGE,AUTHORIZE as FILE_AUTHORIZE
from origin_service.release import V11_NATIVE,PUBLIC,NETWORK,RUNTIME

class Fixture(desktop.DesktopFixture):
    def __init__(self,base,enabled=True):
        super().__init__(base,'controlled' if enabled else 'legacy')
        self.enabled=enabled;self.process=None;self.log=None;self.identity_config=None
    async def start(self):
        self.outgoing=ClientSession(timeout=ClientTimeout(total=5),trust_env=False,cookie_jar=CookieJar(unsafe=True))
        self.issuer_port=desktop.fixture_module.free_port()
        command=[sys.executable,'-B',str(ROOT/'scripts/serve-connected.py'),'--port',str(self.issuer_port),'--origin',self.origin,'--base-path',self.base,'--runtime-dir',str(self.root/'runtime')]
        if self.enabled:command+=['--guest-network-policy-sha256',self.policy.sha256,'--user-files']
        self.log=(self.root/'issuer.log').open('wb')
        self.process=await asyncio.create_subprocess_exec(*command,stdout=self.log,stderr=self.log,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        until=time.monotonic()+45
        while time.monotonic()<until:
            assert self.process.returncode is None,'Issuer exited: '+(self.root/'issuer.log').read_text()
            try:
                async with self.outgoing.get('http://127.0.0.1:'+str(self.issuer_port)+'/config.json',headers={'Host':urlsplit(self.origin).netloc}) as response:
                    if response.status==200:self.identity_config=await response.json();break
            except (ClientError,TimeoutError):pass
            await asyncio.sleep(.05)
        assert self.identity_config is not None,'Actual issuer CLI never became ready'
        self.legacy=relay_module.Relay(self.origin,identity_config_port=self.issuer_port,base_path=self.base,cookie_secret=self.cookie)
        self.frontend=self.legacy
        if self.enabled:
            self.usage_temp=tempfile.TemporaryDirectory(prefix='.codi-controlled-usage-',dir=Path.home());usage_root=Path(self.usage_temp.name)
            for name in ['policy','anonymous','registered']:(usage_root/name).mkdir(mode=0o700)
            self.permissions_path=usage_root/'policy/permissions.sqlite3';initialize_permissions(self.permissions_path,owner_uid=os.getuid())
            paths={};credentials={}
            for role in ['anonymous','registered']:
                usage_path=usage_root/role/'usage.sqlite3';initialize_usage(usage_path,role)
                self.ledgers[role]=UsageLedger(usage_path,role,Permissions(self.permissions_path,owner_uid=os.getuid()))
                paths[role]=str(self.root/(role+'.sock'));credentials[role]=secrets.token_urlsafe(32)
                worker=WireWorker(role,self.origin,self.policy,self.identity_config['identity'],credentials[role],base_path=self.base,lease_poll_seconds=.02,usage=self.ledgers[role])
                runner=web.AppRunner(worker.app(),access_log=None);await runner.setup();self.runners.append(runner);await web.UnixSite(runner,paths[role]).start();self.workers[role]=worker
            self.descriptor={'version':VERSION,'origin':self.origin,'basePath':self.base,'policy':self.policy.value(),'policySHA256':self.policy.sha256,'issuerPolicy':self.identity_config['identity'],'frontendUID':os.getuid(),'frontendGID':os.getgid(),'workerSockets':paths,'guardUnit':'codi-net-controlled-fixture-guard.service'}
            self.frontend=ControlledFrontend(self.legacy,self.descriptor,credentials);self.coordinator=self.frontend.coordinator
        app=web.Application();app.router.add_route('*',self.base+'/{path:.*}',self.proxy)
        runner=web.AppRunner(app,access_log=None);await runner.setup();self.runners.append(runner);await web.TCPSite(runner,'127.0.0.1',urlsplit(self.origin).port).start()
    async def proxy(self,request):
        path=request.match_info['path']
        if path.startswith('api/'):
            headers={k:v for k,v in request.headers.items() if k.lower() not in {'connection','transfer-encoding','upgrade'}}
            async with self.outgoing.request(request.method,'http://127.0.0.1:'+str(self.issuer_port)+'/'+path,headers=headers,data=await request.read(),allow_redirects=False) as response:
                return web.Response(body=await response.read(),status=response.status,headers={k:v for k,v in response.headers.items() if k.lower() not in {'connection','transfer-encoding','content-length'}})
        if path=='guest-network':return await self.frontend.relay(request)
        if not path:self.cookie_gets+=1
        if path=='guest-access/client.mjs':self.sdk_gets+=1
        response=await self.frontend.assets(request)
        response.headers['Cross-Origin-Opener-Policy']='same-origin';response.headers['Cross-Origin-Embedder-Policy']='require-corp'
        return response
    async def close(self):
        try:
            if self.process and self.process.returncode is None:
                self.process.terminate()
                try:await asyncio.wait_for(self.process.wait(),8)
                except TimeoutError:self.process.kill();await self.process.wait()
            if self.log:self.log.close()
        finally:await super().close()

async def http_checks(fixture):
    checks=[];url=fixture.origin+fixture.base+'/'
    def check(name,value):assert value,name;checks.append(name)
    async with ClientSession(timeout=ClientTimeout(total=5),trust_env=False,cookie_jar=CookieJar(unsafe=True)) as client:
        async with client.get(url) as response:
            check('real Relay index loads',response.status==200 and b'desktop' in (await response.read()).lower())
            cookie=response.cookies['codi_guest_relay'];check('mount-scoped HttpOnly Strict cookie',cookie['path']==fixture.base+'/' and cookie['httponly'] and cookie['samesite']=='Strict')
        async with client.get(url+'config.json') as response:
            config=await response.json();check('actual issuer identity preserved',response.status==200 and config['identity']==fixture.identity_config['identity']);check('config never cached',response.headers['Cache-Control']=='no-store')
        async with client.get(url+'guest-access/client.mjs') as response:
            body=await response.read()
            check('SDK available only with explicit control',response.status==(200 if fixture.enabled else 404))
            if fixture.enabled:check('exact private SDK explicitly served',hashlib.sha256(body).digest()==hashlib.sha256((ROOT/'guest_service/client.mjs').read_bytes()).digest() and response.content_type=='text/javascript')
        for path in ['guest_service/client.mjs','guest_service/runtime.py','guest_service/frontend.py','origin_service/guest_authority.py','scripts/serve-connected.py','connected-release.json']:
            async with client.get(url+path) as response:check('private source denied '+path,response.status==404)
        key=config['identity']['authorityKeys'][0]['jwk']
        for path,target in [('/api/v1/guest-network/challenge','/api/v1/guest-network/authorize'),(FILE_CHALLENGE,FILE_AUTHORIZE)]:
            async with client.post(fixture.origin+fixture.base+path,headers={'Origin':fixture.origin},json={'key':key,'path':fixture.base+target}) as response:
                check('optional authority composition '+path,response.status==(200 if fixture.enabled else 404))
        if not fixture.enabled:
            check('off mode has no authorization metadata','authorization' not in config['guestNetwork'] and 'durableAccountLimits' not in config['guestNetwork']);return checks
        check('matching mount and policy advertised',config['guestNetwork']['authorization']==metadata(fixture.base,fixture.policy.sha256)['authorization'])
        check('file gateway metadata survives composition',config['gateway']['basePath']==fixture.base+'/gateway')
        check('durable policy omits old restart-reset claim',config['guestNetwork']['durableAccountLimits'] is True and 'serviceCapReset' not in config['guestNetwork']['previewPolicy'])
        async with client.head(url+'guest-access/client.mjs') as response:check('SDK HEAD has no body',response.status==200 and not await response.read())
        # Old binary-only tabs still get an anonymous virtual gateway, with no
        # unsolicited control messages or login promotion.
        ws=await client.ws_connect(url+'guest-network',headers={'Origin':fixture.origin})
        try:
            mac=bytes.fromhex('022215000001');arp=bytes([255])*6+mac+b'\x08\x06'+b'\0\x01\x08\0\x06\x04\0\x01'+mac+socket.inet_aton('10.86.0.2')+bytes(6)+socket.inet_aton('10.86.0.1')
            await ws.send_bytes(arp);message=await asyncio.wait_for(ws.receive(),5)
            check('legacy binary tab receives actual anonymous QEMU ARP',message.type==WSMsgType.BINARY and message.data[12:14]==b'\x08\x06' and message.data[20:22]==b'\0\2')
            check('legacy wire never starts registered QEMU',not fixture.workers['registered'].processes)
        finally:await ws.close()
        async def fake_config(request):return web.json_response(fake_config.value,status=fake_config.status)
        fake_config.value=copy.deepcopy(fixture.identity_config);fake_config.status=200
        app=web.Application();app.router.add_get('/config.json',fake_config);runner=web.AppRunner(app,access_log=None);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start();fixture.legacy.identity_config_port=site._server.sockets[0].getsockname()[1]
        try:
            changes=[('missing metadata',lambda v:v.pop('guestNetwork')),('wrong policy',lambda v:v['guestNetwork']['authorization'].update(policySHA256='0'*64)),('wrong client path',lambda v:v['guestNetwork']['authorization'].update(clientPath='/wrong.mjs')),('wrong issuer key',lambda v:v['identity']['authorityKeys'][0].update(kid='changed')),('wrong origin',lambda v:v['identity'].update(issuer='https://other.invalid')),('oversized configuration',lambda v:v.update(extra='x'*70000))]
            for name,mutate in changes:
                fake_config.value=copy.deepcopy(fixture.identity_config);mutate(fake_config.value)
                async with client.get(url+'config.json') as response:check('issuer mismatch fails closed '+name,response.status==502)
            fake_config.value=copy.deepcopy(fixture.identity_config);fake_config.status=503
            async with client.get(url+'config.json') as response:check('issuer outage fails closed',response.status==502)
        finally:fixture.legacy.identity_config_port=fixture.issuer_port;await runner.cleanup()
        for name,mutate in [('policy digest',lambda v:v.update(policySHA256='0'*64)),('private authority key',lambda v:v['issuerPolicy']['authorityKeys'][0]['jwk'].update(d='forbidden')),('shared socket',lambda v:v['workerSockets'].update(registered=v['workerSockets']['anonymous'])),('socket traversal',lambda v:v['workerSockets'].update(anonymous='/tmp/../wire.sock')),('root frontend',lambda v:v.update(frontendUID=0))]:
            value=copy.deepcopy(fixture.descriptor);mutate(value)
            try:validate(value)
            except ValueError:checks.append('descriptor refusal '+name)
            else:raise AssertionError('Accepted invalid descriptor '+name)
    return checks

async def main():
    witnesses=[]
    for base,enabled in [('',False),('/hidden',False),('',True),('/hidden',True)]:
        fixture=Fixture(base,enabled)
        try:
            await fixture.start();checks=await http_checks(fixture)
            value={'basePath':base,'enabled':enabled,'checks':checks,'actualIssuerCLI':True}
            fixture.sdk_gets=0
            if enabled:
                value['desktop']=await asyncio.to_thread(desktop.browser,fixture,base=='/hidden');assert fixture.sdk_gets==1
            witnesses.append(value);print(json.dumps({'phase':'controlled frontend passed','basePath':base,'enabled':enabled}),flush=True)
        finally:await fixture.close()
    return witnesses

if __name__=='__main__':
    names=sorted(V11_NATIVE|PUBLIC|{'network/'+name for name in NETWORK}|{'.build/v86/'+name for name in RUNTIME}|{'assets/terminal-initramfs.cpio.gz','guest_service/runtime.py','guest_service/frontend.py','scripts/guest-controlled-frontend-check.py','scripts/guest-desktop-browser-check.py','scripts/guest-client-browser-check.py','scripts/touch-preview-check.py','origin_service/guest_authority.py','guest_service/coordinator.py','guest_service/worker.py','guest_service/usage.py','guest_service/frames.py','guest_service/egress.py','guest_service/authorization.py','guest_service/client.mjs'})
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};result={'status':'FAIL','scope':__doc__,'sha256':hashes,'liveChanged':False,'installedCredentialTest':False,'kernelIntegration':False}
    try:
        witnesses=asyncio.run(main());assert hashes=={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};result.update(status='PASS',witnesses=witnesses)
    finally:
        output=ROOT/'.build/checks/guest-controlled-frontend-result.json'
        if output.exists():output.rename(output.with_name('guest-controlled-frontend-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
