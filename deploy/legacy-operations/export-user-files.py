#!/usr/bin/env python3
"""Export only the file worker's declared code/dependency lock; never user state."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT=Path(__file__).resolve().parent.parent
FILES=[*('gateway_service/'+name for name in ['__init__.py','auth.py','policy.py','user_store.py','http.py','transfers.py','client.mjs']),
       'codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py',
       'scripts/serve-user-files.py','requirements.lock']
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    target=args.output.absolute()
    if '..' in target.parts or target.exists() or any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('Choose a new private worker export directory')
    if not target.is_relative_to(ROOT/'.build/gateways'):raise ValueError('Export the worker only into the private gateway build directory')
    target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.files-worker-',dir=target.parent))
    try:
        metadata={'version':'codi-private-file-service/1','files':{}}
        for name in FILES:
            source=ROOT/name
            if source.is_symlink() or not source.is_file() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):raise ValueError('Regular declared source required')
            raw=source.read_bytes();destination=stage/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw);destination.chmod(0o644)
            metadata['files'][name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        raw=(json.dumps(metadata,indent=2,sort_keys=True)+'\n').encode();(stage/'files-service.json').write_bytes(raw);(stage/'files-service.json').chmod(0o644)
        for directory in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:directory.chmod(0o755)
        stage.rename(target);print(json.dumps({'status':'PASS','manifestSHA256':hashlib.sha256(raw).hexdigest(),'files':len(FILES),'privateStateIncluded':False,'installed':False},indent=2))
    finally:
        if stage.exists():shutil.rmtree(stage)
