#!/usr/bin/env python3
"""Prepare a locked gateway identity and private storage; no listener or routes.

Run only from the authenticated root-owned bundle. Existing owners/modes are
validated and never silently changed. Issuer database is opened read-only by
root; only active account subjects, never credentials, reach the gateway user.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pwd
import sqlite3
import stat
import subprocess
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
ACCOUNT = 'codi-gateway'
STATE_PARENT = Path('/var/lib/codi-gateway')
DATA_PARENT = Path('/var/lib/codi-user-files')
AUTH_DB = Path('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3')

def protected(path, *, owner=0, mode=0o755):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != owner or stat.S_IMODE(info.st_mode) != mode:
        raise ValueError('Unsafe directory: ' + str(path))
    for parent in path.parents:
        info = parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Unsafe storage ancestor: ' + str(parent))

def active_subjects():
    for path in AUTH_DB.parents:
        info = path.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o022:
            raise ValueError('Unsafe issuer database ancestor')
    info = AUTH_DB.lstat()
    issuer = pwd.getpwnam('codi-issuer')
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != issuer.pw_uid or stat.S_IMODE(info.st_mode) != 0o600:
        raise ValueError('Unsafe issuer account database')
    db = sqlite3.connect('file:' + quote(str(AUTH_DB), safe='/') + '?mode=ro', uri=True, timeout=2)
    try:
        # Select only identifiers. No usernames or password material is copied.
        subjects = [row[0] for row in db.execute('SELECT accounts.subject FROM accounts JOIN account_policy USING(subject) WHERE disabled=0 ORDER BY accounts.subject')]
        if len(subjects) > 1024:
            raise ValueError('Explicit storage capacity review required')
        return subjects
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error('Root is required to validate locked account and custody')
    spec = importlib.util.spec_from_file_location('service_accounts', ROOT/'scripts/install-service-accounts.py')
    account_module = importlib.util.module_from_spec(spec);spec.loader.exec_module(account_module)
    user, group = account_module.validate(ACCOUNT, 1001)
    for parent in [STATE_PARENT, DATA_PARENT]:
        if parent.exists() or parent.is_symlink():
            protected(parent)
        else:
            protected(parent.parent)
        instance = parent/'ksu'
        if instance.exists() or instance.is_symlink():
            if not user:
                raise ValueError('Retained storage exists without its service account')
            protected(instance, owner=user.pw_uid, mode=0o700)
    subjects = active_subjects()
    before = {}
    for role in ['issuer', 'steward', 'guest']:
        before[role] = subprocess.check_output(['systemctl', 'show', 'codi-ksu-hidden-'+role+'.service', '-p', 'MainPID', '--value'], text=True).strip()
        if not before[role].isdigit() or int(before[role]) <= 0:
            raise ValueError('Existing role not healthy')
    report = {'status': 'PASS', 'action': 'apply' if args.apply else 'plan',
              'account': ACCOUNT, 'accountAlreadyExists': bool(user),
              'stateRoot': str(STATE_PARENT/'ksu'), 'dataRoot': str(DATA_PARENT/'ksu'),
              'activeRegisteredAccounts': len(subjects), 'beforePids': before,
              'publicServiceStarted': False, 'routingChanged': False}
    if args.apply:
        fd = os.open('/run/lock/codi-user-storage.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
                raise ValueError('Unsafe storage operator lock')
            fcntl.flock(fd, fcntl.LOCK_EX)
            # Revalidate after the operator lock, before mutations.
            user, group = account_module.validate(ACCOUNT, 1001)
            if group is None:
                subprocess.run(['groupadd', '--system', ACCOUNT], check=True)
            if user is None:
                subprocess.run(['useradd', '--system', '--gid', ACCOUNT, '--home-dir', '/nonexistent', '--no-create-home', '--shell', '/usr/sbin/nologin', ACCOUNT], check=True)
            user, group = account_module.validate(ACCOUNT, 1001)
            for parent in [STATE_PARENT, DATA_PARENT]:
                if not parent.exists():
                    parent.mkdir(mode=0o755)
                protected(parent)
                instance = parent/'ksu'
                if not instance.exists():
                    instance.mkdir(mode=0o700);os.chown(instance, user.pw_uid, group.gr_gid)
                protected(instance, owner=user.pw_uid, mode=0o700)
            command = ['runuser', '-u', ACCOUNT, '--', '/usr/bin/python3', '-I', '-B', str(ROOT/'scripts/storage-admin.py'), '--state-root', str(STATE_PARENT/'ksu'), '--data-root', str(DATA_PARENT/'ksu')]
            child = subprocess.run(command, input=json.dumps({'subjects': subjects}), text=True, capture_output=True, timeout=60, check=True)
            report['registry'] = json.loads(child.stdout)
            report['uid'], report['gid'] = user.pw_uid, group.gr_gid
            # The service must have no path to issuer password/key state.
            denied = subprocess.run(['runuser', '-u', ACCOUNT, '--', '/usr/bin/test', '-r', str(AUTH_DB)], capture_output=True)
            if denied.returncode != 1:
                raise ValueError('Gateway can unexpectedly read issuer credentials')
            report['issuerDatabaseUnreadableByGateway'] = True
            for other in ['codi-issuer', 'codi-steward', 'codi-guest', 'caddy']:
                denied = subprocess.run(['runuser', '-u', other, '--', '/usr/bin/test', '-r', str(STATE_PARENT/'ksu/permissions.sqlite3')], capture_output=True)
                if denied.returncode != 1:
                    raise ValueError('Private storage readable by another service')
            report['privateDatabaseUnreadableByOtherServices'] = True
        finally:
            os.close(fd)
    after = {role: subprocess.check_output(['systemctl', 'show', 'codi-ksu-hidden-'+role+'.service', '-p', 'MainPID', '--value'], text=True).strip() for role in before}
    if before != after:
        raise ValueError('Existing native role restarted during storage preparation')
    report['afterPids'] = after
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
