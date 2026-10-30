#!/usr/bin/env python3
"""Pinned reader-first recovery-format preparation on the native25 contract.

Uses managed upgrade/recovery and hosting lock; no backend transition, authority
renewal, data restore, route/port/firewall or boot-policy change.
Root4 retention is bound to the explicit protected renewal receipt; Root3 data
snapshots remain historical baselines and are never restored.
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

OLD='138a5129e7f64f5dc735492af640562c1d208083a6a0cec73ad20a1c2faf84ef'
NEW='e5164042e2f5b5b46cfb479afa43c5ad34137ac3427b58cc016f27881e831615'
OLD_DIR=Path('/srv/codi-connected/releases/native25-'+OLD[:16])
DEST=Path('/srv/codi-connected/releases/native25-'+NEW[:16])
HELPER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
OPERATOR=Path('/srv/codi-rooms/operators/53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc')
WORKER='870df3f9fd7efc2dbb1d5256da98476662c1ea5df95ae987c75e1472ebfd14d4'
BASELINE=Path('/srv/codi-connected/hosted-peer-inspect-1792890782972029188-result.json')
ROOT4_RECEIPT=Path('/srv/codi-connected/explicit-root4-renewal-1792923955401574954-result.json')
ROOT4_RECEIPT_SHA='4b899c22a953dbb8cbd9569d465dbcaa60f45a618062f6696f4d7f903185d50c'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(action,commit):
    assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
    assert sha(HELPER)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    spec=importlib.util.spec_from_file_location('topology_publish_helper',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.protected(HELPER);m.NATIVE_DIR=DEST
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
        if action!='recover':assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json','reader-backend-transition.json'])
        return c
    def backend():
        op=m.module('topology_publish_rooms',OPERATOR/'room_service/operator.py').Manager(m.ROOM_CONFIG)
        with op.locked():c=op.load();assert c['manifestSHA256']==WORKER;return c,op.inspect(c),op.health(c)
    def usage(c):
        state=Path(json.loads(Path(c['guestNetwork']['configFile']).read_bytes())['stateRoot']);out={}
        for role in ['anonymous','registered']:
            with sqlite3.connect('file:'+str(state/role/'usage.sqlite3')+'?mode=ro',uri=True) as db:out[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
        return out
    def verified():
        contract=m.module('topology_publish_contract',DEST/'origin_service/release.py');v=contract.verify(DEST);assert v['manifestSHA256']==NEW and v['files']==298
        previous=json.loads((OLD_DIR/'connected-release.json').read_bytes())['files'];new=json.loads((DEST/'connected-release.json').read_bytes())['files']
        assert all(new[n]==previous[n] for n in contract.V19_NATIVE)
        def catalog(folder):
            import re
            graph=json.loads((folder/'assets/desktop/network-release.json').read_bytes())
            text=(folder/graph['coreDirectory']/'desktop-apps.js').read_text()
            loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',text)[0]
            name='assets/desktop/'+re.search(r'apps-v2-[a-f0-9]{64}\.json',(folder/loader).read_text())[0]
            return {a['id']:a for a in json.loads((folder/name).read_bytes())['apps']}
        a,b=catalog(OLD_DIR),catalog(DEST);assert a.keys()==b.keys() and len(a)==7
        assert all(a[n]==b[n] for n in a if n!='rooms')
        for name,app in b.items():
            for n,r in app['files'].items():
                p=DEST/Path(app['path']).parent/n;assert r=={'bytes':p.stat().st_size,'sha256':sha(p)}
        graph=json.loads((DEST/'assets/desktop/network-release.json').read_bytes())
        assert not re.search(r'proposalRecovery\s*:\s*true',(DEST/graph['coreDirectory']/'networking.js').read_text())
        assert 'proposalRecovery=false' in (DEST/graph['directory']/'hosted-room-client.mjs').read_text()
        assert 'def _recover(' not in (Path(json.loads(m.ROOM_CONFIG.joinpath('managed.json').read_bytes())['release'])/'room_service/store.py').read_text()
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
        c=config();before=m.capture(c);used=usage(c);bc,bs,bh=backend()
        result={'status':'PASS','action':action,'sourceCommit':commit,'beforeManifestSHA256':c['manifestSHA256']}
        if action=='stage':
            assert c['manifestSHA256']==OLD;m.install(m.REPO/'tools/codiserver/reader-recovery-reader-r1/release',DEST,'connected-release.json',NEW);result['releaseVerification']=verified()
        elif action in ['activate','rollback']:
            result['releaseVerification']=verified();target=DEST if action=='activate' else OLD_DIR;pin=NEW if action=='activate' else OLD
            if c['manifestSHA256']==pin:result['operation']={'status':'already-current','servicesRestarted':False}
            else:
                result['native']=notice(c,lambda:m.native('upgrade','--release',target,'--python',m.PYTHON));assert result['native']['operation']['status']=='upgraded'
            assert config()['manifestSHA256']==pin
        elif action=='recover':result['operation']=m.native('recover-operation')
        elif action=='verify':
            result['releaseVerification']=verified();result['nativeStatus']=m.native('status')
            assert sha(BASELINE)=='43fb53090747c89c43f9b64012416a75a54a21fdf5ad36a1b3f184e860b98e5f'
            preserved(json.loads(BASELINE.read_bytes())['state'],c)
        else:raise ValueError('Unknown action')
        after=config();result['state']=preserved(before,after);ac,ast,ah=backend()
        retained=m.module('topology_publish_retained',OPERATOR/'room_service/operator.py').retained
        assert ac==bc and ah==bh and retained(bs,ast)
        current=usage(after)
        for role,rows in used.items():
            values={(r[0],r[1]):r[2:] for r in current[role]}
            assert all((r[0],r[1]) in values and all(a>=b for a,b in zip(values[(r[0],r[1])],r[2:])) for r in rows)
        assert m.hosting_pins()==m.NEW_PINS
        result.update(afterManifestSHA256=after['manifestSHA256'],nativeConfigSHA256=sha(m.CONTROL),roomHealth=ah,backendUnchanged=True,guestUsageFloorsPreserved=True,hostingUnchanged=True,routerPortsChanged=False,bootPolicyChanged=False,dataRestored=False,rootMinted=False)
        return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','activate','rollback','recover','verify']);p.add_argument('--commit',required=True);a=p.parse_args()
    try:v=main(a.action,a.commit)
    except Exception as error:
        import traceback
        v={'status':'FAIL','action':a.action,'error':str(error),'traceback':traceback.format_exc(),'recoveryRequired':'Inspect native rollout journal; recover code without restoring user data'}
    receipt=Path('/srv/codi-connected')/('recovery-reader-'+a.action+'-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(v,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':v['status'],'action':a.action,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt),'manifestSHA256':v.get('afterManifestSHA256'),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
