#!/usr/bin/env python3
"""Temporarily change one network rule with a conflict-safe timed restoration.

Run only from its root-owned installation on box-webhost. This test-only
operator changes either outgoing or login rules for at most two minutes. A
concurrent operator edit is retained rather than overwritten.
"""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile

POLICY=Path('/etc/codi-browser/access-policy.json')
LOCK=POLICY.parent/('.'+POLICY.name+'.lock')
JOURNAL=Path('/var/lib/codi-ingress/browser-policy-test-journal.json')
SCRIPT=Path('/srv/codi-browser/operators/browser-policy-test-guard.py')
BASE='2fe09908c177ad7f33df3d7b0b7a11e1cbe82da594592d7920727e1d2c698d4a'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,data,mode):
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,path);parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(parent)
        finally:os.close(parent)
    finally:
        if os.path.exists(name):os.unlink(name)
def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or len(sys.argv)!=2 or sys.argv[1] not in ('apply','apply-geo','apply-login-geo','restore'):raise ValueError('Root on box-webhost; specify a test or restore')
    if SCRIPT.is_symlink() or not SCRIPT.is_file() or SCRIPT.stat().st_uid!=0 or SCRIPT.stat().st_mode&0o022:raise ValueError('Protected installed helper required')
    fd=os.open(LOCK,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'r+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if POLICY.is_symlink() or POLICY.stat().st_uid!=0 or POLICY.stat().st_mode&0o022:raise ValueError('Unsafe network policy')
        current=POLICY.read_bytes()
        if sys.argv[1] in ('apply','apply-geo','apply-login-geo'):
            if JOURNAL.exists() or sha(current)!=BASE:raise ValueError('Policy changed or a test is already pending')
            value=json.loads(current);assert value['incomingLogin']=={'blockedCidrs':[],'blockedCountries':[]} and value['outgoing']=={'blockedCidrs':[],'blockedCountries':[]}
            if sys.argv[1]=='apply':value['outgoing']['blockedCidrs']=['0.0.0.0/0','::/0']
            elif sys.argv[1]=='apply-geo':value['outgoing']['blockedCountries']=['AU','CA']
            else:value['incomingLogin']['blockedCountries']=['US']
            candidate=(json.dumps(value,indent=2)+'\n').encode()
            unit='codi-browser-policy-test-restore-'+secrets.token_hex(6)
            journal={'before':base64.b64encode(current).decode(),'beforeSHA256':BASE,'candidateSHA256':sha(candidate),'unit':unit}
            write(JOURNAL,(json.dumps(journal,sort_keys=True)+'\n').encode(),0o600)
            try:
                subprocess.run(['/usr/bin/systemd-run','--quiet','--on-active=120s','--unit='+unit,'/usr/bin/python3','-I','-B',str(SCRIPT),'restore'],check=True,capture_output=True,timeout=15)
                write(POLICY,candidate,0o644)
            except BaseException:
                if sha(POLICY.read_bytes())==sha(candidate):write(POLICY,current,0o644)
                JOURNAL.unlink(missing_ok=True);raise
            print('Temporary network rule active; automatic restore scheduled in two minutes: '+unit+'.timer')
        else:
            if not JOURNAL.exists():
                if sha(current)!=BASE:raise ValueError('No test journal and policy differs from baseline')
                print('Policy already restored.');return
            if JOURNAL.is_symlink() or JOURNAL.stat().st_uid!=0 or JOURNAL.stat().st_mode&0o077:raise ValueError('Unsafe test journal')
            journal=json.loads(JOURNAL.read_text());before=base64.b64decode(journal['before'],validate=True)
            if sha(before)!=BASE or journal['beforeSHA256']!=BASE:raise ValueError('Invalid saved baseline')
            if sha(current)==journal['candidateSHA256']:write(POLICY,before,0o644)
            elif sha(current)!=BASE:raise ValueError('Policy changed concurrently; retained for operator review')
            JOURNAL.unlink();print('Original network policy restored.')


if __name__=='__main__':main()
