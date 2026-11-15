#!/usr/bin/env python3
"""Exercise or activate the pinned issuer-only file-limit code upgrade.

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
OLD_RELEASE='/srv/codi-connected/releases/browser-issuer-profile28-r3'
NEW_RELEASE='/srv/codi-connected/releases/browser-issuer-profile28-large-r3'
OLD_MANIFEST='957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d'
NEW_MANIFEST='0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2'
SOURCE='d32c182fe5043a1671d460bd27325cf72750d94e771dbd070f523537eee407e8'
SITES='a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260'
CADDY='c098afe8572a12105527e17773c14f551075c52854617838b5477ab136ea55a0'
OPERATOR_SHA='fefe6b861650cd76e5187d95860d63903d3c2184ab2ce3fca77e73ce55b8bbe4'


def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed backend operator changed')
    spec=importlib.util.spec_from_file_location('codi_backend_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.OLD_RELEASE=OLD_RELEASE;op.NEW_RELEASE=NEW_RELEASE;op.MANAGER=NEW_RELEASE+'/scripts/manage-services.py'
    op.JOURNAL=op.STATE/'large-file-issuer-journal.json';op.RECEIPT=op.STATE/'large-file-issuer-result.json'
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
    with tempfile.TemporaryDirectory(prefix='codi-large-issuer-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(op.SOURCE.read_bytes());(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
