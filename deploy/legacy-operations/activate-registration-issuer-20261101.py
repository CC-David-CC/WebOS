#!/usr/bin/env python3
"""Exercise or activate the pinned classroom login issuer code upgrade.

The existing backend operator supplies its managed code transition, journal,
rollback, hosting lock and cross-site checks. No user data is restored.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile

OPERATOR=Path('/srv/codi-browser/operators/backend-b7c31de02/activate-browser-backend.py')
OLD_RELEASE='/srv/codi-connected/releases/classroom-login-r1'
NEW_RELEASE='/srv/codi-connected/releases/registration-admission-r1'
OLD_MANIFEST='9d4bbe6dfe4f82e2dbb472e4ce8c1a7d0061f4466b4e5533d0b71a8ad8d22533'
NEW_MANIFEST='51a3991f7a158c2f181899fcbc0eea89978b649d3c97689efc517311d98b3a6a'
SOURCE='fb6df35217cf19d5c138f67ebbc3ffc8a3514a75c0cb85e0ae5b568819560935'
SITES='b93ce79d3e1c2e8a8d521503b3294acc2f3886ca8c397d2f2fbbd5a7b4f8a2cb'
CADDY='3f14e33f5d3fa731b2d533552a90fd194b5ac0cab40bdc87e3811149c593203b'
OPERATOR_SHA='fefe6b861650cd76e5187d95860d63903d3c2184ab2ce3fca77e73ce55b8bbe4'


def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed backend operator changed')
    spec=importlib.util.spec_from_file_location('codi_backend_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.OLD_RELEASE=OLD_RELEASE;op.NEW_RELEASE=NEW_RELEASE;op.MANAGER=NEW_RELEASE+'/scripts/manage-services.py'
    op.JOURNAL=op.STATE/'registration-admission-issuer-journal.json';op.RECEIPT=op.STATE/'registration-admission-issuer-result.json'
    op.PINS.update(oldSource=SOURCE,candidateSource=SOURCE,oldManifest=SITES,candidateManifest=SITES,
                   oldCaddy=CADDY,candidateCaddy=CADDY,candidateRelease=NEW_MANIFEST)
    original=op.wait_checks
    def check(expected):
        original(expected)
        status,raw=op.request('ksu.codes','/config.json')
        if status!=200 or json.loads(raw).get('gateway',{}).get('fileBytes')!=134217728:raise ValueError('Issuer did not advertise 128 MiB')
    op.wait_checks=check
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    if sha((Path(OLD_RELEASE)/'connected-release.json').read_bytes())!=OLD_MANIFEST:raise ValueError('Old release changed')
    with tempfile.TemporaryDirectory(prefix='codi-classroom-issuer-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(op.SOURCE.read_bytes());(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
