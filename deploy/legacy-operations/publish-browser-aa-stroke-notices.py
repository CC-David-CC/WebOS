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
BACKUP=Path('/var/lib/codi-ingress/browser-aa-stroke-notices-backup.json')
PINS={
 'emscripten-licenses.txt':('04dd62fdc18dc6b94bfa439f55b4103de6bb34394b53e8e6167264dd8d2b8ada','6a9f854cf96527b7f6469d6e5307d84e85d34f27e2177737fca491f139ada62c'),
 'notice-manifest.json':('df4e896c4d37024e38e805b037f6402a90e7427c5a362f55fe950e83ac529252','8d50d8ebabf55c585f12827802d5720434efaa1129783cceeaa790d9f6ad2944'),
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
        expected=json.loads(old['notice-manifest.json']);notice=data['emscripten-licenses.txt']
        expected['files']['emscripten-licenses.txt']={'bytes':len(notice),'sha256':sha(notice)}
        if json.loads(data['notice-manifest.json'])!=expected or any(n not in notice for n in (b'third_party/rust/aa-stroke/src/bezierflattener.rs',b'third_party/rust/aa-stroke/src/tri_rasterize.rs',b'Copyright 2012 VMware, Inc.',b'Licensed to the .NET Foundation')):raise ValueError('Unexpected manifest')
        if BACKUP.exists() or BACKUP.is_symlink():raise ValueError('Backup exists')
        put(BACKUP,(json.dumps({k:base64.b64encode(v).decode() for k,v in old.items()},sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('emscripten-licenses.txt','notice-manifest.json'):put(ROOT/name,data[name],0o644)
            if any(sha(safe(ROOT/name))!=pins[1] for name,pins in PINS.items()):raise ValueError('Installed content changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published exact pinned aa-stroke source notices; prior files retained at',BACKUP)

if __name__=='__main__':main()
