#!/usr/bin/env python3
"""Real Chrome SDK atomic snapshot/tail reads and signed adversarial responses.

Owned loopback HTTP/SQLite issuer, real WebCrypto/IndexedDB; no v86 or WAN.
Simulated authority rotation is verified with explicit verifier time, without
changing browser/server clock for the actual live SDK flow. Not8k acceptance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);return v
support=module('atomic_browser_support',ROOT/'scripts/hosted-peer-check.py');fixture,driver=support.fixture,support.driver

def run():
    sessions=[];checks=[];f=None;other=None
    sources=[Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted((ROOT/'network').glob('*.mjs')),*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserInstances':1,'actualV86Desktops':0,'wholeGoalComplete':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        v=driver.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
    def snap(node):return js('return client.snapshot(arguments[0]);',[node])
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    try:
        with tempfile.TemporaryDirectory(prefix='codi-atomic-browser-') as directory:
            folder=Path(directory);f=fixture.Fixture(folder);f.clock.realtime=True;owner=fixture.Actor(f,'atomic_browser_owner')
            created=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Browser atomic sync'});node=fixture.jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id'];grant=created['grant']
            for seq in range(1,41):owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,seq,'Saved '+str(seq))})
            public=folder/'public';shutil.copytree(ROOT/'network',public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
            (public/'loader.mjs').write_text('import("./fixture.mjs").catch(e=>window.fixtureFatal=e.stack);');(public/'index.html').write_text('<!doctype html><title>Atomic sync browser</title><script type="module" src="/loader.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'};(public/'fixture-config.json').write_text(json.dumps(config))
            sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(sid);driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':f.origin+'/?window=1&sync=1'})
            driver.wait(lambda:js('if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'),30)
            js("window.atomicPackets=[];window.replaceAtomic=null;const original=fetch;window.fetch=async(u,o)=>{const r=await original(u,o);let op;try{op=JSON.parse(JSON.parse(o?.body||'{}').request||'{}').operation;}catch{}if(op==='sync'&&r.ok){const p=await r.clone().json();atomicPackets.push(structuredClone(p));if(replaceAtomic)return new Response(JSON.stringify(replaceAtomic),{status:200,headers:{'Content-Type':'application/json'}});}return r;};")
            task('await client.open(params[0]);return true;',[node]);first=snap(node)
            ops=js("return httpOperations.filter(v=>v.path==='/rooms/use').map(v=>v.operation);")
            check('cold anonymous SDK reads one authorized sync operation and verifies bounded checkpoint state',ops==['sync'] and first['selected']['count']==40 and first['selected']['omitted']==8 and first['selected']['format']=='snapshot' and first['delivery']['serverAtomicLoads']==1)
            owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,41,'One atomic tail')});task('await client.open(params[0]);return true;',[node]);second=snap(node)
            check('next SDK refresh uses one atomic operation and merges its single receipt into the retained window',js("return httpOperations.filter(v=>v.path==='/rooms/use').map(v=>v.operation).join(',');")=='sync,sync' and second['selected']['count']==41 and second['selected']['omitted']==9 and second['selected']['format']=='tail' and len(second['selected']['records'])==32 and second['delivery']['serverAtomicLoads']==2)
            js('window.replaceAtomic=structuredClone(atomicPackets[0]);')
            rejected=task("try{await client.open(params[0]);return false;}catch(e){return e.message.includes('rollback');}",[node])
            check('a genuinely signed older atomic response cannot roll back the saved cursor',rejected and snap(node)['selected']['count']==41 and snap(node)['delivery']['serverAtomicLoads']==2)
            js("window.replaceAtomic=structuredClone(atomicPackets[1]);const parts=replaceAtomic.bootstrap.head.split('.'),p=JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')));p.exp+=60;parts[1]=btoa(JSON.stringify(p)).replace(/=/g,'').replace(/\\+/g,'-').replace(/\\//g,'_');replaceAtomic.bootstrap.head=replaceAtomic.state.head=parts.join('.');")
            rejected=task('try{await client.open(params[0]);return false;}catch{return true;}',[node])
            check('forged authority freshness is refused and leaves accepted history unchanged',rejected and snap(node)['selected']['count']==41)
            other_room=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Different requested scope'});other_node=fixture.jose.inspect(other_room['descriptor'],fixture.POLICY_TYPE)[1]['node_id']
            js('window.replaceAtomic=structuredClone(atomicPackets[0]);')
            wrong_scope=task("try{await client.open(params[0]);return false;}catch(e){return e.message.includes('another chat');}",[other_node])
            check('a valid foreign cold checkpoint cannot satisfy the requested room or create a saved bookmark',wrong_scope and not snap(other_node)['selected']['stored'] and snap(node)['selected']['count']==41)
            js('window.replaceAtomic=null;')
            verifier=task("const v=await import('/network/hosted-room-authority.mjs');const first=await v.verifyHostedSync(atomicPackets[0],config.hostedRooms.controllerKey,config.identity),floor=first.room.floor;let n=0;for(const change of [p=>p.bootstrap.head=atomicPackets[0].bootstrap.head,p=>p.bootstrap.grant='unexpected',p=>p.state.entries.push(...Array(33).fill(p.state.entries[0]))]){const p=structuredClone(atomicPackets[1]);change(p);try{await v.verifyHostedSync(p,config.hostedRooms.controllerKey,config.identity,{floor,tailRequested:true});}catch{n++;}}try{await v.verifyHostedSync(atomicPackets[1],config.hostedRooms.controllerKey,config.identity,{floor,tailRequested:false});}catch{n++;}return n;")
            check('browser verifier rejects inconsistent heads, implicit grants, oversized and unrequested tails',verifier==4)
            continuity_folder=folder/'continuity';continuity_folder.mkdir();other=fixture.Fixture(continuity_folder);other.clock.realtime=False;writer=fixture.Actor(other,'continuity_owner');reader=fixture.Actor(other)
            boot=writer.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Authority continuity'});continuity_node=fixture.jose.inspect(boot['descriptor'],fixture.POLICY_TYPE)[1]['node_id']
            args={'node_id':continuity_node,'after':None,'lease':None,'tail':False};start=reader.operation('sync',args);h=fixture.jose.inspect(start['bootstrap']['head'],fixture.HEAD_TYPE)[1];floor={'nodeId':continuity_node,'descriptorHash':fixture.token_id(boot['descriptor'],fixture.POLICY_TYPE),'leaseRevision':1,'leaseHash':fixture.token_id(boot['lease'],fixture.LEASE_TYPE),'count':0,'hash':h['hash'],'permissionRevision':h['permission_revision']}
            args.update(after={'index':0,'hash':h['hash']},lease={'revision':1,'hash':floor['leaseHash']})
            for _ in range(2):other.clock.value+=151;reader.operation('sync',args)
            bridge=reader.operation('sync',args);bad=fixture.jose.inspect(bridge['continuity']['proof'],fixture.LEASE_BRIDGE_TYPE)[1];bad['node_id']=fixture.secrets.token_urlsafe(32);wrong=fixture.jose.sign(bad,other.store.key,fixture.LEASE_BRIDGE_TYPE)
            proof=task("const d=params[0],v=await import('/network/hosted-room-authority.mjs'),o={floor:d.floor,now:d.now};await v.verifyHostedSync(d.packet,d.key,d.policy,o);let refused=0;for(const kind of ['missing','foreign']){const p=structuredClone(d.packet);p.continuity=kind==='missing'?null:{proof:d.wrong};try{await v.verifyHostedSync(p,d.key,d.policy,o);}catch{refused++;}}return refused;",[{'packet':bridge,'key':other.store.public,'policy':other.policy,'floor':floor,'now':int(other.clock()),'wrong':wrong}])
            check('real browser verifies multi-revision continuity and rejects missing or controller-signed foreign bridges',proof==2)
            task('await client.open(params[0]);return true;',[node]);check('normal authorized refresh remains usable after signed adversarial responses',snap(node)['selected']['count']==41 and not snap(node)['selected']['error'])
            budget=task("await client.close();pool.close();const {sessionBudget}=await import('/network/resource-budget.mjs');return sessionBudget(currentSession).snapshot();")
            check('all atomic RPC, cryptographic, queued-byte, connection and metadata leases release on close',not any(v for k,v in budget.items() if k!='closed'))
            result.update(status='PASS',resourceCleanup=budget,normalReadOperations=['sync','sync'])
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        for s in sessions:driver.call('/session/'+s,method='DELETE')
        if other:other.close()
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
