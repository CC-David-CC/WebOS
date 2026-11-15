#!/usr/bin/env python3
"""Freeze the root operator graph; no private configuration or key is copied."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('reader_export',ROOT/'scripts/export-reader-coordinator.py')
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
FILES=worker.FILES|{'reader_service/operator.py','file_service/__init__.py','file_service/operator.py','scripts/manage-reader-coordinator.py'}

def verify(target):
    target=Path(target)
    if target.is_symlink() or not target.is_dir():raise ValueError('Regular operator directory required')
    m=json.loads((target/'reader-operator.json').read_text())
    if set(m)!={'version','files'} or m['version']!='codi-reader-coordinator-operator/1' or set(m['files'])!=FILES:raise ValueError('Exact operator graph required')
    found=set()
    for p in target.rglob('*'):
        if p.is_symlink():raise ValueError('No linked operator input')
        if p.is_dir():continue
        if not p.is_file() or p.stat().st_nlink!=1:raise ValueError('Regular unlinked operator input required')
        name=str(p.relative_to(target));found.add(name)
        if name!='reader-operator.json' and m['files'].get(name)!={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}:raise ValueError('Changed or extra operator input')
    if found!=FILES|{'reader-operator.json'}:raise ValueError('Missing operator input')
    return hashlib.sha256((target/'reader-operator.json').read_bytes()).hexdigest()

def export(target):
    target=Path(target).absolute()
    if target.exists() or '..' in target.parts or not target.is_relative_to(ROOT/'.build') or any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('Choose a new local managed build directory')
    target.mkdir(parents=True)
    records={}
    for name in sorted(FILES):
        source=ROOT/name
        if not source.is_file() or source.is_symlink():raise ValueError('Regular operator input required')
        p=target/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,p);p.chmod(0o644)
        records[name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    raw=(json.dumps({'version':'codi-reader-coordinator-operator/1','files':records},sort_keys=True,indent=2)+'\n').encode()
    (target/'reader-operator.json').write_bytes(raw)
    for p in [target,*target.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
    return {'status':'PASS','directory':str(target),'manifestSHA256':verify(target),'files':len(records),'privateStateCopied':False,'installed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-directory',type=Path,required=True);a=p.parse_args();print(json.dumps(export(a.output_directory)))
