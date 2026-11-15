#!/usr/bin/env python3
"""Export the batched-version file worker against the exact live dependency lock.

This creates only a private candidate. It does not install or change account
data, the running gateway, issuer, proxy limits or the desktop frontend.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE_PIN='be4a9ef3a613c2e90517fae427d4d2256b97b74ee2134c10cafe263fc2440eac'
CHANGED={'gateway_service/user_store.py','gateway_service/http.py','gateway_service/client.mjs'}


def digest(raw):return hashlib.sha256(raw).hexdigest()
def build(base,destination):
    base=Path(base).absolute();destination=Path(destination).absolute()
    if base.is_symlink() or not base.is_dir() or destination.exists() or destination.is_symlink() or not destination.parent.is_dir():raise ValueError('Existing baseline and new output required')
    if base in destination.parents or destination in base.parents:raise ValueError('Baseline and output must be disjoint')
    raw=(base/'files-service.json').read_bytes()
    if digest(raw)!=BASE_PIN:raise ValueError('Unexpected live worker manifest')
    old=json.loads(raw)
    spec=importlib.util.spec_from_file_location('files_exporter',ROOT/'scripts/export-user-files.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
    expected=set(exporter.FILES)
    paths=['active-system/'+name for name in exporter.FILES if name!='requirements.lock']
    changed_source=subprocess.run(['git','-C',str(ROOT.parent),'status','--porcelain','--',*paths],check=True,capture_output=True,text=True).stdout
    if changed_source:raise ValueError('Commit worker source before exporting a release candidate')
    if old.get('version')!='codi-private-file-service/1' or set(old.get('files',{}))!=expected:raise ValueError('Unexpected live worker contract')
    actual=set()
    for p in base.rglob('*'):
        if p.is_symlink():raise ValueError('Linked baseline refused')
        if p.is_dir():continue
        if not p.is_file():raise ValueError('Unexpected baseline entry')
        name=p.relative_to(base).as_posix();actual.add(name)
        if name!='files-service.json':
            data=p.read_bytes()
            if old['files'].get(name)!={'bytes':len(data),'sha256':digest(data)}:raise ValueError('Changed baseline file: '+name)
    if actual!=expected|{'files-service.json'}:raise ValueError('Missing or extra baseline inputs')
    stage=Path(tempfile.mkdtemp(prefix='.batch-version-worker-',dir=destination.parent))
    try:
        records={};changed=set()
        for name in exporter.FILES:
            source=(ROOT/name) if name!='requirements.lock' else (base/name)
            if source.is_symlink() or not source.is_file():raise ValueError('Expected regular source: '+name)
            data=source.read_bytes()
            if len(data)>262144:raise ValueError('Unexpected source size: '+name)
            record={'bytes':len(data),'sha256':digest(data)};records[name]=record
            if record!=old['files'][name]:changed.add(name)
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o644)
        if changed!=CHANGED:raise ValueError('Unexpected worker source differences: '+repr(sorted(changed)))
        raw=(json.dumps({'version':'codi-private-file-service/1','files':records},indent=2,sort_keys=True)+'\n').encode()
        (stage/'files-service.json').write_bytes(raw);(stage/'files-service.json').chmod(0o644)
        for path in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:path.chmod(0o755)
        stage.rename(destination)
        return {'manifestSHA256':digest(raw),'changed':sorted(changed),'requirementsPreserved':True,'installed':False}
    finally:
        if stage.exists():shutil.rmtree(stage)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(build(a.base,a.output),indent=2))
    except (ValueError,OSError) as error:p.error(str(error))
