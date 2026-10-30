#!/usr/bin/env python3
"""Real four-Chrome RTC, separate coordinator and Caddy: peer-first introductions.

No manual signaling, fake SDP, clock/capacity override, VM, production deployment
or8k claim. Stop/restart discovery while keeping saved-chat/P2P available.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import traceback
import hashlib

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
support=module('coordinator_browser_support',ROOT/'scripts/hosted-peer-check.py');fixture,driver=support.fixture,support.driver
separate=module('coordinator_browser_process',ROOT/'scripts/reader-coordinator-fixture.py')

def run(caddy,network_root=ROOT/'network'):
    sessions=[];f=None;coordinator=None;held=False;checks=[];temporary=tempfile.TemporaryDirectory(prefix='codi-coordinator-browser-')
    result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowsers':4,'actualV86Desktops':0,'manualSeedLinks':0,'wholeGoalComplete':False}
    sources=[Path(__file__),ROOT/'scripts/reader-coordinator-fixture.py',ROOT/'scripts/reader-coordinator-check.py',ROOT/'scripts/hosted-room-check.py',ROOT/'scripts/hosted-peer-page.mjs',*sorted((ROOT/'reader_service').glob('*.py')),*sorted((ROOT/'room_service').glob('*.py')),*sorted(network_root.glob('*.mjs'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        v=driver.call('/session/'+s+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),e=>done({ok:false,error:e.stack}));','args':args});assert v['ok'],v;return v.get('value')
    def wait(fn,seconds=90):return driver.wait(fn,seconds)
    def state(s,node=None):return js(s,'return client.snapshot(arguments[0]);',[node])
    def links(s):return js(s,'return pool.list().filter(e=>e.state==="ready");')
    def ordinary(s):return js(s,'return httpOperations.filter(r=>!r.reader).length;')
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    try:
        folder=Path(temporary.name);f=fixture.Fixture(folder,front_origin=separate.front_origin());f.clock.realtime=True
        coordinator=separate.CoordinatorFixture(f,caddy);public=folder/'public';shutil.copytree(network_root,public/'network');shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
        # Sealed modules use their production-relative vendor path. At this
        # fixture's shallower /network mount it resolves to /vendor instead.
        vendor=public/'vendor/chess';vendor.mkdir(parents=True);shutil.copyfile(ROOT/'assets/vendor/chess/chess.mjs',vendor/'chess.mjs')
        (public/'loader.mjs').write_text('import("./fixture.mjs").catch(e=>window.fixtureFatal=e.stack);');(public/'index.html').write_text('<!doctype html><title>Separate coordinator</title><script type="module" src="./loader.mjs"></script>')
        config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'};(public/'fixture-config.json').write_text(json.dumps(config))
        f.http.reader_slots.acquire();f.http.reader_slots.acquire();held=True
        for i in range(4):
            sid=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(sid);driver.call('/session/'+sid+'/timeouts',{'script':120000});driver.call('/session/'+sid+'/url',{'url':f.origin+'/?directory=1&window=1&sync=1&coordinator=1'+('&owner=1' if i==0 else '')});wait(lambda:js(sid,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
        a,b,c,d=sessions;node=task(a,'return await client.create("Independent coordinator peer first");');task(a,'return await client.send(params[0],"Initial accepted checkpoint");',[node]);result['ownedRoom']=node
        for s in sessions[1:]:task(s,'await client.open(params[0]);return true;',[node])
        check('four actual clients start without peer seeds while legacy room discovery is saturated',all(not links(s) for s in sessions) and f.http.reader_rates=={})
        for s in sessions:js(s,'window.directoryPump=setInterval(()=>client.tick(),1000);client.tick();')
        wait(lambda:all(len(links(s))==3 for s in sessions),120)
        stats=[state(s)['delivery'] for s in sessions]
        check('new discovery key/path bootstraps real RTC without touching saved-chat discovery slots',all(v['directory']['mode']=='separate' and v['directory']['bootstrap']>=1 for v in stats) and f.http.reader_rates=={})
        check('actual peer-mediated offers supplement bounded coordinator bootstrap',sum(v['readers']['peerOffers'] for v in stats)>0 and sum(v['readers']['directoryOffers'] for v in stats)>0)
        coordinator.stop_coordinator();before={s:ordinary(s) for s in sessions[1:]};task(a,'return await client.send(params[0],"Saved chat and P2P with coordinator stopped");',[node]);wait(lambda:all(state(s,node)['selected']['count']==2 for s in sessions[1:]),40)
        check('stopping coordinator leaves saved-chat writes and existing RTC data paths available',all(state(s,node)['selected']['source']=='peer' and ordinary(s)==before[s] for s in sessions[1:]))
        ids={s:js(s,'return currentSession.public.sid;') for s in sessions};peer_before=sum(state(s)['delivery']['readers']['peerOffers'] for s in sessions)
        for s in [a,b]:js(s,'for(const e of pool.list())if(e.peerId===arguments[0])pool.closeEntry(e.id,"Owned leaf edge loss");',[ids[d]])
        wait(lambda:len(links(d))==1)
        wait(lambda:all(len(links(s))==3 for s in sessions),100)
        check('one remaining friend introduces missing peers while coordinator is still down',coordinator.child.poll() is not None and sum(state(s)['delivery']['readers']['peerOffers'] for s in sessions)>peer_before)
        before={s:ordinary(s) for s in sessions[1:]};task(a,'return await client.send(params[0],"Data after entirely peer-mediated repair");',[node]);wait(lambda:all(state(s,node)['selected']['count']==3 for s in sessions[1:]),40)
        check('peer-repaired group continues verified receipt delivery without reader HTTP fallback',all(state(s,node)['selected']['source']=='peer' and ordinary(s)==before[s] for s in sessions[1:]))
        bootstrap=[state(s)['delivery']['directory']['bootstrap'] for s in sessions];coordinator.start_coordinator()
        wait(lambda:all(state(s)['delivery']['directory']['bootstrap']>v for s,v in zip(sessions,bootstrap)),100)
        check('restarted independent coordinator reacquires discovery-only tickets without resetting chat floors',all(state(s,node)['selected']['count']==3 for s in sessions) and f.http.reader_rates=={})
        cleanup=[]
        for s in sessions:cleanup.append(task(s,'clearInterval(directoryPump);await client.close();pool.close();const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();'))
        check('all four browser clients release every tracked resource after separate discovery and repair',all(not any(v for k,v in q.items() if k!='closed') for q in cleanup))
        result.update(status='PASS',resourceCleanup=cleanup,coordinatorSeparateProcess=True,caddySeparateProcess=True,legacyDiscoveryRequests=0,installedSandboxProven=False,networkRoot=str(network_root))
    except Exception as e:
        result.update(error=str(e),traceback=traceback.format_exc(),diagnostics=[])
        for s in sessions:
            try:result['diagnostics'].append(js(s,'return {fatal:window.fixtureFatal,state:window.client?.snapshot(arguments[0]),peers:window.pool?.list()};',[result.get('ownedRoom')]))
            except Exception as error:result['diagnostics'].append({'error':str(error)})
    finally:
        for s in sessions:
            try:driver.call('/session/'+s,method='DELETE')
            except Exception as e:result.setdefault('cleanupErrors',[]).append(str(e));result['status']='FAIL'
        if held:f.http.reader_slots.release();f.http.reader_slots.release()
        if coordinator:coordinator.close()
        if f:f.close()
        temporary.cleanup()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=v for p,v in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--caddy',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--network-root',type=Path,default=ROOT/'network');a=p.parse_args();assert not a.output.exists();v=run(a.caddy.resolve(),a.network_root.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
