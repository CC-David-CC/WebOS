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
 'index.html':('05c0af0b4c3b8a0f78ddcb6968ad4bf3a6bc5b1ebcd0e3975609dec0d4acfd1f','e85858cf36d3cd958fd3d06676d3a67166173213aea95a7f053de595a55c22c2'),
 'notice-manifest.json':('59e8bea78d9562cc13434336e8f32494a9b2893b470f0be98576467b377d6a16','c1607ae1f635b9b4310a7b30a4e07b7056510322b3ff3937355dc06c8c54a3cb'),
}
ARCHIVE='codi-browser-source-15c9672ce-folder.tar.zst'
ARCHIVE_SHA='00832167e24d5fffbccb4277a60e181eb5ade40c0b52a385076191ec2dfb9b04'
SOURCE_SHA='fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935'


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
        journal=STATE/'browser-source-index-folder-15c-backup.json'
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
