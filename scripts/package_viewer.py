#!/usr/bin/env python3
"""Verify committed source inputs and package an owned existing-viewer candidate.

Only public files and dependency notices enter the archive. No deployment action.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent.parent
BASE_BYTES = 256 * 1024 * 1024
OPTIONAL_ENGINES = {app: 64 * 1024 * 1024 for app in ('gridcraft', 'deckcraft', 'photocraft', 'figcraft', 'anicraft', 'lightcraft', 'soundcraft')}
OPTIONAL_ENGINES['designcraft'] = 96 * 1024 * 1024
OPTIONAL_ENGINES['vectorcraft'] = 128 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(folder, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                                    '-c', 'core.hooksPath=/dev/null', '-C', str(folder), *args],
                                   env=dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1'))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    site, archive = args.site.absolute(), args.archive.absolute()
    if site.is_relative_to(ROOT) or archive.is_relative_to(site) or archive.exists():
        parser.error('Existing external candidate and new separate archive required')
    for target in (site, archive):
        if any(p.is_symlink() for p in (target, *target.parents)):
            parser.error('Direct paths required')
    build = json.loads((site / 'viewer-build.json').read_text())
    assert build['schema'] == 'webos-existing-viewer-build/1'
    if build.get('developmentOnly'):
        parser.error('This development profile is for loopback tests')
    assert not (site / 'viewer-release.json').exists(), 'Candidate already packaged'
    owners = set()
    packages = {}
    for row in build['sourceInputs']:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        file = ROOT / relative
        assert file.is_file() and digest(file.read_bytes()) == row['sha256'], 'Build source changed'
        parts = relative.parts
        if 'node_modules' in parts:
            index = max(i for i, p in enumerate(parts) if p == 'node_modules')
            end = index + (3 if parts[index + 1].startswith('@') else 2)
            package = ROOT.joinpath(*parts[:end])
            if (package / 'package.json').is_file():
                packages[package] = json.loads((package / 'package.json').read_text())
        else:
            owner = Path(*parts[:2]) if parts[0] in ('apps', 'platform', 'libraries', 'engines', 'assets', 'tooling') else Path('.')
            source_path = relative.relative_to(owner) if owner != Path('.') else relative
            assert digest(git(ROOT / owner, 'show', 'HEAD:' + source_path.as_posix())) == row['sha256'], 'Uncommitted source input'
            owners.add(owner)
    overrides_root = ROOT / 'platform/runtime/active-system/tools/app-builder'
    overrides = json.loads((overrides_root / 'dependency-notices.json').read_text())
    notices = []
    for folder, package in sorted(packages.items(), key=lambda row: str(row[0])):
        name, version = package['name'], package['version']
        files = [f for f in folder.iterdir() if f.is_file() and re.match(r'^(licen[cs]e|copying|notice)', f.name, re.I)]
        selected = [(f.name, f.read_bytes()) for f in files]
        if not selected:
            override = overrides.get(name + '@' + version)
            assert override, 'Missing reviewed dependency notice: ' + name
            file = overrides_root / override['path']
            data = file.read_bytes()
            assert digest(data) == override['sha256']
            selected = [(file.name, data)]
        label = re.sub(r'[^A-Za-z0-9_.-]', '_', name) + '-' + version
        paths = []
        for filename, data in selected:
            assert len(data) <= 1024 * 1024 and Path(filename).name == filename
            target = site / 'notices/js' / label / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert target.read_bytes() == data
            else:
                target.write_bytes(data)
            paths.append(target.relative_to(site).as_posix())
        notices.append({'name': name, 'version': version, 'license': package.get('license'), 'notices': paths})
    (site / 'notices/js-packages.json').write_text(json.dumps(notices, indent=2) + '\n')
    components = {owner.as_posix(): git(ROOT / owner, 'rev-parse', 'HEAD').decode().strip() for owner in sorted(owners)}
    components['apps/wordcraft'] = git(ROOT / 'apps/wordcraft', 'rev-parse', 'HEAD').decode().strip()
    if 'pdfcraftEngine' in build:
        components['apps/pdfcraft'] = git(ROOT / 'apps/pdfcraft', 'rev-parse', 'HEAD').decode().strip()
    for app in OPTIONAL_ENGINES:
        if app + 'Engine' in build:
            components['apps/' + app] = git(ROOT / 'apps' / app, 'rev-parse', 'HEAD').decode().strip()
    for owner, commit in components.items():
        if owner == '.':
            continue
        pin = git(ROOT, 'ls-tree', 'HEAD', '--', owner).decode().strip()
        assert pin == f'160000 commit {commit}\t{owner}', 'Parent pin differs from build source: ' + owner
    records = []
    for file in sorted(site.rglob('*')):
        assert not file.is_symlink()
        if not file.is_file():
            continue
        relative = file.relative_to(site)
        assert not any(part.startswith('.') or part in ('node_modules', 'target', '__pycache__') for part in relative.parts)
        data = file.read_bytes()
        records.append({'path': relative.as_posix(), 'bytes': len(data), 'sha256': digest(data)})
    base_bytes = sum(row['bytes'] for row in records)
    for app in OPTIONAL_ENGINES:
        engine = build.get(app + 'Engine')
        engine_bytes = sum(row['bytes'] for row in records if row['path'].startswith(app + '/'))
        if engine is None:
            assert app not in build['apps'] and not engine_bytes, 'Unexpected unselected component: ' + app
            continue
        assert app in build['apps'] and 0 < engine_bytes < OPTIONAL_ENGINES[app]
        receipt_bytes = (site / app / 'component-build.json').read_bytes()
        assert digest(receipt_bytes) == engine['receiptSHA256']
        assert engine_bytes == engine['bytes'] + len(receipt_bytes)
        assert components['apps/' + app] == engine['sourceCommit']
        base_bytes -= engine_bytes
    assert base_bytes < BASE_BYTES, 'Unexpected viewer and baseline engine growth'
    receipt = {'schema': 'webos-existing-viewer-release/1', 'parentCommit': git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
               'components': components, 'engine': build['engine'],
               **({'pdfcraftEngine': build['pdfcraftEngine']} if 'pdfcraftEngine' in build else {}),
               **{app + 'Engine': build[app + 'Engine'] for app in OPTIONAL_ENGINES if app + 'Engine' in build},
               'apps': build['apps'], 'files': records,
               'backend': 'Existing ksu.codes service and account state retained; deployment report records running backend pins and concurrency configuration',
               'npmLockSHA256': digest((ROOT / 'package-lock.json').read_bytes())}
    data = (json.dumps(receipt, indent=2) + '\n').encode()
    (site / 'viewer-release.json').write_bytes(data)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, 'w:gz', compresslevel=6) as tar:
        for file in sorted(site.rglob('*')):
            if file.is_file():
                tar.add(file, arcname=file.relative_to(site).as_posix(), recursive=False)
    print(json.dumps({'releaseId': digest(data), 'archiveSHA256': digest(archive.read_bytes()),
                      'files': len(records) + 1, 'payloadBytes': sum(row['bytes'] for row in records) + len(data),
                      'archiveBytes': archive.stat().st_size, 'javascriptPackagesWithNotices': len(notices)}))


if __name__ == '__main__':
    main()
