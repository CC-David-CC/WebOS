#!/usr/bin/env python3
"""Actual Chrome/RTC clients bootstrap and repair with no seed peer.

Disposable issuer/SQLite/HTTP; real browser ES256 and bounded PoW Worker. No
v86/public/private-VM changes, fake SDP, mocked clock or8k/large-island proof.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('directory_browser_fixture',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
fixture,driver=support.fixture,support.driver


def run(participants=2):
    assert participants in (2,4)
    sessions=[];checks=[];f=None;held=False
    sources=[Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted((ROOT/'network').glob('*.mjs')),*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result=dict(status='FAIL',scope=__doc__,checks=checks,actualBrowsers=participants,actualV86Desktops=0,explicitSeedLinks=0,productionChanged=False,privateVMChanged=False,fullGoalComplete=False)

    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        value=driver.call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=params[params.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
    def wait(fn,seconds=90):return driver.wait(fn,seconds)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def snap(s,node=None):return js(s,'return client.snapshot(arguments[0]);',[node])
    def connected(s):return js(s,'return pool.list().filter(e=>e.state==="ready").map(e=>e.id);')
    def reads(s):return js(s,'return httpOperations.filter(v=>!v.reader).length;')
    try:
        with tempfile.TemporaryDirectory(prefix='codi-directory-browser-') as folder:
            folder=Path(folder);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public'
            shutil.copytree(ROOT/'network',public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
            (public/'fixture-loader.mjs').write_text('import("/fixture.mjs").catch(e=>window.fixtureFatal=e.stack);')
            (public/'index.html').write_text('<!doctype html><title>Reader directory bootstrap</title><script type="module" src="/fixture-loader.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'}
            (public/'fixture-config.json').write_text(json.dumps(config))
            for suffix in ['?owner=1&directory=1',*['?directory=1']*(participants-1)]:
                sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(sid)
                driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':f.origin+'/'+suffix})
                wait(lambda:js(sid,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
            a,b=sessions[0],sessions[1 if participants==2 else 2];node=task(a,'return await client.create("Recover without any seed connection");');result['ownedRoom']=node
            task(a,'return await client.send(params[0],"Initial accepted state");',[node])
            for s in sessions[1:]:task(s,'await client.open(params[0]);return true;',[node])
            check('both browsers start with zero peer connections and independently verified server state',all(js(s,'return pool.list().length===0;') for s in sessions) and snap(b,node)['selected']['count']==1)
            for s in sessions:js(s,'window.directoryPump=setInterval(()=>client.tick(),1000);client.tick();')
            began=time.monotonic();wait(lambda:all(len(connected(s))==participants-1 for s in sessions));result['bootstrapSeconds']=round(time.monotonic()-began,3)
            check('scoped directory plus browser-paid work creates an actual authenticated RTC link without seed signaling',all(snap(s)['delivery']['directory']['work']>=1 and snap(s)['delivery']['readers']['connected']>=1 for s in sessions))
            before=reads(b);task(a,'return await client.send(params[0],"Accepted over the discovered peer path");',[node]);wait(lambda:snap(b,node)['selected']['count']==2)
            check('discovered peer resumes accepted receipt delivery without ordinary server reads',snap(b,node)['selected']['source']=='peer' and reads(b)==before)
            f.http.reader_slots.acquire();f.http.reader_slots.acquire();held=True
            # Stop the metadata lane, not the already-established data channels.
            task(a,'return await client.send(params[0],"P2P survives unavailable discovery");',[node]);wait(lambda:snap(b,node)['selected']['count']==3)
            check('existing P2P delivery survives discovery service saturation',snap(b,node)['selected']['source']=='peer' and reads(b)==before and connected(a) and connected(b))
            old={s:connected(s) for s in sessions}
            island=[b] if participants==2 else sessions[2:]
            fallback_before={s:(snap(s)['delivery']['serverLoads'],reads(s)) for s in island}
            identities=[js(s,'return currentSession.public.sid;') for s in sessions]
            internal={}
            for index,s in enumerate(sessions):
                keep=[] if participants==2 else identities[:2] if index<2 else identities[2:]
                internal[s]=js(s,'const keep=new Set(arguments[0]),saved=[];for(const e of pool.list()){if(keep.has(e.peerId)&&e.state==="ready")saved.push(e.id);else pool.closeEntry(e.id,"Owned complete partition fixture");}return saved;',[keep])
            wait(lambda:all(len(connected(s))==(0 if participants==2 else 1) for s in sessions))
            if participants==4:check('two separated two-reader islands keep their existing internal RTC connections',all(len(internal[s])==1 for s in sessions))
            task(a,'return await client.send(params[0],"Accepted while cross-island RTC paths are down");',[node]);wait(lambda:all(snap(s,node)['selected']['count']==4 for s in island),45)
            check('complete separation falls back to authoritative state without losing the verified position',any(snap(s)['delivery']['serverLoads']>fallback_before[s][0] and reads(s)>fallback_before[s][1] for s in island))
            f.http.reader_slots.release();f.http.reader_slots.release();held=False
            began=time.monotonic();wait(lambda:all(len(connected(s))==participants-1 for s in sessions),100);result['completeSplitRepairSeconds']=round(time.monotonic()-began,3)
            check('metadata recovery creates fresh cross-partition paths while preserving internal connections',all(set(internal[s])<=set(connected(s)) and len(set(connected(s))-set(old[s]))>0 for s in sessions))
            before=reads(b);task(a,'return await client.send(params[0],"Return to P2P after complete separation");',[node]);wait(lambda:snap(b,node)['selected']['count']==5)
            check('a fully repaired group returns to peer receipts without further ordinary reads',snap(b,node)['selected']['source']=='peer' and reads(b)==before)
            result['directoryStats']=[snap(s)['delivery']['directory'] for s in sessions];cleanup=[]
            for s in sessions:
                task(s,'clearInterval(directoryPump);await client.close();pool.close();return true;')
                wait(lambda:js(s,'return !client.snapshot().delivery.directory.busy&&client.snapshot().delivery.directory.processing===0&&client.snapshot().delivery.readers.jobs===0;'))
                cleanup.append(task(s,'const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();'))
            check('closing both clients releases worker jobs, mail queues, RTC and all shared leases',all(not any(v for k,v in stats.items() if k!='closed') for stats in cleanup))
            result.update(status='PASS',resourceCleanup=cleanup,serverDirectory=f.store.rendezvous.snapshot(),serverAcceptanceStillAuthoritative=True,partitionGroups=[1,1] if participants==2 else [2,2])
    except Exception as error:
        import traceback
        result.update(error=str(error),traceback=traceback.format_exc(),diagnostics=[])
        for s in sessions:
            try:result['diagnostics'].append({'state':js(s,'return {ready:window.fixtureReady,fatal:window.fixtureFatal,network:window.client?.snapshot(arguments[0]),peers:window.pool?.list(),http:window.httpOperations?.slice(-12)};',[result.get('ownedRoom')]),'logs':driver.call('/session/'+s+'/log',{'type':'browser'})})
            except Exception as e:result['diagnostics'].append({'error':str(e)})
        if f:result['serverDirectory']=f.store.rendezvous.snapshot()
    finally:
        if held:f.http.reader_slots.release();f.http.reader_slots.release()
        for s in sessions:
            try:driver.call('/session/'+s,method='DELETE')
            except Exception as error:result.setdefault('cleanupErrors',[]).append(str(error));result['status']='FAIL'
        result['ownedBrowserContextsClosed']=len(sessions)
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(name).read_bytes()).hexdigest()!=pin for name,pin in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--participants',type=int,choices=[2,4],default=2);args=p.parse_args();assert not args.output.exists()
    value=run(args.participants);args.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'checks':len(value['checks']),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS' else 1)
