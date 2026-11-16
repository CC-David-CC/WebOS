#!/usr/bin/env python3
"""Inspect or restore known read-only Craft upstream configuration after a clone.

Never fetches, pushes, switches branches, moves refs or changes selected source.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def git(folder, *args, required=True):
    result = subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                             '-c', 'core.hooksPath=/dev/null', '-C', str(folder), *args],
                            env=dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_NO_LAZY_FETCH='1',
                                     GIT_TERMINAL_PROMPT='0'), capture_output=True, text=True)
    if required and result.returncode:
        raise RuntimeError('Git operation failed in ' + str(folder.relative_to(ROOT)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--configure', action='store_true', help='Add missing verified upstreams and branch tracking only')
    args = parser.parse_args()
    components = json.loads((ROOT / 'migration/CRAFT-UPSTREAMS.json').read_text())['components']
    preflight = []
    for row in components:
        folder = (ROOT / row['path']).resolve()
        if not folder.is_relative_to(ROOT) or not (folder / '.git').is_file():
            raise ValueError('Expected initialized owned submodule: ' + row['path'])
        remote = git(folder, 'remote', 'get-url', 'upstream', required=False)
        if remote.returncode == 0 and remote.stdout.strip() != row['upstream']:
            raise ValueError('Unexpected upstream; refusing to overwrite: ' + row['path'])
        preflight.append((row, folder, remote.returncode == 0))
    results = []
    for row, folder, present in preflight:
        branch = row['trackingBranch']
        head = git(folder, 'rev-parse', 'HEAD').stdout.strip()
        if args.configure:
            if not present:
                git(folder, 'remote', 'add', 'upstream', row['upstream'])
            git(folder, 'config', 'branch.' + branch + '.remote', 'upstream')
            git(folder, 'config', 'branch.' + branch + '.merge', 'refs/heads/' + branch)
        assert git(folder, 'rev-parse', 'HEAD').stdout.strip() == head
        results.append({'path': row['path'], 'upstreamConfigured': present or args.configure,
                        'trackingBranch': branch, 'workingSourceUnchanged': True})
    print(json.dumps({'configured': args.configure, 'networkActions': 0, 'components': results}, indent=2))


if __name__ == '__main__':
    main()
