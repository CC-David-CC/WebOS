#!/usr/bin/env python3
"""Isolated SDK agents in browser frames, real identities/IDB/authorization/RTC.

Published network bytes, one native IndexedDB namespace per agent. The supervisor
passes commands and room IDs, never checkpoint/chat data. Not one browser or v86
per agent, public WAN, production admission capacity or8k acceptance by itself.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shlex
import shutil
import tempfile
import time
import traceback
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('agent_load_support',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
fixture,driver=support.fixture,support.driver


def run(release,participants,per_browser,admission_interval,atomic_sync=False,shared_storage_control=False,chrome_binary='/snap/chromium/current/usr/lib/chromium-browser/chrome',failure_probe=False,proposal_recovery=False,reader_coordinator=False,caddy=None,steady_seconds=0,island_control=False):
    sessions=[];checks=[];f=None;temporary=None;owners={};run_id=secrets.token_hex(16);coordinator=None;legacy_slots_held=False
    manifest=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest()
    graph=json.loads((release/'assets/desktop/network-release.json').read_bytes())
    sources=[Path(__file__),ROOT/'scripts/hosted-agent-loader.mjs',ROOT/'scripts/hosted-agent-host.mjs',ROOT/'scripts/hosted-peer-page.mjs',ROOT/'scripts/hosted-room-check.py',ROOT/'scripts/touch-preview-check.py',*sorted((ROOT/'room_service').glob('*.py')),ROOT/'origin_service/room_authority.py',ROOT/'origin_service/lifecycle.py',ROOT/'codiserver-server-v0.3.0/codiauth/service.py',ROOT/'codiserver-server-v0.3.0/codiauth/jose.py']
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    if reader_coordinator:
        for p in [ROOT/'scripts/reader-coordinator-fixture.py',ROOT/'scripts/reader-coordinator-check.py',ROOT/'scripts/serve-reader-coordinator.py',*sorted((ROOT/'reader_service').glob('*.py'))]:pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(status='FAIL',scope=__doc__,checks=checks,logicalAgents=participants,actualBrowserInstances=0,actualV86Desktops=0,testedManifestSHA256=manifest,wholeGoalComplete=False,admissionIntervalSeconds=admission_interval,atomicSync=atomic_sync,sharedStorageNegativeControl=shared_storage_control,chromeBinary=chrome_binary,logicalCPUs=__import__('os').cpu_count(),proposalRecovery=proposal_recovery)
    result.update(readerCoordinator=reader_coordinator,separateCoordinatorProcess=False,separateCaddyProcess=False,steadySecondsRequested=steady_seconds)
    result['islandPartitionControl']=island_control
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        v=driver.call('/session/'+s+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert v['ok'],v;return v.get('value')
    def wait(fn,seconds=180):return driver.wait(fn,seconds)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def act(i,method,*args):return task(owners[i],'return await agentLab[params[0]](...params.slice(1));',[method,i,*args])
    def snapshots():return [v for s in sessions for v in js(s,'return agentLab.snapshots(arguments[0]);',[node])]
    def summaries():return [v for s in sessions for v in js(s,'return agentLab.summaries(arguments[0]);',[node])]
    def http_stats():return [v for s in sessions for v in js(s,'return agentLab.httpStats();')]
    def memory():
        # Linux RSS sums include shared pages more than once. PSS apportions
        # shared pages. Neither is the SDK's metadata accounting or JS heap.
        browser_args=[driver.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Browser.getBrowserCommandLine','params':{}})['arguments'] for s in sessions]
        roots=[];processes={}
        for p in Path('/proc').iterdir():
            if not p.name.isdigit():continue
            try:
                argv=[v for v in (p/'cmdline').read_bytes().split(b'\0') if v]
                # Snap Chromium rewrites its process title to one space-separated
                # argv entry. Parse that form without executing any command text.
                if len(argv)==1:argv=[v.encode() for v in shlex.split(argv[0].decode())]
                status=dict(line.split(':',1) for line in (p/'status').read_text().splitlines());processes[int(p.name)]=(int(status['PPid']),int(status.get('VmRSS','0 kB').split()[0]))
                if any(next(a for a in args if a.startswith('--user-data-dir=')).encode() in argv and b'--type=renderer' not in argv and not any(a.startswith(b'--type=') for a in argv) for args in browser_args):roots.append(int(p.name))
            except (OSError,ValueError,StopIteration):continue
        assert len(roots)==len(sessions),('owned browser process roots',roots)
        owned=set(roots)
        while True:
            children={pid for pid,(parent,_) in processes.items() if parent in owned}
            if children<=owned:break
            owned|=children
        pss=0;read=0
        for pid in owned:
            try:
                rollup=dict(line.split(':',1) for line in (Path('/proc')/str(pid)/'smaps_rollup').read_text().splitlines() if ':' in line)
                pss+=int(rollup['Pss'].split()[0]);read+=1
            except (OSError,KeyError,ValueError):pass
        services={}
        if coordinator:
            for label,process in [('discovery',coordinator.child),('caddy',coordinator.front)]:
                assert process and process.poll() is None,'Owned '+label+' process stopped'
                proc=Path('/proc')/str(process.pid);status=dict(line.split(':',1) for line in (proc/'status').read_text().splitlines() if ':' in line)
                rollup=dict(line.split(':',1) for line in (proc/'smaps_rollup').read_text().splitlines() if ':' in line)
                ticks=(proc/'stat').read_text().rsplit(')',1)[1].split()
                services[label]={'pid':process.pid,'rssKiB':int(status['VmRSS'].split()[0]),'pssKiB':int(rollup['Pss'].split()[0]),'threads':int(status['Threads']),'openFDs':len(list((proc/'fd').iterdir())),'cpuTicks':int(ticks[11])+int(ticks[12])}
        return {'ownedBrowserRoots':roots,'ownedProcessCount':len(owned),'rssKiB':sum(processes[pid][1] for pid in owned),'pssKiB':pss,'pssReadableProcesses':read,'separateServices':services}
    def joined_graph():
        values=summaries();g={v['sid']:{e['peerId'] for e in v['peers'] if e['state']=='ready'} for v in values}
        if not all(3<=len(peers)<=6 for peers in g.values()):return False
        todo=[next(iter(g))];seen=set()
        while todo:
            n=todo.pop()
            if n in seen or n not in g:continue
            seen.add(n);todo.extend(g[n]-seen)
        return len(seen)==participants
    try:
        temporary=tempfile.TemporaryDirectory(prefix='codi-agent-load-')
        folder=Path(temporary.name)
        if reader_coordinator:
            spec=importlib.util.spec_from_file_location('load_coordinator_fixture',ROOT/'scripts/reader-coordinator-fixture.py');separate=importlib.util.module_from_spec(spec);spec.loader.exec_module(separate)
            f=fixture.Fixture(folder,front_origin=separate.front_origin())
        else:f=fixture.Fixture(folder)
        f.clock.realtime=True;public=folder/'public'
        shutil.copytree(release/graph['directory'],public/graph['directory'])
        for n,r in graph['modules'].items():
            p=public/graph['directory']/n;assert r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},n
        vendor=release/'assets/vendor/chess'
        if vendor.exists():shutil.copytree(vendor,public/'assets/vendor/chess')
        (public/'network-release.json').write_bytes((release/'assets/desktop/network-release.json').read_bytes())
        code=(ROOT/'scripts/hosted-peer-page.mjs').read_text().replace('./network/','/'+graph['directory']+'/');(public/'fixture.mjs').write_text(code)
        for src,dest in [('hosted-agent-loader.mjs','agent-loader.mjs'),('hosted-agent-host.mjs','agent-host.mjs')]:shutil.copyfile(ROOT/'scripts'/src,public/dest)
        if shared_storage_control:
            p=public/'agent-loader.mjs';text=p.read_text();old='prefix=`codi-agent-${run}-${index}-`';assert text.count(old)==1
            p.write_text(text.replace(old,'prefix=`codi-agent-${run}-`'))
            result['mutatedFixtureLoaderSHA256']=hashlib.sha256(p.read_bytes()).hexdigest()
        (public/'agent.html').write_text('<!doctype html><title>SDK load agent</title><script type="module" src="/agent-loader.mjs"></script>')
        (public/'index.html').write_text('<!doctype html><title>Owned agent load</title><script type="module" src="/agent-host.mjs"></script>')
        config=f.issuer.config();config['hostedRooms']=dict(version='codi-hosted-room/1',basePath='/rooms',controllerKey=f.store.public,certificatePath='/api/v1/room-control/controller',challengePath='/api/v1/room-control/challenge',authorizePath='/api/v1/room-control/authorize');(public/'fixture-config.json').write_text(json.dumps(config))
        if reader_coordinator:
            coordinator=separate.CoordinatorFixture(f,caddy)
            f.http.reader_slots.acquire();f.http.reader_slots.acquire();legacy_slots_held=True
            result.update(separateCoordinatorProcess=True,separateCaddyProcess=True,caddySHA256=hashlib.sha256(Path(caddy).read_bytes()).hexdigest(),coordinatorHTTPTransport=coordinator.http_transport,coordinatorHTTPServerSourceSHA256=coordinator.http_server_sha256)
        for first in range(0,participants,per_browser):
            s=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':chrome_binary,'args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']},'goog:loggingPrefs':{'browser':'ALL'}}}})['sessionId'];sessions.append(s)
            driver.call('/session/'+s+'/timeouts',{'script':120000});driver.call('/session/'+s+'/url',{'url':f.origin+'/?run='+run_id+('&sync=1' if atomic_sync else '')+('&recover=1' if proposal_recovery else '')+('&coordinator=1' if reader_coordinator else '')});wait(lambda:js(s,'return window.agentHostReady===true;'))
            for i in range(first,min(first+per_browser,participants)):
                owners[i]=s;task(s,'return await agentLab.start(params[0],params[0]===0);',[i])
        result['actualBrowserInstances']=len(sessions)
        policies=[v for s in sessions for v in js(s,'return agentLab.recoveryPolicy();')]
        check('every SDK agent uses the explicitly requested deployed recovery policy',len(policies)==participants and all(v is proposal_recovery for v in policies))
        modes=[v for s in sessions for v in js(s,'return agentLab.directoryPolicy();')]
        check('every SDK agent uses the explicitly requested discovery service',len(modes)==participants and all(v==('separate' if reader_coordinator else 'shared') for v in modes))
        result['resourceSampleIntervalMilliseconds']=1000
        print(json.dumps({'phase':'agents-started','agents':participants,'browsers':len(sessions)}),flush=True)
        node=act(0,'create','Independent agent positions');result['ownedRoom']=node
        act(0,'send',node,'Initial checkpoint for every agent');result['admittedAgents']=1
        # Clients run as they join, as on the desktop. An all-agents-start
        # barrier can outlive the first room's signed lease at larger loads.
        for s in sessions:js(s,'agentLab.startPump();')
        admission_started=time.monotonic()
        for i in range(1,participants):
            time.sleep(admission_interval);act(i,'open',node);result['admittedAgents']=i+1
            if i%32==0:print(json.dumps({'admitted':i+1,'total':participants}),flush=True)
        result['roomAdmissionSeconds']=round(time.monotonic()-admission_started,3)
        if failure_probe:raise RuntimeError('Owned diagnostic cleanup probe after admission')
        print(json.dumps({'phase':'channel-admission-complete','agents':participants,'elapsedSeconds':result['roomAdmissionSeconds']}),flush=True)
        inspection_started=time.monotonic();saved=[]
        for s in sessions:saved.extend(task(s,'return await agentLab.savedAll();'))
        saved.sort(key=lambda v:v['index']);counts=[next(r['floor']['count'] for r in v['rows'] if r['kind']=='room') for v in saved]
        result['storageInspectionSeconds']=round(time.monotonic()-inspection_started,3)
        check('each logical agent has a distinct native IndexedDB namespace with the verified initial floor',len(saved)==participants and [v['index'] for v in saved]==list(range(participants)) and len({v['database'] for v in saved})==participants and counts==[1]*participants)
        initial=summaries();check('all logical agents retain distinct signed identities during automatic warmup',len({v['sid'] for v in initial})==participants)
        assignment={}
        def island_graph():
            values=summaries();g={v['sid']:{p['peerId'] for p in v['peers'] if p['state']=='ready'} for v in values}
            if any(len(peers)<4 or any(assignment[p]!=assignment[sid] for p in peers) for sid,peers in g.items()):return False
            for group in [0,1]:
                expected={sid for sid in g if assignment[sid]==group};todo=[next(iter(expected))];seen=set()
                while todo:
                    sid=todo.pop()
                    if sid in seen:continue
                    seen.add(sid);todo.extend(g[sid]-seen)
                if seen!=expected:return False
            return True
        def bridges():
            return sorted({tuple(sorted([v['sid'],p['peerId']])) for v in summaries() for p in v['peers'] if p['state']=='ready' and assignment[v['sid']]!=assignment[p['peerId']]})
        if island_control:
            wait(joined_graph,180)
            assignment={v['sid']:int(v['index']>=participants//2) for v in summaries()}
            for s in sessions:js(s,'agentLab.partition(arguments[0]);',[list(assignment.items())])
            wait(island_graph,180)
            # Drain all <=30s pre-partition introductions before healing. This
            # prevents an old in-flight offer from standing in for a genuine
            # full-degree island discovery probe.
            time.sleep(35);assert island_graph(),'Owned islands lost their healthy local topology'
            check('signed connection denial forms two independent healthy islands without SDP seeds',island_graph())
        blocked=sum(js(s,'return agentLab.setReaderFallback(false);') for s in sessions)
        assert blocked==participants-1;result['httpReadBlockedAgents']=blocked
        print(json.dumps({'phase':'reader-http-blocked','agents':blocked}),flush=True)
        wait(lambda:all(not v['state']['busy'] for v in summaries()))
        act(0,'send',node,'New checkpoint accepted only after every reader HTTP path is blocked')
        if island_control:
            wait(lambda:all(v['state']['selected']['count']==2 for v in summaries() if assignment[v['sid']]==0),60)
            time.sleep(5)
            check('partitioned audience retains its old verified head while ordinary read fallback is blocked',all(v['state']['selected']['count']==1 for v in summaries() if assignment[v['sid']]==1))
            for s in sessions:js(s,'agentLab.partition(null);')
        began=time.monotonic();wait(joined_graph,240);result['bootstrapSeconds']=round(time.monotonic()-began,3)
        check('the real scoped directory and browser work form one bounded RTC graph without manual signaling',joined_graph())
        wait(lambda:all(v['state']['selected']['count']==2 for v in summaries()))
        check('independent readers acquire the later checkpoint through RTC with HTTP read fallback blocked',all(v['state']['selected']['source']=='peer' for v in summaries() if v['index']!=0))
        if island_control:
            wait(lambda:len(bridges())>=2,180);result['repairedIslandBridges']=bridges()
            check('restored discovery repairs full-degree islands with at least two real crossing links',len(bridges())>=2)
            left,right=bridges()[0];a=next(v for v in summaries() if v['sid']==left)
            task(owners[a['index']],'return agentLab.closePeer(params[0],params[1]);',[a['index'],right])
            act(0,'send',node,'State after one real bridge failed')
            wait(lambda:all(v['state']['selected']['count']==3 for v in summaries()),120)
            check('losing a crossing bridge retains peer-only accepted-state delivery to both islands',all(v['state']['selected']['source']=='peer' for v in summaries() if v['index']!=0))
        measurements=[]
        for batch in range(6):
            before=summaries();wire=sum(v['wireBytes'] for v in before);began=time.monotonic()
            task(owners[0],'for(let n=0;n<8;n++)await agentLab.send(0,params[0],`Agent batch ${params[1]} message ${n}`);return true;',[node,batch])
            count=2+int(island_control)+(batch+1)*8;wait(lambda:all(v['state']['selected']['count']==count for v in summaries()),180);values=snapshots();elapsed=time.monotonic()-began
            measurements.append({'batch':batch,'acceptedMessages':8,'convergenceSeconds':round(elapsed,3),'authenticatedApplicationBytes':sum(v['wireBytes'] for v in values)-wire,'maxRetainedRecords':max(len(v['state']['selected']['records']) for v in values),'chromeJSHeaps':[driver.call('/session/'+s+'/goog/cdp/execute',{'cmd':'Runtime.getHeapUsage','params':{}})['usedSize'] for s in sessions],'nativeMemory':memory()})
            check('batch '+str(batch)+' converges with bounded retained records and no duplicate retained operation',all(len(v['state']['selected']['records'])<=32 and len({r['eventId'] for r in v['state']['selected']['records']})==len(v['state']['selected']['records']) for v in values))
        result['measurements']=measurements
        steady=[];began=time.monotonic()
        if steady_seconds:
            while True:
                values=summaries();check_count=all(v['state']['selected']['count']==50+int(island_control) for v in values)
                assert check_count,'Steady-state readers diverged after converged burst'
                steady.append({'elapsedSeconds':round(time.monotonic()-began,3),'nativeMemory':memory(),'authenticatedApplicationBytes':sum(v['wireBytes'] for v in values)})
                if time.monotonic()-began>=steady_seconds:break
                time.sleep(max(0,min(10,steady_seconds-(time.monotonic()-began))))
            result['steadySamples']=steady
            check('mostly-reading steady interval retains the verified head with measured browser and separate-service resources',len(steady)>=2)
        last=snapshots()
        result['identityRenewals']=sum(v['renewals'] for v in last)
        check('original identities retain valid certificates through real issuer renewal when needed',not any(v['renewalError'] for v in last))
        check('every agent crosses the retained-history window with the same verified count and explicit omission',all(v['state']['selected']['count']==50+int(island_control) and v['state']['selected']['omitted']>=18 for v in last))
        check('neighbor and automatic/pending work caps hold at the measured final state',all(len(v['state']['delivery']['readers']['members'])<=6 and v['state']['delivery']['readers']['automaticConnections']<=8 and v['state']['delivery']['readers']['pending']<=4 for v in last))
        result['sampledResourcePeaks']=[js(s,'return agentLab.telemetry();') for s in sessions]
        check('sampled neighbor/automatic/pending/job caps hold throughout the measured run',all(v['peaks']['neighbors']<=6 and v['peaks']['automatic']<=8 and v['peaks']['pending']<=4 and v['peaks']['jobs']<=16 for v in result['sampledResourcePeaks']))
        result['httpTelemetry']=http_stats()
        if atomic_sync:check('all reader ordinary server history operations use the single atomic request',all(not any(n for key,n in v['byOperation'].items() if key in ['ordinary:/rooms/use:describe','ordinary:/rooms/use:history','ordinary:/rooms/use:snapshot']) for v in result['httpTelemetry'] if v['index']!=0))
        cleanup=[v for s in sessions for v in task(s,'return await agentLab.close();')]
        check('all agents release every tracked lease and close their actual position databases',len(cleanup)==participants and all(not any(x for k,x in v['budget'].items() if k!='closed') for v in cleanup))
        if reader_coordinator:check('legacy saved-chat discovery slots remain saturated and unused by every agent',f.http.reader_rates=={})
        result.update(status='PASS',resourceCleanup=cleanup,independentInitialFloors=counts,serverDirectory=f.store.rendezvous.snapshot() if not reader_coordinator else {'mode':'separate','legacyReaderRequests':0,'privateCoordinatorSnapshotExposed':False})
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc(),diagnostics=[])
        result['fixturePresentDuringDiagnostics']=bool(temporary and Path(temporary.name).is_dir() and f and f.state.is_dir())
        if coordinator and getattr(coordinator,'logfile',None) and coordinator.logfile.exists():
            with coordinator.logfile.open('rb') as errors:errors.seek(max(0,coordinator.logfile.stat().st_size-6000));result['coordinatorDiagnosticTail']=errors.read().decode(errors='replace')
        try:result['httpTelemetry']=http_stats()
        except Exception as failure:result['httpTelemetryError']=str(failure)
        if f:result['ordinaryServerRateState']={k:list(v) for k,v in f.http.rates.items()}
        for s in sessions:
            try:result['diagnostics'].append({'actors':js(s,'return window.agentLab?.snapshots(arguments[0]);',[result.get('ownedRoom')]),'logs':driver.call('/session/'+s+'/log',{'type':'browser'})})
            except Exception as failure:result['diagnostics'].append({'error':str(failure)})
    finally:
        for s in sessions:
            if result['status']!='PASS':
                try:result.setdefault('failureResourceCleanup',[]).extend(task(s,'return await agentLab.close();'))
                except Exception as error:result.setdefault('cleanupErrors',[]).append(str(error))
            try:driver.call('/session/'+s,method='DELETE')
            except Exception as error:result.setdefault('cleanupErrors',[]).append(str(error));result['status']='FAIL'
        try:
            if legacy_slots_held:f.http.reader_slots.release();f.http.reader_slots.release()
            if coordinator:coordinator.close()
            if f:f.close()
        finally:
            # Preserve fixture files until browser diagnostics and owned clients stop.
            if temporary:
                temporary.cleanup();result['temporaryFixtureRemoved']=not Path(temporary.name).exists()
    result.update(sourceSHA256=pins,sourceChangedDuringTest=any(hashlib.sha256(Path(n).read_bytes()).hexdigest()!=p for n,p in pins.items()))
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--participants',type=int,choices=[4,16,128,512,2048,8000],default=4);p.add_argument('--per-browser',type=int,default=32);p.add_argument('--admission-interval',type=float,default=.6);p.add_argument('--atomic-sync',action='store_true');p.add_argument('--shared-storage-control',action='store_true',help='Owned negative control: intentionally share agent storage and expect isolation failure');p.add_argument('--proposal-recovery',action='store_true',help='Match current deployed SDK construction');p.add_argument('--reader-coordinator',action='store_true');p.add_argument('--caddy',type=Path);p.add_argument('--steady-seconds',type=int,default=0);p.add_argument('--island-control',action='store_true');p.add_argument('--failure-probe',action='store_true',help='Owned four-agent failure to verify diagnostic and teardown ordering');p.add_argument('--chrome-binary',type=Path,default=Path('/snap/chromium/current/usr/lib/chromium-browser/chrome'));p.add_argument('--driver-url',default=driver.DRIVER);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert 1<=a.per_browser<=32 and a.admission_interval>=0 and not a.output.exists() and (not a.failure_probe or a.participants==4)
    assert 0<=a.steady_seconds<=600
    assert not a.island_control or a.reader_coordinator and a.participants==16
    assert not a.reader_coordinator or a.caddy and a.caddy.is_absolute() and a.caddy.is_file(),'Separate coordinator load requires pinned actual Caddy binary'
    endpoint=urlsplit(a.driver_url);assert endpoint.scheme=='http' and endpoint.hostname in ['127.0.0.1','localhost'] and endpoint.port and not endpoint.path and not endpoint.query and not endpoint.fragment and not endpoint.username and not endpoint.password
    assert a.chrome_binary.is_absolute() and a.chrome_binary.is_file();driver.DRIVER=a.driver_url
    v=run(a.release.resolve(),a.participants,a.per_browser,a.admission_interval,a.atomic_sync,a.shared_storage_control,str(a.chrome_binary),a.failure_probe,a.proposal_recovery,a.reader_coordinator,a.caddy,a.steady_seconds,a.island_control);a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'agents':a.participants,'browsers':v['actualBrowserInstances'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
