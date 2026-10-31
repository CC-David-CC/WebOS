#!/usr/bin/env python3
"""Publish the exact compiled-RLBox notices update with rollback data."""
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
 'index.html':('277dd5673456f92bb50568bdc14ea205a4bf113a2ad93f9eeb723a99e00b0227','a3aef50c90631e9322e10f78cd5b81d569cf4c3b374a0c29e0c71485177b6c99'),
 'emscripten-licenses.txt':('cfec82baaa9cc83eb238288f493d2116a14603c34aadebab15c7796c4d7cd9c3','28b3c6267097ecfa2e40dc56de5715348ca011652a2b26817f7cbba15e2570b7'),
 'notice-manifest.json':('dae7deb910d1b27042ea8cf39a5a8a772178e85ba414e4c38ba4e200141b3104','b9734b398bbf0760819c18c562806cb6edb67d695c4faab0dcd4f43e34088d50'),
}
ARCHIVE='codi-browser-source-29a71d717.tar.zst'
ARCHIVE_SHA='f231dfee54279c20c6bca77988b556d6fcad7c8886792eb78c63e1f9c10b680b'
SOURCE_SHA='2d04ab00dc0e17003f94155b4f812b640ed2f9ed897e4f3685b8cb2bbbda41cb'


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
        expected=json.loads(old['notice-manifest.json'])
        for name in ('index.html','emscripten-licenses.txt'):
            expected['files'][name]={'bytes':len(data[name]),'sha256':digest(data[name])}
        if candidate!=expected or b'Liberation Sans' not in data['index.html'] or not data['emscripten-licenses.txt'].startswith(old['emscripten-licenses.txt']):raise ValueError('Unexpected notice change')
        journal=STATE/'browser-source-rlbox-notice-backup.json'
        if journal.exists():raise ValueError('Source index backup already exists')
        backup={k:base64.b64encode(v).decode() for k,v in old.items()};put(journal,(json.dumps(backup,sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('emscripten-licenses.txt','notice-manifest.json','index.html'):put(ROOT/name,data[name],0o644)
            if any(digest(safe(ROOT/k))!=v[1] for k,v in FILES.items()):raise ValueError('Installed notices changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published pinned RLBox notices; prior notices retained in',journal)


if __name__=='__main__':main()
