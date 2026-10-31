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
 'index.html':('4f4ac065e5840e0f01d80898dc87df777ff0f9b18ce69cc55deca5217a7b28f3','8ba2ec5c5b7195be331c0d130bdd0b24ed4d4d1b5db3c3d15499ebeb0a08cbba'),
 'notice-manifest.json':('1423f0fc9b32005bafc15f43fc3386e7cc928dc83ad882571acddad047a379b5','45ccd10bc607f1215e852ad3a9350634b50a3fd60fa431e33332f306f583d315'),
}
ARCHIVE='codi-browser-source-485928f3f.tar.zst'
ARCHIVE_SHA='e3d823eeb3d042ca051f7b12c2c775a945660036c7ec3ca55bd07588e32bf968'
SOURCE_SHA='bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5'


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
        journal=STATE/'browser-source-index-485-backup.json'
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
