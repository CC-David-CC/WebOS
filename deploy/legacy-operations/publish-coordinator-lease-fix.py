#!/usr/bin/env python3
"""SDK-only correction for membership refresh across a lease boundary.

Same HTTPS ingress; existing room/account/file stores and floors are never
restored. Hosting remains byte-identical. Native code recovery uses the existing native
rollout journal; no ingress operation is performed by this publisher.
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
import sys
import time

OLD='5ac541f0e439dc0808ece01115f4aa1307e6e531449bddd7c38bfd8175c5329e'
NEW='b3c292a13b6a7c1d69f15d9c23c27a15d58009646ae030e1a7806607abcbb897'
OLD_DIR=Path('/srv/codi-connected/releases/native25-'+OLD[:16]);DEST=Path('/srv/codi-connected/releases/native25-'+NEW[:16])
HELPER=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
ROOM_OPERATOR=Path('/srv/codi-rooms/operators/53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc')
READER_OPERATOR=Path('/srv/codi-readers/operators/325e7d9eb47a882636eb8253b9fe79700f76449d1428d39f64397ee1a53699f5')
WORKER='081bd143a37d486d1984d92389c0b1eb649563d052e3e793bdbd21de7542acdf'
JOURNAL=Path('/etc/codi-readers/ksu/ingress-pending.json')
ROOT4=Path('/srv/codi-connected/explicit-root4-renewal-1792923955401574954-result.json')
ROOT4_SHA='4b899c22a953dbb8cbd9569d465dbcaa60f45a618062f6696f4d7f903185d50c'
BASE={'common.py':'7174daa24a88fab02594f5eb1eb8648eda3412ec252c4f1525c98509d66102f4','sites.toml':'df92e3ef42d24f296768af83a34282b282dcbfff2e6324b4399e1a4c3f78d4b5','Caddy':'42161b4b7235cfaadfdc884b37df2a6fe7a500c5edc897f8bd7d986a769d07c2'}
PREPARE={'common.py':'26da0e71121f385f54abf36247afd0bb575b3c5926906403cc09d735bd0e1bd9','sites.toml':'2666cf91b3d30ec45391a50e5b7943a0cfc41dc71273e9ffe6da2c68118d2ba0','Caddy':'56f8cc0ed46d0e36ebbeb5cffa92f2a6b4feac3cd2405ec18ac29b05de4ee0fc'}
ACTIVE={'common.py':'26da0e71121f385f54abf36247afd0bb575b3c5926906403cc09d735bd0e1bd9','sites.toml':'9bccf2519656c22f6f0043aa03b673fbfeac9c21e4f3928934922208914afa7e','Caddy':'2a7cbaf41186112fdc47c95af7abdbbf3689faf5b149ee72031a161743b94270'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main(action,commit):
    assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and re.fullmatch('[a-f0-9]{40}',commit)
    assert sha(HELPER)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    m=module('coordinator_publish_helpers',HELPER);m.protected(HELPER);m.OPERATOR_DIR=ROOM_OPERATOR;m.NATIVE_DIR=DEST
    m.protected(READER_OPERATOR/'reader-operator.json');assert sha(READER_OPERATOR/'reader-operator.json')==READER_OPERATOR.name
    safe=module('coordinator_publish_safe',READER_OPERATOR/'file_service/operator.py')
    packet=m.REPO/'tools/codiserver/reader-coordinator-lease-fix-r1'
    assert sha(ROOT4)==ROOT4_SHA;renewal=json.loads(ROOT4.read_bytes());assert renewal['status']=='PASS' and renewal['operatorResult']['revision']==4
    def config():
        m.protected(m.CONTROL);c=json.loads(m.CONTROL.read_bytes())
        assert c['basePath']=='' and c['origin']=='https://ksu.codes' and c['instance']=='codi-ksu-hidden' and c['python']==str(m.PYTHON)
        assert (c['manifestSHA256'],c['release']) in [(OLD,str(OLD_DIR)),(NEW,str(DEST))]
        assert sha(Path(c['release'])/'connected-release.json')==c['manifestSHA256']
        assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
        if action!='recover-native':assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json','reader-backend-transition.json'])
        return c
    def backend():
        manager=m.room_manager()
        with manager.locked():
            c=manager.load();assert c['manifestSHA256']==WORKER;return c,manager.inspect(c),manager.health(c)
    def reader():
        sys.path.insert(0,str(READER_OPERATOR))
        from reader_service.operator import Manager
        op=Manager('/etc/codi-readers/ksu')
        with op.locked():return op.health(op.load())
    def usage(c):
        root=Path(json.loads(Path(c['guestNetwork']['configFile']).read_bytes())['stateRoot']);out={}
        for role in ['anonymous','registered']:
            with sqlite3.connect('file:'+str(root/role/'usage.sqlite3')+'?mode=ro',uri=True) as db:out[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
        return out
    def preserved(before,c):
        now=m.capture(c)
        for key in ['keys','cookie','fileConfig','filesPIDs','website','prototypeManifest','blog']:assert now[key]==before[key],key
        for key in ['accounts','users','permissions']:assert set(before[key])<=set(now[key]),key
        for name,pin in before['documents'].items():assert now['documents'].get(name)==pin,name
        for key in ['issuerKeyId','rootKeyId','realm','serviceKeyId']:assert now['authorityBinding'][key]==before['authorityBinding'][key]==renewal['after']['authorityBinding'][key],key
        assert now['authorityBinding']['rootRevision']==before['authorityBinding']['rootRevision']==4
        assert now['authorityBinding']['publisherRevision']>=before['authorityBinding']['publisherRevision']
        fence=json.loads((m.CONTROL.parent/'recovery-fence.json').read_bytes());assert fence['rootFloor']==4
        return now
    def verified():
        contract=module('coordinator_publish_contract',DEST/'origin_service/release.py');v=contract.verify(DEST);assert v['manifestSHA256']==NEW and v['files']==298
        a=json.loads((OLD_DIR/'connected-release.json').read_bytes())['files'];b=json.loads((DEST/'connected-release.json').read_bytes())['files']
        assert all(a[n]==b[n] for n in contract.V19_NATIVE)
        assert all(b[n]==r for n,r in a.items() if '/apps/' in n)
        old=json.loads((OLD_DIR/'assets/desktop/network-release.json').read_bytes());new=json.loads((DEST/'assets/desktop/network-release.json').read_bytes())
        assert len(new['modules'])==len(old['modules'])==40 and old['modules'].keys()==new['modules'].keys()
        assert {n for n in old['modules'] if old['modules'][n]!=new['modules'][n]}=={'hosted-room-client.mjs'}
        assert 'readerCoordinator:true' in (DEST/new['coreDirectory']/'networking.js').read_text()
        assert 'proposalRecovery:true' in (DEST/new['coreDirectory']/'networking.js').read_text()
        assert 'readerCoordinator:true' in (OLD_DIR/old['coreDirectory']/'networking.js').read_text()
        return v
    def notice(c,fn):
        args=[m.PYTHON,'-I','-B',Path(c['release'])/'scripts/desktop-maintenance.py','--directory',Path(c['stateRoot'])/'public']
        scheduled=json.loads(m.run([*args,'scheduled','--in-seconds','10','--duration','240','--message','Development network update in 10 seconds. Please save your work. Unsaved browser work is not backed up.']))
        time.sleep(10);ok=False
        try:value=fn();ok=True;return {'scheduledNotice':scheduled,'operation':value}
        finally:m.run([*args,'cancelled','--duration','120','--message','Development update finished. Reload for the current version. Unsaved browser work was not backed up.' if ok else 'Development update interrupted; recovery may be needed. Unsaved browser work was not backed up.'])
    with (m.HOST/'.controller.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        git=lambda *args:m.run(['runuser','-u','dflanag3','--','git','-C',m.REPO,*args])
        assert git('rev-parse','HEAD')==commit and not git('status','--porcelain')
        if action!='recover-hosting':assert not JOURNAL.exists(),'Recover pending ingress before other operations'
        c=config();before=m.capture(c);used=usage(c);bc,bs,bh=backend();rh=reader();pins=m.hosting_pins();assert pins==ACTIVE
        result={'status':'PASS','action':action,'sourceCommit':commit,'beforeManifestSHA256':c['manifestSHA256']}
        if action=='stage':
            assert c['manifestSHA256']==OLD and pins in [PREPARE,ACTIVE];m.install(packet/'release',DEST,'connected-release.json',NEW);result['releaseVerification']=verified()
        elif action=='activate':
            assert pins in [PREPARE,ACTIVE];result['releaseVerification']=verified()
            result['native']=notice(c,lambda:m.native('upgrade','--release',DEST,'--python',m.PYTHON)) if c['manifestSHA256']!=NEW else {'status':'already-current'}
            assert config()['manifestSHA256']==NEW
        elif action=='rollback':
            assert pins in [BASE,PREPARE,ACTIVE];result['releaseVerification']=verified()
            # Both SDKs use the same separate coordinator; ingress stays active.
            if c['manifestSHA256']!=OLD:result['native']=notice(c,lambda:m.native('upgrade','--release',OLD_DIR,'--python',m.PYTHON))
            assert config()['manifestSHA256']==OLD
        elif action=='recover-native':result['native']=m.native('recover-operation')
        elif action=='verify':
            assert pins in [BASE,PREPARE,ACTIVE];assert c['manifestSHA256'] in [OLD,NEW];result['releaseVerification']=verified();result['nativeStatus']=m.native('status')
            common,_=m.hosting_modules();assert common.caddy(common.load(),'production')==Path('/etc/caddy/Caddyfile').read_text()
        else:raise ValueError('Unknown coordinator action')
        assert m.hosting_pins()==pins,'SDK-only correction changed hosting'
        after=config();result['state']=preserved(before,after);ac,ast,ah=backend();assert ac==bc and ah==bh
        assert module('coordinator_room_retention',ROOM_OPERATOR/'room_service/operator.py').retained(bs,ast)
        current=usage(after)
        for role,rows in used.items():
            values={(r[0],r[1]):r[2:] for r in current[role]};assert all((r[0],r[1]) in values and all(a>=b for a,b in zip(values[(r[0],r[1])],r[2:])) for r in rows)
        result.update(afterManifestSHA256=after['manifestSHA256'],nativeConfigSHA256=sha(m.CONTROL),roomHealth=ah,readerHealth=reader(),hostingPins=m.hosting_pins(),guestUsageFloorsPreserved=True,backendUnchanged=True,routerPortsChanged=False,bootPolicyChanged=False,dataRestored=False,rootMinted=False)
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['stage','activate','rollback','recover-native','verify']);p.add_argument('--commit',required=True);a=p.parse_args()
    try:v=main(a.action,a.commit)
    except Exception as e:
        import traceback
        v={'status':'FAIL','action':a.action,'error':str(e),'traceback':traceback.format_exc(),'recoveryRequired':'Inspect /etc/codi-readers/ksu/ingress-pending.json and native rollout journal; recover code/routes without restoring any service data'}
    receipt=Path('/srv/codi-connected')/('reader-coordinator-'+a.action+'-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(v,f,indent=2);f.write('\n')
    print(json.dumps({'status':v['status'],'action':a.action,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt),'manifestSHA256':v.get('afterManifestSHA256'),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
