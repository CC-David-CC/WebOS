#!/usr/bin/env python3
"""Keep current + one rollback expanded build; inspect by default, apply explicitly.

Only generated connected-* directories directly under this project's .build/releases
are eligible. Active process paths and explicit pinned keeps are never removed.
Git retains compact source history; this tool never removes source/state or VMs.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.build/releases'

def run(keeps,apply):
    base=BASE.resolve();assert base==ROOT/'.build/releases' and not BASE.is_symlink()
    retained={}
    for item in keeps:
        folder=Path(item['path']).resolve();assert folder.parent==base and folder.is_dir() and not (BASE/folder.name).is_symlink()
        assert hashlib.sha256((folder/'connected-release.json').read_bytes()).hexdigest()==item['manifestSHA256']
        retained[folder.name]=['pinned current/rollback']
    def reference(raw,pid):
        prefix=str(base)+'/'
        if prefix in raw:
            name=raw.split(prefix,1)[1].split('/',1)[0].split(chr(0),1)[0]
            retained.setdefault(name,[]).append('active PID '+pid)
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            for arg in (proc/'cmdline').read_bytes().split(b'\0'):reference(arg.decode(errors='ignore'),proc.name)
            try:reference(os.readlink(proc/'cwd'),proc.name)
            except OSError:pass
            for fd in (proc/'fd').iterdir():
                try:reference(os.readlink(fd),proc.name)
                except OSError:pass
        except OSError:pass
    removed=[];total=0
    for folder in sorted(base.iterdir()):
        if folder.name in retained or folder.is_symlink() or not folder.is_dir() or not folder.name.startswith('connected-'):continue
        assert folder.resolve().parent==base
        size=int(subprocess.check_output(['du','-sx','--block-size=1',str(folder)],text=True).split()[0])
        if apply:shutil.rmtree(folder)
        removed.append({'name':folder.name,'bytes':size});total+=size
    return {'status':'PASS','applied':apply,'candidates':removed,'approxBytesReclaimed'if apply else'approxReclaimableBytes':total,'retained':retained}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--policy',type=Path,default=ROOT/'.build/development-retention.json');p.add_argument('--apply',action='store_true');a=p.parse_args()
    value=json.loads(a.policy.read_bytes());assert set(value)=={'version','current','rollback'} and value['version']==1
    result=run([value['current'],value['rollback']],a.apply)
    if a.apply:
        out=ROOT/'.build/checks'/('development-build-prune-'+str(time.time_ns())+'-result.json');out.write_text(json.dumps(result,indent=2)+chr(10))
    print(json.dumps(result,indent=2))
