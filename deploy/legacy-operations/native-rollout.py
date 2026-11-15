#!/usr/bin/env python3
"""Recoverable code rollout with a guest-preserving coherent checkpoint.

Run with an authenticated, root-owned profile10/11/12/13/14/15/16/17/18 operator. The existing operator
owns code switch/rollback and its maintenance journal. This outer journal owns
checkpoint stop/resume, including process death before the inner switch begins.
No data restore, authority provisioning, renewal, policy or hosting change.
"""
import argparse
import hashlib
import http.client
from http.cookies import SimpleCookie
import importlib.util
import json
import os
from pathlib import Path
import secrets
import sqlite3
import stat
import subprocess
import sys
import time
from urllib.parse import quote, urlsplit

JOURNAL = 'native-rollout.json'
ROLES = ['issuer', 'steward', 'guest']

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def cookie(config):
    connection = http.client.HTTPConnection('127.0.0.1', config['ports']['guest'], timeout=10)
    try:
        connection.request('GET', '/', headers={'Host': urlsplit(config['origin']).netloc})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError('Guest index unavailable; preserve the existing connection credential')
        values = SimpleCookie()
        for key, value in response.getheaders():
            if key.lower() == 'set-cookie':
                values.load(value)
        if 'codi_guest_relay' not in values:
            raise ValueError('Guest index did not supply its connection credential')
        raw = values['codi_guest_relay'].value.encode('ascii')
        if not __import__('re').fullmatch(rb'[A-Za-z0-9_-]{43,128}', raw):
            raise ValueError('Guest connection credential has an invalid format')
        return raw
    finally:
        connection.close()

def accounts(config):
    file = Path(config['stateRoot']) / 'issuer/state/accounts.sqlite3'
    with sqlite3.connect('file:' + quote(str(file), safe='/') + '?mode=ro', uri=True, timeout=5) as db:
        rows = db.execute('SELECT username,subject,password_hash,created FROM accounts ORDER BY username').fetchall()
    return {digest(json.dumps(row, separators=(',', ':'), ensure_ascii=True).encode()) for row in rows}

def baseline(config):
    state = Path(config['stateRoot'])
    files = ['issuer/state/issuer.pem', 'operator/root/root.pem',
             'operator/root/authority.sqlite3', 'steward/service.pem']
    return {'files': {name: digest((state / name).read_bytes()) for name in files},
            'accounts': sorted(accounts(config))}

def preserved(config, saved):
    state = Path(config['stateRoot'])
    if any(digest((state / name).read_bytes()) != expected for name, expected in saved['files'].items()):
        raise ValueError('Authority/account signing state changed; preserve the rollout journal for review')
    current = accounts(config)
    if not set(saved['accounts']) <= current:
        raise ValueError('An existing account changed; preserve state and the rollout journal for review')
    return len(current)

def write(op, path, value):
    op.atomic(path, json.dumps(value, indent=2).encode() + b'\n')

def guest_pid(op, config):
    return int(op.systemctl('show', op.unit(config, 'guest'), '-p', 'MainPID', '--value').strip())

def finish(op, config_path, journal, status, detail=None):
    from origin_service import deployment, maintenance
    current = op.load(config_path)
    deployment.validate_pair(op, current, journal['before'], journal['after'])
    deployment.start_checked(op, current, journal['activeRoles'], config_path)
    count = preserved(current, journal['baseline'])
    held_cookie = digest(cookie(current)) == journal['cookieSHA256']
    if current == journal['after'] and not held_cookie:
        raise ValueError('Upgraded guest credential changed; preserve the journal for review')
    report = {'status': status, 'id': journal['id'], 'release': current['release'],
              'manifestSHA256': current['manifestSHA256'], 'activeRoles': journal['activeRoles'],
              'keysAuthorityAndExistingAccountsPreserved': True, 'existingAccounts': len(journal['baseline']['accounts']),
              'currentAccounts': count, 'guestCookiePreserved': held_cookie,
              'checkpointGuestPidPreserved': journal.get('checkpointGuestPidPreserved', False),
              'checkpoint': journal.get('checkpoint'), 'dataRestored': False,
              'hostingOrTurnPolicyChanged': False}
    if detail:
        report['detail'] = detail
    write(op, config_path.parent / 'native-rollout-last.json', report)
    (config_path.parent / JOURNAL).unlink()
    maintenance.sync_directory(config_path.parent)
    return report

