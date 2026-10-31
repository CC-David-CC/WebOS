#!/usr/bin/env python3
"""Publish the exact Liberation Sans notice update with rollback data."""
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
 'index.html':('6bdf74d80a890f9df6fef1186002d5b0a3376a6abbb02d8a6207828f1019408e','149d07a70d65321ebf4921e0b72d8b4b4efcd7d71978266ff6cbae75f074360d'),
 'emscripten-licenses.txt':('c655022b1b1308f46d39e45d6e9b8db34c0b356e0041c7c49f4e943c89c0ecc6','4b87b95e8c51dde5861703e11ce57c416f178497fab403b73033f6db48f550ad'),
 'notice-manifest.json':('f7a9370f2d46132ad956db6c67226ee606ad4143a6c33ced048ab6d5f7e271f0','ba4aaebbdf5a9b6d0f54da91f035b2cbd43a40c45e38ce1457eec68d2aebbbcc'),
}
ARCHIVE='codi-browser-source-2ed6d0259.tar.zst'
ARCHIVE_SHA='49f1c63f6160a58d9d6624d5baa35589fae1a74580f32cbb8883f71f9a203b0b'
SOURCE_SHA='3ac0cf3bc1dda9063c0cd3494c71d83a706681b7a8cdc682a0d8f77dcace8ff3'


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
        journal=STATE/'browser-source-font-notice-backup.json'
        if journal.exists():raise ValueError('Source index backup already exists')
        backup={k:base64.b64encode(v).decode() for k,v in old.items()};put(journal,(json.dumps(backup,sort_keys=True)+'\n').encode(),0o600)
        try:
            for name in ('emscripten-licenses.txt','notice-manifest.json','index.html'):put(ROOT/name,data[name],0o644)
            if any(digest(safe(ROOT/k))!=v[1] for k,v in FILES.items()):raise ValueError('Installed notices changed')
        except BaseException:
            for name,raw in old.items():put(ROOT/name,raw,0o644)
            raise
    print('Published pinned font notice; prior notices retained in',journal)


if __name__=='__main__':main()
