#!/usr/bin/env python3
"""Export the closed discovery-only worker graph, without state or installation."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
FILES={'reader_service/__init__.py','reader_service/contract.py','reader_service/http.py','reader_service/delegation.py',
       'room_service/__init__.py','room_service/contract.py','room_service/rendezvous.py',
       'codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py',
       'requirements.lock','scripts/serve-reader-coordinator.py','scripts/refresh-reader-delegation.py'}

def build(target):
    target=Path(target).resolve();assert not target.exists() and target.is_relative_to(ROOT/'.build');target.mkdir(parents=True)
    records={}
    for name in sorted(FILES):
        p=ROOT/name;assert p.is_file() and not p.is_symlink();q=target/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);q.chmod(0o644);records[name]={'bytes':q.stat().st_size,'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
    raw=(json.dumps({'version':'codi-reader-coordinator-worker/1','files':records},sort_keys=True,indent=2)+'\n').encode();(target/'reader-worker.json').write_bytes(raw)
    return {'status':'PASS','directory':str(target),'manifestSHA256':hashlib.sha256(raw).hexdigest(),'files':len(records),'roomStoreIncluded':False,'privateStateCopied':False,'installed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-directory',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();assert not a.receipt.exists();v=build(a.output_directory);a.receipt.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
