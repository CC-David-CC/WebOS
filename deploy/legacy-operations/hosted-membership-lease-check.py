#!/usr/bin/env python3
"""Real signed Chrome membership refresh crossing the room lease boundary.

Logical clock moves149s then2s after the join reply to reproduce the observed
real-clock128-agent race. No capacity/WAN/v86 claim and no signature bypass.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import traceback

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('member_lease_support',ROOT/'scripts/hosted-peer-check.py');support=importlib.util.module_from_spec(s);s.loader.exec_module(support);fixture,driver=support.fixture,support.driver

def run():
    checks=[];sid=None;f=None;tmp=tempfile.TemporaryDirectory(prefix='codi-member-lease-');sources=[Path(__file__),ROOT/'network/hosted-room-client.mjs',ROOT/'network/hosted-room-authority.mjs'];pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','checks':checks,'scope':__doc__,'actualBrowsers':1,'actualV86Desktops':0,'clockBoundaryInjected':True,'wholeGoalComplete':False}
    def js(code,args=[]):return driver.call('/session/'+sid+'/execute/sync',{'script':code,'args':args})
    def task(code,args=[]):
        d=driver.call('/session/'+sid+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),e=>done({ok:false,error:e.stack}));','args':args});assert d['ok'],d;return d.get('value')
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    try:
        folder=Path(tmp.name);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public';shutil.copytree(ROOT/'network',public/'network');shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
        (public/'index.html').write_text('<!doctype html><script type="module" src="/fixture.mjs"></script>')
        config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'};(public/'fixture-config.json').write_text(json.dumps(config))
        original=f.server.get_app()
        def controlled(env,start):
            if env.get('PATH_INFO')=='/fixture/advance' and env.get('REQUEST_METHOD')=='POST':
                f.clock.offset=151;start('200 OK',[('Content-Type','application/json'),('Content-Length','2')]);return [b'{}']
            return original(env,start)
        f.server.set_app(controlled)
        sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':f.origin+'/?owner=1&window=1&sync=1'});driver.wait(lambda:js('if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'),30)
        node=task('return await client.create("Membership lease race");');task('return await client.send(params[0],"Before renewal boundary");',[node]);before=js('return client.snapshot(arguments[0]).selected;',[node]);check('real registered browser starts at the original signed lease with one accepted event',before['leaseRevision']==1 and before['count']==1 and before['joined'])
        f.clock.offset=149
        js('window.leaseRealNow=Date.now.bind(Date);window.leaseOffset=149000;Date.now=()=>leaseRealNow()+leaseOffset;window.leaseBoundaryArmed=true;window.leaseJoinReplies=0;window.leaseLastGrant=null;window.leaseReplacement=null;const original=fetch;window.fetch=async(u,o)=>{let op;try{op=JSON.parse(JSON.parse(o?.body||"{}").request||"{}").operation;}catch{}const response=await original(u,o);if(op==="join"){leaseJoinReplies++;const data=await response.clone().json();leaseLastGrant=data.grant;if(leaseBoundaryArmed){leaseBoundaryArmed=false;await original("/fixture/advance",{method:"POST"});leaseOffset=151000;}if(leaseReplacement){data.grant=leaseReplacement;return new Response(JSON.stringify(data),{status:response.status,headers:response.headers});}}return response;};')
        check('actual clock-controlled join is armed immediately before the150s lease-renewal boundary',js('return leaseBoundaryArmed;'))
        task('return await client.send(params[0],"Exactly once across renewal");',[node]);state=js('return client.snapshot(arguments[0]).selected;',[node])
        check('atomic state and membership refresh finish across a genuinely signed lease change',state['leaseRevision']>before['leaseRevision'] and state['joined'] and not state['error'])
        with f.store.lock(),f.store.db() as db:
            r=db.execute('SELECT count,lease_revision FROM rooms WHERE node=?',(node,)).fetchone()
            events=db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0]
        check('one user send creates exactly one durable new event and retains both verified records',r[0]==state['count']==events==2 and sum(v['text']=='Exactly once across renewal' for v in state['records'])==1)
        check('stale membership refresh is bounded and atomic mode never falls back to split snapshots',js('return leaseJoinReplies===2&&!httpOperations.some(r=>r.operation==="snapshot");'))
        # A controller-signed but foreign-author grant is not a recoverable
        # lease race. It must fail before any fresh membership request or write.
        claims=fixture.jose.inspect(js('return leaseLastGrant;'),fixture.MEMBER_TYPE)[1]
        claims['author']['sid']=str(fixture.uuid.uuid4());bad=fixture.jose.sign(claims,f.store.key,fixture.MEMBER_TYPE)
        f.clock.offset=301;js('leaseOffset=301000;leaseReplacement=arguments[0];leaseJoinReplies=0;',[bad])
        refusal=task('try{await client.send(params[0],"Foreign grant must never send");return {accepted:true};}catch(e){return {accepted:false,error:e.message};}',[node])
        check('controller-signed foreign-author grant is refused without an automatic membership retry',refusal=={'accepted':False,'error':'Invalid hosted membership grant'} and js('return leaseJoinReplies===1;'))
        with f.store.lock(),f.store.db() as db:assert db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0]==2
        check('invalid grant neither creates a pending origin nor writes a durable event',not js('return client.snapshot(arguments[0]).selected.pending;',[node]))
        js('leaseReplacement=null;');task('return await client.send(params[0],"Valid action after refusal");',[node])
        with f.store.lock(),f.store.db() as db:assert db.execute('SELECT count(*) FROM events WHERE node=?',(node,)).fetchone()[0]==3
        check('a fresh valid action remains usable after foreign-grant refusal',js('return client.snapshot(arguments[0]).selected.count===3;',[node]))
        budget=task('await client.close();pool.close();const {sessionBudget}=await import("/network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();')
        check('all crypto, RPC, worker, connection and metadata leases release after crossing renewal',not any(v for k,v in budget.items() if k!='closed'))
        result.update(status='PASS',resourceCleanup=budget,leaseBefore=before['leaseRevision'],leaseAfter=state['leaseRevision'],durableEventsAfterBoundary=events,durableEventsAfterRefusalAndFreshAction=3)
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    finally:
        if sid:driver.call('/session/'+sid,method='DELETE')
        if f:f.close()
        tmp.cleanup()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=v for p,v in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run();a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
