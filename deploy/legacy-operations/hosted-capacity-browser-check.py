#!/usr/bin/env python3
"""Real Chrome capacity retry, fresh authorization, P2P bypass and cancellation.

Owned HTTP/SQLite/signing/IndexedDB/RTC fixture. Transient empty/plain503 and
429 are injected at the transport boundary, never accepted state or signatures.
No native timing/capacity override, public deployment, v86 or8k claim.
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
spec=importlib.util.spec_from_file_location('capacity_browser_support',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support);fixture,driver=support.fixture,support.driver

def run(network_source):
    sessions=[];checks=[];f=None;sources=[Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted(network_source.glob('*.mjs'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserInstances':2,'actualV86Desktops':0,'wholeGoalComplete':False}
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        v=driver.call('/session/'+s+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
    def wait(fn,seconds=15):return driver.wait(fn,seconds)
    def snap(s,node=None):return js(s,'return client.snapshot(arguments[0]);',[node])
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    try:
        with tempfile.TemporaryDirectory(prefix='codi-capacity-browser-') as directory:
            folder=Path(directory);f=fixture.Fixture(folder);f.clock.realtime=True;owner=fixture.Actor(f,'capacity_owner');rooms=[]
            for n in range(3):
                created=owner.operation('create',{'request_id':fixture.secrets.token_urlsafe(32),'label':'Capacity case '+str(n)});node=fixture.jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id'];owner.operation('accept',{'node_id':node,'grant':created['grant'],'event':owner.origin(created['grant'],1,'Original '+str(n))});rooms.append((node,created['grant']))
            public=folder/'public';shutil.copytree(network_source,public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs');(public/'loader.mjs').write_text('import("./fixture.mjs").catch(e=>window.fixtureFatal=e.stack);');(public/'index.html').write_text('<!doctype html><title>Capacity retry</title><script type="module" src="/loader.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'};(public/'fixture-config.json').write_text(json.dumps(config))
            for suffix in ['?owner=1&window=1&sync=1','?window=1&sync=1']:
                s=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s);driver.call('/session/'+s+'/timeouts',{'script':120000});driver.call('/session/'+s+'/url',{'url':f.origin+'/'+suffix});wait(lambda:js(s,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
            a,b=sessions
            js(a,"""window.readFailures=2;window.writeFailures=false;window.permanent=false;window.malformed=false;window.forever=false;window.readAttempts=0;window.writeAttempts=0;window.nonces=[];window.ownedTimers=new Map();window.transportMode=null;window.transportFailures=0;window.resetWrite=false;
