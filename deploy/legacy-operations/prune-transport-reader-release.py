#!/usr/bin/env python3
"""Remove only superseded native25/138 after the e007 upgrade/rollback checks."""
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

def main():
    assert os.geteuid()==0 and socket.gethostname()=='box-webhost'
    helper=Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(helper)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    spec=importlib.util.spec_from_file_location('retention_helper',helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    current='e007ad370162489503f3b172170d7b6f4244b9d9ae21cf5161fd4c9e745e8392'
    rollback='e5164042e2f5b5b46cfb479afa43c5ad34137ac3427b58cc016f27881e831615'
    obsolete='138a5129e7f64f5dc735492af640562c1d208083a6a0cec73ad20a1c2faf84ef'
    base=Path('/srv/codi-connected/releases');target=base/('native25-'+obsolete[:16])
    with (m.HOST/'.controller.lock').open('rb') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        m.protected(m.CONTROL);config_bytes=m.CONTROL.read_bytes();config=json.loads(config_bytes)
        assert config['manifestSHA256']==current and config['release']==str(base/('native25-'+current[:16]))
        assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json','native-rollout.json','site-cutover.json','reader-backend-transition.json'])
        assert m.hosting_pins()==m.NEW_PINS
        for pin in [current,rollback]:
            folder=base/('native25-'+pin[:16]);m.protected(folder)
            contract=m.module('retention_contract_'+pin[:8],folder/'origin_service/release.py')
            assert contract.verify(folder)['manifestSHA256']==pin
        before=m.capture(config)
        if target.exists():
            m.protected(target);assert target.parent==base and sha(target/'connected-release.json')==obsolete
            for proc in Path('/proc').glob('[0-9]*'):
                try:
                    assert str(target).encode() not in (proc/'cmdline').read_bytes(),str(proc)
                    for name in ['cwd','exe',*['fd/'+p.name for p in (proc/'fd').iterdir()]]:
                        try:assert not os.readlink(proc/name).startswith(str(target)),str(proc/name)
                        except OSError:pass
                except (FileNotFoundError,ProcessLookupError):pass
            size=int(subprocess.check_output(['du','-sx','--block-size=1',str(target)],text=True).split()[0])
            shutil.rmtree(target)
        else:size=0
        assert not target.exists() and m.CONTROL.read_bytes()==config_bytes and m.capture(config)==before and m.hosting_pins()==m.NEW_PINS
        result={'status':'PASS','removed':str(target),'approxBytesReclaimed':size,'retained':[str(base/('native25-'+pin[:16])) for pin in [current,rollback]],'currentAndOneUsableRollback':True,'privateStateAndConfigUnchanged':True,'servicesRestarted':False}
        receipt=Path('/srv/codi-connected')/('transport-reader-retention-'+str(time.time_ns())+'-result.json')
        fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n')
        return {**result,'rootReceipt':str(receipt),'rootReceiptSHA256':sha(receipt)}

if __name__=='__main__':print(json.dumps(main()))
