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
 'index.html':('64e06a7aed14a64f0a56d4e4f2e8dfc4eb98932c0aaf03204d5a9f4490227edd','81955daf2abf8e4ce82743b5278d40862afd75bea462b251a9b5f720d5f1e614'),
 'firefox-licenses.html':('76b13200702f3ac866753a73109a9bf9a49751afde14edac2396bf22128d77f4','863ab7630592181f9c16be9f509cbc0b859c56124af4711d8a519c6b4c79fa0e'),
 'notice-manifest.json':('6285a85f3f8213064f38bb85c859f357e1586b17fdab634f281a859cd5ba15f4','b149d4c620611e8284a0920c5cc85ea69ce28a61bb3ac0e5ea0a2233c7c391dd'),
}
ARCHIVE='codi-browser-source-ed78ff4b3.tar.zst'
ARCHIVE_SHA='0b6f94ae5573bb80d430085cdad66bb3720fdb63d8e5883166412f5219b34139'
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
        expected['files']['firefox-licenses.html']={'bytes':len(data['firefox-licenses.html']),'sha256':digest(data['firefox-licenses.html'])}
        if old['firefox-licenses.html'].count(b'href="/browser-sources/"')!=1 or data['firefox-licenses.html']!=old['firefox-licenses.html'].replace(b'href="/browser-sources/"',b'href="./"'):raise ValueError('Unexpected Firefox license change')
        if candidate!=expected or ARCHIVE.encode() not in data['index.html']:raise ValueError('Unexpected manifest or index change')
        journal=STATE/'browser-source-index-ed78-backup.json'
        if journal.exists():raise ValueError('Source index backup already exists')
        backup={k:base64.b64encode(v).decode() for k,v in old.items()};put(journal,(json.dumps(backup,sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('firefox-licenses.html','index.html','notice-manifest.json'):put(ROOT/name,data[name],0o644)
            if any(digest(safe(ROOT/k))!=v[1] for k,v in FILES.items()):raise ValueError('Installed notices changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published pinned source index; prior notices retained in',journal)


if __name__=='__main__':main()
