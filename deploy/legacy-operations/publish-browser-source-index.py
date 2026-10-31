#!/usr/bin/env python3
"""Publish the pinned release source link after its route is available."""
import base64
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import tempfile

ROOT=Path('/srv/codi-browser/source-staging/engine-6736dce5')
LOCK=Path('/home/dflanag3/webhost-sites/.controller.lock')
STATE=Path('/var/lib/codi-ingress')
FILES={
 'index.html':('e086e64059757c69319573e5138b34e59d623f48534abeb5220450d6ad1bf414','5a49aaf2d9758fbd66d5f5b5d99860d9d3935f8e92abac27ffcf67d43b1e2914'),
 'notice-manifest.json':('d6671aeccfc5e8084119cf13b9fa4e65236fbf71d894c6cc1f821c27d446a1ac','c0e531f029edc945418d167618971460bc47404d473069d86a43aaf3dd91e7d8'),
}
ARCHIVE='codi-browser-source-adece7482.tar.zst'
ARCHIVE_SHA='2e64c1c3856f622af986157059eca6f8f14a8c73e275829d397372b70701c127'
SOURCE_SHA='6ac5e114fe7ed8949f2c8ce3876cafa1745353ef0409c4d2bc13600067ea3226'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_uid!=0 or path.stat().st_mode&0o022:raise ValueError('Unsafe file: '+str(path))
    return path.read_bytes()
def put(path,data,mode):
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
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    payload=json.load(sys.stdin)
    if set(payload)!=set(FILES):raise ValueError('Unexpected candidate files')
    data={k:base64.b64decode(v,validate=True) for k,v in payload.items()}
    if any(digest(data[k])!=v[1] for k,v in FILES.items()):raise ValueError('Candidate notice changed')
    with LOCK.open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        source=Path('/home/dflanag3/webhost-sites/ops/common.py')
        if digest(source.read_bytes())!=SOURCE_SHA or digest(safe(ROOT/ARCHIVE))!=ARCHIVE_SHA:raise ValueError('Source route or archive changed')
        old={k:safe(ROOT/k) for k in FILES}
        if any(digest(old[k])!=v[0] for k,v in FILES.items()):raise ValueError('Existing notices changed')
        previous=json.loads(old['notice-manifest.json']);candidate=json.loads(data['notice-manifest.json'])
        expected=json.loads(old['notice-manifest.json']);expected['sourceArchives'][ARCHIVE]=ARCHIVE_SHA
        expected['files']['index.html']={'bytes':len(data['index.html']),'sha256':digest(data['index.html'])}
        if candidate!=expected or ARCHIVE.encode() not in data['index.html']:raise ValueError('Unexpected manifest or index change')
        journal=STATE/'browser-source-index-adece-backup.json'
        if journal.exists():raise ValueError('Source index backup already exists')
        backup={k:base64.b64encode(v).decode() for k,v in old.items()};put(journal,(json.dumps(backup,sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('notice-manifest.json','index.html'):put(ROOT/name,data[name],0o644)
            if any(digest(safe(ROOT/k))!=v[1] for k,v in FILES.items()):raise ValueError('Installed notices changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published pinned source index; prior notices retained in',journal)


if __name__=='__main__':main()
