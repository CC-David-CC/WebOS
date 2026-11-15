#!/usr/bin/env python3
"""Test worker Ethernet bridge with the real local signed guest relay.

Actual Chrome, v86, Linux, signed account grants, relay and QEMU ARP; no live
deployment or external ICMP/Internet is claimed. Test-owned state is removed.
"""
import asyncio,importlib.util,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('guest_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from aiohttp import web
fixture.PAGE=b'''<!doctype html><meta charset="utf-8"><title>Worker relay fixture</title><script type="module" src="fixture.mjs"></script>'''
fixture.SCRIPT=r'''
import {GuestNetworkAdapter} from './guest-access/client.mjs';
import {beginSession,logoutSession} from './network/identity.mjs';
window.fixtureFatal=null;window.fixtureReady=false;window.shellText='';window.receivedPackets=[];window.sentPackets=[];window.networkStates=[];window.workerTraces=[];window.bootOutput='';window.workerReply=undefined;
try{
 const config=await(await fetch('config.json')).json();window.currentIdentity=await beginSession(config,'anonymous');
 const listeners=new Map(),bus={register:(name,fn,owner)=>listeners.set(name,fn.bind(owner)),send:(name,frame)=>{if(name==='net0-receive'){receivedPackets.push(frame.length);worker.postMessage({type:'frame',frame});}}};
 window.worker=new Worker('fixture-worker.js');window.adapter=new GuestNetworkAdapter({bus},config,{getSession:()=>currentIdentity,onStatus:value=>networkStates.push(value)});
 let line='';const decoder=new TextDecoder();
 worker.onerror=e=>fixtureFatal=e.message;
 worker.onmessage=({data})=>{if(data.type==='trace'){workerTraces.push(data.message);return;}if(data.type==='fatal'){fixtureFatal=data.message;return;}if(data.type==='frame'){sentPackets.push(data.frame.length);listeners.get('net0-send')?.(data.frame);return;}if(data.type==='reply'){window.workerReply=data.value;return;}if(data.type!=='serial')return;bootOutput=(bootOutput+data.text).slice(-4096);
  for(const ch of data.text){line+=ch;if(ch==='\n'){const text=line.replace(/\r?\n$/,'');line='';if(text==='\x1eCDMUX R 2'){fixtureReady=true;worker.postMessage({type:'serial',text:'\x1eCDMUX O 2 80 24\n'});}else{const m=/^\x1eCDMUX D 2 ([0-9a-f]*)$/.exec(text);if(m){const bytes=Uint8Array.from(m[1].match(/../g)||[],v=>parseInt(v,16));shellText+=decoder.decode(bytes,{stream:true}).replace(/\r/g,'');worker.postMessage({type:'serial',text:'\x1eCDMUX A 2 '+bytes.length+'\n'});}}}}
 };
 window.command=text=>worker.postMessage({type:'serial',text:'\x1eCDMUX I 2 '+[...new TextEncoder().encode(text)].map(b=>b.toString(16).padStart(2,'0')).join('')+'\n'});
 window.account=async(kind,name='',password='')=>{const old=currentIdentity;currentIdentity=await beginSession(config,kind,name,password);adapter.syncSession();await logoutSession(config,old).catch(()=>{});return currentIdentity.public.kind;};
 window.arp=()=>{const bytes=new Uint8Array([255,255,255,255,255,255,2,34,21,0,0,1,8,6,0,1,8,0,6,4,0,1,2,34,21,0,0,1,10,86,0,2,0,0,0,0,0,0,10,86,0,1]);bytes.set(fixtureMAC,6);bytes.set(fixtureMAC,22);adapter.send(bytes);};
 worker.postMessage({type:'start'});
}catch(error){fixtureFatal=error.stack;}
'''
class WorkerFixture(fixture.Fixture):
 async def proxy(self,request):
  if request.path==self.base+'/fixture-worker.js':return web.Response(body=(ROOT/'scripts/fixtures/guest-worker-network.js').read_bytes(),content_type='text/javascript',headers={'Cross-Origin-Embedder-Policy':'require-corp'})
  return await super().proxy(request)
def browser(url):
 call,wait=fixture.call,fixture.wait;sid=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
 def js(code,args=[]):return call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
 def task(code,args=[]):
  r=call('/session/'+sid+'/execute/async',{'script':'const p=Array.from(arguments),done=p.pop();(async()=>{'+code+'})().then(x=>done({ok:true,value:x}),e=>done({ok:false,error:String(e)}));','args':args});assert r['ok'],r;return r['value']
 def ready():
  fatal=js('return fixtureFatal;');assert not fatal,fatal
  return js('return fixtureReady&&shellText.includes("$");')
 def command(text,expected):js('command(arguments[0]);',[text]);wait(lambda:js('return shellText.includes(arguments[0]);',[expected]),45)
 try:
  call('/session/'+sid+'/timeouts',{'script':60000});call('/session/'+sid+'/url',{'url':url});wait(ready,120);wait(lambda:js('return adapter.mode==="anonymous";'),30)
  command('export NET_KEEP=worker_shell; printf shared_worker > /home/guest/network-keep.txt; printf "\\nNET_INITIAL_OK\\n"\r','\nNET_INITIAL_OK\n')
  command('printf "\\nNET_MAC="; cat /sys/class/net/eth0/address; printf "\\nNET_MAC_END\\n"\r','\nNET_MAC_END\n')
  assert js('const m=/\\nNET_MAC=([0-9a-f:]+)\\n/.exec(shellText);if(!m)return false;window.fixtureMAC=Uint8Array.from(m[1].split(":"),v=>parseInt(v,16));return fixtureMAC.length===6;')
  js('arp();');wait(lambda:js('return receivedPackets.length>0;'),20)
  command('printf "\\nNET_RX="; cat /sys/class/net/eth0/statistics/rx_packets; printf "\\nNET_RX_END\\n"\r','\nNET_RX_END\n')
  assert js('const m=/\\nNET_RX=([0-9]+)\\n/.exec(shellText);return m&&Number(m[1])>0;')
  name='wrk'+__import__('secrets').token_hex(6);password=__import__('secrets').token_hex(16)
  assert task('return await account("auth",p[0],p[1]);',[name,password])=='registered';wait(lambda:js('return adapter.mode==="registered";'),30)
  command('printf "\\nNET_REGISTERED=%s:" "$NET_KEEP"; cat /home/guest/network-keep.txt\r','\nNET_REGISTERED=worker_shell:shared_worker')
  assert task('worker.postMessage({type:"read",id:1,path:"/network-keep.txt"});while(workerReply===undefined)await new Promise(r=>setTimeout(r,20));return workerReply;')=='shared_worker'
  js('window.beforeSocket=adapter.socket;window.beforePackets=receivedPackets.length;adapter.socket.close();')
  wait(lambda:js('return adapter.socket&&adapter.socket!==beforeSocket&&adapter.socket.readyState===WebSocket.OPEN&&adapter.mode==="registered";'),45)
  js('arp();');wait(lambda:js('return receivedPackets.length>beforePackets;'),20)
  command('printf "\\nNET_RECONNECT=%s\\n" "$NET_KEEP"\r','\nNET_RECONNECT=worker_shell')
  assert task('return await account("anonymous");')=='anonymous';wait(lambda:js('return adapter.mode==="anonymous";'),30)
  command('printf "\\nNET_RETAINED=%s\\n" "$NET_KEEP"\r','\nNET_RETAINED=worker_shell')
  assert js('return receivedPackets.every(n=>n>=14&&n<=1518)&&sentPackets.every(n=>n>=14&&n<=1518);')
  return {'workerLinux':True,'shellAndFileSurviveAccountChanges':True,'actualSignedRegisteredGrant':True,'realRelayARP':True,'linuxReceivedPackets':True,'registeredRelayReconnect':True,'guestFrameBounds':True}
 finally:
  try:task('adapter.destroy();worker.postMessage({type:"stop",id:2});while(workerReply!==true)await new Promise(r=>setTimeout(r,20));return true;')
  except Exception:pass
  call('/session/'+sid,method='DELETE')
async def main():
 for base in ('','/hidden'):
  instance=WorkerFixture(base)
  try:
   await instance.start();result=await asyncio.to_thread(browser,instance.origin+base+'/');print(json.dumps({'status':'PASS','base':base,'result':result}),flush=True)
  finally:await instance.close()
if __name__=='__main__':asyncio.run(main())