const timeout=setTimeout,cancel=clearTimeout;window.setTimeout=(fn,delay,...args)=>{const stack=new Error().stack,kind=stack.includes('#capacityGate')?'capacity':delay===90000?'read-deadline':delay===15000?'http':null;let id;id=timeout(()=>{ownedTimers.delete(id);fn(...args);},delay);if(kind)ownedTimers.set(id,{kind,delay});return id;};window.clearTimeout=id=>{ownedTimers.delete(id);return cancel(id);};
const native=fetch;window.fetch=(u,o)=>{let body,op;try{body=JSON.parse(o?.body||'{}');op=JSON.parse(body.request||'{}').operation;}catch{}
if(op==='sync'){readAttempts++;const p=JSON.parse(atob(body.proof.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));nonces.push(p.nonce);
if(transportFailures>0){transportFailures--;
if(transportMode==='fetch')return native(u,o).then(()=>{throw new TypeError('Failed to fetch');});
if(transportMode==='body')return native(u,o).then(()=>{let sent=false;return new Response(new ReadableStream({pull(c){if(!sent){sent=true;c.enqueue(new TextEncoder().encode('{'));}else c.error(new TypeError('Connection reset'));}}),{status:200});});
if(transportMode==='utf8')return native(u,o).then(()=>new Response(new Uint8Array([255]),{status:200}));
if(transportMode==='timeout'||transportMode==='abort')return native(u,o).then(()=>new Promise((resolve,reject)=>{window.transportStarted=true;o.signal.addEventListener('abort',()=>reject(o.signal.reason),{once:true});}));}
if(readFailures>0||forever){readFailures--;return Promise.resolve(new Response('',{status:503,headers:{'Retry-After':'1'}}));}
if(permanent)return Promise.resolve(new Response(JSON.stringify({error:'Logical history capacity reached'}),{status:429}));
if(malformed)return Promise.resolve(new Response('not JSON',{status:200}));}
if(op==='create'&&resetWrite){writeAttempts++;return native(u,o).then(()=>{throw new TypeError('Failed to fetch');});}
if(op==='create'&&writeFailures){writeAttempts++;return Promise.resolve(new Response('Server busy',{status:503,headers:{'Retry-After':'60'}}));}
return native(u,o);};""")
            js(a,"window.readResult=null;window.readJob=Promise.all(arguments[0].map(node=>client.open(node)));readJob.then(()=>readResult={ok:true},e=>readResult={ok:false,error:e.message});",[[rooms[0][0],rooms[1][0]]])
            wait(lambda:js(a,'return readFailures===0&&client.snapshot().delivery.serverRetryAfterSeconds>0;'))
            state=task(a,"const {sessionBudget}=await import('/network/resource-budget.mjs');return {budget:sessionBudget(currentSession).snapshot(),timers:[...ownedTimers.values()]};")
            check('concurrent transient failures release active RPC work and share one capacity timer',state['budget']['repairJobs']==0 and state['budget']['crypto']==0 and state['budget']['queuedBytes']==0 and sum(t['kind']=='capacity' for t in state['timers'])==1)
            wait(lambda:js(a,'return readResult!==null;'));check('empty503 reads retry whole authorizations and succeed without nonce reuse',js(a,'return readResult.ok&&readAttempts===4&&new Set(nonces).size===4&&client.snapshot().delivery.httpReadRetries===2;') and all(snap(a,n)['selected']['count']==1 for n,_ in rooms[:2]))
            check('successful read retries clear all owned timeout and capacity timers',js(a,'return ownedTimers.size===0;'))
            for mode in ['fetch','body','timeout']:
                before=js(a,'transportMode=arguments[0];transportFailures=1;return readAttempts;',[mode]);began=time.monotonic()
                task(a,'await client.open(params[0]);return true;',[rooms[0][0]])
                check(mode+' interruption retries once with a new nonce and no retained timeout',js(a,'return readAttempts===arguments[0]+2&&new Set(nonces).size===nonces.length&&ownedTimers.size===0;',[before]) and (mode!='timeout' or time.monotonic()-began>=15))
            before=js(a,"transportMode='utf8';transportFailures=1;return readAttempts;")
            invalid=task(a,'try{await client.open(params[0]);return false;}catch(e){return e.name==="TypeError";}',[rooms[0][0]])
            check('invalid UTF-8 TypeError stays a validation failure without retry',invalid and js(a,'return readAttempts===arguments[0]+1&&ownedTimers.size===0;',[before]))
            before=js(a,"transportMode='fetch';transportFailures=9;return readAttempts;")
            exhausted=task(a,'try{await client.open(params[0]);return false;}catch(e){return e.name==="HostedTransportError";}',[rooms[0][0]])
            check('continuous connection resets stop after four complete authorized reads',exhausted and js(a,'return readAttempts===arguments[0]+4&&ownedTimers.size===0;',[before]))
            time.sleep(1.6)
            before=js(a,"transportMode='abort';transportFailures=1;transportStarted=false;abortTransport=new AbortController();abortResult=null;client.open(arguments[0],{signal:abortTransport.signal}).then(()=>abortResult={ok:true},e=>abortResult={ok:false,name:e.name});return readAttempts;",[rooms[0][0]])
            wait(lambda:js(a,'return transportStarted;'));js(a,"abortTransport.abort(new DOMException('View closed','AbortError'));");wait(lambda:js(a,'return abortResult!==null;'))
            check('caller abort during fetch is not a retriable transport timeout',js(a,'return !abortResult.ok&&abortResult.name==="AbortError"&&readAttempts===arguments[0]+1&&ownedTimers.size===0;',[before]))
            before=js(a,"transportMode=null;transportFailures=0;resetWrite=true;return writeAttempts;")
            refused=task(a,"try{await client.create('No automatic reset write');return false;}catch(e){return e.name==='HostedTransportError';}")
            check('a connection reset never automatically repeats a write',refused and js(a,'return writeAttempts===arguments[0]+1&&client.snapshot().intents.length===1;',[before]))
            js(a,'resetWrite=false;');time.sleep(1.6)
            before=js(a,'window.permanent=true;return readAttempts;')
            refusal=task(a,"try{await client.open(params[0]);return false;}catch(e){return e.status===429&&e.retryAfterSeconds===0;}",[rooms[0][0]])
            check('a logical quota refusal is not automatically retried or turned into global backoff',refusal and js(a,'return readAttempts===arguments[0]+1&&client.snapshot().delivery.serverRetryAfterSeconds===0;',[before]))
            js(a,'window.permanent=false;window.malformed=true;');before=js(a,'return readAttempts;')
            invalid=task(a,'try{await client.open(params[0]);return false;}catch{return true;}',[rooms[0][0]])
            check('malformed success data remains a validation failure and is never silently retried',invalid and js(a,'return readAttempts===arguments[0]+1;',[before]) and snap(a,rooms[0][0])['selected']['count']==1)
            js(a,'window.malformed=false;window.forever=true;');before=js(a,'return readAttempts;')
            exhausted=task(a,"try{await client.open(params[0]);return false;}catch(e){return e.status===503;}",[rooms[2][0]])
            check('continuous transient failure stops after four complete read attempts',exhausted and js(a,'return readAttempts===arguments[0]+4&&ownedTimers.size===0;',[before]))
            js(a,'window.forever=false;');time.sleep(1.6)
            task(a,'await client.open(params[0]);return true;',[rooms[0][0]])
            owner.operation('accept',{'node_id':rooms[0][0],'grant':rooms[0][1],'event':owner.origin(rooms[0][1],2,'P2P during server cooldown')});task(b,'await client.open(params[0]);return true;',[rooms[0][0]])
            offer=task(a,'const r=await pool.offer();return {id:r.entry.id,token:r.token};');answer=task(b,'const r=await pool.answer(params[0]);return {id:r.entry.id,token:r.token};',[offer['token']]);task(a,'await pool.accept(params[0],params[1]);return true;',[offer['id'],answer['token']]);wait(lambda:js(a,'return pool.get(arguments[0]).link.hostedWindowReady;',[offer['id']]))
            js(a,'window.writeFailures=true;');refused=task(a,"try{await client.create('No implicit write retry');return false;}catch(e){return e.status===503;}")
            time.sleep(.1);check('writing operations are attempted once and retain their recovery intent',refused and js(a,'return writeAttempts===2&&client.snapshot().intents.length===2;'))
            before=js(a,'return readAttempts;');task(a,'await client.open(params[0]);return true;',[rooms[0][0]])
            check('verified RTC reads remain usable while server HTTP is in a sixty-second cooldown',snap(a,rooms[0][0])['selected']['count']==2 and snap(a,rooms[0][0])['selected']['source']=='peer' and js(a,'return readAttempts===arguments[0]&&client.snapshot().delivery.serverRetryAfterSeconds>45;',[before]))
            js(a,"window.abortRead=new AbortController();window.cancelledRead=null;window.cancelJob=client.open(arguments[0],{signal:abortRead.signal}).then(()=>cancelledRead={ok:true},e=>cancelledRead={ok:false,name:e.name});",[rooms[1][0]])
            wait(lambda:js(a,"return [...ownedTimers.values()].some(v=>v.kind==='capacity');"))
            js(a,"abortRead.abort(new DOMException('View closed','AbortError'));");wait(lambda:js(a,'return cancelledRead!==null;'))
            check('closing a waiting read cancels it without a new server attempt',js(a,'return !cancelledRead.ok&&cancelledRead.name==="AbortError"&&readAttempts===arguments[0];',[before]))
            cleanup=[]
            for s in sessions:cleanup.append(task(s,"await client.close();pool.close();const {sessionBudget}=await import('/network/resource-budget.mjs');return sessionBudget(currentSession).snapshot();"))
            check('identity close cancels the shared timer and releases all retained resources',js(a,'return ownedTimers.size===0;') and all(not any(v for k,v in x.items() if k!='closed') for x in cleanup))
            result.update(status='PASS',resourceCleanup=cleanup,automaticWriteRetries=0,sharedCapacityTimers=1,foregroundReadAttemptLimit=4,foregroundReadDeadlineMilliseconds=90000)
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        for s in sessions:driver.call('/session/'+s,method='DELETE')
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--network-source',type=Path,default=ROOT/'network');p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.network_source.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