def recover(op, config_path):
    from origin_service import deployment, maintenance
    path = config_path.parent / JOURNAL
    journal = json.loads(op.read_owned(path, 0, 0o600, 4194304))
    required = {'version', 'id', 'phase', 'created', 'before', 'after', 'activeRoles', 'baseline', 'cookieSHA256', 'guestPid', 'checkpointDirectory'}
    optional = {'checkpoint', 'checkpointGuestPidPreserved', 'codeResult'}
    if not required <= set(journal) <= required | optional or journal['version'] != 'codi-native-rollout/1' or journal['activeRoles'] != ROLES:
        raise ValueError('Unrecognized rollout journal; retain it for review')
    current = op.load(config_path, verify_installation=False)
    deployment.validate_pair(op, current, journal['before'], journal['after'])
    if (config_path.parent / 'maintenance.json').exists():
        inner = json.loads(op.read_owned(config_path.parent / 'maintenance.json', 0, 0o600))
        if inner.get('version') != 'codi-code-transition/1' or inner.get('before') != journal['before'] or inner.get('after') != journal['after']:
            raise ValueError('A different maintenance operation is pending; retain both journals')
        deployment.recover(op, current, config_path)
        current = op.load(config_path)
    maintenance.require_clean(op, config_path)
    # Early interruption changed only availability. Starting an already-running
    # guest is a no-op, preserving its exact process and socket credential.
    status = 'committed-rollout-recovered' if current == journal['after'] else 'interrupted-rollout-resumed-before'
    return finish(op, config_path, journal, status)

