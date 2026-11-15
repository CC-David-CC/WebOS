#!/usr/bin/env python3
"""Build a source-only, hash-pinned Browser audit operator bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]
FILES=('active-system/scripts/manage-browser-audit.py',
       'active-system/scripts/render-browser-service.py',
       'active-system/browser_service/audit_switch.py')

def build(destination):
    destination=Path(destination).absolute()
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():raise ValueError('Choose a new output under an existing parent')
    if subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain','--',*FILES],text=True):raise ValueError('Commit operator sources before export')
    stage=Path(tempfile.mkdtemp(prefix='.browser-audit-operator-',dir=destination.parent))
    try:
        files={}
        for name in FILES:
            source=ROOT/name
            if source.is_symlink() or not source.is_file():raise ValueError('Missing operator source')
            raw=source.read_bytes()
            if len(raw)>1024*1024:raise ValueError('Operator source too large')
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);target.chmod(0o644)
            files[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        manifest={'version':'codi-browser-audit-operator/1','files':files}
        raw=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode();(stage/'browser-audit-operator.json').write_bytes(raw)
        for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
        stage.rename(destination);return {'manifestSHA256':hashlib.sha256(raw).hexdigest(),'directory':str(destination),'files':len(files)}
    finally:
        if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(build(a.output),indent=2))
    except (ValueError,OSError,subprocess.CalledProcessError) as error:p.error(str(error))
