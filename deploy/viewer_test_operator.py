#!/usr/bin/env python3
"""Guarded operator for the explicitly authorized ksu.codes test update only.

Run through verified box-webhost SSH as root. init/stage/prepare do not activate.
Raw configuration backups remain root-only, outside all web roots.
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
import time
import urllib.request

STAGE = Path('/srv/data/.webos-viewer-stage-20261116-01')
BASE = Path('/srv/data/webos-viewer-releases')
BACKUP = Path('/var/backups/webos-viewer-20261116-02')
CADDY = Path('/etc/caddy/Caddyfile')
DROPIN = Path('/etc/systemd/system/webos-rebuild-test.service.d/60-existing-viewer.conf')
SERVICE = 'webos-rebuild-test.service'
PEERS = ['caddy.service', 'codi-beta-frontend.service', 'codi-beta-gateway.service', 'codi-beta-issuer.service', 'codi-shared-ingress.service']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def command(*args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT, text=True).strip()


def fetch(path, beta=False):
    with urllib.request.urlopen(('https://beta.ksu.codes' if beta else 'https://ksu.codes') + path, timeout=30) as response:
        return response.read(), dict(response.headers)


def backend_fetch(port, path):
    request = urllib.request.Request('http://127.0.0.1:' + str(port) + path, headers={'Host': 'ksu.codes', 'Origin': 'https://ksu.codes'})
    with urllib.request.urlopen(request, timeout=3) as response:
        return response.read()


def backend_ready(port, instance):
    for attempt in range(30):
        try:
            health = json.loads(backend_fetch(port, '/healthz'))
            assert health['instanceId'] == instance
            return
        except Exception:
            if attempt == 29:
                raise
            time.sleep(0.5)


def peers():
    return {name: command('systemctl', 'show', name, '--property=MainPID', '--value') for name in PEERS}


def block(text, host):
    found = re.search(r'^' + re.escape(host) + r' \{\s*$', text, re.M)
    assert found, 'Expected unique site block'
    end = re.search(r'^}\s*$', text[found.end():], re.M)
    assert end
    return found.start(), found.end() + end.end()


def replace_config(data, plan):
    temporary = CADDY.with_name('.Caddyfile.webos-viewer-20261116')
    fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, plan['mode'])
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.fchmod(stream.fileno(), plan['mode']); os.fchown(stream.fileno(), plan['uid'], plan['gid'])
    os.replace(temporary, CADDY)


def unpack(archive, destination, manifest_name, public, uid, gid):
    assert not destination.exists() and not destination.is_symlink()
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        assert len(members) < 10000 and len({m.name for m in members}) == len(members)
        assert all(m.isfile() and not Path(m.name).is_absolute() and not any(p.startswith('.') or p in ('node_modules', 'target', '__pycache__') for p in Path(m.name).parts) for m in members)
        assert sum(m.size for m in members) < 200 * 1024 * 1024
        manifest_bytes = tar.extractfile(manifest_name).read()
        manifest = json.loads(manifest_bytes)
        records = {row['path']: row for row in manifest['files']}
        assert set(records) | {manifest_name} == {m.name for m in members}
        destination.mkdir(mode=0o755 if public else 0o750)
        destination.chmod(0o755 if public else 0o750)
        if not public:
            os.chown(destination, uid, gid)
        for member in members:
            data = tar.extractfile(member).read()
            if member.name != manifest_name:
                assert len(data) == records[member.name]['bytes'] and digest(data) == records[member.name]['sha256']
            file = destination / member.name
            current = destination
            for part in Path(member.name).parts[:-1]:
                current = current / part
                if not current.exists():
                    current.mkdir(mode=0o755 if public else 0o750)
                    current.chmod(0o755 if public else 0o750)
                    if not public:
                        os.chown(current, uid, gid)
            file.write_bytes(data); file.chmod(0o644 if public else 0o640)
            if not public:
                os.chown(file, uid, gid)
        return manifest, digest(manifest_bytes)


def rollback(plan):
    current = digest(CADDY.read_bytes())
    assert current in (plan['beforeSHA256'], plan['candidateSHA256'], plan['rollbackSHA256']), 'Concurrent Caddy edit; refusing overwrite'
    if DROPIN.exists():
        assert digest(DROPIN.read_bytes()) in (plan['dropinSHA256'], plan['rollbackDropinSHA256']), 'Unexpected service override; refusing replacement'
        DROPIN.write_bytes((BACKUP / 'service.dropin.rollback').read_bytes()); DROPIN.chmod(0o644)
        command('systemctl', 'daemon-reload')
        command('systemctl', 'restart', SERVICE)
        backend_ready(38142, plan['instanceId'])
    replace_config((BACKUP / 'Caddyfile.rollback').read_bytes(), plan)
    command('systemctl', 'reload', 'caddy.service')


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['init', 'stage', 'prepare', 'activate', 'rollback'])
    parser.add_argument('--release')
    parser.add_argument('--frontend-sha')
    parser.add_argument('--backend-sha')
    args = parser.parse_args()
    assert os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'box-webhost'
    uid, gid = int(os.environ['SUDO_UID']), int(os.environ['SUDO_GID'])
    if args.mode == 'init':
        assert not STAGE.exists() and not STAGE.is_symlink()
        STAGE.mkdir(mode=0o700); os.chown(STAGE, uid, gid)
        if BASE.exists():
            assert not BASE.is_symlink() and (BASE / '.owner').read_text() == 'webos-existing-viewer/1\n'
        else:
            BASE.mkdir(mode=0o755); BASE.chmod(0o755); (BASE / '.owner').write_text('webos-existing-viewer/1\n')
        print(json.dumps({'status': 'private-staging-ready', 'dataDiskFreeBytes': os.statvfs(BASE).f_bavail * os.statvfs(BASE).f_frsize})); return
    assert args.release and re.fullmatch('[0-9a-f]{64}', args.release)
    release = BASE / args.release
    if args.mode == 'stage':
        assert not release.exists()
        for name, expected in [('viewer.tar.gz', args.frontend_sha), ('backend.tar.gz', args.backend_sha)]:
            file = STAGE / name
            assert file.is_file() and not file.is_symlink() and file.stat().st_uid == uid
            assert digest(file.read_bytes()) == expected
        assert os.statvfs(BASE).f_bavail * os.statvfs(BASE).f_frsize > 1024**3
        release.mkdir(mode=0o755); release.chmod(0o755)
        frontend, identity = unpack(STAGE / 'viewer.tar.gz', release / 'public', 'viewer-release.json', True, uid, gid)
        backend, _ = unpack(STAGE / 'backend.tar.gz', release / 'backend', 'backend-release.json', False, uid, gid)
        assert identity == args.release and frontend['parentCommit'] == backend['parentCommit']
        assert backend['concurrentTransfers'] == 8 and backend['sharedConcurrentTransfers'] == 16
        command('sudo', '-u', 'caddy', 'test', '-r', str(release / 'public/index.html'))
        print(json.dumps({'status': 'staged-not-active', 'release': args.release, 'publicRoot': str(release / 'public')})); return
    if args.mode == 'prepare':
        assert not BACKUP.exists() and not DROPIN.exists() and not DROPIN.is_symlink()
        assert (release / 'public/viewer-release.json').is_file() and (release / 'backend/backend-release.json').is_file()
        pid = int(command('systemctl', 'show', SERVICE, '--property=MainPID', '--value'))
        argv = Path('/proc/' + str(pid) + '/cmdline').read_bytes().decode().strip('\0').split('\0')
        assert Path('/proc/' + str(pid)).stat().st_uid == uid
        private = argv[argv.index('--private-root') + 1]
        origin = argv[argv.index('--origin') + 1]
        assert origin == 'https://ksu.codes' and argv[argv.index('--port') + 1] == '38140'
        assert Path(private).is_dir() and json.loads((Path(private) / 'development.json').read_text())['origin'] == origin
        # The previous listener did not set SO_REUSEADDR. Use fresh loopback
        # ports for activation and rollback instead of racing its TIME_WAIT.
        for port in (38141, 38142):
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', port))
        raw = CADDY.read_bytes(); text = raw.decode(); start, end = block(text, 'ksu.codes'); old = text[start:end]
        roots = list(re.finditer(r'(?m)^(\s*root \* )(\S+)$', old)); assert len(roots) == 1
        root = roots[0]; new = old[:root.start(2)] + str(release / 'public') + old[root.end(2):]
        assert old.count('reverse_proxy 127.0.0.1:38140') == 1
        new = new.replace('reverse_proxy 127.0.0.1:38140', 'reverse_proxy 127.0.0.1:38141')
        candidate = (text[:start] + new + text[end:]).encode()
        rollback_block = old.replace('reverse_proxy 127.0.0.1:38140', 'reverse_proxy 127.0.0.1:38142')
        rollback_config = (text[:start] + rollback_block + text[end:]).encode()
        assert candidate.decode().replace(new, old, 1) == text
        BACKUP.mkdir(mode=0o700)
        (BACKUP / 'Caddyfile.before').write_bytes(raw); (BACKUP / 'Caddyfile.candidate').write_bytes(candidate)
        (BACKUP / 'Caddyfile.rollback').write_bytes(rollback_config)
        for name in ['before', 'candidate', 'rollback']:
            run = subprocess.run(['caddy', 'validate', '--config', str(BACKUP / ('Caddyfile.' + name)), '--adapter', 'caddyfile'], capture_output=True)
            (BACKUP / ('validate-' + name + '.log')).write_bytes(run.stdout + run.stderr); assert run.returncode == 0
        script = release / 'backend/run_development.py'
        dropin = '[Service]\nExecStart=\nExecStart=' + argv[0] + ' ' + str(script) + ' --public-root ' + str(release / 'public') + ' --private-root ' + private + ' --port 38141 --origin https://ksu.codes --account-transfers 8 --shared-transfers 16\nWorkingDirectory=' + str(release / 'backend') + '\nEnvironment=PYTHONPATH=' + str(release / 'backend/packages') + '\n'
        (BACKUP / 'service.dropin.candidate').write_text(dropin)
        old_args = argv[:]; old_args[old_args.index('--port') + 1] = '38142'
        assert all(re.fullmatch(r'[A-Za-z0-9_./:-]+', arg) for arg in old_args)
        rollback_dropin = '[Service]\nExecStart=\nExecStart=' + ' '.join(old_args) + '\nWorkingDirectory=' + str(Path('/proc/' + str(pid) + '/cwd').resolve()) + '\nEnvironment=PYTHONPATH=\n'
        (BACKUP / 'service.dropin.rollback').write_text(rollback_dropin)
        health = json.loads(fetch('/healthz')[0]); issuer = fetch('/.well-known/codi-issuer.json')[0]; beta = fetch('/', beta=True)[0]
        info = CADDY.stat()
        plan = {'release': args.release, 'publicRoot': str(release / 'public'), 'privateRoot': private, 'backendPIDBefore': pid,
                'beforeSHA256': digest(raw), 'candidateSHA256': digest(candidate), 'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
                'dropinSHA256': digest(dropin.encode()), 'rollbackDropinSHA256': digest(rollback_dropin.encode()), 'rollbackSHA256': digest(rollback_config), 'issuerSHA256': digest(issuer), 'instanceId': health['instanceId'], 'betaIndexSHA256': digest(beta), 'peerPIDs': peers()}
        (BACKUP / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
        print(json.dumps({'status': 'validated-not-active', 'release': args.release, 'rollbackDirectory': str(BACKUP), 'onlyKsuRouteChanges': True})); return
    plan = json.loads((BACKUP / 'plan.json').read_text()); assert plan['release'] == args.release
    if args.mode == 'rollback':
        rollback(plan); print(json.dumps({'status': 'rolled-back', 'release': args.release})); return
    assert digest(CADDY.read_bytes()) == plan['beforeSHA256'] and not DROPIN.exists()
    # Read only an aggregate counter as the existing service user. No account
    # identifiers or file contents are inspected or copied.
    query = "import sqlite3,time,sys;from pathlib import Path;p=Path(sys.argv[1]);db=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True);n=db.execute('SELECT count(*) FROM gateway_active_uses WHERE expires>?',(int(time.time()),)).fetchone()[0];print(n)"
    active = command('sudo', '-u', '#' + str(uid), 'python3', '-c', query, str(Path(plan['privateRoot']) / 'storage-state/permissions.sqlite3'))
    assert active == '0', 'Active account transfers; defer restart'
    try:
        DROPIN.parent.mkdir(mode=0o755, exist_ok=True)
        DROPIN.write_bytes((BACKUP / 'service.dropin.candidate').read_bytes()); DROPIN.chmod(0o644)
        command('systemctl', 'daemon-reload'); command('systemctl', 'restart', SERVICE)
        backend_ready(38141, plan['instanceId'])
        assert digest(backend_fetch(38141, '/.well-known/codi-issuer.json')) == plan['issuerSHA256']
        config = json.loads(backend_fetch(38141, '/config.json')); assert config['gateway']['concurrentTransfers'] == 8 and config['gateway']['sharedConcurrentTransfers'] == 16
        assert config['gateway']['fileBytes'] == 128 * 1024 * 1024
        replace_config((BACKUP / 'Caddyfile.candidate').read_bytes(), plan); command('systemctl', 'reload', 'caddy.service')
        assert json.loads(fetch('/healthz')[0])['instanceId'] == plan['instanceId']
        receipt = json.loads((release / 'public/viewer-release.json').read_text()); files = {r['path']: r for r in receipt['files']}
        for name in ['index.html', 'style.css', 'bootstrap.js', 'app.js', 'assets/desktop/account-services.mjs']:
            data, headers = fetch('/' if name == 'index.html' else '/' + name)
            assert digest(data) == files[name]['sha256'] and headers.get('Cross-Origin-Opener-Policy') == 'same-origin' and headers.get('Cross-Origin-Embedder-Policy') == 'require-corp'
        assert digest(fetch('/', beta=True)[0]) == plan['betaIndexSHA256'] and peers() == plan['peerPIDs']
        result = {'status': 'active-awaiting-hosted-browser-check', 'release': args.release, 'sameAccountState': True, 'sameIssuer': True, 'sameInstance': True, 'betaUnchanged': True, 'limits': {'account': 8, 'shared': 16}}
    except BaseException as error:
        rollback(plan)
        (BACKUP / 'activation-failure.json').write_text(json.dumps({'error': type(error).__name__, 'rolledBack': True}) + '\n')
        raise
    (BACKUP / 'activation.json').write_text(json.dumps(result, indent=2) + '\n'); print(json.dumps(result))


if __name__ == '__main__':
    main()
