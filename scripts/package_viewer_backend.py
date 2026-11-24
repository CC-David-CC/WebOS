#!/usr/bin/env python3
"""Package test-server code without account data or dependency installation."""
import argparse
import hashlib
import json
import os
import re
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
    packaging = parser.add_mutually_exclusive_group()
    packaging.add_argument('--guest-network-base', type=Path,
                        help='Retain backend package versions from this release receipt and add the pinned guest modules')
    packaging.add_argument('--retained-backend', type=Path,
                           help='Retain verified packages and guest runtime from this installed backend directory')
    args = parser.parse_args()
    retained = None
    if args.guest_network_base:
        retained = json.loads(args.guest_network_base.read_bytes())
        if retained['schema'] != 'webos-viewer-backend/1' or set(retained['components']) != {
                'platform/accounts', 'platform/runtime', 'platform/storage'}:
            raise ValueError('Expected a viewer backend release with the three retained platform packages')
    out, archive = args.output.absolute(), args.archive.absolute()
    assert not out.exists() and not archive.exists() and not out.is_relative_to(ROOT)
    assert not archive.is_relative_to(out)
    out.mkdir(mode=0o700)
    versions = {}
    running = None
    if args.retained_backend:
        source = args.retained_backend.resolve(strict=True)
        running = json.loads((source / 'backend-release.json').read_bytes())
        if running['schema'] != 'webos-viewer-backend/1' or (running['concurrentTransfers'], running['sharedConcurrentTransfers']) != (8, 16):
            raise ValueError('Expected the retained viewer backend with the current transfer limits')
        versions = {key: running['components'][key] for key in
                    ('platform/accounts', 'platform/runtime', 'platform/storage')}
        for record in running['files']:
            name = record['path']
            if not (name.startswith('packages/') or name == 'serve-viewer-wire.py'):
                continue
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts or relative.as_posix() != name:
                raise ValueError(f'Invalid retained package path: {name}')
            path = source / relative
            data = path.read_bytes()
            if not path.resolve().is_relative_to(source) or len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError(f'Retained package bytes differ: {name}')
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(data)
    for name in (() if running else ('accounts', 'runtime', 'storage')):
        owner = 'platform/' + name
        commit = ACCOUNTS_BACKEND if name == 'accounts' else git(owner, 'rev-parse', 'HEAD').decode().strip()
        if retained:
            commit = retained['components'][owner]
            if not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit):
                raise ValueError('Expected a full retained component commit')
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
    extensions = {}
    if retained:
        old = {r['path']: r for r in retained['files'] if r['path'].startswith('packages/')}
        actual = {p.relative_to(out).as_posix(): p for p in (out / 'packages').rglob('*') if p.is_file()}
        if set(old) != set(actual) or any(hashlib.sha256(p.read_bytes()).hexdigest() != old[n]['sha256']
                                          for n, p in actual.items()):
            raise ValueError('Retained package content differs from the running release')
        for owner, prefix, paths in (
            ('platform/accounts', 'src', ['webos_accounts/guest_authority.py']),
            ('apps/linux', 'server', [f'guest_service/{name}.py' for name in (
                '__init__', 'authorization', 'coordinator', 'egress', 'frames', 'installation',
                'runtime', 'unix_transport', 'usage', 'viewer', 'worker')]),
        ):
            entry = git('.', 'ls-tree', 'HEAD', '--', owner).decode().split()
            if len(entry) != 4 or entry[:2] != ['160000', 'commit'] or entry[3] != owner:
                raise ValueError(f'Expected a pinned submodule at {owner}')
            extensions[owner] = entry[2]
            for source in paths:
                target = out / 'packages' / source
                if target.exists():
                    raise ValueError(f'Guest extension would replace {source}')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(git(owner, 'show', entry[2] + ':' + prefix + '/' + source))
        worker = git('apps/linux', 'show', extensions['apps/linux'] + ':scripts/serve-viewer-wire.py')
        (out / 'serve-viewer-wire.py').write_bytes(worker)
    server = git('.', 'show', 'HEAD:scripts/run_development.py')
    assert server == (ROOT / 'scripts/run_development.py').read_bytes()
    (out / 'run_development.py').write_bytes(server)
    owner = 'platform/accounts'
    management_pin = git('.', 'rev-parse', 'HEAD:' + owner).decode().strip()
    module = 'src/webos_accounts/management.py'
    (out / 'packages/webos_accounts/management.py').write_bytes(git(owner, 'show', management_pin + ':' + module))
    (out / 'account_management_http.py').write_bytes(git('.', 'show', 'HEAD:scripts/account_management_http.py'))
    # The reset timer imports the same operator as the detached mail lifecycle test.
    for name in ("policy", "subject_mailboxes"):
        path = "deploy/mailcraft/" + name + ".py"
        (out / "packages" / ("mailcraft_policy.py" if name == "policy" else name + ".py")).write_bytes(git(".", "show", "HEAD:" + path))
    mail_gateway = git('.', 'show', 'HEAD:deploy/mailcraft/sso_gateway.py')
    (out / 'mailcraft_sso.py').write_bytes(mail_gateway)
    for name in git('.', 'ls-tree', '-r', '--name-only', 'HEAD', '--', 'scripts/webos_weather', 'scripts/webos_compute').decode().splitlines():
        target = out / Path(name).relative_to('scripts')
        target.parent.mkdir(parents=True, exist_ok=True)
        data = git('.', 'show', 'HEAD:' + name)
        assert data == (ROOT / name).read_bytes()
        target.write_bytes(data)
    for owner, module, names in (
        ('apps/gpu-monitor', 'gpu_monitor_backend', ('__init__.py', 'fleet.py')),
        ('apps/image-studio', 'image_studio_backend', ('__init__.py', 'gateway.py', 'render.py')),
        ('apps/remote-desktop', 'remote_desktop_backend', ('__init__.py', 'relay.py', 'sessions.py')),
        ('apps/webos-chat', 'webos_chat_backend', ('__init__.py', 'chat.py', 'live.py')),
    ):
        entry = git('.', 'ls-tree', 'HEAD', '--', owner).decode().split()
        if len(entry) != 4 or entry[:2] != ['160000', 'commit'] or entry[3] != owner:
            raise ValueError(f'Expected a pinned submodule at {owner}')
        versions[owner] = entry[2]
        for name in names:
            target = out / module / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(owner, 'show', entry[2] + ':server/' + name))
    records = [{'path': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(out.rglob('*')) if p.is_file()]
    value = {'schema': 'webos-viewer-backend/1', 'parentCommit': git('.', 'rev-parse', 'HEAD').decode().strip(),
             'components': versions, 'accountsPolicy': 'Exact retained source matching the current installed Accounts backend; no delegation-policy upgrade',
             'concurrentTransfers': 8, 'sharedConcurrentTransfers': 16, 'files': records}
    value['accountManagementSource'] = management_pin
    if retained:
        value['guestNetworkComponents'] = extensions
        value['baseBackendParent'] = retained['parentCommit']
    if running:
        for name in ('guestNetworkComponents', 'baseBackendParent'):
            if name in running:
                value[name] = running[name]
    (out / 'backend-release.json').write_text(json.dumps(value, indent=2) + '\n')
    with tarfile.open(archive, 'w:gz') as tar:
        for file in sorted(out.rglob('*')):
            if file.is_file():
                tar.add(file, arcname=file.relative_to(out).as_posix(), recursive=False)
    print(json.dumps({'archiveSHA256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'bytes': archive.stat().st_size, 'files': len(records) + 1}))


if __name__ == '__main__':
    main()
