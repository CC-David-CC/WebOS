#!/usr/bin/env python3
"""Reconcile declared app assets with source and the locked beta reference cache."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def safe_path(base, name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Unsafe declared asset path')
    target = base.joinpath(*relative.parts)
    if not target.resolve().is_relative_to(base.resolve()):
        raise ValueError('Asset escapes component or reference cache')
    return target


def inspect(root):
    scope = json.loads((root / 'migration/scope.json').read_text())
    lock = json.loads((root / 'artifacts/reference-beta.lock.json').read_text())
    reference = root / lock['payload_path']
    catalog = {app['id']: app for app in lock['catalog']['apps']}
    apps = []
    for app in scope['registered_apps']:
        component = root / app['component_path']
        if app['id'] == 'jsketcher':
            component = component / 'webos'
        manifest = component / 'app.json'
        if not manifest.is_file():
            apps.append({'id': app['id'], 'manifest': None, 'assets': [],
                         'note': 'No app.json at owned entrypoint; build inputs require separate review'})
            continue
        declarations = json.loads(manifest.read_text()).get('assets', [])
        payload = catalog.get(app['id'])
        records = []
        for name in declarations:
            source = safe_path(component, name)
            record = {'path': name, 'source_present': source.is_file(),
                      'reference_available': False}
            metadata = payload['files'].get(name) if payload else None
            if metadata:
                relative = PurePosixPath(payload['path']).parent / name
                target = safe_path(reference, str(relative))
                if target.is_file():
                    with target.open('rb') as stream:
                        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                    if target.stat().st_size != metadata['bytes'] or digest != metadata['sha256']:
                        raise ValueError('Reference asset differs from lock: ' + app['id'] + '/' + name)
                    record.update(reference_available=True, reference_path=str(target.relative_to(root)),
                                  bytes=metadata['bytes'], sha256=digest)
                    if source.is_file():
                        with source.open('rb') as stream:
                            record['source_matches_reference'] = hashlib.file_digest(stream, 'sha256').hexdigest() == digest
            records.append(record)
        apps.append({'id': app['id'], 'manifest': str(manifest.relative_to(root)), 'assets': records})
    records = [record for app in apps for record in app['assets']]
    return {'scope': 'Declared file paths only; reference payload bytes are not proof of source rebuild or complete dynamic asset graph',
            'registered_entries': len(apps), 'declared_assets': len(records),
            'source_present': sum(r['source_present'] for r in records),
            'verified_reference_available': sum(r['reference_available'] for r in records),
            'missing_from_source_and_reference': sum(not r['source_present'] and not r['reference_available'] for r in records),
            'apps': apps}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    print(json.dumps(inspect(args.root.resolve()), indent=2))