def upgrade(op, config_path, release, python, backup_parent, phase=lambda name: None):
    from origin_service import deployment, guest_cookie, maintenance
    current = op.load(config_path)
    maintenance.guard(op, current, config_path)
    journal_path = config_path.parent / JOURNAL
    if journal_path.exists():
        raise ValueError('A native rollout is pending; recover it before starting another')
    if deployment.active(op, current) != ROLES:
        raise ValueError('Review role availability before the three-role rollout')
    profile = json.loads((Path(release) / 'connected-release.json').read_text())['version']
    if profile not in ('codi-connected-development/10','codi-connected-development/11','codi-connected-development/12','codi-connected-development/13','codi-connected-development/14','codi-connected-development/15','codi-connected-development/16','codi-connected-development/17','codi-connected-development/18'):
        raise ValueError('This rollout requires a persistent-cookie profile10/11/12/13/14/15/16/17/18 candidate')
    held = cookie(current)
    source = guest_cookie.source(current)
    op.path(source.parent.parent)
    op.directory(source.parent, 0o700)
    if not source.exists():
        op.atomic(source, held)
    if guest_cookie.validate_source(op, current) != held:
        raise ValueError('Protected cookie differs from the live guest; refusing rotation')
    after = deployment.target(op, current, release, python)
    deployment.syntax(op, after, config_path)
    if after == current:
        return {'status': 'already-current', 'release': current['release'], 'guestCookiePreserved': True}
    parent = op.path(backup_parent)
    if __import__('stat').S_IMODE(parent.stat().st_mode) != 0o700:
        raise ValueError('Checkpoint parent must be root-private')
    id = secrets.token_hex(16)
    journal = {'version': 'codi-native-rollout/1', 'id': id, 'phase': 'prepared', 'created': int(time.time()),
               'before': current, 'after': after, 'activeRoles': ROLES, 'baseline': baseline(current),
               'cookieSHA256': digest(held), 'guestPid': guest_pid(op, current),
               'checkpointDirectory': str(parent / ('native-' + id))}
    write(op, journal_path, journal)
    phase('prepared')
    try:
        op.stop(current, ['steward', 'issuer'])
        phase('roles-stopped')
        journal['phase'] = 'checkpointing';write(op, journal_path, journal)
        saved = maintenance.backup(op, current, config_path, Path(journal['checkpointDirectory']))
        if not saved['guestRelayKeptRunning'] or guest_pid(op, current) != journal['guestPid'] or digest(cookie(current)) != journal['cookieSHA256']:
            raise ValueError('Guest continuity was lost during checkpointing')
        maintenance.verify_backup(op, Path(saved['directory']), saved['manifestSHA256'])
        journal['checkpoint'] = saved
        journal['checkpointGuestPidPreserved'] = True
        journal['phase'] = 'checkpointed';write(op, journal_path, journal)
        phase('checkpointed')
        deployment.start_checked(op, current, ROLES, config_path)
        phase('roles-resumed')
        journal['phase'] = 'switching';write(op, journal_path, journal)
        changed = deployment.upgrade(op, current, config_path, Path(release), Path(python))
        journal['codeResult'] = changed
        journal['phase'] = 'code-returned';write(op, journal_path, journal)
        phase('code-returned')
        if changed['status'] != 'upgraded':
            return finish(op, config_path, journal, 'candidate-failed-rolled-back')
        return finish(op, config_path, journal, 'upgraded')
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        # Recovery never restores old account/authority data or rotates secrets.
        recover(op, config_path)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['upgrade', 'recover'])
    parser.add_argument('--operator', type=Path, required=True)
    parser.add_argument('--operator-manifest-sha256', required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--release', type=Path)
    parser.add_argument('--python', type=Path)
    parser.add_argument('--backup-parent', type=Path)
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Requires root and a reviewed immutable operator')
    if args.action == 'upgrade' and not all([args.release, args.python, args.backup_parent]):
        parser.error('Upgrade requires candidate release, Python and backup parent')
    operator = args.operator.absolute()
    if operator.name != 'manage-services.py' or operator.parent.name != 'scripts':
        parser.error('Use the installed candidate manage-services.py')
    release = operator.parent.parent
    raw = (release / 'connected-release.json').read_bytes()
    if digest(raw) != args.operator_manifest_sha256:
        parser.error('Operator manifest differs from the reviewed candidate')
    metadata = json.loads(raw)
    if metadata['version'] not in ('codi-connected-development/10','codi-connected-development/11','codi-connected-development/12','codi-connected-development/13','codi-connected-development/14','codi-connected-development/15','codi-connected-development/16','codi-connected-development/17','codi-connected-development/18'):
        parser.error('A profile10/11/12/13/14/15/16/17/18 operator is required')
    for path in [release, *release.parents, *release.rglob('*')]:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or info.st_uid != 0 or info.st_gid != 0 or info.st_mode & 0o022:
            parser.error('Operator and ancestors must be root-owned and protected')
        if path.is_relative_to(release) and path.is_file() and path.name != 'connected-release.json':
            name = str(path.relative_to(release))
            if info.st_nlink != 1 or metadata['files'].get(name) != {'bytes': info.st_size, 'sha256': digest(path.read_bytes())}:
                parser.error('Installed operator file differs from its manifest')
    if set(metadata['files']) != {str(p.relative_to(release)) for p in release.rglob('*') if p.is_file() and p.name != 'connected-release.json'}:
        parser.error('Installed candidate is incomplete')
    spec = importlib.util.spec_from_file_location('native_rollout_operator', args.operator)
    op = importlib.util.module_from_spec(spec);sys.modules[spec.name] = op;spec.loader.exec_module(op)
    with op.locked(args.config):
        if metadata['version'] in ('codi-connected-development/15','codi-connected-development/16','codi-connected-development/17','codi-connected-development/18'):
            from origin_service import signin_migration
            signin_migration.guard(op,args.config,'upgrade')
        result = recover(op, args.config) if args.action == 'recover' else upgrade(op, args.config, args.release, args.python, args.backup_parent)
    print(json.dumps(result, indent=2))
    if result['status'] == 'candidate-failed-rolled-back':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
