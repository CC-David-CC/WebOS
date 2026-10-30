#!/usr/bin/env python3
"""Real Chrome/v86 adapter and same-origin network grants, root and hidden mounts.

Disposable local HTTP issuer/Unix/QEMU/coordinator; no public deployment or
kernel confinement here. Network tests send only virtual gateway ARP. Actual
Linux shell/file continuity is checked across identities and cookie reconnection.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import socket
import sys
import tempfile
import threading
import time
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server
from aiohttp import ClientSession,ClientTimeout,web
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.lifecycle import Service
from origin_service.guest_authority import GuestAuthority
from origin_service.http_server import BoundedServer,QuietHandler
from guest_service.coordinator import GuestCoordinator
from guest_service.egress import EgressPolicy
from guest_service.worker import WireWorker
from codiauth.service import Config
spec=importlib.util.spec_from_file_location('guest_browser_staging',ROOT/'scripts/serve-connected.py');staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging)
spec=importlib.util.spec_from_file_location('guest_browser_helpers',ROOT/'scripts/touch-preview-check.py');helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
call,wait=helpers.call,helpers.wait
PAGE=b'''<!doctype html><meta charset="utf-8"><title>Local guest adapter integration fixture</title><p>Local Linux network fixture</p><script src=".build/v86/libv86.js"></script><script src="desktop-apps.js"></script><script type="module" src="fixture.mjs"></script>'''
SCRIPT=r'''
import {GuestNetworkAdapter} from './guest-access/client.mjs';
import {beginSession,logoutSession} from './network/identity.mjs';
window.fixtureFatal=null;window.fixtureReady=false;window.shellText='';window.receivedPackets=[];window.networkStates=[];
try{
 const config=await (await fetch('config.json')).json();window.fixtureConfig=config;window.currentIdentity=await beginSession(config,'anonymous');
 const vm=new V86({wasm_path:'.build/v86/v86.wasm',memory_size:256*1024*1024,bios:{url:'.build/v86/seabios.bin'},vga_bios:{url:'.build/v86/vgabios.bin'},bzimage:{url:'.build/v86/vmlinuz'},initrd:{url:'assets/terminal-initramfs.cpio.gz'},net_device:{type:'virtio'},filesystem:{},cmdline:'console=ttyS0,115200n8 rdinit=/init panic=-1 quiet loglevel=0 guest_net=1',autostart:true,disable_keyboard:true,disable_mouse:true,disable_speaker:true});
 window.fixtureVM=vm;window.adapter=new GuestNetworkAdapter(vm,config,{getSession:()=>currentIdentity,onStatus:value=>networkStates.push(value)});
 const sendBus=vm.bus.send.bind(vm.bus);vm.bus.send=(event,frame)=>{if(event==='net0-receive')receivedPackets.push({length:frame.length,type:frame[12]*256+frame[13]});return sendBus(event,frame);};
 let line='',bootstrap='';const decoder=new TextDecoder();
 vm.add_listener('serial0-output-byte',byte=>{
  const ch=String.fromCharCode(byte);line+=ch;
  if(ch!=='\n')return;const text=line.replace(/\r?\n$/,'');line='';
  if(text==='\x1eCDMUX R'){fixtureReady=true;vm.serial0_send('\x1eCDMUX O 2\n');}
  else {const m=/^\x1eCDMUX D 2 ([0-9a-f]*)$/.exec(text);if(m)shellText+=decoder.decode(Uint8Array.from(m[1].match(/../g)||[],v=>parseInt(v,16)),{stream:true}).replace(/\r/g,'');else bootstrap+=text+'\n';}
 });
 vm.add_listener('emulator-ready',()=>guestFiles.connect(vm,{networkRelay:true}).catch(e=>fixtureFatal=e.stack));
 window.command=text=>vm.serial0_send('\x1eCDMUX I 2 '+[...new TextEncoder().encode(text)].map(b=>b.toString(16).padStart(2,'0')).join('')+'\n');
 window.account=async(kind,name='',password='')=>{
  const old=currentIdentity;currentIdentity=await beginSession(config,kind,name,password);adapter.syncSession();await logoutSession(config,old).catch(()=>{});return currentIdentity.public.kind;
 };
 window.arp=()=>{
  const bytes=new Uint8Array([255,255,255,255,255,255,2,34,21,0,0,1,8,6,0,1,8,0,6,4,0,1,2,34,21,0,0,1,10,86,0,2,0,0,0,0,0,0,10,86,0,1]);if(window.fixtureMAC){bytes.set(fixtureMAC,6);bytes.set(fixtureMAC,22);}adapter.send(bytes);
 };
}catch(error){fixtureFatal=error.stack;}
'''

def free_port():
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));return sock.getsockname()[1]

class Fixture:
    def __init__(self,base):
        self.base=base;self.temp=tempfile.TemporaryDirectory(prefix='codi-guest-browser-');self.root=Path(self.temp.name);self.origin='http://127.0.0.1:'+str(free_port());self.cookie=secrets.token_urlsafe(32);self.cookie_gets=0;self.runners=[];self.workers={};self.http=None;self.thread=None;self.outgoing=None
        self.policy=EgressPolicy(('1.1.1.1',),('1.1.1.3',))
    def worker_usage(self,role):return None
    async def start(self):
        f=self;public=staging.stage(self.root/'public')
        class Issuer(Service):
            def config(self):
                value=super().config();value['guestNetwork']={'relayPath':f.base+'/guest-network','authorization':{'version':'codi-guest-network-auth/1','policySHA256':f.policy.sha256,'clientPath':f.base+'/guest-access/client.mjs'}};return value
        self.issuer=Issuer(Config(self.root/'issuer',public,origin=self.origin,rate_per_minute=1000),base_path=self.base)
        self.http=make_server('127.0.0.1',0,staging.HeadSupport(GuestAuthority(self.issuer,self.policy.sha256)),server_class=BoundedServer,handler_class=QuietHandler);self.thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start()
        endpoints={}
        for role in ['anonymous','registered']:
            secret=secrets.token_urlsafe(32);path=str(self.root/(role+'.sock'));worker=WireWorker(role,self.origin,self.policy,self.issuer.config()['identity'],secret,base_path=self.base,lease_poll_seconds=.02,usage=self.worker_usage(role))
            runner=web.AppRunner(worker.app(),access_log=None);await runner.setup();self.runners.append(runner);await web.UnixSite(runner,path).start();self.workers[role]=worker;endpoints[role]={'socket':path,'secret':secret}
        self.coordinator=GuestCoordinator(self.origin,self.policy,endpoints,self.cookie,base_path=self.base)
        self.outgoing=ClientSession(timeout=ClientTimeout(total=30),trust_env=False)
        app=web.Application();app.router.add_route('*','/{tail:.*}',self.proxy);runner=web.AppRunner(app,access_log=None);await runner.setup();self.runners.append(runner);await web.TCPSite(runner,'127.0.0.1',urlsplit(self.origin).port).start()
    async def proxy(self,request):
        path=request.path
        if self.base:
            if not path.startswith(self.base+'/'):raise web.HTTPNotFound()
            path=path[len(self.base):]
        if path=='/':
            self.cookie_gets+=1;response=web.Response(body=PAGE,content_type='text/html',headers={'Cross-Origin-Opener-Policy':'same-origin','Cross-Origin-Embedder-Policy':'require-corp'})
            response.set_cookie('codi_guest_relay',self.cookie,httponly=True,samesite='Strict',path=self.base+'/',max_age=3600);return response
        if path=='/fixture.mjs':return web.Response(body=SCRIPT.encode(),content_type='text/javascript')
        if path=='/guest-access/client.mjs':return web.Response(body=(ROOT/'guest_service/client.mjs').read_bytes(),content_type='text/javascript')
        if path=='/guest-network':return await self.coordinator.relay(request)
        headers={k:v for k,v in request.headers.items() if k.lower() not in {'connection','transfer-encoding','upgrade'}}
        body=await request.read() if request.can_read_body else None
        async with self.outgoing.request(request.method,'http://127.0.0.1:'+str(self.http.server_port)+path,headers=headers,data=body,allow_redirects=False) as response:
            return web.Response(body=await response.read(),status=response.status,headers={k:v for k,v in response.headers.items() if k.lower() not in {'connection','transfer-encoding','content-length'}})
    async def close(self):
        for runner in reversed(self.runners):await runner.cleanup()
        if self.outgoing:await self.outgoing.close()
        if self.http:
            await asyncio.to_thread(self.http.shutdown);self.thread.join(3);self.http.server_close()
        assert all(not w.processes and w.active==0 for w in self.workers.values())
        self.temp.cleanup()

def browser(url):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId']
    def js(source,args=[]):return call('/session/'+session+'/execute/sync',{'script':source,'args':args})
    def task(source,args=[]):
        value=call('/session/'+session+'/execute/async',{'script':'const params=arguments,done=arguments[arguments.length-1];(async()=>{'+source+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.message}));','args':args})
        assert value['ok'],value;return value.get('value')
    def ready():
        fatal=js('return window.fixtureFatal');assert not fatal,fatal
        return js('return window.fixtureReady&&typeof guestFiles!=="undefined"&&guestFiles.ready&&shellText.includes("$")')
    def network(mode):wait(lambda:js('return window.adapter?.mode===arguments[0]',[mode]),30)
    def command(text,expected):
        js('command(arguments[0]);',[text]);wait(lambda:js('return shellText.includes(arguments[0])',[expected]),30)
    try:
        call('/session/'+session+'/timeouts',{'script':60000});call('/session/'+session+'/url',{'url':url});wait(ready,120);network('anonymous')
        js('window.originalVM=fixtureVM;window.originalFS=fixtureVM.fs9p;window.originalSocket=adapter.socket;window.fixtureName="net_"+crypto.randomUUID().replaceAll("-","").slice(0,12);window.fixturePassword=crypto.randomUUID()+crypto.randomUUID();')
        command('export NET_KEEP=shell_alive; echo shared_file_alive > /home/guest/network-keep.txt; printf "\\nNET_INITIAL_OK\\n"\r','\nNET_INITIAL_OK\n')
        command('printf "\\nNET_MAC="; cat /sys/class/net/eth0/address; printf "\\nNET_MAC_END\\n"\r','\nNET_MAC_END\n')
        assert js('const m=/\\nNET_MAC=([0-9a-f:]+)\\n/.exec(shellText);if(!m)return false;window.fixtureMAC=Uint8Array.from(m[1].split(":"),v=>parseInt(v,16));return fixtureMAC.length===6;')
        js('arp()');wait(lambda:js('return receivedPackets.some(p=>p.type===2054)'),10)
        command('printf "\\nNET_RX="; cat /sys/class/net/eth0/statistics/rx_packets; printf "\\nNET_RX_END\\n"\r','\nNET_RX_END\n')
        assert js('const m=/\\nNET_RX=([0-9]+)\\n/.exec(shellText);return m&&Number(m[1])>0;')
        before=js('return receivedPackets.length')
        assert task('return await account("auth",fixtureName,fixturePassword)==="registered";');network('registered')
        command('printf "\\nNET_REGISTERED=%s:" "$NET_KEEP"; cat /home/guest/network-keep.txt\r','\nNET_REGISTERED=shell_alive:shared_file_alive')
        assert task('return new TextDecoder().decode(await fixtureVM.read_file("/network-keep.txt"))==="shared_file_alive\\n";')
        assert js('return fixtureVM===originalVM&&fixtureVM.fs9p===originalFS&&adapter.socket===originalSocket')
        task('await account("anonymous");return true;');network('anonymous')
        command('printf "\\nNET_ANON=%s:" "$NET_KEEP"; cat /home/guest/network-keep.txt\r','\nNET_ANON=shell_alive:shared_file_alive')
        task('await account("auth",fixtureName,fixturePassword);return true;');network('registered')
        # Delete only the owned browser cookie, then force an actual reconnection.
        call('/session/'+session+'/cookie/codi_guest_relay',method='DELETE')
        js('window.beforeReconnectSocket=adapter.socket;adapter.socket.close();')
        wait(lambda:js('return adapter.socket&&adapter.socket!==beforeReconnectSocket&&adapter.socket.readyState===WebSocket.OPEN'),30);network('registered')
        command('printf "\\nNET_RECONNECT=%s:" "$NET_KEEP"; cat /home/guest/network-keep.txt\r','\nNET_RECONNECT=shell_alive:shared_file_alive')
        js('arp()');wait(lambda:js('return receivedPackets.length>arguments[0]',[before]),10)
        assert js('return fixtureVM===originalVM&&fixtureVM.fs9p===originalFS&&receivedPackets.every(p=>p.length>=14&&p.length<=1518)&&!document.cookie.includes("codi_guest_relay")')
        # A response begun under one identity may not promote after switching.
        task('window.realFetch=fetch;window.delayedGrant=null;window.fetch=async(...args)=>{const response=await realFetch(...args);if(String(args[0]).endsWith("/guest-network/authorize"))return new Promise(resolve=>{delayedGrant=()=>resolve(response);});return response;};adapter.reset();adapter.nextAuth=0;adapter.syncSession();return true;')
        wait(lambda:js('return typeof delayedGrant==="function"'),15)
        task('await account("anonymous");delayedGrant();window.fetch=realFetch;return true;');network('anonymous');time.sleep(.3)
        assert js('return adapter.mode==="anonymous"&&currentIdentity.public.kind==="anonymous"&&fixtureVM===originalVM')
        command('printf "\\nNET_LATE=%s:" "$NET_KEEP"; cat /home/guest/network-keep.txt\r','\nNET_LATE=shell_alive:shared_file_alive')
        return {'url':url,'actualV86LinuxBoot':True,'realHTTPWebCryptoGrants':True,'actualQEMUARP':True,'actualLinuxNICReceivesReply':True,'samePublicSocketAcrossAccountSwitch':True,'linuxShellAndSharedFilePreserved':True,'cookieRenewedWithoutVMReload':True,'registeredReconnectWorks':True,'staleIdentityResponseDiscarded':True,'controlTextNeverDeliveredToNIC':True,'hostTransportCookieHttpOnly':True}
    finally:
        try:task('adapter?.destroy();await fixtureVM?.destroy();return true;')
        except Exception:pass
        call('/session/'+session,method='DELETE')

async def main():
    witnesses=[]
    for base in ['', '/hidden']:
        fixture=Fixture(base)
        try:
            await fixture.start();witness=await asyncio.to_thread(browser,fixture.origin+base+'/');witness['cookieIndexGets']=fixture.cookie_gets;assert fixture.cookie_gets>=3;witnesses.append(witness)
            print(json.dumps({'phase':'Chrome/v86 adapter passed','basePath':base}),flush=True)
        finally:await fixture.close()
    return witnesses

if __name__=='__main__':
    result={'status':'FAIL','scope':__doc__}
    try:result.update(status='PASS',witnesses=asyncio.run(main()))
    finally:
        names=['guest_service/client.mjs','guest_service/coordinator.py','guest_service/worker.py','guest_service/frames.py','guest_service/egress.py','guest_service/authorization.py','origin_service/guest_authority.py','scripts/guest-client-browser-check.py']
        result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names};output=ROOT/'.build/checks/guest-client-browser-result.json'
        if output.exists():output.rename(output.with_name('guest-client-browser-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
