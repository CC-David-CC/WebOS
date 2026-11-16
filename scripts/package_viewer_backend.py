#!/usr/bin/env python3
"""Package test-server code without account data or dependency installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS_BACKEND = 'c53a2f64b287b1f59bd90cdcd355766c5d713e63'


def git(owner, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.hooksPath=/dev/null', '-C', str(ROOT / owner), *args])


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    out, archive = args.output.absolute(), args.archive.absolute()
    assert not out.exists() and not archive.exists() and not out.is_relative_to(ROOT)
    assert not archive.is_relative_to(out)
    out.mkdir(mode=0o700)
    versions = {}
    for name in ('accounts', 'runtime', 'storage'):
        owner = 'platform/' + name
        commit = ACCOUNTS_BACKEND if name == 'accounts' else git(owner, 'rev-parse', 'HEAD').decode().strip()
        versions[owner] = commit
        prefix = 'src/webos_' + name + '/'
        files = git(owner, 'ls-tree', '-r', '--name-only', commit, '--', prefix).decode().splitlines()
        for source in files:
            if Path(source).suffix not in ('.py', '.json', '.mjs', '.txt'):
                continue
            relative = Path('packages') / ('webos_' + name) / source[len(prefix):]
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(owner, 'show', commit + ':' + source))
    server = git('.', 'show', 'HEAD:scripts/run_development.py')
    assert server == (ROOT / 'scripts/run_development.py').read_bytes()
    (out / 'run_development.py').write_bytes(server)
    records = [{'path': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
    value = {'schema': 'webos-viewer-backend/1', 'parentCommit': git('.', 'rev-parse', 'HEAD').decode().strip(),
             'components': versions, 'accountsPolicy': 'Exact retained source matching the current installed Accounts backend; no delegation-policy upgrade',
             'concurrentTransfers': 8, 'sharedConcurrentTransfers': 16, 'files': records}
    (out / 'backend-release.json').write_text(json.dumps(value, indent=2) + '\n')
    with tarfile.open(archive, 'w:gz') as tar:
        for file in sorted(out.rglob('*')):
            if file.is_file():
                tar.add(file, arcname=file.relative_to(out).as_posix(), recursive=False)
    print(json.dumps({'archiveSHA256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'bytes': archive.stat().st_size, 'files': len(records) + 1}))


if __name__ == '__main__':
    main()
