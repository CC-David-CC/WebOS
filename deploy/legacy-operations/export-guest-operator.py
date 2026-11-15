#!/usr/bin/env python3
"""Export the root guest lifecycle operator without private configs or keys."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from guest_service.operator import OPERATOR_FILES
def record(file):return {'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
def verify(folder):
    folder=Path(folder)
    if any(p.is_symlink() for p in [folder,*folder.parents]) or not folder.is_dir():raise ValueError('Real guest operator directory required')
    manifest=folder/'guest-operator.json'
    if manifest.is_symlink() or not manifest.is_file():raise ValueError('Regular operator manifest required')
    value=json.loads(manifest.read_text())
    if set(value)!={'version','files'} or value['version']!='codi-guest-network-operator/1' or set(value['files'])!=OPERATOR_FILES:raise ValueError('Exact operator allowlist required')
    found=set()
    for file in folder.rglob('*'):
        if file.is_symlink():raise ValueError('Linked guest operator input')
        if file.is_dir():continue
        if not file.is_file() or file.stat().st_nlink!=1:raise ValueError('Regular unlinked guest operator input required')
        name=str(file.relative_to(folder));found.add(name)
        if name!='guest-operator.json' and value['files'].get(name)!=record(file):raise ValueError('Changed or extra operator input')
    if found!=OPERATOR_FILES|{'guest-operator.json'}:raise ValueError('Missing operator input')
    return {'status':'PASS','manifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'files':value['files']}
def export(target):
    target=Path(target).absolute()
    if '..' in target.parts or target.exists() or any(p.is_symlink() for p in [target,*target.parents]) or not target.is_relative_to(ROOT/'.build/guest-operators'):raise ValueError('Choose a new private guest-operator build directory')
    target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.guest-operator-',dir=target.parent))
    try:
        for name in sorted(OPERATOR_FILES):
            source=ROOT/name
            if not source.is_file() or any(p.is_symlink() for p in [source,*source.parents]):raise ValueError('Regular operator source required')
            file=stage/name;file.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,file)
        (stage/'guest-operator.json').write_text(json.dumps({'version':'codi-guest-network-operator/1','files':{name:record(stage/name) for name in sorted(OPERATOR_FILES)}},sort_keys=True,indent=2)+'\n')
        for file in [stage,*stage.rglob('*')]:file.chmod(0o755 if file.is_dir() else 0o644)
        verify(stage);stage.rename(target)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(target)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--output',type=Path);action.add_argument('--verify',type=Path);args=parser.parse_args()
    print(json.dumps(export(args.output) if args.output else verify(args.verify),indent=2))
