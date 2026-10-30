#!/usr/bin/env python3
"""Real Chrome client config validation; errors cannot select legacy transport.

Root and hidden mounts use actual local issuer/Unix/QEMU/v86 fixtures. Only
the configuration response is substituted for the malformed-response cases.
Actual installed off/on compatibility is a separate VM receipt.
"""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('protocol_client_fixture',ROOT/'scripts/guest-client-browser-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
call,wait=fixture.call,fixture.wait

def browser(url,base):
    session=call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
    def js(script,args=[]):return call('/session/'+session+'/execute/sync',{'script':script,'args':args})
    def task(script):
        value=call('/session/'+session+'/execute/async',{'script':'const done=arguments[arguments.length-1];(async()=>{'+script+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':[]});assert value['ok'],value;return value['value']
    try:
        call('/session/'+session+'/timeouts',{'script':60000});call('/session/'+session+'/url',{'url':url})
        wait(lambda:js('return fixtureReady&&adapter?.socket?.readyState===WebSocket.OPEN&&guestFiles.ready'),120)
        return task(r'''
const results=[],originalVM=fixtureVM,originalFS=fixtureVM.fs9p,originalFetch=fetch,config=fixtureConfig;
const copy=()=>JSON.parse(JSON.stringify(config));
const legacy=()=>{const v=copy();v.guestNetwork={relayPath:adapter.path,egress:'relay-host',relayRevision:'1'.repeat(64),previewPolicy:{version:'bounded-preview/1'}};return v;};
async function test(name,value,expected,status=200){
 const raw=typeof value==='string'?value:JSON.stringify(value);let options;
 window.fetch=async(path,opts)=>{if(path!==adapter.base+'/config.json')throw Error('Unexpected config URL');options=opts;return new Response(raw,{status,headers:{'Content-Type':'application/json'}});};
 try{
  let answer,error;try{answer=await adapter.currentProtocol(new AbortController().signal);}catch(e){error=e;}
  if(expected==='reject'){if(!error)throw Error('Invalid configuration accepted: '+name);}
  else if(error||answer!==expected)throw Error('Wrong protocol '+name+': '+error?.message);
  if(options.credentials!=='same-origin'||options.mode!=='same-origin'||options.redirect!=='error'||options.cache!=='no-store')throw Error('Unbounded or cross-origin config fetch');
  results.push({name,rejected:!!error,controlled:answer??null});
 }finally{window.fetch=originalFetch;}
}
await test('matching typed protocol',copy(),true);
const reordered=copy();reordered.identity=Object.fromEntries(Object.entries(reordered.identity).reverse());await test('issuer property order is immaterial',reordered,true);
await test('explicit known binary protocol',legacy(),false);
for(const [name,change] of [
 ['missing guest metadata',v=>delete v.guestNetwork],
 ['unknown relay path',v=>v.guestNetwork.relayPath='/other'],
 ['null authorization is not disabled',v=>v.guestNetwork.authorization=null],
 ['changed policy digest',v=>v.guestNetwork.authorization.policySHA256='0'.repeat(64)],
 ['changed SDK path',v=>v.guestNetwork.authorization.clientPath='/other.mjs'],
 ['unknown auth version',v=>v.guestNetwork.authorization.version='unknown/1'],
 ['extra auth fields',v=>v.guestNetwork.authorization.extra=true],
 ['changed origin',v=>v.identity.issuer='https://other.invalid'],
 ['changed API mount',v=>v.identity.apiBase='/other/api/v1'],
 ['changed audience',v=>v.identity.audience='other'],
 ['changed authority class',v=>v.identity.authorityClass='official'],
 ['changed issuer key ID',v=>v.identity.authorityKeys[0].kid='other'],
 ['changed issuer public key',v=>v.identity.authorityKeys[0].jwk.x='A'.repeat(43)],
 ['private issuer key field',v=>v.identity.authorityKeys[0].jwk.d='forbidden'],
 ['additional authority key',v=>v.identity.authorityKeys.push(v.identity.authorityKeys[0])],
 ['extra issuer fields',v=>v.identity.extra=true]
]){const v=copy();change(v);await test(name,v,'reject');}
for(const [name,change] of [
 ['unknown binary version',v=>v.guestNetwork.previewPolicy.version='unknown/1'],
 ['missing binary version',v=>delete v.guestNetwork.previewPolicy],
 ['missing binary revision',v=>delete v.guestNetwork.relayRevision],
 ['coercible binary revision refused',v=>v.guestNetwork.relayRevision=[v.guestNetwork.relayRevision]],
 ['unknown binary egress',v=>v.guestNetwork.egress='direct']
]){const v=legacy();change(v);await test(name,v,'reject');}
await test('HTTP failure never downgrades',{},'reject',503);
await test('redirect response never downgrades',{},'reject',302);
await test('oversized configuration refused','x'.repeat(65537),'reject');
const duplicate=JSON.stringify(copy()).replace(/}$/,',"guestNetwork":'+JSON.stringify(legacy().guestNetwork)+'}');await test('duplicate protocol fields refused',duplicate,'reject');
await test('deeply nested configuration refused','{"nested":'+ '['.repeat(26)+'0'+']'.repeat(26)+'}','reject');
const sent=[],socket=adapter.socket,send=socket.send.bind(socket),kind=currentIdentity.public.kind;
try{
 socket.send=value=>{if(typeof value==='string')sent.push(value);else send(value);};adapter.controlled=false;currentIdentity.public.kind='registered';adapter.reset();adapter.syncSession();adapter.control({type:'codi-guest-network-begin/1'});
 if(sent.length||adapter.authRequested||adapter.mode==='registered')throw Error('Binary mode emitted control or assumed registered privilege');
 results.push({name:'binary mode never emits auth/reset controls or assumes registered privilege',rejected:false,controlled:false});
}finally{currentIdentity.public.kind=kind;adapter.controlled=true;socket.send=send;adapter.reset();}
const oldMAC=adapter.mac,announcements=[];
try{
 socket.send=value=>announcements.push(new Uint8Array(value));adapter.mac=null;adapter.announceLink(socket);
 if(announcements.length)throw Error('Unknown MAC emitted an announcement');
 results.push({name:'unknown Linux MAC emits no fabricated link announcement',rejected:false,controlled:true});
 adapter.mac=Uint8Array.from([2,34,21,0,0,1]);adapter.announceLink(socket);
 if(announcements.length!==2||announcements.some((v,i)=>v.length!==42||v[12]!==8||v[13]!==6||v[20]!==0||v[21]!==1||v.slice(6,12).some((n,j)=>n!==adapter.mac[j])||v.slice(22,28).some((n,j)=>n!==adapter.mac[j])||v.slice(28,32).join('.')!=='10.86.0.2'||v.slice(38,42).join('.')!==('10.86.0.'+[1,3][i])))throw Error('Unbounded or incorrectly scoped link announcement');
 results.push({name:'link announcement contains only bounded gateway/DNS ARP requests',rejected:false,controlled:true});
}finally{adapter.mac=oldMAC;socket.send=send;}
if(fixtureVM!==originalVM||fixtureVM.fs9p!==originalFS)throw Error('Configuration validation replaced Linux');
return {checks:results,linuxInstanceRetained:true,basePath:adapter.base};
''')
    finally:
        try:task('adapter?.destroy();await fixtureVM?.destroy();return true;')
        except Exception:pass
        call('/session/'+session,method='DELETE')

async def main():
    witnesses=[]
    for base in ['', '/hidden']:
        current=fixture.Fixture(base)
        try:
            await current.start();witnesses.append(await asyncio.to_thread(browser,current.origin+base+'/',base))
        finally:await current.close()
    return witnesses
if __name__=='__main__':
    names=['guest_service/client.mjs','network/crypto.mjs','network/strict-json.mjs','scripts/guest-protocol-browser-check.py','scripts/guest-client-browser-check.py'];hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names};value={'status':'FAIL','scope':__doc__,'sha256':hashes}
    try:
        value.update(status='PASS',witnesses=asyncio.run(main()));assert hashes=={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    finally:
        out=ROOT/'.build/checks/guest-protocol-browser-result.json'
        if out.exists():out.rename(out.with_name('guest-protocol-browser-before-'+str(time.time_ns())+'.json'))
        out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
