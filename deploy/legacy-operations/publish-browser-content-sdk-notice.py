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
BACKUP=Path('/var/lib/codi-ingress/browser-content-sdk-notice-backup.json')
PINS={
 'emscripten-licenses.txt':('fbca71d13f022e85945e762d7cb5a9d9939ac7b25cbf803b0b1a24759b5d8329','ee553fd12a0e8ef825cae8661f19c86c6f15e83dbf0592caf8b5c249eeab7c01'),
 'notice-manifest.json':('b149d4c620611e8284a0920c5cc85ea69ce28a61bb3ac0e5ea0a2233c7c391dd','1230180107f7157ba7b2be53d883c5a334d5057506d5e75019eaacb671c8e3a3'),
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
        if json.loads(data['notice-manifest.json'])!=expected or b'third_party/content_analysis_sdk/LICENSE' not in notice:raise ValueError('Unexpected manifest')
        if BACKUP.exists() or BACKUP.is_symlink():raise ValueError('Backup exists')
        put(BACKUP,(json.dumps({k:base64.b64encode(v).decode() for k,v in old.items()},sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('emscripten-licenses.txt','notice-manifest.json'):put(ROOT/name,data[name],0o644)
            if any(sha(safe(ROOT/name))!=pins[1] for name,pins in PINS.items()):raise ValueError('Installed content changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published exact pinned Content Analysis SDK notice; prior files retained at',BACKUP)

if __name__=='__main__':main()
