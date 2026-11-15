#!/usr/bin/env python3
"""Export the five-file standalone site operator without private service state."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
FILES = ['site_cutover/__init__.py', 'site_cutover/coordinator.py', 'site_cutover/managed.py',
         'scripts/site-cutover.py', 'scripts/native-rollout.py']


def export(parent):
    values = {n: (ROOT/n).read_bytes() for n in FILES}
    for raw in values.values():
        ast.parse(raw.decode())
    manifest = (json.dumps({'version': 'codi-site-cutover-operator/1',
                           'files': {n: {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                                     for n, raw in values.items()}}, indent=2, sort_keys=True)+'\n').encode()
    key = hashlib.sha256(manifest).hexdigest()
    values['site-cutover-operator.json'] = manifest
    destination = parent/key
    if destination.exists():
        if {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()} != set(values):
            raise ValueError('Existing export has unlisted/missing files')
        for n, raw in values.items():
            if (destination/n).is_symlink() or (destination/n).read_bytes() != raw:
                raise ValueError('Existing immutable export differs')
    else:
        destination.mkdir(parents=True)
        for n, raw in values.items():
            p = destination/n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
    return {'status': 'PASS', 'directory': str(destination), 'manifestSHA256': key,
            'declaredFiles': len(FILES), 'privateStateIncluded': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-parent', type=Path, default=ROOT/'.build/site-cutover-operators')
    args = parser.parse_args()
    print(json.dumps(export(args.output_parent), indent=2))
