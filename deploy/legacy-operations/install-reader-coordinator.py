#!/usr/bin/env python3
"""Install pinned discovery candidate privately; no public route or SDK change.

Run only from the reviewed Git packet. Copies and rechecks closed root-owned
artifacts before importing the new operator through the protected runtime.
Existing discovery signing material survives interruption and explicit retries.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile

WORKER='d302ae97a8df296a90b6fa570cf5df191d4b16b2c14165b8a0bc3e17ecb04d33'
OPERATOR='325e7d9eb47a882636eb8253b9fe79700f76449d1428d39f64397ee1a53699f5'
NATIVE='fa0bb0d8301207b5585afaddf4f3582179782fcefd25be1913d450841df576ef'
ROOMS='92f95a5da745fc7e8f2b2829d8812dd15bf6d4b7b2d888eaf7eea6b87ed5bbe6'
RUNTIME=Path('/srv/codi-connected/venvs/517179c/bin/python')

def sha(raw):return hashlib.sha256(raw).hexdigest()

def protected(path,directory=False):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('Protected absolute installation path required')
    for p in [path,*path.parents]:
        s=p.lstat()
        if p.is_symlink() or s.st_uid!=0 or s.st_mode&0o022:raise ValueError('Protected root-owned installation path required')
    if directory and not path.is_dir():raise ValueError('Protected directory required')
    return path

def verify(folder,name,pin):
    raw=(folder/name).read_bytes()
    if sha(raw)!=pin:raise ValueError('Candidate manifest pin changed')
    m=json.loads(raw);found=set()
    if set(m)!={'version','files'}:raise ValueError('Exact artifact manifest required')
    for p in folder.rglob('*'):
        if p.is_symlink():raise ValueError('No linked installation input')
        if p.is_dir():continue
        if not p.is_file() or p.stat().st_nlink!=1:raise ValueError('Regular unlinked artifact required')
        n=str(p.relative_to(folder));found.add(n);b=p.read_bytes()
        if n!=name and m['files'].get(n)!={'bytes':len(b),'sha256':sha(b)}:raise ValueError('Changed or extra installation input')
    if found!=set(m['files'])|{name}:raise ValueError('Missing installation input')
    return m

def install(source,kind,name,pin):
    verify(source,name,pin);parent=protected(Path('/srv/codi-readers')/kind,True);target=parent/pin
    if target.exists():protected(target,True);verify(target,name,pin);return target
    stage=Path(tempfile.mkdtemp(prefix='.install-',dir=parent))
    try:
        shutil.copytree(source,stage,dirs_exist_ok=True)
        for p in [stage,*stage.rglob('*')]:
            if p.is_symlink():raise ValueError('No linked installation input')
            os.chown(p,0,0);p.chmod(0o755 if p.is_dir() else 0o644)
        verify(stage,name,pin);stage.rename(target)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return target

def main(a):
    if os.geteuid()!=0:raise ValueError('Explicit root-owned installer required')
    # Binding to current service configuration prevents accidental installation
    # after an unrelated authority/endpoint/backend change.
    for path,pin in [('/etc/codi-connected/ksu/managed.json',NATIVE),('/etc/codi-rooms/ksu/managed.json',ROOMS)]:
        if sha(protected(path).read_bytes())!=pin:raise ValueError('Live service configuration changed; re-review candidate')
    protected(RUNTIME.parent.parent,True)
    for path in ['/srv/codi-readers','/srv/codi-readers/workers','/srv/codi-readers/operators','/etc/codi-readers']:
        p=Path(path)
        if not p.exists():protected(p.parent,True);p.mkdir(mode=0o755)
        protected(p,True)
    worker=install(a.source/'worker','workers','reader-worker.json',WORKER)
    operator=install(a.source/'operator','operators','reader-operator.json',OPERATOR)
    # This import runs only after the exact graph has been copied and verified
    # under root custody. argv0 is the full venv interpreter path.
    code='''import json,sys,os
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from reader_service.operator import Manager,safe
from room_service.contract import jose
request=json.loads(sys.argv[3]);manager=Manager('/etc/codi-readers/ksu')
with manager.locked():
 c=manager.configure(**request,recover=manager.journal.exists())
 value=manager.start(c)
 print(json.dumps({'status':'PASS','config':c,'health':value,'publicIngressChanged':False,'sdkChanged':False,'rootAuthorityKeyUsed':False}))
'''
    room_config=json.loads(protected('/etc/codi-rooms/ksu/managed.json').read_bytes())
    identity=json.loads(protected('/etc/codi-rooms/ksu/issuer-policy.json').read_bytes())
    source=Path(room_config['stateRoot'])/'controller.pem';owner=source.stat().st_uid
    request={'instance':'codi-readers-ksu','release':str(worker),'manifest_sha256':WORKER,'python':str(RUNTIME),'identity':identity,'room_key_source':str(source),'room_key_uid':owner,'base_path':'','port':8143,'unit_dir':'/etc/systemd/system'}
    child=subprocess.run([str(RUNTIME),'-I','-B','-c',code,str(operator),str(worker),json.dumps(request)],check=True,capture_output=True,text=True,timeout=90)
    value=json.loads(child.stdout)
    for path,pin in [('/etc/codi-connected/ksu/managed.json',NATIVE),('/etc/codi-rooms/ksu/managed.json',ROOMS)]:
        if sha(protected(path).read_bytes())!=pin:raise ValueError('Unrelated managed config changed during installation')
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if not a.output.is_absolute() or a.output.exists() or a.output.is_symlink():p.error('New absolute root receipt path required')
    protected(a.output.parent,True);value=main(a);fd=os.open(a.output,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
    print(json.dumps({'status':value['status'],'receipt':str(a.output),'worker':WORKER,'operator':OPERATOR,'publicIngressChanged':False,'sdkChanged':False}))
