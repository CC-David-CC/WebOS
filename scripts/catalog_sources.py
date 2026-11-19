#!/usr/bin/env python3
"""Describe existing component sources. No builds, installs, network or ref changes."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_ENTRIES = {
    'platform/desktop': ['active-system/index.html', 'active-system/app.js', 'active-system/style.css'],
    'apps/calculator': ['apps/system/calculator/index.mjs'],
    'apps/help': ['apps/system/help/index.mjs'],
    'apps/files': ['apps/system/files/index.mjs'],
    'apps/fieldcraft': ['apps/fieldcraft-web/Cargo.toml', 'apps/fieldcraft-web/index.html'],
    'apps/pcbcraft': ['apps/pcbcraft-web/Cargo.toml', 'apps/pcbcraft-web/index.html'],
    'apps/pcbcraft-app': ['assemble.sh'],
    'apps/sketchcraft': ['app/index.html', 'Cargo.toml'],
}
PLANNED = {'math-path', 'fraction-farm', 'word-weaver', 'market-math', 'rule-detective', 'pocket-conquest', 'tile-islands'}


def git(*args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', '-c', 'core.hooksPath=/dev/null', '-C', str(ROOT), *args], env=env, text=True)


def catalog():
    records = []
    for line in git('ls-files', '--stage').splitlines():
        meta, relative = line.split('\t', 1)
        if not meta.startswith('160000 '):
            continue
        folder = ROOT / relative
        files = set(p.name for p in folder.iterdir() if p.is_file() and p.name != '.git')
        manifests = sorted(files & {'Cargo.toml', 'Cargo.lock', 'package.json', 'package-lock.json', 'app.json', 'pyproject.toml', 'CMakeLists.txt', 'Makefile', 'Gruntfile.js'})
        entries = ORIGINAL_ENTRIES.get(relative, [])[:]
        entries += [name for name in ['index.mjs', 'index.html', 'main.py', 'model.mjs', 'core.mjs', 'client.mjs'] if name in files]
        docs = [name for name in ['README.md', 'Readme.md', 'MIGRATION.md', 'BUILDING.md', 'PROVENANCE.json'] if name in files]
        package_entries = []
        dependencies = []
        if 'package.json' in files:
            package = json.loads((folder / 'package.json').read_text())
            pending = [package.get('exports', {}), package.get('main', {})]
            while pending:
                item = pending.pop()
                if isinstance(item, str) and item.startswith('./') and '*' not in item:
                    package_entries.append(item)
                elif isinstance(item, dict):
                    pending.extend(item.values())
            dependencies = sorted(set(package.get('dependencies', {})) | set(package.get('devDependencies', {})) | set(package.get('peerDependencies', {})))
        for name in entries:
            if not (folder / name).is_file():
                raise ValueError('Missing designated source entry: ' + relative + '/' + name)
        records.append({'id': folder.name, 'path': relative, 'group': relative.split('/')[0],
                        'kind': 'planned-game-core' if folder.name in PLANNED else 'upstream-craft-app' if relative.startswith('apps/') and folder.name.endswith('craft') else 'component-source',
                        'sourceEntries': list(dict.fromkeys(entries)), 'packageEntrypoints': sorted(set(package_entries)),
                        'buildDefinitions': manifests, 'npmDependencies': dependencies, 'documentation': docs,
                        'sourceDirectories': sorted(p.name for p in folder.iterdir() if p.is_dir() and p.name not in {'.git', 'node_modules', 'target', 'dist', '__pycache__'}),
                        'scope': 'Existing source locations and declared recipes, not functional or build qualification.'})
    return {'schema': 'webos-source-catalog/1', 'selectedVersions': 'Parent Git links are authoritative; this catalog does not duplicate pins.', 'components': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Update the parent source catalog JSON and Markdown')
    args = parser.parse_args()
    value = catalog()
    if args.write:
        (ROOT / 'migration/SOURCE-CATALOG.json').write_text(json.dumps(value, indent=2) + '\n')
        lines = ['# On-disk component sources', '', 'Source locations only. Component versions are selected by the parent Git links. No parity, deployment or all-app runtime claim.', '', '| Component | Source silo | Source entries / build definitions |', '|---|---|---|']
        for row in value['components']:
            entries = row['sourceEntries'] or row['buildDefinitions'] or row['documentation']
            lines.append('| ' + row['id'] + (' (planned core)' if row['kind'] == 'planned-game-core' else '') + ' | `' + row['path'] + '/` | ' + ', '.join('`' + name + '`' for name in entries) + ' |')
        lines += ['', 'The JSON catalog separately records package integration entries and source directories. For Desktop, active-system/ is the existing intended viewer; the rejected replacement is removed. Historical operator/research/test sources remain explicitly historical and are not default runnable commands.', '', 'Dependencies declared in package/Cargo/build manifests may require installation or externally locked inputs. See component documentation, artifacts/README.md and CRAFT-BUILD-INPUTS.md. Do not execute inherited build/deployment operators blindly.']
        (ROOT / 'migration/SOURCE-CATALOG.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'components': len(value['components']), 'groups': {group: sum(row['group'] == group for row in value['components']) for group in sorted({row['group'] for row in value['components']})}, 'wroteCatalog': args.write}))


if __name__ == '__main__':
    main()
