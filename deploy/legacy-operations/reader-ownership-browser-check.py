#!/usr/bin/env python3
"""Two actual RTC peers exercise automatic-link ownership and retirement guards.

Real keys/signaling/transport and shared budget. Explicitly tagged fixture links
test the pool contract; this is not automatic topology or large-scale proof.
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
spec=importlib.util.spec_from_file_location('ownership_fixture',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
fixture,driver=support.fixture,support.driver


def run(network):
    sessions=[];checks=[];f=None
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted(network.glob('*.mjs'))]}
    result=dict(status='FAIL',scope=__doc__,checks=checks,actualBrowsers=2,actualV86Desktops=0)
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        v=driver.call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=params[params.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
    def wait(fn):return driver.wait(fn,45)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def connect(owner):
        offer=task(a,'const r=await pool.offer({readerRoom:params[0]});return {id:r.entry.id,token:r.token};',[owner])
        answer=task(b,'const r=await pool.answer(params[0],{readerRoom:params[1]});return {id:r.entry.id,token:r.token};',[offer['token'],owner])
        task(a,'await pool.accept(params[0],params[1]);return true;',[offer['id'],answer['token']])
        for s,e in [(a,offer['id']),(b,answer['id'])]:wait(lambda:js(s,'const l=pool.get(arguments[0]).link;return l.hostedWindowReady&&!l.pendingSend&&!l.pendingReceive&&!l.channel.bufferedAmount;',[e]));js(s,'window.entryId=arguments[0];',[e])
    def disconnect():
        for s in sessions:js(s,'pool.closeEntry(entryId,"Owned contract-test link");')
    try:
        with tempfile.TemporaryDirectory(prefix='codi-reader-owner-') as folder:
            folder=Path(folder);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public'
            shutil.copytree(network,public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
            (public/'index.html').write_text('<!doctype html><script type="module" src="/fixture.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']=dict(version='codi-hosted-room/1',basePath='/rooms',controllerKey=f.store.public,certificatePath='/api/v1/room-control/controller',challengePath='/api/v1/room-control/challenge',authorizePath='/api/v1/room-control/authorize')
            (public/'fixture-config.json').write_text(json.dumps(config))
            for suffix in ['?owner=1&readers=1','?readers=1']:
                s=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
                driver.call('/session/'+s+'/timeouts',{'script':120000});driver.call('/session/'+s+'/url',{'url':f.origin+'/'+suffix});wait(lambda:js(s,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
            a,b=sessions;node=task(a,'return await client.create("Reader ownership contract");')
            task(b,'await client.open(params[0]);return true;',[node]);connect(None)
            check('a manual invitation is never eligible for automatic retirement',all(js(s,'return !pool.beginReaderRetirement(entryId,arguments[0]);',[node]) for s in sessions));disconnect()
            connect(node)
            check('a new exclusive automatic connection can enter and cancel idle retirement',all(js(s,'const ok=pool.beginReaderRetirement(entryId,arguments[0]);pool.cancelReaderRetirement(entryId);return ok&&!pool.get(entryId).link.closed;',[node]) for s in sessions))
            check('retirement cannot be completed without a prior local freeze',js(a,'return !pool.finishReaderRetirement(entryId,arguments[0])&&!pool.get(entryId).link.closed;',[node]))
            held=task(a,'''const ok=pool.beginReaderRetirement(entryId,params[0]);let selected=false,sent=false;
              try{pool.protect(entryId);selected=true;}catch{}
              try{await pool.get(entryId).link.send('Must not begin while closing');sent=true;}catch{}
              pool.cancelReaderRetirement(entryId);return {ok,selected,sent,protected:pool.get(entryId).protected};''',[node])
            check('a frozen idle connection refuses a new direct-chat claim until cancel',held==dict(ok=True,selected=False,sent=False,protected=False))
            task(a,'await pool.get(entryId).link.send("Direct chat pins both ends");return true;')
            wait(lambda:js(b,'return directMessages.some(m=>m.text==="Direct chat pins both ends");'))
            check('sent and authenticated received direct chat protect both endpoints',all(js(s,'return pool.get(entryId).protected&&!pool.beginReaderRetirement(entryId,arguments[0]);',[node]) for s in sessions));disconnect()
            connect(node);js(a,'pool.protect(entryId);')
            check('selecting a direct-chat peer protects it before the first message is sent',js(a,'return pool.get(entryId).protected&&!pool.beginReaderRetirement(entryId,arguments[0]);',[node]));disconnect()
            connect(node)
            other=task(a,'return await client.create("A separate shared room");');task(b,'await client.open(params[0]);return true;',[other])
            task(a,'await pool.get(entryId).link.sendHostedApplication({op:"get",request_id:"A".repeat(43),node:params[0]});return true;',[other])
            wait(lambda:js(b,'return pool.get(entryId).protected;'))
            check('another hosted room sharing the same RTC connection protects both ends',all(js(s,'return pool.get(entryId).protected&&!pool.beginReaderRetirement(entryId,arguments[0]);',[node]) for s in sessions));disconnect()
            # No background synchronization: advance both real signature clocks
            # into the server lease-renewal window with the member grant valid.
            f.clock.offset=160
            js(a,'const original=Date.now;Date.now=()=>original()+160000;')
            task(a,'return await client.send(params[0],"Send after lease renewal threshold");',[node])
            state=js(a,'return client.snapshot(arguments[0]).selected;',[node])
            check('a valid member sends across room-lease renewal without a false head-scope error',state['count']==1 and not state['pending'])
            with f.store.lock(),f.store.db() as db:
                lease,count=db.execute('SELECT lease_revision,count FROM rooms WHERE node=?',(node,)).fetchone()
            check('renewed authority keeps one accepted original operation without resetting history',lease>=2 and count==1)
            cleanup=[]
            for s in sessions:
                task(s,'await client.close();pool.close();return true;')
                cleanup.append(task(s,'const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();'))
            check('all actual RTC and metadata leases are released',all(not any(v for k,v in item.items() if k!='closed') for item in cleanup))
            result.update(status='PASS',resourceCleanup=cleanup,renewedLeaseRevision=lease)
    except Exception as error:result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        for s in sessions:
            try:driver.call('/session/'+s,method='DELETE')
            except Exception as error:result.setdefault('cleanupErrors',[]).append(str(error));result['status']='FAIL'
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--network-root',type=Path,default=ROOT/'network');p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
    value=run(a.network_root.resolve());a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'checks':len(value['checks']),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS'else 1)
