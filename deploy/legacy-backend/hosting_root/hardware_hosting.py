"""Signal Studio profile for box-webhost's existing managed-site controller.

Installed as ops/hardware_hosting.py; other sites retain their original paths.
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

DOMAIN = 'hardware.ksu.codes'
DATA = Path('/var/lib/hardware-studio')
CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'; object-src 'none'; frame-ancestors 'none'"


def check(s):
    if s['domain'] != DOMAIN or s.get('hardware_studio') is not True:
        raise ValueError('Signal hosting profile is restricted to its exact hostname')


def unit(s):
    check(s)
    from common import unit as standard_unit
    original = dict(s)
    original.pop('hardware_studio')
    return standard_unit(original).replace(
        'Environment=PYTHONDONTWRITEBYTECODE=1\n',
        'Environment=PYTHONDONTWRITEBYTECODE=1\n'
        f'Environment=HC_DATA_DIR={DATA}\n'
        'MemoryMax=512M\nTasksMax=64\nLogRateLimitIntervalSec=30s\nLogRateLimitBurst=100\n'
        'StateDirectory=hardware-studio\nStateDirectoryMode=0700\n'
        f'ReadWritePaths={DATA}\n')


def caddy_lines(s):
    check(s)
    return ['\theader >Content-Security-Policy \"' + CSP + '\"',
            '\tbasic_auth {', '\t\timport /etc/caddy/private/hardware-users', '\t}',
            '\t@private_api path /api/ingest/* /api/login /docs /redoc /openapi.json',
            '\trespond @private_api 404']


def request(s, path='/healthz', port=None):
    check(s)
    route = '/api/healthz' if path == '/healthz' else path
    connection = http.client.HTTPConnection('127.0.0.1', port or s['port'], timeout=8)
    try:
        connection.request('GET', route, headers={'Host': s['domain']})
        response = connection.getresponse()
        body = response.read()
        assert response.status == 200, (route, response.status)
        if route == '/api/healthz':
            assert json.loads(body) == {'status': 'ok', 'simulated': True}
        else:
            assert b'<title>Signal Studio</title>' in body
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
    files = sorted(p for folder in [source/'app', source/'src/hardware_chat'] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    if any(p.is_symlink() for folder in [source/'app', source/'src/hardware_chat'] for p in folder.rglob('*')):
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
    shutil.copytree(source/'src/hardware_chat', dest/'hardware_chat', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
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
        log_path = w.STATE / 'hardware-candidate.log'
        w.STATE.mkdir(exist_ok=True, mode=0o700)
        with log_path.open('w') as log:
            process = subprocess.Popen(['runuser', '-u', s['user'], '--', 'env',
                'PYTHONDONTWRITEBYTECODE=1', 'HC_DATA_DIR=' + temporary,
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
                    raise RuntimeError('Signal candidate failed its private health check')
                request(s, '/', port=port)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=20)
    DATA.mkdir(exist_ok=True, mode=0o700)
    os.chown(DATA, a.pw_uid, a.pw_gid)
    w.run(['runuser','-u',s['user'],'--','env','HC_DATA_DIR='+str(DATA),
           'HC_SCENARIO='+str(dest/'hardware_chat/fixtures/demo.json'),py,'-m','hardware_chat','init'],cwd=dest)
    prior = w.release_state(s)
    resume_simulator = subprocess.run(['systemctl','is-active','--quiet','hardware-simulator.service']).returncode == 0
    if resume_simulator:
        w.run(['systemctl','stop','hardware-simulator.service'])
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
    finally:
        if resume_simulator:
            w.run(['systemctl','start','hardware-simulator.service'])
    w.record_release(s, rid, prior['current'])
    print('Deployed ' + s['domain'] + ': ' + rid, flush=True)


def smoke(s, fetch):
    """Unauthenticated public health is the whole-site password challenge."""
    check(s)
    domain=s['domain']
    status,_,headers,_=fetch(domain,'/studio.js?check=1',secure=False)
    assert status in (301,302,307,308) and headers['location']=='https://'+domain+'/studio.js?check=1'
    status,body,headers,certificate=fetch(domain)
    assert status==401 and headers.get('www-authenticate','').startswith('Basic ')
    assert "default-src 'none'" in headers['content-security-policy']
    for route in ['/studio.js','/studio.css','/api/healthz','/api/v1/network','/docs','/.git/config']:
        code,_,head,_=fetch(domain,route)
        assert code==401 and head.get('www-authenticate','').startswith('Basic '),route
    return {'result':'PASS','https_password_gate':401,'certificate':certificate,
            'checks':['verified TLS','HTTP redirect','whole-site Basic challenge'],
            'authenticated_acceptance':'See separate live HTTPS/Q4 browser receipt.'}
