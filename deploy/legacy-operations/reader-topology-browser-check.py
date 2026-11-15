#!/usr/bin/env python3
"""Real Chrome identities merge two full RTC reader islands.

Real disposable issuer/SQLite, signatures, PoW and RTC. Manual seed chains only
inside each island. Measured wire payloads and Chrome heaps; no v86/VM/public
changes, wire-overhead accounting or8k claim. Supports ten or32 browsers.
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
spec=importlib.util.spec_from_file_location('topology_fixture',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
fixture,driver=support.fixture,support.driver


def run(network,participants=10):
    assert participants in (10,32)
    half=participants//2
    sessions=[];checks=[];f=None
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted(network.glob('*.mjs'))]}
    result=dict(status='FAIL',scope=__doc__,checks=checks,actualBrowsers=participants,actualV86Desktops=0,manualCrossIslandLinks=0,fullGoalComplete=False,load={'writers':1,'readers':participants-1,'burstBatches':3,'acceptedMessagesPerBatch':8})
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        value=driver.call('/session/'+s+'/execute/async',{'script':'const params=arguments,done=params[params.length-1];(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
    def wait(fn,seconds=120):return driver.wait(fn,seconds)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def snap(s,node=None):return js(s,'return client.snapshot(arguments[0]);',[node])
    def graph():return {ids[s]:{e['peerId'] for e in js(s,'return pool.list().filter(e=>e.state==="ready");')} for s in sessions}
    def cross(g):return {(a,b) for a in groups[0] for b in g[a] if b in groups[1] and a in g.get(b,set())}
    def components(g,removed=None):
        pending=set(g)-{removed};parts=[]
        while pending:
            seen=set();todo=[next(iter(pending))]
            while todo:
                n=todo.pop()
                if n not in pending or n in seen:continue
                seen.add(n);todo.extend(g[n]-{removed})
            pending-=seen;parts.append(seen)
        return parts
    def connect(a,b):
        offer=task(a,'const r=await pool.offer();return {id:r.entry.id,token:r.token};')
        answer=task(b,'const r=await pool.answer(params[0]);return {id:r.entry.id,token:r.token};',[offer['token']])
        task(a,'await pool.accept(params[0],params[1]);return true;',[offer['id'],answer['token']])
        for s,e in [(a,offer['id']),(b,answer['id'])]:wait(lambda:js(s,'return pool.get(arguments[0]).link.hostedWindowReady;',[e]))
    try:
        with tempfile.TemporaryDirectory(prefix='codi-reader-topology-') as folder:
            folder=Path(folder);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public'
            shutil.copytree(network,public/'network',ignore=shutil.ignore_patterns('*.md'));shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
            (public/'fixture-loader.mjs').write_text('import("/fixture.mjs").catch(e=>window.fixtureFatal=e.stack);')
            (public/'index.html').write_text('<!doctype html><title>Full reader islands</title><script type="module" src="/fixture-loader.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']=dict(version='codi-hosted-room/1',basePath='/rooms',controllerKey=f.store.public,certificatePath='/api/v1/room-control/controller',challengePath='/api/v1/room-control/challenge',authorizePath='/api/v1/room-control/authorize')
            (public/'fixture-config.json').write_text(json.dumps(config))
            for index in range(participants):
                s=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
                driver.call('/session/'+s+'/timeouts',{'script':120000});driver.call('/session/'+s+'/url',{'url':f.origin+'/?directory=1'+('&owner=1' if index==0 else '')})
                wait(lambda:js(s,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
                js(s,'''window.discoveryOffline=true;window.readsOffline=false;const original=fetch;
                  window.topologyWireBytes=0;const priorState=client.peerState.bind(client);client.peerState=e=>{
                    if(e.state==='ready'&&!e.topologyWireObserved&&e.link.channel){e.topologyWireObserved=true;const send=e.link.channel.send.bind(e.link.channel);
                      e.link.channel.send=wire=>{topologyWireBytes+=new TextEncoder().encode(wire).length;return send(wire);};}return priorState(e);};
                  window.topologyPeaks={members:0,pending:0,automatic:0,jobs:0};window.topologyProbe=setInterval(()=>{const r=client.snapshot().delivery.readers;
                    topologyPeaks.members=Math.max(topologyPeaks.members,r.members.length);topologyPeaks.pending=Math.max(topologyPeaks.pending,r.pending);
                    topologyPeaks.automatic=Math.max(topologyPeaks.automatic,r.automaticConnections);topologyPeaks.jobs=Math.max(topologyPeaks.jobs,r.jobs);},100);
                  window.fetch=(url,options)=>{const path=typeof url==='string'?url:url.url,reader=options?.headers?.['Codi-Reader']==='rendezvous/1';
                    if(discoveryOffline&&reader)return Promise.reject(new TypeError('Owned discovery isolation'));
                    let op;try{op=JSON.parse(JSON.parse(options?.body||'{}').request||'{}').operation;}catch{}
                    if(readsOffline&&!reader&&path.endsWith('/rooms/use')&&op!=='append')return Promise.reject(new TypeError('Owned read fallback isolation'));
                    return original(url,options);};''')
            ids={s:js(s,'return currentSession.public.sid;') for s in sessions};groups=[set(ids[s] for s in sessions[:half]),set(ids[s] for s in sessions[half:])]
            a=sessions[0];node=task(a,'return await client.create("Join full islands without manual cross links");');result['ownedRoom']=node
            task(a,'return await client.send(params[0],"Initial full-island checkpoint");',[node])
            for s in sessions[1:]:task(s,'await client.open(params[0]);return true;',[node])
            # Intra-island seed chains. Automatic discovery fills each node's
            # target4; larger islands must remain partial meshes, not cliques.
            for island in [sessions[:half],sessions[half:]]:
                for left,right in zip(island,island[1:]):connect(left,right)
                for s in island:js(s,'window.topologyPump=setInterval(()=>client.tick(),1000);client.tick();')
            wait(lambda:all(4<=len(g[n])<=6 and g[n]<=group for group in groups for n in group) if (g:=graph()) else False,180)
            isolated=graph();result['initialDegrees']={k:len(v) for k,v in isolated.items()}
            check('two separate full reader islands have bounded authenticated neighbor sets',len(components(isolated))==2 and not cross(isolated))
            before=[snap(s)['delivery']['readers']['sampled'] for s in sessions];began=time.monotonic()
            for s in sessions:js(s,'discoveryOffline=false;')
            def redundant():
                g=graph();return len(cross(g))>=2 and len(components(g))==1 and all(len(components(g,n))==1 for n in g)
            wait(redundant,180);result['mergeSeconds']=round(time.monotonic()-began,3);merged=graph()
            check('already full islands create redundant cross links with no manual cross-island signaling',len(cross(merged))>=2)
            check('merged graph remains connected after removal of any single participant',all(len(components(merged,n))==1 for n in merged))
            check('healthy full readers continue bounded in-band sampling',any(snap(s)['delivery']['readers']['sampled']>v for s,v in zip(sessions,before)))
            wait(lambda:sum(snap(s)['delivery']['readers']['replaced'] for s in sessions)>0,90)
            check('an excess automatic connection is retired only after the real two-endpoint exchange',sum(snap(s)['delivery']['readers']['replaced'] for s in sessions)>0)
            # Stop discovery and ordinary reads; a fresh accepted state must
            # actually traverse the new RTC bridges, not the fallback service.
            for s in sessions[1:]:js(s,'discoveryOffline=true;readsOffline=true;')
            js(a,'discoveryOffline=true;')
            task(a,'return await client.send(params[0],"Accepted across automatically merged islands");',[node])
            wait(lambda:all(snap(s,node)['selected']['count']==2 for s in sessions),90)
            check('all verified heads converge through RTC while reader HTTP fallback is disabled',all(snap(s,node)['selected']['source']=='peer' for s in sessions[1:]))
            # Remove one real bridge, preserving all other transport objects.
            left,right=next(iter(cross(graph())));left_s=next(s for s in sessions if ids[s]==left)
            js(left_s,'const e=pool.list().find(e=>e.peerId===arguments[0]&&e.state==="ready");pool.closeEntry(e.id,"Owned bridge failure");',[right])
            task(a,'return await client.send(params[0],"Accepted after one bridge failed");',[node])
            wait(lambda:all(snap(s,node)['selected']['count']==3 for s in sessions),90)
            check('loss of one actual cross-island bridge preserves RTC-only convergence',all(snap(s,node)['selected']['source']=='peer' for s in sessions[1:]))
            result['burstMeasurements']=[]
            for batch in range(3):
                before_bytes=sum(js(s,'return topologyWireBytes;') for s in sessions);began=time.monotonic()
                task(a,'for(let n=0;n<8;n++)await client.send(params[0],`Structured text burst ${params[1]} message ${n}`);return true;',[node,batch])
                count=3+(batch+1)*8;wait(lambda:all(snap(s,node)['selected']['count']==count for s in sessions),120)
                elapsed=time.monotonic()-began;after_bytes=sum(js(s,'return topologyWireBytes;') for s in sessions)
                heaps=[driver.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}})['usedSize'] for s in sessions]
                accounted=[task(s,'const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot().metadataBytes;') for s in sessions]
                result['burstMeasurements'].append({'batch':batch,'acceptedMessages':8,'convergenceSeconds':round(elapsed,3),'aggregateAuthenticatedApplicationBytes':after_bytes-before_bytes,'meanApplicationBytesPerReaderPerSecond':round((after_bytes-before_bytes)/participants/elapsed,2),'chromeJSHeapBytes':heaps,'accountedMetadataBytes':accounted})
            check('three eight-message bursts converge with all reader HTTP fallback still blocked',all(snap(s,node)['selected']['count']==27 and snap(s,node)['selected']['source']=='peer' for s in sessions[1:]))
            stats=[snap(s)['delivery']['readers'] for s in sessions];result['readerStats']=stats;result['degrees']={k:len(v) for k,v in graph().items()}
            check('all readers keep six-neighbor/eight-automatic/four-pending and bounded work/cache caps',all(len(v['members'])<=6 and v['automaticConnections']<=8 and v['pending']<=4 and v['retiring']<=4 and v['hintsPending']<=64 and v['jobs']<=16 for v in stats))
            result['sampledResourcePeaks']=[js(s,'return topologyPeaks;') for s in sessions]
            check('100ms samples also stay inside the neighbor/pending/automatic/job limits during merges',all(p['members']<=6 and p['pending']<=4 and p['automatic']<=8 and p['jobs']<=16 for p in result['sampledResourcePeaks']))
            cleanup=[]
            for s in sessions:
                task(s,'clearInterval(topologyPump);clearInterval(topologyProbe);await client.close();pool.close();return true;')
                wait(lambda:js(s,'return client.snapshot().delivery.readers.jobs===0&&!client.snapshot().delivery.directory.busy&&client.snapshot().delivery.directory.processing===0;'))
                cleanup.append(task(s,'const {sessionBudget}=await import("./network/resource-budget.mjs");return sessionBudget(currentSession).snapshot();'))
            check('closing every browser releases all connection/work/metadata leases',all(not any(v for k,v in item.items() if k!='closed') for item in cleanup))
            result.update(status='PASS',resourceCleanup=cleanup,serverDirectory=f.store.rendezvous.snapshot())
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc(),diagnostics=[])
        for s in sessions:
            try:result['diagnostics'].append(js(s,'return {sid:window.currentSession?.public.sid,fatal:window.fixtureFatal,state:window.client?.snapshot(arguments[0]),peers:window.pool?.list()};',[result.get('ownedRoom')]))
            except Exception as failure:result['diagnostics'].append({'error':str(failure)})
    finally:
        for s in sessions:
            try:driver.call('/session/'+s,method='DELETE')
            except Exception as error:result.setdefault('cleanupErrors',[]).append(str(error));result['status']='FAIL'
        if f:f.close()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(name).read_bytes()).hexdigest()!=pin for name,pin in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--network-root',type=Path,default=ROOT/'network');p.add_argument('--participants',type=int,choices=[10,32],default=10);p.add_argument('--output',type=Path,required=True);args=p.parse_args();assert not args.output.exists()
    value=run(args.network_root.resolve(),args.participants);args.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'checks':len(value['checks']),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS' else 1)
