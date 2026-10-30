#!/usr/bin/env python3
"""Actual HTTP/SQLite signed chat-state checkpoint and Chrome proof acceptance.

Owned temporary fixtures only. No native install, desktop integration, durable
browser floor store, chess state, quorum, P2P, real15day wait, WAN or8k claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
fixture=module('snapshot_http_fixture',ROOT/'scripts/hosted-room-check.py')
driver=module('snapshot_browser_driver',ROOT/'scripts/touch-preview-check.py')


def run(network_root):
    checks=[];result={'status':'FAIL','scope':__doc__,'checks':checks,'productionChanged':False,'privateVMChanged':False,
        'actualLoopbackHTTP':True,'actualBrowsers':1,'desktopIntegrated':False,'privateKeysUploaded':False,'wholeGoalComplete':False}
    session=None;f=None
    sources=[Path(__file__),ROOT/'scripts/hosted-snapshot-page.mjs',ROOT/'scripts/hosted-room-check.py',ROOT/'origin_service/room_authority.py',*sorted((ROOT/'room_service').glob('*.py'))]
    pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    pins.update({'network/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in network_root.glob('*.mjs')})
    def check(name,value):assert value,name;checks.append(name);print(json.dumps({'check':name}),flush=True)
    def payload(bundle):return fixture.jose.verify(bundle['snapshot'],f.store.public,fixture.SNAPSHOT_TYPE,120000)
    try:
        with tempfile.TemporaryDirectory(prefix='codi-hosted-snapshot-') as temporary:
            folder=Path(temporary);f=fixture.Fixture(folder);owner=fixture.Actor(f,'snapshot_owner');anon=fixture.Actor(f)
            created=owner.operation('create',{'request_id':secrets.token_urlsafe(32),'label':'Checkpoint conversation'});node=fixture.jose.inspect(created['descriptor'],fixture.POLICY_TYPE)[1]['node_id'];grant=created['grant']
            empty=anon.operation('snapshot',{'node_id':node,'after':None})
            check('empty public room snapshot binds true genesis and no server folder',payload(empty)['checkpoint']['index']==0 and not payload(empty)['window']['entries'] and not (folder/'users').exists())
            for n in range(1,101):owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,n,'Saved note'+str(n))})
            bootstrap=owner.operation('describe',{'node_id':node});fresh=anon.operation('snapshot',{'node_id':node,'after':None});p=payload(fresh)
            check('actual HTTPS-independent HTTP endpoint serializes accepted100 using at most32 tail receipts',p['checkpoint']['index']==100 and 0<len(p['window']['entries'])<=32 and p['window']['start']['index']>=68 and len(fixture.jose.dumps(fresh).encode())<131072)
            first=anon.operation('history',{'node_id':node,'after':None,'limit':1});anchored=anon.operation('snapshot',{'node_id':node,'after':first['next']})
            check('server binds fast-forward to the requested exact accepted ancestor',payload(anchored)['from']==first['next'])
            anon.operation('snapshot',{'node_id':node,'after':{'index':1,'hash':secrets.token_urlsafe(32)}},expected=409)
            anon.operation('snapshot',{'node_id':node,'after':{'index':101,'hash':secrets.token_urlsafe(32)}},expected=400)
            check('wrong hash and future cursor refuse fast-forward without resetting state',True)
            f.reopen();reopened=anon.operation('snapshot',{'node_id':node,'after':None})
            check('worker reopen reproduces the same current checkpoint and recent state',payload(reopened)==p)
            for n in range(101,104):owner.operation('accept',{'node_id':node,'grant':grant,'event':owner.origin(grant,n,'Tail note'+str(n))})
            tail=anon.operation('history',{'node_id':node,'after':p['checkpoint'],'limit':64})
            check('history after snapshot transfers only three newer accepted records',len(tail['entries'])==3 and tail['next']['index']==103 and tail['complete'])
            latest=owner.operation('describe',{'node_id':node})
            def forged(change):
                q=json.loads(fixture.jose.dumps(payload(anchored)));change(q)
                return {**anchored,'snapshot':fixture.jose.sign(q,f.store.key,fixture.SNAPSHOT_TYPE)}
            bad={
                'wrong requested ancestor hash':forged(lambda q:q['from'].update(hash=secrets.token_urlsafe(32))),
                'wrong requested ancestor index':forged(lambda q:q['from'].update(index=2)),
                'wrong room':forged(lambda q:q.update(node_id=secrets.token_urlsafe(32))),
                'wrong descriptor':forged(lambda q:q.update(descriptor_hash=secrets.token_urlsafe(32))),
                'chess state substituted for chat':forged(lambda q:q.update(kind='chess/1')),
                'wrong accepted head':forged(lambda q:q['checkpoint'].update(hash=secrets.token_urlsafe(32))),
                'wrong current permission revision':forged(lambda q:q.update(permission_revision=2)),
                'missing visible tail record':forged(lambda q:q['window']['entries'].pop(0)),
                'wrong visible predecessor':forged(lambda q:q['window']['start'].update(hash=secrets.token_urlsafe(32))),
                'unexpected state field':forged(lambda q:q.update(execute='not allowed')),
            }
            # A single-record window reaches the signed head, removing unrelated
            # predecessor checks as a reason to reject the wrong lane.
            r=fixture.jose.inspect(payload(anchored)['window']['entries'][-1],fixture.RECEIPT_TYPE)[1];e=fixture.jose.inspect(r['event'],fixture.ORIGIN_TYPE)[1]
            e['lane']='chess.moves';r['event']=fixture.jose.sign(e,owner.key,fixture.ORIGIN_TYPE);r['event_id']=fixture.token_id(r['event'],fixture.ORIGIN_TYPE)
            token=fixture.jose.sign(r,f.store.key,fixture.RECEIPT_TYPE);wrong_hash=fixture.token_id(token,fixture.RECEIPT_TYPE)
            q=payload(anchored);q['window']={'start':{'index':99,'hash':r['previous_hash']},'entries':[token]};q['checkpoint']['hash']=wrong_hash
            h=fixture.jose.inspect(anchored['head'],fixture.HEAD_TYPE)[1];h['hash']=wrong_hash
            bad['signed wrong origin lane']={**anchored,'snapshot':fixture.jose.sign(q,f.store.key,fixture.SNAPSHOT_TYPE),'head':fixture.jose.sign(h,f.store.key,fixture.HEAD_TYPE)}
            fork_payload=payload(fresh);fork_payload['from']=dict(p['checkpoint']);fork_payload['checkpoint']['hash']=secrets.token_urlsafe(32)
            fork_head=fixture.jose.inspect(fresh['head'],fixture.HEAD_TYPE)[1];fork_head['hash']=fork_payload['checkpoint']['hash']
            fork={**fresh,'snapshot':fixture.jose.sign(fork_payload,f.store.key,fixture.SNAPSHOT_TYPE),'head':fixture.jose.sign(fork_head,f.store.key,fixture.HEAD_TYPE)}
            # A separate large-note room proves byte pressure, rather than only
            # counting a fixed number of tiny messages.
            big=owner.operation('create',{'request_id':secrets.token_urlsafe(32),'label':'Large notes'});big_node=fixture.jose.inspect(big['descriptor'],fixture.POLICY_TYPE)[1]['node_id']
            for n in range(1,17):owner.operation('accept',{'node_id':big_node,'grant':big['grant'],'event':owner.origin(big['grant'],n,'\U0001f600'*1024)})
            large_bootstrap=owner.operation('describe',{'node_id':big_node});large=anon.operation('snapshot',{'node_id':big_node,'after':None});lp=payload(large)
            check('maximum UTF16-size notes obey serialized byte bounds without deleting omitted history',0<len(lp['window']['entries'])<16 and lp['checkpoint']['index']==16 and len(fixture.jose.dumps(large).encode())<131072 and len(anon.operation('history',{'node_id':big_node,'after':None,'limit':1})['entries'])==1)
            old_now=int(f.clock());f.clock.value+=15*86400;f.reopen();returned=fixture.Actor(f,'snapshot_owner',signin=True)
            long_bootstrap=returned.operation('describe',{'node_id':node});long_snapshot=returned.operation('snapshot',{'node_id':node,'after':first['next']})
            check('fresh account session resumes the same room and checkpoint after simulated15days',returned.identity['sub']==owner.identity['sub'] and payload(long_snapshot)['checkpoint']['index']==103 and payload(long_snapshot)['from']==first['next'])
            data={'now':old_now,'policy':f.policy,'controllerKey':f.store.public,'bootstrap':created,'fresh':fresh,'first':first,'anchored':anchored,'tail':tail,'bad':bad,'fork':fork,'latestBootstrap':latest,'emptyBootstrap':created,'empty':empty,'largeBootstrap':large_bootstrap,'large':large,'long':{'now':int(f.clock()),'bootstrap':long_bootstrap,'snapshot':long_snapshot}}
            public=folder/'public';(public/'index.html').write_text('<!doctype html><title>Chat checkpoint proof</title><script type="module" src="/fixture.mjs"></script>');(public/'fixture.json').write_text(fixture.jose.dumps(data))
            shutil.copyfile(ROOT/'scripts/hosted-snapshot-page.mjs',public/'fixture.mjs');shutil.copytree(network_root,public/'network',ignore=shutil.ignore_patterns('*.md'))
            session=driver.call('/session',{'capabilities':{'alwaysMatch':{'browserName':'chrome','goog:chromeOptions':{'binary':'/snap/chromium/current/usr/lib/chromium-browser/chrome','args':['--headless=new','--no-sandbox','--disable-dev-shm-usage']}}}})['sessionId']
            driver.call('/session/'+session+'/timeouts',{'script':60000});driver.call('/session/'+session+'/url',{'url':f.origin+'/'})
            driver.wait(lambda:driver.call('/session/'+session+'/execute/sync',{'script':'return window.snapshotProofReady===true;','args':[]}),30)
            browser=driver.call('/session/'+session+'/execute/async',{'script':'const done=arguments[arguments.length-1];runSnapshotProofs().then(done,error=>done({status:"FAIL",checks:window.snapshotProofChecks||[],error:error.stack}));','args':[]})
            result['browser']=browser;assert browser['status']=='PASS',browser.get('error')
            check('actual Chrome independently verifies fast-forward tail and signed adversarial branches',True)
            result.update(status='PASS',serverChecks=len(checks),browserChecks=len(browser['checks']),materializedChatCheckpointImplemented=True,fullPrefixReplayRequired=False)
    except Exception as error:
        import traceback;result.update(error=str(error),traceback=traceback.format_exc())
    finally:
        if session:driver.call('/session/'+session,method='DELETE');result['ownedBrowserContextsClosed']=1
        if f:f.close()
    result['sourceSHA256']=pins;result['sourceChangedDuringTest']=any(hashlib.sha256((network_root/Path(name).name if name.startswith('network/') else ROOT/name).read_bytes()).hexdigest()!=pin for name,pin in pins.items())
    if result['sourceChangedDuringTest']:result['status']='FAIL'
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--network-root',type=Path,default=ROOT/'network');a=parser.parse_args();assert not a.output.exists()
    value=run(a.network_root);a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'serverChecks':len(value['checks']),'browserChecks':value.get('browserChecks'),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS' else 1)
