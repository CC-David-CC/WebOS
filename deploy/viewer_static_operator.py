#!/usr/bin/env python3
"""Guarded static-only update of the existing box-webhost ksu.codes test viewer.

No backend restart, account-state writes, beta changes or Git publication.
Run via the verified SSH alias with sudo; backups remain root-only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import tarfile
import urllib.request

BASE = Path('/srv/data/webos-viewer-releases')
CADDY = Path('/etc/caddy/Caddyfile')
PEERS = ['caddy.service', 'webos-rebuild-test.service', 'codi-beta-frontend.service',
         'codi-beta-gateway.service', 'codi-beta-issuer.service', 'codi-shared-ingress.service']
BASE_BYTES = 256 * 1024 * 1024
OPTIONAL_ENGINES = {app: 64 * 1024 * 1024 for app in ('gridcraft', 'deckcraft', 'photocraft', 'figcraft', 'anicraft', 'lightcraft')}
OPTIONAL_ENGINES['designcraft'] = 96 * 1024 * 1024
OPTIONAL_ENGINES['vectorcraft'] = 128 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(*args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()


def fetch(path, beta=False):
    with urllib.request.urlopen(('https://beta.ksu.codes' if beta else 'https://ksu.codes') + path, timeout=30) as response:
        return response.read(), dict(response.headers)


def peers():
    return {name: command('systemctl', 'show', name, '--property=MainPID', '--value') for name in PEERS}


def replace(data, plan, tag):
    temporary = CADDY.with_name('.Caddyfile.' + tag)
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_WRONLY, plan['mode'])
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), plan['mode']); os.fchown(stream.fileno(), plan['uid'], plan['gid'])
    os.replace(temporary, CADDY)


def continuity(plan):
    assert json.loads(fetch('/healthz')[0])['instanceId'] == plan['instanceId']
    assert sha(fetch('/.well-known/codi-issuer.json')[0]) == plan['issuerSHA256']
    assert sha(fetch('/', True)[0]) == plan['betaIndexSHA256']
    assert peers() == plan['peerPIDs']


def with_wordcraft_print_policy(block):
    """Split the existing CSP into mutually exclusive matchers; widen frame-src only.

    Refuse unfamiliar/already customized policies instead of silently overwriting
    another operator's change. Rollback restores the complete original file.
    """
    policy = re.compile(r'(?m)^(\s*)header >Content-Security-Policy "([^"\n]+)"$')
    matches = list(policy.finditer(block))
    assert len(matches) == 1 and '@wordcraft_print' not in block and '@other_viewer' not in block
    match = matches[0]
    base = match.group(2)
    assert base.count("frame-src 'self';") == 1 and "object-src 'none';" in base
    printing = base.replace("frame-src 'self';", "frame-src 'self' blob:;")
    indent = match.group(1)
    lines = [
        '@wordcraft_print path /wordcraft/index.html',
        '@other_viewer not path /wordcraft/index.html',
        'header @other_viewer >Content-Security-Policy "' + base + '"',
        'header @wordcraft_print >Content-Security-Policy "' + printing + '"',
    ]
    return block[:match.start()] + ('\n'.join(indent + line for line in lines)) + block[match.end():]


def verify_archive_inventory(tar, release_id):
    members = tar.getmembers()
    assert len(members) < 10000 and len({m.name for m in members}) == len(members)
    assert all(m.isfile() and not Path(m.name).is_absolute() and not any(p.startswith('.') or p in ('node_modules', 'target', '__pycache__') for p in Path(m.name).parts) for m in members)
    total_bytes = sum(m.size for m in members)
    assert total_bytes < BASE_BYTES + sum(OPTIONAL_ENGINES.values())
    receipt_bytes = tar.extractfile('viewer-release.json').read()
    assert sha(receipt_bytes) == release_id
    receipt = json.loads(receipt_bytes)
    assert receipt['schema'] == 'webos-existing-viewer-release/1'
    records = {row['path']: row for row in receipt['files']}
    assert set(records) | {'viewer-release.json'} == {m.name for m in members}
    for app in OPTIONAL_ENGINES:
        engine = receipt.get(app + 'Engine')
        engine_bytes = sum(m.size for m in members if m.name.startswith(app + '/'))
        if engine is None:
            assert app not in receipt['apps'] and not engine_bytes
            continue
        assert app in receipt['apps'] and 0 < engine_bytes < OPTIONAL_ENGINES[app]
        engine_receipt = records[app + '/component-build.json']
        assert engine_receipt['sha256'] == engine['receiptSHA256']
        assert engine_bytes == engine['bytes'] + engine_receipt['bytes']
        assert receipt['components']['apps/' + app] == engine['sourceCommit']
        total_bytes -= engine_bytes
    assert total_bytes < BASE_BYTES
    return members, records


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['init', 'stage', 'prepare', 'activate', 'rollback'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('--release')
    parser.add_argument('--archive-sha')
    parser.add_argument('--expected-current')
    parser.add_argument('--wordcraft-print-policy', action='store_true', help='Allow generated PDF blob frames only on the WordCraft HTML response')
    args = parser.parse_args()
    assert os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'box-webhost'
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,59}', args.tag)
    assert not BASE.is_symlink() and (BASE / '.owner').read_text() == 'webos-existing-viewer/1\n'
    stage = Path('/srv/data/.webos-' + args.tag)
    backup = Path('/var/backups/webos-' + args.tag)
    if args.mode == 'init':
        assert not stage.exists() and not stage.is_symlink()
        stage.mkdir(mode=0o700); os.chown(stage, int(os.environ['SUDO_UID']), int(os.environ['SUDO_GID']))
        print(json.dumps({'status': 'private-stage-ready', 'path': str(stage)})); return
    assert args.release and re.fullmatch('[0-9a-f]{64}', args.release)
    public = BASE / args.release / 'public'
    if args.mode == 'stage':
        assert args.archive_sha and re.fullmatch('[0-9a-f]{64}', args.archive_sha)
        archive = stage / 'viewer.tar.gz'
        assert archive.is_file() and not archive.is_symlink() and archive.stat().st_uid == int(os.environ['SUDO_UID'])
        assert sha(archive.read_bytes()) == args.archive_sha and not public.parent.exists()
        assert os.statvfs(BASE).f_bavail * os.statvfs(BASE).f_frsize > 1024**3
        with tarfile.open(archive, 'r:gz') as tar:
            members, records = verify_archive_inventory(tar, args.release)
            public.mkdir(parents=True, mode=0o755); public.parent.chmod(0o755); public.chmod(0o755)
            for member in members:
                data = tar.extractfile(member).read()
                if member.name != 'viewer-release.json':
                    assert len(data) == records[member.name]['bytes'] and sha(data) == records[member.name]['sha256']
                file = public / member.name
                file.parent.mkdir(parents=True, exist_ok=True)
                for directory in file.parents:
                    if directory == public: break
                    directory.chmod(0o755)
                file.write_bytes(data); file.chmod(0o644)
        command('sudo', '-u', 'caddy', 'test', '-r', str(public / 'index.html'))
        print(json.dumps({'status': 'verified-not-active', 'release': args.release})); return
    if args.mode == 'prepare':
        assert not backup.exists() and not backup.is_symlink()
        assert args.expected_current and re.fullmatch('[0-9a-f]{64}', args.expected_current)
        assert (public / 'viewer-release.json').is_file()
        before = CADDY.read_bytes(); text = before.decode()
        block = re.search(r'^ksu.codes \{.*?^}', text, re.M | re.S); assert block
        old = block.group(0); roots = list(re.finditer(r'(?m)^(\s*root \* )(\S+)$', old)); assert len(roots) == 1
        root = roots[0]; assert root.group(2) == str(BASE / args.expected_current / 'public')
        new = old[:root.start(2)] + str(public) + old[root.end(2):]
        if args.wordcraft_print_policy:
            new = with_wordcraft_print_policy(new)
        candidate = (text[:block.start()] + new + text[block.end():]).encode()
        assert candidate.decode().replace(new, old, 1) == text
        backup.mkdir(mode=0o700)
        for name, data in [('before', before), ('candidate', candidate)]:
            config = backup / ('Caddyfile.' + name); config.write_bytes(data)
            run = subprocess.run(['caddy', 'validate', '--config', str(config), '--adapter', 'caddyfile'], capture_output=True)
            (backup / ('validate-' + name + '.log')).write_bytes(run.stdout + run.stderr); assert run.returncode == 0
        info = CADDY.stat()
        plan = {'release': args.release, 'previousRelease': args.expected_current, 'beforeSHA256': sha(before), 'candidateSHA256': sha(candidate),
                'wordcraftPrintPolicy': args.wordcraft_print_policy, 'desktopCSP': fetch('/')[1].get('Content-Security-Policy'),
                'uid': info.st_uid, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode), 'instanceId': json.loads(fetch('/healthz')[0])['instanceId'],
                'issuerSHA256': sha(fetch('/.well-known/codi-issuer.json')[0]), 'betaIndexSHA256': sha(fetch('/', True)[0]), 'peerPIDs': peers()}
        (backup / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
        print(json.dumps({'status': 'validated-not-active', 'rollbackDirectory': str(backup)})); return
    plan = json.loads((backup / 'plan.json').read_text()); assert plan['release'] == args.release
    assert sha(CADDY.read_bytes()) in (plan['beforeSHA256'], plan['candidateSHA256']), 'Unknown concurrent configuration edit'
    if args.mode == 'rollback':
        replace((backup / 'Caddyfile.before').read_bytes(), plan, args.tag); command('systemctl', 'reload', 'caddy.service'); continuity(plan)
        print(json.dumps({'status': 'rolled-back', 'release': args.release})); return
    assert sha(CADDY.read_bytes()) == plan['beforeSHA256']; continuity(plan)
    try:
        replace((backup / 'Caddyfile.candidate').read_bytes(), plan, args.tag); command('systemctl', 'reload', 'caddy.service')
        continuity(plan)
        receipt = json.loads((public / 'viewer-release.json').read_text()); files = {row['path']: row for row in receipt['files']}
        apps = json.loads((public / 'assets/desktop/apps.json').read_text())
        app = next(row for row in apps['apps'] if row['id'] == 'files')
        for name in ['index.html', 'style.css', 'assets/desktop/apps.json', app['path']]:
            data, headers = fetch('/' if name == 'index.html' else '/' + name)
            assert sha(data) == files[name]['sha256']
            assert headers.get('Cross-Origin-Opener-Policy') == 'same-origin' and headers.get('Cross-Origin-Embedder-Policy') == 'require-corp'
        if plan.get('wordcraftPrintPolicy'):
            assert fetch('/')[1].get('Content-Security-Policy') == plan['desktopCSP']
            assert fetch('/wordcraft/index.html')[1].get('Content-Security-Policy') == plan['desktopCSP'].replace("frame-src 'self';", "frame-src 'self' blob:;")
    except BaseException:
        assert sha(CADDY.read_bytes()) in (plan['beforeSHA256'], plan['candidateSHA256'])
        replace((backup / 'Caddyfile.before').read_bytes(), plan, args.tag); command('systemctl', 'reload', 'caddy.service'); raise
    result = {'status': 'active-awaiting-browser-check', 'release': args.release, 'backendAndBetaPIDsUnchanged': True, 'sameInstanceAndIssuer': True}
    (backup / 'activation.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))


if __name__ == '__main__':
    main()
