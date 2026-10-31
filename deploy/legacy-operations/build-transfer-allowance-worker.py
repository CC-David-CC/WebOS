#!/usr/bin/env python3
"""Build a private worker candidate changing only daily transfer limits."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE='53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0'
CHANGED='gateway_service/transfers.py'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def build(base,destination):
    base=Path(base).absolute();destination=Path(destination).absolute()
    if not base.is_dir() or base.is_symlink() or destination.exists() or destination.is_symlink() or not destination.parent.is_dir():raise ValueError('Existing baseline and new destination required')
    if base in destination.parents or destination in base.parents:raise ValueError('Baseline and destination must be disjoint')
    manifest=base/'files-service.json';raw=manifest.read_bytes()
    if sha(raw)!=BASE:raise ValueError('Wrong live worker baseline')
    data=json.loads(raw)
    if data.get('version')!='codi-private-file-service/1':raise ValueError('Wrong worker format')
    actual={p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    if actual!=set(data['files'])|{'files-service.json'} or any(p.is_symlink() for p in base.rglob('*')):raise ValueError('Unexpected baseline files')
    for name,record in data['files'].items():
        content=(base/name).read_bytes()
        if record!={'bytes':len(content),'sha256':sha(content)}:raise ValueError('Changed baseline: '+name)
    if subprocess.check_output(['git','-C',str(ROOT.parent),'status','--porcelain','--','active-system/'+CHANGED],text=True):raise ValueError('Commit transfer source first')
    source=(ROOT/CHANGED).read_bytes()
    if source== (base/CHANGED).read_bytes():raise ValueError('Expected changed transfer source')
    before=(base/CHANGED).read_bytes()
    old=b'daily_bytes=512*1024*1024, shared_daily_bytes=2*1024*1024*1024'
    new=b'daily_bytes=50*1024**3, shared_daily_bytes=200*1024**3'
    if before.count(old)!=1 or source!=before.replace(old,new,1):raise ValueError('Candidate includes unrelated changes')
    stage=Path(tempfile.mkdtemp(prefix='.allowance-worker-',dir=destination.parent))
    try:
        shutil.copytree(base,stage,dirs_exist_ok=True)
        (stage/CHANGED).write_bytes(source);data['files'][CHANGED]={'bytes':len(source),'sha256':sha(source)}
        result=(json.dumps(data,indent=2,sort_keys=True)+'\n').encode();(stage/'files-service.json').write_bytes(result)
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        stage.rename(destination)
        return {'directory':str(destination),'manifestSHA256':sha(result),'changed':[CHANGED]}
    finally:
        if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(build(a.base,a.output),indent=2))
    except (ValueError,OSError,subprocess.CalledProcessError) as error:p.error(str(error))
