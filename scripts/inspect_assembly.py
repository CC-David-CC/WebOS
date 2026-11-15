#!/usr/bin/env python3
"""Inspect source composition without fetching, building, or touching account state."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

PLATFORM = frozenset(('runtime', 'desktop', 'login', 'accounts', 'storage'))
SHARED_ROLES = {name: 'libraries' for name in (
    'craft-libs', 'egui', 'codemirror', 'gltf-transform', 'wavesurfer', 'tone',
    'zip', 'mermaid', 'echarts', 'plotly', 'pdfme', 'maplibre', 'transformers',
    'trystero', 'tanstack-virtual', 'webtorrent', 'yjs', 'learning-game-core')}
SHARED_ROLES.update({'craft-fonts': 'assets', 'craft-i18n': 'assets',
                     'craft-common-actions': 'tooling', 'rooms': 'legacy'})
CORE = frozenset(('runtime', 'desktop', 'login', 'accounts', 'storage', 'files', 'wordcraft'))


def organized_path(component, path):
    parts = Path(path).parts
    role = SHARED_ROLES.get(component, 'platform' if component in PLATFORM else
                            'engines' if component.startswith('engine-') else 'apps')
    return (len(parts) == 2 and parts[0] == role and
            '..' not in parts and not Path(path).is_absolute())


def git(root, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0')
    result = subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                             '-c', 'core.hooksPath=/dev/null', '-C', str(root), *args],
                            env=env, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError('Local Git inspection failed: ' + ' '.join(args[:2]))
    return result.stdout.strip()


def inspect(root):
    root = Path(root).resolve()
    links = {}
    for line in git(root, 'ls-files', '--stage').splitlines():
        info, path = line.split('\t', 1)
        mode, commit, stage = info.split()
        if mode == '160000':
            links[path] = commit
    records = []
    errors = []
    for line in git(root, 'config', '--file', str(root / '.gitmodules'), '--get-regexp',
                    r'^submodule\..*\.path$').splitlines():
        key, path = line.split(None, 1)
        component = key[len('submodule.'):-len('.path')]
        url = git(root, 'config', '--file', str(root / '.gitmodules'), '--get', key[:-4] + 'url')
        if not re.fullmatch(r'[a-z][a-z0-9-]*', component):
            errors.append('Invalid component identity')
            continue
        if not organized_path(component, path):
            errors.append('Component outside organized source layout: ' + path)
        if url != '../' + component + '.git':
            errors.append('Unexpected sibling origin URL: ' + component)
        if path not in links:
            errors.append('Submodule path lacks a Git link: ' + path)
            continue
        child = root / path
        try:
            head = git(child, 'rev-parse', 'HEAD')
            git_dir = Path(git(child, 'rev-parse', '--absolute-git-dir'))
            if head != links[path]:
                errors.append('Checkout differs from selected commit: ' + path)
            if not git_dir.is_relative_to(root / '.git' / 'modules'):
                errors.append('Component metadata outside this assembly: ' + path)
            if (git_dir / 'objects/info/alternates').exists():
                errors.append('Component depends on an object alternate: ' + path)
            if git(child, 'status', '--porcelain', '--untracked-files=all'):
                errors.append('Component has uncommitted changes: ' + path)
            records.append({'id': component, 'path': path, 'commit': head})
        except (RuntimeError, OSError):
            errors.append('Component checkout unavailable: ' + path)
    if set(links) != {r['path'] for r in records}:
        errors.append('Git links and available component checkouts disagree')
    return {'parent_commit': git(root, 'rev-parse', 'HEAD'), 'components': records,
            'component_count': len(records), 'missing_core_sources': sorted(CORE - {r['id'] for r in records}),
            'errors': errors, 'scope': 'source composition only; no functional readiness claim'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--require-core', action='store_true')
    args = parser.parse_args()
    report = inspect(args.root)
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['errors'] or args.require_core and report['missing_core_sources'] else 0)
