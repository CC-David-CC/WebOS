#!/usr/bin/env python3
"""Export only reviewed Browser-relay source into an immutable runtime tree.

No user data, generated browser engine, Python venv, issuer secret or public
asset is included. Operators must separately provision private policies and
install the runtime and service after testing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parent
FILES=(
    'active-system/scripts/serve-browser-relay.py',
    'active-system/scripts/browser-audit-report.py',
    'active-system/browser_service/__init__.py',
    'active-system/browser_service/authorization.py',
    'active-system/browser_service/http.py',
    'active-system/browser_service/sessions.py',
    'active-system/network_policy/__init__.py',
    'active-system/network_policy/policy.py',
    'active-system/codiserver-server-v0.3.0/codiauth/__init__.py',
    'active-system/codiserver-server-v0.3.0/codiauth/jose.py',
    'apps/system/browser/relay/__init__.py',
    'apps/system/browser/relay/policy.py',
    'apps/system/browser/relay/wisp.py',
    'apps/system/browser/relay/audit.py',
    'apps/system/browser/relay/download.py',
    'apps/system/browser/relay/report.py',
    'apps/system/browser/relay/report_requests.py',
)

def digest(raw):return hashlib.sha256(raw).hexdigest()
def build(destination):
    destination=Path(destination).absolute();parent=destination.parent
    if destination.exists() or destination.is_symlink() or not parent.is_dir():raise ValueError('A new output directory under an existing directory is required')
    changed=subprocess.check_output(['git','-C',str(WORKSPACE),'status','--porcelain','--',*FILES],text=True)
    if changed:raise ValueError('Commit runtime sources before exporting the pinned artifact')
    stage=Path(tempfile.mkdtemp(prefix='.browser-relay-stage-',dir=parent))
    try:
        records={}
        for name in FILES:
            source=WORKSPACE/name
            if source.is_symlink() or not source.is_file():raise ValueError('Expected reviewed source: '+name)
            raw=source.read_bytes()
            if len(raw)>1024*1024:raise ValueError('Unexpectedly large source: '+name)
            target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);target.chmod(0o644)
            records[name]={'bytes':len(raw),'sha256':digest(raw)}
        commit=subprocess.check_output(['git','-C',str(WORKSPACE),'rev-parse','HEAD'],text=True).strip()
        manifest={'version':'codi-browser-relay-runtime/1','sourceCommit':commit,'files':records}
        raw=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
        (stage/'browser-relay-runtime.json').write_bytes(raw)
        for path in [stage,*stage.rglob('*')]:
            if path.is_symlink():raise ValueError('Linked artifact refused')
            path.chmod(0o755 if path.is_dir() else 0o644)
        stage.rename(destination)
        return {'directory':str(destination),'manifestSHA256':digest(raw),'files':len(records),'sourceCommit':commit}
    finally:
        if stage.exists():shutil.rmtree(stage)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    try:print(json.dumps(build(a.output),indent=2))
    except (ValueError,OSError,subprocess.CalledProcessError) as error:p.error(str(error))
