#!/usr/bin/env python3
"""Exercise candidate Worker client with real signed local guest relay and QEMU."""
import asyncio,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('worker_network_fixture',ROOT/'scripts/guest-worker-network-check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.fixture.SCRIPT=r'''
import {GuestNetworkAdapter} from './guest-access/client.mjs';
import {beginSession,logoutSession} from './network/identity.mjs';
import {GuestWorkerClient} from './assets/desktop/guest-worker-client.mjs';
window.fixtureFatal=null;window.fixtureReady=false;window.shellText='';window.receivedPackets=[];window.sentPackets=[];window.networkStates=[];window.workerReply=undefined;
try{
 const config=await(await fetch('config.json')).json(),image=await(await fetch('assets/terminal/v2/image.json')).json();window.currentIdentity=await beginSession(config,'anonymous');
 const url=name=>new URL(name,document.baseURI).href;
 const vm=window.fixtureVM=new GuestWorkerClient(url('assets/desktop/guest-worker-runtime.js'),{onFatal:e=>fixtureFatal=e.message});
 const send=vm.bus.send,register=vm.bus.register;vm.bus.send=(name,frame)=>{if(name==='net0-receive')receivedPackets.push(frame.length);send(name,frame);};vm.bus.register=(name,fn,owner)=>register(name,frame=>{sentPackets.push(frame.length);fn.call(owner,frame);},null);
 window.adapter=new GuestNetworkAdapter(vm,config,{getSession:()=>currentIdentity,onStatus:value=>networkStates.push(value)});
 let line='';const decoder=new TextDecoder();vm.add_listener('serial0-output-byte',byte=>{const ch=String.fromCharCode(byte);line+=ch;if(ch!=='\n')return;const text=line.replace(/\r?\n$/,'');line='';if(text==='\x1eCDMUX R 2'){fixtureReady=true;vm.serial0_send('\x1eCDMUX O 2 80 24\n');}else{const match=/^\x1eCDMUX D 2 ([0-9a-f]*)$/.exec(text);if(match){const bytes=Uint8Array.from(match[1].match(/../g)||[],v=>parseInt(v,16));shellText+=decoder.decode(bytes,{stream:true}).replace(/\r/g,'');vm.serial0_send('\x1eCDMUX A 2 '+bytes.length+'\n');}}});
 vm.add_listener('download-error',event=>fixtureFatal='Download: '+event.file_name);
 window.worker={postMessage:data=>{if(data.type==='read')vm.read_file(data.path).then(bytes=>workerReply=new TextDecoder().decode(bytes),e=>fixtureFatal=e.message);else if(data.type==='stop')vm.destroy().then(()=>workerReply=true);}};
 window.command=text=>vm.serial0_send('\x1eCDMUX I 2 '+[...new TextEncoder().encode(text)].map(b=>b.toString(16).padStart(2,'0')).join('')+'\n');
 window.account=async(kind,name='',password='')=>{const old=currentIdentity;currentIdentity=await beginSession(config,kind,name,password);adapter.syncSession();await logoutSession(config,old).catch(()=>{});return currentIdentity.public.kind;};
 window.arp=()=>{const bytes=new Uint8Array([255,255,255,255,255,255,2,34,21,0,0,1,8,6,0,1,8,0,6,4,0,1,2,34,21,0,0,1,10,86,0,2,0,0,0,0,0,0,10,86,0,1]);bytes.set(fixtureMAC,6);bytes.set(fixtureMAC,22);adapter.send(bytes);};
 vm.start({wasm_path:url('.build/v86/v86.wasm'),memory_size:256*1024*1024,bios:{url:url('.build/v86/seabios.bin')},vga_bios:{url:url('.build/v86/vgabios.bin')},bzimage:{url:url('.build/v86/vmlinuz')},initrd:{url:url(image.path)},net_device:{type:'virtio'},filesystem:{},cmdline:'console=ttyS0,115200n8 rdinit=/init panic=-1 quiet loglevel=0 guest_net=1',autostart:true,disable_keyboard:true,disable_mouse:true,disable_speaker:true});
}catch(error){fixtureFatal=error.stack;}
'''
if __name__=='__main__':asyncio.run(m.main())
