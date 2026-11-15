#!/usr/bin/env python3
"""Retain corrected b3/5ac and shared081 backend; prune exact superseded code."""
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

NEW='b3c292a13b6a7c1d69f15d9c23c27a15d58009646ae030e1a7806607abcbb897'
ROLLBACK='5ac541f0e439dc0808ece01115f4aa1307e6e531449bddd7c38bfd8175c5329e'
WORKER='081bd143a37d486d1984d92389c0b1eb649563d052e3e793bdbd21de7542acdf'
OLD_WORKER='870df3f9fd7efc2dbb1d5256da98476662c1ea5df95ae987c75e1472ebfd14d4'
OP='53aa99303600f942a6f40b63718e26f2e73d78bffa0c458ba3d6bebb83a034fc'

def main():
    assert os.geteuid()==0 and socket.gethostname()=='box-webhost'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    helper=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
    assert sha(helper)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    s=importlib.util.spec_from_file_location('producer_retention_helper',helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.OPERATOR_DIR=Path('/srv/codi-rooms/operators')/OP
    def graph(folder,manifest,pin):
        m.protected(folder);assert sha(folder/manifest)==pin;records=json.loads((folder/manifest).read_bytes())['files']
        assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(records)|{manifest}
        for n,r in records.items():
            p=folder/n;m.protected(p);assert r=={'bytes':p.stat().st_size,'sha256':sha(p)}
    targets=[(Path('/srv/codi-connected/releases/native25-'+pin[:16]),'connected-release.json',pin) for pin in ['e007ad370162489503f3b172170d7b6f4244b9d9ae21cf5161fd4c9e745e8392','b97dce3bb9956d5ed352f238b84d8f0797e18650f315a687f69d4e7eb3718b8d']]
    targets += [(Path('/srv/codi-rooms/workers')/OLD_WORKER,'room-worker.json',OLD_WORKER)]
    m.NEW_PINS={'common.py':'26da0e71121f385f54abf36247afd0bb575b3c5926906403cc09d735bd0e1bd9','sites.toml':'9bccf2519656c22f6f0043aa03b673fbfeac9c21e4f3928934922208914afa7e','Caddy':'2a7cbaf41186112fdc47c95af7abdbbf3689faf5b149ee72031a161743b94270'}
    with (m.HOST/'.controller.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        c=json.loads(m.CONTROL.read_bytes());assert c['manifestSHA256']==NEW and c['release']=='/srv/codi-connected/releases/native25-'+NEW[:16]
        assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json','reader-backend-transition.json'])
        assert m.hosting_pins()==m.NEW_PINS
        for pin in [NEW,ROLLBACK]:graph(Path('/srv/codi-connected/releases/native25-'+pin[:16]),'connected-release.json',pin)
        for pin in [WORKER]:graph(Path('/srv/codi-rooms/workers')/pin,'room-worker.json',pin)
        graph(m.OPERATOR_DIR,'room-operator.json',OP)
        op=m.room_manager()
        with op.locked():
            rc=op.load();assert rc['manifestSHA256']==WORKER and c['hostedRooms']['operatorRelease']==str(m.OPERATOR_DIR)
            assert not op.journal.exists();op.check_units(rc);before=m.capture(c);room_before=op.inspect(rc);health=op.health(rc);config_bytes=m.CONTROL.read_bytes();room_bytes=(m.ROOM_CONFIG/'managed.json').read_bytes()
            present=[v for v in targets if v[0].exists()]
            for path,manifest,pin in present:graph(path,manifest,pin)
            for proc in Path('/proc').glob('[0-9]*'):
                try:
                    args=(proc/'cmdline').read_bytes()
                    assert not any(str(path).encode() in args for path,_,_ in present),str(proc)
                    for name in ['cwd','exe',*['fd/'+p.name for p in (proc/'fd').iterdir()]]:
                        try:assert not any(os.readlink(proc/name).startswith(str(path)) for path,_,_ in present),str(proc/name)
                        except OSError:pass
                except (FileNotFoundError,ProcessLookupError):pass
            for unit in Path('/etc/systemd/system').glob('*.service'):
                if unit.is_symlink():continue
                text=unit.read_text();assert not any(str(path) in text for path,_,_ in present),str(unit)
            removed=[]
            for path,_,_ in present:
                size=int(subprocess.check_output(['du','-sx','--block-size=1',str(path)],text=True).split()[0]);shutil.rmtree(path);removed.append({'path':str(path),'bytes':size})
            assert m.CONTROL.read_bytes()==config_bytes and (m.ROOM_CONFIG/'managed.json').read_bytes()==room_bytes
            m.preserved(before,c)
            assert op.inspect(rc)['controllerKey']==room_before['controllerKey']
            assert op.health(rc)==health and op.journal.exists() is False and m.hosting_pins()==m.NEW_PINS
            operator=m.module('producer_retained_room',m.OPERATOR_DIR/'room_service/operator.py');assert operator.retained(room_before,op.inspect(rc))
            result={'status':'PASS','removed':removed,'approxBytesReclaimed':sum(r['bytes'] for r in removed),'currentAndOneUsableRollback':True,'nativeCurrent':NEW,'nativeRollback':ROLLBACK,'workerCurrent':WORKER,'workerSharedByBothSDKs':True,'operator':OP,'privateStateAndConfigPreserved':True,'servicesRestarted':False,'dataRestored':False}
            receipt=Path('/srv/codi-connected')/('coordinator-retention-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.write('\n')
            return {**result,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt)}

if __name__=='__main__':print(json.dumps(main()))
