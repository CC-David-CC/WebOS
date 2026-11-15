"""Cardboard Studio profile for box-webhost's existing managed-site controller.

Installed as ops/cardboard_hosting.py; other sites retain their original paths.
"""
import hashlib
import http.client
import json
import os
from pathlib import Path
import signal
import socket
import stat
import subprocess
import tempfile
import time
import shutil

DOMAIN = 'cardboard.ksu.codes'
DATA = Path('/var/lib/cardboard-studio')
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; object-src 'none'; frame-ancestors 'none'"


def check(s):
    if s['domain'] != DOMAIN or s.get('cardboard_studio') is not True:
        raise ValueError('Cardboard hosting profile is restricted to its exact hostname')


def unit(s):
    check(s)
    from common import unit as standard_unit
    original = dict(s)
    original.pop('cardboard_studio')
    return standard_unit(original).replace(
        'Environment=PYTHONDONTWRITEBYTECODE=1\n',
        'Environment=PYTHONDONTWRITEBYTECODE=1\n'
        f'Environment=CARDBOARD_DATA_DIR={DATA}\n'
        'StateDirectory=cardboard-studio\nStateDirectoryMode=0700\n'
        f'ReadWritePaths={DATA}\n')


def caddy_lines(s):
    check(s)
    return ['\theader >Content-Security-Policy "' + CSP + '"']


def request(s, path='/healthz', port=None):
    check(s)
    route = '/api/health' if path == '/healthz' else path
    connection = http.client.HTTPConnection('127.0.0.1', port or s['port'], timeout=8)
    try:
        connection.request('GET', route, headers={'Host': s['domain']})
        response = connection.getresponse()
        body = response.read()
        assert response.status == 200, (route, response.status)
        if route == '/api/health':
            assert json.loads(body) == {'status': 'ok'}
        else:
            assert b'<title>Cardboard Studio</title>' in body
    finally:
        connection.close()


def deploy(s, w):
    """Immutable release, isolated candidate database, existing operator rollback."""
    check(s)
    a, owner = w.account(s), w.owner()
    source = w.ROOT / 'sites' / s['domain']
    lock = source / 'requirements.lock.txt'
    if not lock.is_file():
        raise RuntimeError('A reviewed Linux runtime dependency lock is required')
    files = sorted(p for p in (source / 'app').rglob('*') if p.is_file())
    if any(p.is_symlink() for p in (source / 'app').rglob('*')):
        raise RuntimeError('Application source must not contain symlinks')
    digest = hashlib.sha256()
    for p in files + [lock]:
        digest.update(p.relative_to(source).as_posix().encode())
        digest.update(p.read_bytes())
    rid = w.stamp() + '-' + digest.hexdigest()[:8]
    dest = w.BASE / s['domain'] / 'releases' / rid
    dest.mkdir(mode=0o750)
    os.chown(dest, owner.pw_uid, a.pw_gid)
    shutil.copytree(source / 'app', dest / 'app')
    shutil.copy2(lock, dest / 'requirements.lock.txt')
    for p in [dest] + list(dest.rglob('*')):
        os.chown(p, owner.pw_uid, a.pw_gid)
    prefix = ['runuser', '-u', owner.pw_name, '--']
    w.run(prefix + ['python3', '-m', 'venv', str(dest / '.venv')])
    py = str(dest / '.venv/bin/python')
    w.run(prefix + [py, '-m', 'pip', 'install', '--disable-pip-version-check', '--only-binary=:all:', '-r', str(dest / 'requirements.lock.txt')])
    w.run(prefix + [py, '-m', 'pip', 'check'])
    for p in [dest] + list(dest.rglob('*')):
        if not p.is_symlink():
            executable = p.stat().st_mode & stat.S_IXUSR
            os.chown(p, 0, a.pw_gid)
            os.chmod(p, 0o750 if p.is_dir() or executable else 0o640)
    # The candidate cannot create or modify the real project's SQLite database.
    with tempfile.TemporaryDirectory(prefix='candidate-', dir=w.BASE / s['domain']) as temporary:
        os.chown(temporary, a.pw_uid, a.pw_gid)
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        log_path = w.STATE / 'cardboard-candidate.log'
        w.STATE.mkdir(exist_ok=True, mode=0o700)
        with log_path.open('w') as log:
            process = subprocess.Popen(['runuser', '-u', s['user'], '--', 'env',
                'PYTHONDONTWRITEBYTECODE=1', 'CARDBOARD_DATA_DIR=' + temporary,
                py, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
                '--port', str(port), '--no-access-log'], cwd=dest,
                stdout=log, stderr=log, start_new_session=True)
            try:
                for _ in range(60):
                    try:
                        request(s, port=port)
                        break
                    except (OSError, AssertionError):
                        if process.poll() is not None:
                            raise RuntimeError('Candidate stopped; see ' + str(log_path))
                        time.sleep(.25)
                else:
                    raise RuntimeError('Cardboard candidate failed its private health check')
                request(s, '/', port=port)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=20)
    if not (DATA / 'studio.sqlite3').is_file():
        raise RuntimeError('Preserved production database must be installed before activation')
    prior = w.release_state(s)
    w.point(s, rid)
    try:
        w.install_unit(s)
        w.run(['systemctl', 'restart', s['service']])
        w.healthy(s)
        w.run(['systemctl', 'enable', s['service']], stdout=subprocess.DEVNULL)
    except Exception:
        if prior['current']:
            w.point(s, prior['current'])
            w.run(['systemctl', 'restart', s['service']])
            w.healthy(s)
        else:
            w.run(['systemctl', 'stop', s['service']])
        raise
    w.record_release(s, rid, prior['current'])
    print('Deployed ' + s['domain'] + ': ' + rid, flush=True)


def smoke(s, fetch):
    check(s)
    d = s['domain']
    status, _, headers, _ = fetch(d, '/catalog?check=1', secure=False)
    assert status in (301, 302, 307, 308)
    assert headers['location'] == 'https://' + d + '/catalog?check=1'
    redirect_status = status
    status, body, headers, certificate = fetch(d)
    assert status == 200 and b'<title>Cardboard Studio</title>' in body
    assert "script-src 'self'" in headers['content-security-policy']
    assert "form-action 'self'" in headers['content-security-policy']
    assert headers['x-content-type-options'] == 'nosniff'
    for route, marker in [('/catalog', b'Design catalog'), ('/static/main.js', b'function'),
                          ('/static/style.css', b'body')]:
        code, body, _, _ = fetch(d, route)
        assert code == 200 and marker in body, route
    code, body, headers, _ = fetch(d, '/api/health')
    assert code == 200 and json.loads(body) == {'status': 'ok'}
    assert headers['cache-control'] == 'no-store'
    code, body, _, _ = fetch(d, '/api/catalog')
    assert code == 200 and len(json.loads(body)['starters']) == 3
    code, _, _, _ = fetch(d, '/api/projects')
    assert code == 401
    for route in ['/.env', '/.git/config', '/app/main.py', '/project-data/studio.sqlite3',
                  '/requirements.lock.txt', '/.venv/pyvenv.cfg', '/static/%2e%2e/%2e%2e/etc/passwd']:
        code, body, _, _ = fetch(d, route)
        assert code in (403, 404) and b'root:x:' not in body, route
    return {'result': 'PASS', 'http_redirect': redirect_status, 'https_get': 200,
            'certificate': certificate, 'checks': ['verified TLS', 'path-preserving redirect',
            'home/catalog/static assets', 'application CSP', 'health', 'public catalog',
            'owner session required', 'private source and data denied']}
