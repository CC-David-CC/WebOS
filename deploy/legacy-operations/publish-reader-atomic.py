#!/usr/bin/env python3
"""Pinned atomic-read/backoff update of the externally reachable development site.

Stage both graphs, activate the backward-compatible worker first, then the SDK.
Rollback selects the previous SDK before its worker. Existing managed journals
recover code only; account/file/room state and authority floors are never reset.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import time

OLD='68085c9b1162d3fd70efb84804e373418e5babb9a2cccfc2aa6149087dc1d52a'
NEW='138a5129e7f64f5dc735492af640562c1d208083a6a0cec73ad20a1c2faf84ef'
OLD_DIR=Path('/srv/codi-connected/releases/native25-'+OLD[:16])
DEST=Path('/srv/codi-connected/releases/native25-'+NEW[:16])
OLD_WORKER='3a6d3c5184e52858abe324e37fd4ca410f66d7d289468efe6f169352d347727b'
WORKER='870df3f9fd7efc2dbb1d5256da98476662c1ea5df95ae987c75e1472ebfd14d4'
WORKER_DIR=Path('/srv/codi-rooms/workers')/WORKER
OLD_WORKER_DIR=Path('/srv/codi-rooms/workers')/OLD_WORKER
OPERATOR_PIN='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc'
OPERATOR=Path('/srv/codi-rooms/operators')/OPERATOR_PIN
HELPER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
BASELINE=Path('/srv/codi-connected/hosted-peer-inspect-1792890782972029188-result.json')
ROOT4_RECEIPT=Path('/srv/codi-connected/explicit-root4-renewal-1792923955401574954-result.json')
ROOT4_RECEIPT_SHA='4b899c22a953dbb8cbd9569d465dbcaa60f45a618062f6696f4d7f903185d50c'
TRANSITION_SHA='636ddac01c1c87d5eb84284b9aa5ba592f9f97f6addc4826afe644a9bd8565a2'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def main(action,commit):
    assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
    assert sha(HELPER)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    m=module('atomic_publish_helper',HELPER);m.protected(HELPER);m.NATIVE_DIR=DEST;m.OPERATOR_DIR=OPERATOR
    transition=Path(__file__).with_name('reader-backend-transition.py');m.protected(transition);assert sha(transition)==TRANSITION_SHA
    b=module('atomic_publish_transition',transition)
    m.protected(ROOT4_RECEIPT);assert sha(ROOT4_RECEIPT)==ROOT4_RECEIPT_SHA
    renewal=json.loads(ROOT4_RECEIPT.read_bytes());assert renewal['status']=='PASS' and renewal['operatorResult']['revision']==4

    def preserved(before,c):
        now=m.capture(c)
        for key in ['keys','cookie','fileConfig','filesPIDs','website','prototypeManifest','blog']:assert now[key]==before[key],key
        for key in ['accounts','users','permissions']:assert set(before[key])<=set(now[key]),key
        for name,pin in before['documents'].items():assert now['documents'].get(name)==pin,name
        for name in ['issuerKeyId','rootKeyId','realm','serviceKeyId']:
            assert now['authorityBinding'][name]==before['authorityBinding'][name]==renewal['after']['authorityBinding'][name],name
        assert before['authorityBinding']['rootRevision'] in [3,4] and now['authorityBinding']['rootRevision']==4
        assert now['authorityBinding']['publisherRevision']>=before['authorityBinding']['publisherRevision']
        fence=json.loads((m.CONTROL.parent/'recovery-fence.json').read_bytes());assert fence['rootFloor']==4
        for name in ['issuerKeyId','rootKeyId','realm']:assert fence[name]==now['authorityBinding'][name],name
        return now

    def config():
        m.protected(m.CONTROL);c=json.loads(m.CONTROL.read_bytes())
        assert c['version']=='codi-managed-instance/5' and c['basePath']=='' and c['origin']=='https://ksu.codes' and c['instance']=='codi-ksu-hidden'
        assert c['stateRoot']=='/var/lib/codi-connected/ksu' and c['python']==str(m.PYTHON)
        assert (c['manifestSHA256'],c['release']) in [(OLD,str(OLD_DIR)),(NEW,str(DEST))]
        assert sha(Path(c['release'])/'connected-release.json')==c['manifestSHA256']
        assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
        if action not in ['recover-backend','recover-native']:
            assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json','reader-backend-transition.json'])
            assert c.get('hostedRooms')
        return c

    def backend():
        op=module('atomic_publish_rooms',OPERATOR/'room_service/operator.py').Manager(m.ROOM_CONFIG)
        with op.locked():
            c=op.load();assert c['manifestSHA256'] in [OLD_WORKER,WORKER]
            return c,op.inspect(c),op.health(c)

    def usage(c):
        state=Path(json.loads(Path(c['guestNetwork']['configFile']).read_bytes())['stateRoot']);out={}
        for role in ['anonymous','registered']:
            with sqlite3.connect('file:'+str(state/role/'usage.sqlite3')+'?mode=ro',uri=True) as db:out[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
        return out

    def verified():
        contract=module('atomic_publish_contract',DEST/'origin_service/release.py');v=contract.verify(DEST);assert v['manifestSHA256']==NEW and v['files']==340
        previous=json.loads((OLD_DIR/'connected-release.json').read_bytes())['files'];new=json.loads((DEST/'connected-release.json').read_bytes())['files']
        assert all(new[n]==previous[n] for n in contract.V19_NATIVE)
        assert all(new[n]==r for n,r in previous.items() if '/apps/' in n)
        b.graph(OPERATOR,'room-operator.json',OPERATOR_PIN,b.OPERATOR_FILES)
        old=b.graph(OLD_WORKER_DIR,'room-worker.json',OLD_WORKER);new_worker=b.graph(WORKER_DIR,'room-worker.json',WORKER)
        assert old['version']==new_worker['version']=='codi-hosted-room-worker/2'
        assert old['files'].keys()==new_worker['files'].keys()
        assert {n for n,r in old['files'].items() if new_worker['files'][n]!=r}=={'room_service/store.py','room_service/http.py','room_service/access.py'}
        return v

    def notice(c,fn):
        args=[m.PYTHON,'-I','-B',Path(c['release'])/'scripts/desktop-maintenance.py','--directory',Path(c['stateRoot'])/'public']
        scheduled=json.loads(m.run([*args,'scheduled','--in-seconds','10','--duration','240','--message','Development update in 10 seconds. Please save your work. Unsaved browser work is not backed up.']))
        time.sleep(10);finished=False
        try:value=fn();finished=True;return {'scheduledNotice':scheduled,'operation':value}
        finally:m.run([*args,'cancelled','--duration','120','--message','Development update finished. Reload to load the current version. Unsaved browser work was not backed up.' if finished else 'Development update interrupted; recovery may be needed. Unsaved browser work was not backed up.'])

    with (m.HOST/'.controller.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        git=lambda *args:m.run(['runuser','-u','dflanag3','--','git','-C',m.REPO,*args])
        assert git('rev-parse','HEAD')==commit and not git('status','--porcelain') and m.hosting_pins()==m.NEW_PINS
        c=config();before=m.capture(c);used=usage(c)
        # A recovery may start with a deliberately stopped/unbound backend.
        bc,bs,bh=backend() if action not in ['recover-backend','recover-native'] else (None,None,None)
        result={'status':'PASS','action':action,'sourceCommit':commit,'beforeManifestSHA256':c['manifestSHA256']}
        if action=='stage':
            assert c['manifestSHA256']==OLD and bc['manifestSHA256']==OLD_WORKER
            package=m.REPO/'tools/codiserver/reader-atomic-update-r1'
            m.install(package/'release',DEST,'connected-release.json',NEW)
            m.install(package/'worker',WORKER_DIR,'room-worker.json',WORKER)
            result['releaseVerification']=verified();result.update(nativeNotActivated=True,backendNotActivated=True)
        elif action in ['activate-backend','rollback-backend','recover-backend']:
            result['releaseVerification']=verified()
            # The same retained controller owns every backend journal, including
            # recovery after the new frontend is active. Its native bytes agree.
            t=b.Transition(m.CONTROL,m.ROOM_CONFIG/'managed.json',OPERATOR,OPERATOR_PIN,OLD_DIR,OLD)
            if action=='activate-backend':result['backend']=notice(c,lambda:t.apply(WORKER_DIR,WORKER))
            elif action=='rollback-backend':
                assert c['manifestSHA256']==OLD,'Select the previous SDK before rolling back its worker'
                result['backend']=notice(c,lambda:t.apply(OLD_WORKER_DIR,OLD_WORKER))
            else:result['backend']=t.recover()
        elif action in ['activate','rollback-native']:
            result['releaseVerification']=verified()
            assert bc['manifestSHA256']==WORKER,'Activate the compatible worker before the new SDK'
            target=DEST if action=='activate' else OLD_DIR;pin=NEW if action=='activate' else OLD
            if c['manifestSHA256']==pin:result['operation']={'status':'already-current','servicesRestarted':False}
            else:
                result['native']=notice(c,lambda:m.native('upgrade','--release',target,'--python',m.PYTHON));assert result['native']['operation']['status']=='upgraded'
            assert config()['manifestSHA256']==pin
        elif action=='recover-native':
            assert not (m.CONTROL.parent/'reader-backend-transition.json').exists()
            result['operation']=m.native('recover-operation')
        elif action=='verify':
            result['releaseVerification']=verified();result['nativeStatus']=m.native('status')
            assert sha(BASELINE)=='43fb53090747c89c43f9b64012416a75a54a21fdf5ad36a1b3f184e860b98e5f'
            preserved(json.loads(BASELINE.read_bytes())['state'],c)
        else:raise ValueError('Unknown action')
        after=config();result['state']=preserved(before,after);ac,ast,ah=backend()
        retained=module('atomic_publish_retained',OPERATOR/'room_service/operator.py').retained
        if bs is not None:assert retained(bs,ast)
        if action not in ['activate-backend','rollback-backend','recover-backend','recover-native']:assert ac==bc and ah==bh
        assert after['manifestSHA256']!=NEW or ac['manifestSHA256']==WORKER
        current=usage(after)
        for role,rows in used.items():
            values={(r[0],r[1]):r[2:] for r in current[role]}
            assert all((r[0],r[1]) in values and all(a>=b for a,b in zip(values[(r[0],r[1])],r[2:])) for r in rows)
        assert m.hosting_pins()==m.NEW_PINS
        result.update(afterManifestSHA256=after['manifestSHA256'],nativeConfigSHA256=sha(m.CONTROL),roomWorkerManifestSHA256=ac['manifestSHA256'],roomHealth=ah,guestUsageFloorsPreserved=True,hostingUnchanged=True,routerPortsChanged=False,bootPolicyChanged=False,dataRestored=False,rootMinted=False)
        return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','activate-backend','rollback-backend','recover-backend','activate','rollback-native','recover-native','verify']);p.add_argument('--commit',required=True);a=p.parse_args()
    try:v=main(a.action,a.commit)
    except Exception as error:
        import traceback
        v={'status':'FAIL','action':a.action,'error':str(error),'traceback':traceback.format_exc(),'recoveryRequired':'Inspect managed backend/native journals; recover code without restoring user data'}
    receipt=Path('/srv/codi-connected')/('reader-atomic-'+a.action+'-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(v,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':v['status'],'action':a.action,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt),'manifestSHA256':v.get('afterManifestSHA256'),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
