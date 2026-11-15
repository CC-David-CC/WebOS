#!/usr/bin/env python3
"""Guarded Browser relay runtime upgrade with server audit kept disabled."""
import base64
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode=True
OPERATOR=Path('/srv/codi-browser/operators/d4919a4b70b077b93037e1a4a4020d5a9c2056f653410ff2d8ab7fea54cb3aa6')
OLD='953a58dc68dde9f1c988fa18857ea344347508f7e07e6c508eb256245e20764a'
NEW='af8d81daf6fdda84d9b563ce6885f862a4d68c0a55bea194d0c9360c47b1092e'
OLD_UNIT='d324ef49601a0fe39852a6d88629fb01106f8c0c12188e7c372172be183bddcb'
NEW_UNIT='afe64734fa5d05bee2544c6a970c6083826028c8b9fccfa129fb21dc3bb02964'
UNIT=Path('/etc/systemd/system/codi-browser-relay.service')
DEST=Path('/etc/codi-browser/destination-policy.json')
HOST_LOCK=Path('/home/dflanag3/webhost-sites/.controller.lock')
POLICY_LOCK=Path('/etc/codi-browser/.destination-policy.json.lock')
JOURNAL=Path('/var/lib/codi-ingress/browser-rule-race-runtime-journal.json')
BACKUP=Path('/var/backups/codi-browser-relay-before-rule-race-runtime.service')
digest=lambda value:hashlib.sha256(value).hexdigest()

def wait_check(op):
    deadline=time.monotonic()+20;last=None
    while time.monotonic()<deadline:
        try:op.check();return
        except (ValueError,OSError,subprocess.SubprocessError) as error:last=error;time.sleep(.25)
    raise ValueError('Browser relay did not become ready: '+str(last))

def operator():
    def protect(p,directory):
        info=p.lstat()
        import stat
        if not (stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)) or info.st_uid!=0 or info.st_mode&0o022 or (not directory and info.st_nlink!=1):raise ValueError('Unprotected operator path')
    for path in (OPERATOR,*OPERATOR.parents):protect(path,True)
    manifest=OPERATOR/'browser-audit-operator.json';raw=manifest.read_bytes()
    protect(manifest,False)
    if digest(raw)!=OPERATOR.name:raise ValueError('Unprotected audit operator')
    value=json.loads(raw);name='active-system/scripts/manage-browser-audit.py';path=OPERATOR/name;data=path.read_bytes()
    for parent in path.parents:
        if parent==OPERATOR:break
        protect(parent,True)
    protect(path,False)
    if value['files'].get(name)!={'bytes':len(data),'sha256':digest(data)}:raise ValueError('Audit operator changed')
    spec=importlib.util.spec_from_file_location('browser_audit_operator',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or len(sys.argv)!=2 or sys.argv[1] not in ('apply','exercise','recover'):raise ValueError('Root on box-webhost and apply, exercise or recover required')
    op=operator();switch,renderer,DestinationPolicy=op.imports()
    for p in (UNIT,DEST,HOST_LOCK,POLICY_LOCK):op.protected(p)
    for p in (UNIT,DEST,POLICY_LOCK,JOURNAL,BACKUP):op.protected_parents(p)
    with HOST_LOCK.open('r+') as host,POLICY_LOCK.open('r+') as lock:
        fcntl.flock(host,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if DestinationPolicy.load(DEST).server_audit_enabled:raise ValueError('Server audit must remain disabled')
        if subprocess.run(['systemctl','show','codi-browser-relay.service','-p','DropInPaths','--value'],check=True,text=True,capture_output=True).stdout.strip():raise ValueError('Unexpected relay drop-ins')
        if sys.argv[1]=='recover':
            op.protected(JOURNAL,mode=0o600);saved=json.loads(JOURNAL.read_bytes());old=base64.b64decode(saved['old'],validate=True);new=base64.b64decode(saved['new'],validate=True)
            if saved.get('version')!='codi-browser-audit-runtime/1' or digest(old)!=OLD_UNIT or digest(new)!=NEW_UNIT or UNIT.read_bytes() not in (old,new):raise ValueError('Runtime journal or unit changed')
            switch.atomic(UNIT,old,0o644);op.restart();wait_check(op);switch.remove_journal(JOURNAL);print('Restored previous relay runtime');return
        backup=BACKUP.with_name('codi-browser-relay-before-rule-race-runtime-exercise.service') if sys.argv[1]=='exercise' else BACKUP
        if JOURNAL.exists() or JOURNAL.is_symlink() or backup.exists() or backup.is_symlink():raise ValueError('Prior upgrade state exists')
        old=UNIT.read_bytes()
        if digest(old)!=OLD_UNIT or old.count(OLD.encode())!=2:raise ValueError('Live relay unit changed')
        new=old.replace(OLD.encode(),NEW.encode())
        if digest(new)!=NEW_UNIT:raise ValueError('Candidate unit changed')
        with tempfile.TemporaryDirectory(prefix='codi-audit-upgrade-') as folder:
            path=Path(folder)/UNIT.name;path.write_bytes(new);subprocess.run(['systemd-analyze','verify',str(path)],check=True,timeout=30)
        fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(old);stream.flush();os.fsync(stream.fileno())
        fd=os.open(backup.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
        data={'version':'codi-browser-audit-runtime/1','old':base64.b64encode(old).decode(),'new':base64.b64encode(new).decode()}
        switch.atomic(JOURNAL,(json.dumps(data,sort_keys=True)+'\n').encode(),0o600)
        try:
            switch.atomic(UNIT,new,0o644);op.restart();wait_check(op)
            if sys.argv[1]=='exercise':switch.atomic(UNIT,old,0o644);op.restart();wait_check(op)
            switch.remove_journal(JOURNAL)
        except Exception:
            if UNIT.read_bytes() not in (old,new):raise ValueError('Unit changed during upgrade; manual recovery required')
            switch.atomic(UNIT,old,0o644);op.restart();wait_check(op);switch.remove_journal(JOURNAL);raise
        print(json.dumps({'status':'rollback-exercised' if sys.argv[1]=='exercise' else 'upgraded','runtime':OLD if sys.argv[1]=='exercise' else NEW,'auditEnabled':False,'rollback':str(backup)}))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.SubprocessError) as error:print('Browser runtime upgrade failed: '+str(error),file=sys.stderr);sys.exit(1)
