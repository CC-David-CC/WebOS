#!/usr/bin/env python3
"""Verify organized immutable artifact inputs without network or filesystem writes."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def check(base, relative, metadata):
    if not base.resolve().is_relative_to(Path(__file__).resolve().parent.parent):
        raise ValueError('Artifact base escapes this assembly')
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts:
        raise ValueError('Unsafe artifact path')
    target = base.joinpath(*name.parts)
    for part in (target, *target.parents):
        if part == base:
            break
        if part.is_symlink():
            raise ValueError('Artifact symlink requires review: ' + relative)
    if not target.is_file() or target.stat().st_size != metadata['bytes']:
        raise ValueError('Missing or wrong-size artifact: ' + relative)
    with target.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != metadata['sha256']:
        raise ValueError('Artifact digest mismatch: ' + relative)
    return metadata['bytes']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs-only', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    artifacts = root / 'artifacts'
    files = total = 0
    inputs = json.loads((artifacts / 'input-files.json').read_text())
    if inputs['version'] != 'webos-build-input-files/1':
        raise ValueError('Unknown input lock version')
    for entry in inputs['files']:
        total += check(artifacts, entry['path'], entry)
        files += 1
    reference_files = 0
    if not args.inputs_only:
        lock = json.loads((artifacts / 'reference-beta.lock.json').read_text())
        if lock['version'] != 'webos-reference-beta-lock/1':
            raise ValueError('Unknown reference lock version')
        catalog = lock['catalog']
        key = hashlib.sha256(json.dumps(catalog, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        if key != lock['catalog_key'] or lock['payload_path'] != 'artifacts/reference-beta/' + key:
            raise ValueError('Reference identity changed')
        base = root / lock['payload_path']
        seen = set()
        for app in catalog['apps']:
            prefix = PurePosixPath(app['path']).parent
            for name, metadata in app['files'].items():
                relative = str(prefix / name)
                if relative in seen:
                    raise ValueError('Duplicate reference path')
                total += check(base, relative, metadata)
                seen.add(relative)
        reference_files = len(seen)
        files += reference_files
    print(json.dumps({'verified_files': files, 'verified_bytes': total,
                      'reference_files': reference_files, 'network': False,
                      'scope': 'locked input bytes only; no functional readiness claim'}))


if __name__ == '__main__':
    main()
