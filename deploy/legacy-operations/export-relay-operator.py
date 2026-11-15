#!/usr/bin/env python3
"""Export exactly the public-source native relay operator, without credentials."""
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = {'relay_service/__init__.py', 'relay_service/manager.py', 'relay_service/certificates.py', 'scripts/manage-relay.py', 'requirements.lock'}


def record(p):
    return {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def verify(folder):
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError('Regular operator directory required')
    manifest = folder / 'relay-operator.json'
    if manifest.is_symlink():
        raise ValueError('Linked manifest refused')
    value = json.loads(manifest.read_text())
    if set(value) != {'version', 'files'} or value['version'] != 'codi-relay-operator/2' or set(value['files']) != FILES:
        raise ValueError('Unexpected operator manifest')
    found = set()
    for p in folder.rglob('*'):
        if p.is_symlink():
            raise ValueError('Linked operator input refused')
        if p.is_dir():
            continue
        if not p.is_file() or p.stat().st_nlink != 1:
            raise ValueError('Regular unlinked operator file required')
        name = str(p.relative_to(folder))
        if name == 'relay-operator.json':
            continue
        if name not in FILES or record(p) != value['files'][name]:
            raise ValueError('Changed or extra operator file')
        found.add(name)
    if found != FILES:
        raise ValueError('Missing operator input')
    return {'directory': str(folder), 'manifestSHA256': hashlib.sha256(manifest.read_bytes()).hexdigest(), 'files': value['files']}


def export(target):
    if target.exists() or target.is_symlink():
        raise ValueError('Choose a new export directory')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.relay-export-', dir=target.parent))
    try:
        for name in sorted(FILES):
            source = ROOT / name
            if source.is_symlink() or not source.is_file() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):
                raise ValueError('Regular source input required')
            dest = stage / name
            dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, dest)
            dest.chmod(0o644)
        value = {'version': 'codi-relay-operator/2', 'files': {name: record(stage / name) for name in sorted(FILES)}}
        (stage / 'relay-operator.json').write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
        for p in [stage, *stage.rglob('*')]:
            p.chmod(0o755 if p.is_dir() else 0o644)
        verify(stage)
        stage.rename(target)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return verify(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output', type=Path)
    group.add_argument('--verify', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.verify) if args.verify else export(args.output), indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))
