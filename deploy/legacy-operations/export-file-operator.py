#!/usr/bin/env python3
"""Export only the root file-service operator, never a private service config."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parent.parent
FILES={'file_service/__init__.py','file_service/operator.py','scripts/manage-user-files.py'}
def record(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def verify(folder):
    if folder.is_symlink() or not folder.is_dir():raise ValueError('Regular operator directory required')
    manifest=folder/'file-operator.json'
    if manifest.is_symlink():raise ValueError('Linked operator manifest')
    value=json.loads(manifest.read_text())
    if set(value)!={'version','files'} or value['version']!='codi-file-operator/1' or set(value['files'])!=FILES:raise ValueError('Unexpected file operator manifest')
    found=set()
    for p in folder.rglob('*'):
        if p.is_symlink():raise ValueError('Linked operator input')
        if p.is_dir():continue
        if not p.is_file() or p.stat().st_nlink!=1:raise ValueError('Regular unlinked operator input required')
        name=str(p.relative_to(folder));found.add(name)
        if name!='file-operator.json' and value['files'].get(name)!=record(p):raise ValueError('Changed/extra operator input')
    if found!=FILES|{'file-operator.json'}:raise ValueError('Operator file missing')
    return {'status':'PASS','manifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'files':value['files']}
def export(target):
    target=target.absolute()
    if '..' in target.parts or target.exists() or any(p.is_symlink() for p in [target,*target.parents]) or not target.is_relative_to(ROOT/'.build/file-operators'):raise ValueError('Choose a new private file-operator build directory')
    target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.file-operator-',dir=target.parent))
    try:
        for name in sorted(FILES):
            source=ROOT/name
            if source.is_symlink() or not source.is_file() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):raise ValueError('Regular operator source required')
            p=stage/name;p.parent.mkdir(exist_ok=True);shutil.copyfile(source,p);p.chmod(0o644)
        (stage/'file-operator.json').write_text(json.dumps({'version':'codi-file-operator/1','files':{name:record(stage/name) for name in sorted(FILES)}},sort_keys=True,indent=2)+'\n')
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        verify(stage);stage.rename(target)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return verify(target)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True);group.add_argument('--output',type=Path);group.add_argument('--verify',type=Path);args=parser.parse_args()
    print(json.dumps(verify(args.verify) if args.verify else export(args.output),indent=2))
