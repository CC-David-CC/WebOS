#!/usr/bin/env python3
"""Publish the exact compiled-Pulse Rust notices update with rollback data."""
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
 'index.html':('4f4ac065e5840e0f01d80898dc87df777ff0f9b18ce69cc55deca5217a7b28f3','4f4ac065e5840e0f01d80898dc87df777ff0f9b18ce69cc55deca5217a7b28f3'),
 'emscripten-licenses.txt':('b1a5cd60fa71ae515da2e05ffb88358b1f2d4925cba2d79ae4ee8b6e6b1eeb6c','cfec82baaa9cc83eb238288f493d2116a14603c34aadebab15c7796c4d7cd9c3'),
 'notice-manifest.json':('06d02470d69637b2315515c51e49b4250ba2d0a97ed9d5fd51941db0a95dfa93','1423f0fc9b32005bafc15f43fc3386e7cc928dc83ad882571acddad047a379b5'),
}
ARCHIVE='codi-browser-source-802621ec2.tar.zst'
ARCHIVE_SHA='128c33ee16a6dde95f5c594b19ef6c8a05cb9b251024e95ac859f888b3a26c90'
SOURCE_SHA='2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b'


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
        journal=STATE/'browser-source-pulse-notice-backup.json'
        if journal.exists():raise ValueError('Source index backup already exists')
        backup={k:base64.b64encode(v).decode() for k,v in old.items()};put(journal,(json.dumps(backup,sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('emscripten-licenses.txt','notice-manifest.json','index.html'):put(ROOT/name,data[name],0o644)
            if any(digest(safe(ROOT/k))!=v[1] for k,v in FILES.items()):raise ValueError('Installed notices changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published pinned Pulse Rust notices; prior notices retained in',journal)


if __name__=='__main__':main()
