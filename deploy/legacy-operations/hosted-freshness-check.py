#!/usr/bin/env python3
"""Four actual Chrome clients relay fresh authority for unchanged public history.

Real issuer/SQLite/signatures/RTC/state windows and native IndexedDB. Followers
cannot read HTTP; only the registered owner refreshes its existing membership.
Not v86, public WAN, replica agreement, long-game or scale acceptance.
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
spec=importlib.util.spec_from_file_location('freshness_support',ROOT/'scripts/hosted-peer-check.py')
support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
fixture,driver=support.fixture,support.driver

def run(network):
    sessions=[];checks=[];f=None
    sources=[Path(__file__),ROOT/'scripts/hosted-peer-page.mjs',*sorted(network.glob('*.mjs'))]
    pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    result={'status':'FAIL','scope':__doc__,'checks':checks,'actualBrowserInstances':4,'actualV86Desktops':0,'wholeGoalComplete':False}
    def js(s,code,args=[]):return driver.call('/session/'+s+'/execute/sync',{'script':code,'args':args})
    def task(s,code,args=[]):
        value=driver.call('/session/'+s+'/execute/async',{'script':'const params=Array.from(arguments),done=params.pop();(async()=>{'+code+'})().then(value=>done({ok:true,value}),error=>done({ok:false,error:error.stack}));','args':args});assert value['ok'],value;return value.get('value')
    def wait(fn,seconds=30):return driver.wait(fn,seconds)
    def check(name,ok):assert ok,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def snap(s):return js(s,'return client.snapshot(arguments[0]);',[node])
    def idle(s):wait(lambda:not snap(s)['busy'])
    def connect(a,b):
        offer=task(a,'const r=await pool.offer();return {id:r.entry.id,token:r.token};')
        answer=task(b,'const r=await pool.answer(params[0]);return {id:r.entry.id,token:r.token};',[offer['token']])
        task(a,'await pool.accept(params[0],params[1]);return true;',[offer['id'],answer['token']])
        wait(lambda:js(a,'return pool.get(arguments[0]).link.hostedWindowReady;',[offer['id']]))
        wait(lambda:js(b,'return pool.get(arguments[0]).link.hostedWindowReady;',[answer['id']]))
        js(a,'instrument(arguments[0]);',[offer['id']]);js(b,'instrument(arguments[0]);',[answer['id']]);return offer['id'],answer['id']
    try:
        with tempfile.TemporaryDirectory(prefix='codi-freshness-') as folder:
            folder=Path(folder);f=fixture.Fixture(folder);f.clock.realtime=True;public=folder/'public'
            shutil.copytree(network,public/'network',ignore=shutil.ignore_patterns('*.md'))
            shutil.copyfile(ROOT/'scripts/hosted-peer-page.mjs',public/'fixture.mjs')
            (public/'loader.mjs').write_text('import("./fixture.mjs").catch(e=>window.fixtureFatal=e.stack);')
            (public/'index.html').write_text('<!doctype html><title>Checkpoint freshness fixture</title><script type="module" src="/loader.mjs"></script>')
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'}
            (public/'fixture-config.json').write_text(json.dumps(config))
            for suffix in ['?window=1&owner=1','?window=1','?window=1','?window=1']:
                s=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];sessions.append(s)
                driver.call('/session/'+s+'/timeouts',{'script':120000});driver.call('/session/'+s+'/url',{'url':f.origin+'/'+suffix})
                wait(lambda:js(s,'if(window.fixtureFatal)throw Error(fixtureFatal);return window.fixtureReady===true;'))
            a,b,c,d=sessions;node=task(a,'return await client.create("Quiet signed history");')
            task(a,'await client.send(params[0],"Only one accepted message");return true;',[node])
            for s in [b,c,d]:task(s,'await client.open(params[0]);return true;',[node])
            ab,ba=connect(a,b);bc,cb=connect(b,c);cd,dc=connect(c,d)
            for s in [b,c,d]:task(s,'await client.open(params[0]);return true;',[node])
            js(a,'window.oldPacket=structuredClone(servedPackets.get(arguments[0]));',[ab])
            check('four separate real identities use a three-edge RTC chain and one accepted history',len({js(s,'return currentSession.public.sid;') for s in sessions})==4 and all(snap(s)['selected']['count']==1 for s in sessions) and all(snap(s)['selected']['source']=='peer' for s in [b,c,d]))
            for s in [b,c,d]:
                js(s,"window.blockedReads=0;const native=fetch;window.fetch=(u,o)=>{const p=typeof u==='string'?u:u.url;if(p.includes('/rooms/')||p.includes('/api/v1/room-control/')){blockedReads++;return Promise.reject(new TypeError('Follower HTTP read blocked'));}return native(u,o);};")
            for s in sessions:js(s,'window.ownedTick=setInterval(()=>client.tick(),100);')
            began=time.monotonic();rounds=[]
            for epoch in range(3):
                time.sleep(12);before=[snap(s)['delivery']['peerLoads'] for s in [b,c,d]];idle(a)
                task(a,'await client.join(params[0]);return true;',[node]);started=time.monotonic()
                wait(lambda:all(snap(s)['delivery']['peerLoads']>n for s,n in zip([b,c,d],before)),5)
                values=[snap(s) for s in [b,c,d]]
                owner_head=snap(a)['selected']['headExpiresAt']
                check('unchanged-head freshness crosses all three RTC hops, epoch '+str(epoch),all(v['selected']['count']==1 and v['selected']['source']=='peer' and v['selected']['headExpiresAt']>=owner_head and not v['selected']['error'] for v in values))
                rounds.append({'epoch':epoch,'convergenceSeconds':round(time.monotonic()-started,3)})
                if epoch==0:
                    # The old proof is authentic and still unexpired. Cut the
                    # other real route so this read must confront the old peer.
                    js(b,'pool.closeEntry(arguments[0]);',[bc]);wait(lambda:js(b,'return pool.list().filter(e=>e.state==="ready").length===1;'))
                    task(a,"const e=pool.get(params[0]);window.restoreFreshSend=e.link.sendHostedApplication.bind(e.link);e.link.sendHostedApplication=async(body,kind)=>{if(body.op!=='chunk')return restoreFreshSend(body,kind);if(body.part)return;const raw=new TextEncoder().encode(JSON.stringify(oldPacket)),total=Math.ceil(raw.length/8192);for(let part=0;part<total;part++){const bytes=raw.subarray(part*8192,(part+1)*8192);let text='';for(const n of bytes)text+=String.fromCharCode(n);await restoreFreshSend({...body,part,total,data:btoa(text).replace(/=/g,'').replace(/\\+/g,'-').replace(/\\//g,'_')},kind);}};return true;",[ab])
                    before_floor=snap(b)['selected'];refused=snap(b)['delivery']['peerRefusals']
                    rejected_read=task(b,"try{await client.open(params[0]);return false;}catch(e){return e.message.includes('Follower HTTP read blocked');}",[node])
                    after_floor=snap(b)['selected']
                    check('an authentic unexpired older head cannot lower session freshness or advance history',rejected_read and after_floor['headExpiresAt']==before_floor['headExpiresAt'] and after_floor['count']==1 and snap(b)['delivery']['peerRefusals']>refused)
                    js(a,'pool.get(arguments[0]).link.sendHostedApplication=restoreFreshSend;',[ab]);bc,cb=connect(b,c)
                    # New links have no room subscriptions. Re-establish the
                    # real read path; reconnecting must not disclose bookmarks.
                    js(c,'pool.closeEntry(arguments[0]);',[cd]);wait(lambda:js(c,'return pool.list().filter(e=>e.state==="ready").length===1;'))
                    task(c,'await client.open(params[0]);return true;',[node]);cd,dc=connect(c,d)
                    task(d,'await client.open(params[0]);return true;',[node])
                    # Exclude the deliberate rejected-read fallback probe from
                    # the following ordinary propagation/no-HTTP assertion.
                    js(b,'window.deliberateReadProbes=blockedReads;blockedReads=0;')
            check('fresh authorized history survives beyond the original thirty-second head expiry without follower HTTP',time.monotonic()-began>30 and all(js(s,'return blockedReads;')==0 for s in [b,c,d]))
            rejected=snap(b)['delivery']['peer']['rejected']
            task(a,"const e=pool.get(params[0]),p=structuredClone(servedPackets.get(params[0]).bootstrap),parts=p.head.split('.'),body=JSON.parse(atob(parts[1].replace(/-/g,'+').replace(/_/g,'/')));body.exp+=60;parts[1]=btoa(JSON.stringify(body)).replace(/=/g,'').replace(/\\+/g,'-').replace(/\\//g,'_');p.head=parts.join('.');await e.link.sendHostedApplication({op:'notice',node:params[1],bootstrap:p});return true;",[ab,node])
            wait(lambda:snap(b)['delivery']['peer']['rejected']>rejected)
            check('an outer-authenticated notice with forged inner head expiry is rejected without changing history',snap(b)['selected']['count']==1 and not snap(b)['selected']['error'])
            cleanup=[]
            for s in sessions:cleanup.append(task(s,"clearInterval(ownedTick);await client.close();pool.close();const {sessionBudget}=await import('/network/resource-budget.mjs');return sessionBudget(currentSession).snapshot();"))
            check('every client releases all tracked leases after freshness work',all(not any(v for k,v in x.items() if k!='closed') for x in cleanup))
            result.update(status='PASS',rounds=rounds,resourceCleanup=cleanup,serverAcceptedMessages=1)
    except Exception as error:
        result.update(error=str(error),traceback=traceback.format_exc(),diagnostics=[])
        for s in sessions:
            try:result['diagnostics'].append(snap(s))
            except Exception as failure:result['diagnostics'].append({'error':str(failure)})
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
    v=run(a.network_root.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
