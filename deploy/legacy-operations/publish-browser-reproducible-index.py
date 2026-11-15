#!/usr/bin/env python3
"""Publish pinned notice additions with rollback under the hosting lock."""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile

ROOT=Path('/srv/codi-browser/source-staging/engine-6736dce5')
LOCK=Path('/home/dflanag3/webhost-sites/.controller.lock')
BACKUP=Path('/var/lib/codi-ingress/browser-source-reproducible-index-backup.json')
PINS={
 'index.html':('c1ad9e91f154c1857490b8ca7cee2b858b77425233c2b7a3f2ff1b273fec5f02','5aece1521b25cc96606d7805b0fd9836f37e55f043f1459aae7386c0b279d939'),
 'notice-manifest.json':('59d34030826c560113f20064ae6a929dafe4fd2dcbe2af4b4267d3a55504dc23','1cd10b58626614a584ebdc74e539ac7653fac56e1953c00a36a424bdd822a500'),
}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def safe(path):
    st=path.lstat()
    if path.is_symlink() or not path.is_file() or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('Unsafe file')
    return path.read_bytes()
def put(path,data,mode):
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(name,path);fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(name):os.unlink(name)
def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('root on box-webhost required')
    import sys
    payload=json.load(sys.stdin)
    if set(payload)!=set(PINS):raise ValueError('Unexpected inputs')
    data={name:base64.b64decode(value,validate=True) for name,value in payload.items()}
    if any(sha(data[name])!=pins[1] for name,pins in PINS.items()):raise ValueError('Candidate changed')
    with LOCK.open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        old={name:safe(ROOT/name) for name in PINS}
        if any(sha(old[name])!=pins[0] for name,pins in PINS.items()):raise ValueError('Baseline changed')
        expected=json.loads(old['notice-manifest.json']);notice=data['index.html']
        expected['files']['index.html']={'bytes':len(notice),'sha256':sha(notice)}
        if json.loads(data['notice-manifest.json'])!=expected or b'codi-browser-source-933db11ea.tar.zst' not in notice:raise ValueError('Unexpected manifest')
        if BACKUP.exists() or BACKUP.is_symlink():raise ValueError('Backup exists')
        put(BACKUP,(json.dumps({k:base64.b64encode(v).decode() for k,v in old.items()},sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('index.html','notice-manifest.json'):put(ROOT/name,data[name],0o644)
            if any(sha(safe(ROOT/name))!=pins[1] for name,pins in PINS.items()):raise ValueError('Installed content changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published reproducible source index; prior files retained at',BACKUP)

if __name__=='__main__':main()
