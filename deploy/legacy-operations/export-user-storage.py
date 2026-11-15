#!/usr/bin/env python3
"""Export private storage source only; never reads accounts or user files."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ['gateway_service/__init__.py', 'gateway_service/policy.py', 'gateway_service/user_store.py',
         'scripts/storage-admin.py', 'scripts/install-user-storage.py',
         'scripts/install-service-accounts.py', 'scripts/user-storage-check.py']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    metadata = {'version': 'codi-private-storage/1', 'files': {}}
    for name in FILES:
        raw = (ROOT/name).read_bytes()
        destination = args.output/name;destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        metadata['files'][name] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    raw = (json.dumps(metadata, indent=2, sort_keys=True) + '\n').encode()
    (args.output/'storage.json').write_bytes(raw)
    print(json.dumps({'status': 'PASS', 'manifestSHA256': hashlib.sha256(raw).hexdigest(), 'files': len(FILES), 'privateStateIncluded': False}))
