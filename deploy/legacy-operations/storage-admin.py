#!/usr/bin/env python3
"""Private operator bootstrap, run as the storage service account, never HTTP.

Only an administrator may pass subjects read from the trusted issuer database.
Accepting these identifiers is NOT browser identity verification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from gateway_service.policy import Principal
from gateway_service.user_store import UserStore, registered

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', required=True)
    parser.add_argument('--data-root', required=True)
    args = parser.parse_args()
    raw = sys.stdin.buffer.read(131073)
    if len(raw) > 131072:
        raise ValueError('Bounded trusted subject input required')
    value = json.loads(raw)
    if not isinstance(value, dict) or set(value) != {'subjects'} or not isinstance(value['subjects'], list) or len(value['subjects']) > 1024:
        raise ValueError('Explicit trusted registered subjects required')
    principals = [Principal(subject, 'operator-bootstrap', 'registered', {}, int(time.time()) + 300) for subject in value['subjects']]
    for principal in principals:
        registered(principal)
    if len({p.sub for p in principals}) != len(principals):
        raise ValueError('Duplicate registered subject')
    store = UserStore(args.state_root, args.data_root)
    for principal in principals:
        store.ensure_user(principal)
    with store.lock(), store.db() as db:
        rows = db.execute('SELECT subject,home_id,state,enabled FROM users ORDER BY subject').fetchall()
        permissions = db.execute('SELECT count(*) FROM permissions').fetchone()[0]
    print(json.dumps({'status': 'PASS', 'activeRegisteredAccountsRequested': len(principals),
                      'retainedRegisteredFolders': len(rows), 'permissions': permissions,
                      'bindingSHA256': hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
                      'anonymousFolders': 0, 'publicServiceStarted': False}))

if __name__ == '__main__':
    main()
