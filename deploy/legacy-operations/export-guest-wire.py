#!/usr/bin/env python3
"""Export only the fixed-role worker runtime, never credentials or service state."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from guest_service.installation import WORKER_FILES

def record(path):return {'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def verify(folder):
    folder=Path(folder)
    if folder.is_symlink() or not folder.is_dir():raise ValueError('Real guest worker runtime directory required')
    manifest=folder/'guest-wire.json'
    if manifest.is_symlink() or not manifest.is_file():raise ValueError('Regular guest worker manifest required')
    value=json.loads(manifest.read_text())
    if set(value)!={'version','files'} or value['version']!='codi-guest-wire-runtime/1' or set(value['files'])!=WORKER_FILES:raise ValueError('Exact worker runtime allowlist required')
    found=set()
    for path in folder.rglob('*'):
        if path.is_symlink():raise ValueError('Linked worker runtime input')
        if path.is_dir():continue
        if not path.is_file() or path.stat().st_nlink!=1:raise ValueError('Regular unlinked worker runtime input required')
        name=str(path.relative_to(folder));found.add(name)
        if name!='guest-wire.json' and value['files'].get(name)!=record(path):raise ValueError('Changed or extra worker runtime input')
    if found!=WORKER_FILES|{'guest-wire.json'}:raise ValueError('Missing worker runtime input')
    return {'status':'PASS','manifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'files':value['files']}
def export(destination):
    destination=Path(destination).absolute()
    if '..' in destination.parts or destination.exists() or any(p.is_symlink() for p in [destination,*destination.parents]) or not destination.is_relative_to(ROOT/'.build/guest-workers'):raise ValueError('Choose a new private guest-worker build directory')
    destination.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.guest-wire-',dir=destination.parent))
    try:
        for name in sorted(WORKER_FILES):
            source=ROOT/name
            if source.is_symlink() or not source.is_file() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):raise ValueError('Regular worker source required')
            path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,path)
        (stage/'guest-wire.json').write_text(json.dumps({'version':'codi-guest-wire-runtime/1','files':{name:record(stage/name) for name in sorted(WORKER_FILES)}},sort_keys=True,indent=2)+'\n')
        for path in [stage,*stage.rglob('*')]:path.chmod(0o755 if path.is_dir() else 0o644)
        verify(stage);stage.rename(destination)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(destination)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--output',type=Path);action.add_argument('--verify',type=Path);args=parser.parse_args()
    print(json.dumps(export(args.output) if args.output else verify(args.verify),indent=2))
