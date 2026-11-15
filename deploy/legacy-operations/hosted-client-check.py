#!/usr/bin/env python3
"""Real HTTP/SQLite/WebCrypto/IndexedDB and generically bundled hosted app views.

Owned temporary source fixture, one actual Chrome, zero v86 guests. Not native20
installation, complete Rooms integration, public WAN, P2P transport or8k proof.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fixture=module('hosted_client_fixture',ROOT/'scripts/hosted-room-check.py');driver=module('hosted_client_driver',ROOT/'scripts/touch-preview-check.py');builder=module('hosted_client_apps',ROOT/'scripts/build-public-apps.py')
class LiveClock(fixture.Clock):
    def __call__(self):return int(time.time())+getattr(self,'offset',0) if getattr(self,'realtime',True) else self.value
fixture.Clock=LiveClock


def run(network_root=ROOT/'network'):
    result={'status':'FAIL','scope':__doc__,'productionChanged':False,'privateVMChanged':False,'actualBrowsers':1,'actualV86Desktops':0,'privateKeysUploaded':False};session=None;f=None
    sources=[Path(__file__),ROOT/'scripts/hosted-client-page.mjs',ROOT/'scripts/hosted-room-check.py',ROOT/'origin_service/room_authority.py',*sorted((ROOT/'room_service').glob('*.py')),*sorted(network_root.glob('*.mjs')),ROOT.parent/'served_apps_public/rooms/hosted-view.mjs',ROOT.parent/'served_apps_public/rooms/mesh-view.css']
    pins={str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    try:
        with tempfile.TemporaryDirectory(prefix='codi-hosted-client-') as temporary:
            folder=Path(temporary);f=fixture.Fixture(folder)
            f.clock.realtime=False;f.clock.value-=15*86400
            old=fixture.Actor(f,'lease_owner');created=old.operation('create',{'request_id':secrets.token_urlsafe(32),'label':'Long absence public chat'});node=fixture.jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id'];accepted=[]
            for n in [1,2]:accepted.append(old.operation('accept',{'node_id':node,'grant':created['grant'],'event':old.origin(created['grant'],n,'Old accepted note'+str(n))}))
            old_boot=old.operation('describe',{'node_id':node});old_now=int(f.clock())
            for _ in range(2):f.clock.value+=200;old.operation('describe',{'node_id':node})
            f.clock.realtime=True;f.reopen();returned=fixture.Actor(f,'lease_owner',signin=True);boot=returned.operation('describe',{'node_id':node});old_lease=fixture.jose.inspect(old_boot['lease'],fixture.LEASE_TYPE)[1]
            after={'revision':old_lease['revision'],'hash':fixture.token_id(old_boot['lease'],fixture.LEASE_TYPE)};bridge=returned.operation('lease_bridge',{'node_id':node,'after':after})
            returned.operation('lease_bridge',{'node_id':node,'after':{**after,'hash':secrets.token_urlsafe(32)}},expected=409)
            p=fixture.jose.inspect(bridge['proof'],fixture.LEASE_BRIDGE_TYPE)[1];p['from']['hash']=secrets.token_urlsafe(32);bad_bridge={'proof':fixture.jose.sign(p,f.store.key,fixture.LEASE_BRIDGE_TYPE)}
            event_id=fixture.jose.inspect(accepted[0]['receipt'],fixture.RECEIPT_TYPE)[1]['event_id'];lookup=returned.operation('lookup',{'node_id':node,'event_id':event_id});bad_lookup={**lookup,'receipt':accepted[1]['receipt']}
            (folder/'public/authority-fixture.json').write_text(fixture.jose.dumps({'node':node,'now':int(f.clock()),'oldNow':old_now,'oldBootstrap':old_boot,'bootstrap':boot,'bridge':bridge,'badBridge':bad_bridge,'lookup':lookup,'badLookup':bad_lookup,'eventId':event_id}))
            config=f.issuer.config();config['hostedRooms']={'version':'codi-hosted-room/1','basePath':'/rooms','controllerKey':f.store.public,'certificatePath':'/api/v1/room-control/controller','challengePath':'/api/v1/room-control/challenge','authorizePath':'/api/v1/room-control/authorize'}
            source=folder/'app-source/rooms';source.mkdir(parents=True)
            for name in ['hosted-view.mjs','mesh-view.css']:shutil.copyfile(ROOT.parent/'served_apps_public/rooms'/name,source/name)
            (source/'index.mjs').write_text("export {mountHostedView as mount} from './hosted-view.mjs';\n")
            assets=folder/'public/assets/desktop';build=builder.build(source.parent,assets,['rooms'],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'))
            public=folder/'public';(public/'fixture-config.json').write_text(json.dumps(config));(public/'index.html').write_text('<!doctype html><title>Hosted client source acceptance</title><script type="module" src="/fixture.mjs"></script>')
            shutil.copyfile(ROOT/'scripts/hosted-client-page.mjs',public/'fixture.mjs');shutil.copytree(network_root,public/'network',ignore=shutil.ignore_patterns('*.md'))
            session=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId'];driver.call('/session/'+session+'/timeouts',{'script':120000})
            def ready():driver.wait(lambda:driver.call('/session/'+session+'/execute/sync',{'script':'return window.hostedClientReady===true;','args':[]}),30)
            def phase(name,args):
                value=driver.call('/session/'+session+'/execute/async',{'script':'const args=arguments,done=args[args.length-1];window.'+name+'(...Array.from(args).slice(0,-1)).then(done,e=>done({status:"FAIL",checks:window.hostedClientChecks||[],error:e.stack}));','args':args});print(json.dumps({'phase':name,'status':value['status'],'checks':len(value.get('checks',[])),'error':value.get('error')}),flush=True);return value
            driver.call('/session/'+session+'/url',{'url':f.origin+'/'});ready();password=secrets.token_urlsafe(32)
            first=phase('phaseOne',[password]);result['phaseOne']=first;assert first['status']=='PASS',first.get('error')
            with f.store.lock(),f.store.db() as db:assert db.execute('SELECT count(*) FROM rooms WHERE owner=?',(first['subject'],)).fetchone()==(2,)
            driver.call('/session/'+session+'/refresh',{});ready();second=phase('phaseTwo',[password,first]);result['phaseTwo']=second;assert second['status']=='PASS',second.get('error')
            preparing=phase('prepareExpiry',[password,second['other']]);result['expiryPreparation']=preparing;assert preparing['status']=='PASS',preparing.get('error')
            f.clock.offset=120;finished=phase('finishExpiry',[]);result['expiryFinish']=finished;assert finished['status']=='PASS',finished.get('error')
            with f.store.lock(),f.store.db() as db:
                assert db.execute('SELECT count(*) FROM rooms WHERE owner=?',(first['subject'],)).fetchone()==(2,)
                assert db.execute('SELECT count(*) FROM events WHERE node=?',(first['node'],)).fetchone()==(4,)
            result.update(status='PASS',checks=first['checks']+finished['checks'],actualPageReload=True,genericAppBundle=build,exactCommittedMessageCount=4,creationRetriesDidNotDuplicateRooms=True,expiryClockAdvancedSeconds=120)
    except Exception as error:
        import traceback;result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if session:driver.call('/session/'+session,method='DELETE');result['ownedBrowserContextsClosed']=1
        if f:f.close()
    result['sourceSHA256']=pins;result['sourceChangedDuringTest']=any(hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()!=pin for name,pin in pins.items())
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--network-root',type=Path,default=ROOT/'network');a=p.parse_args();assert not a.output.exists();v=run(a.network_root.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v.get('checks',[])),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
