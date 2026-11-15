#!/usr/bin/env python3
"""Exercise or activate the pinned large-file ingress on box-webhost.

Run as root on box-webhost, passing the candidate sites.toml on standard input.
The previously installed source-route operator supplies journaling, locking,
rollback and cross-site checks; this wrapper strictly limits the new change.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile

OPERATOR = Path('/srv/codi-browser/operators/sources-37218ff39/activate-browser-sources.py')
OPERATOR_SHA = 'd32d6513c1e3b3d5627dca4cf13235c772b41a1067cff827947e6f0a10bdab99'
SOURCE_SHA = '9bb5e958f27985891b8c927215e4927ddd514870309e271ec0f29790e2de8c68'
OLD_MANIFEST = '3ff13521fdca82c339d39fff09be45258e41f132d893a9e7c9fc51796636d93f'
NEW_MANIFEST = 'a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260'
OLD_CADDY = 'a4d05c0e404188ddf2192dd5f9efb53076aa499f76d5dc2b36e87c6ee7e3df63'
NEW_CADDY = '0abb1284887d57115a48fc6c6a554207930294c0582c420cc1f13e168e5ad016'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if os.geteuid() != 0 or socket.gethostname() != 'box-webhost':
        raise ValueError('Root on box-webhost required')
    if len(sys.argv) != 2 or sys.argv[1] not in ('exercise', 'apply', 'recover'):
        raise ValueError('Specify exercise, apply, or recover')
    if (OPERATOR.is_symlink() or OPERATOR.stat().st_uid != 0
            or OPERATOR.stat().st_mode & 0o022 or sha(OPERATOR.read_bytes()) != OPERATOR_SHA):
        raise ValueError('Installed hosting operator changed')
    spec = importlib.util.spec_from_file_location('codi_source_operator', OPERATOR)
    op = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(op)
    op.JOURNAL = op.STATE / 'large-file-ingress-journal.json'
    op.RECEIPT = op.STATE / 'large-file-ingress-result.json'
    op.PINS.update(oldSource=SOURCE_SHA, newSource=SOURCE_SHA,
                   oldManifest=OLD_MANIFEST, newManifest=NEW_MANIFEST,
                   oldCaddy=OLD_CADDY, newCaddy=NEW_CADDY)
    original_check = op.check

    def check(data, expected):
        original_check(data, expected)
        status, body = op.request('ksu.codes', '/gateway/upload-capabilities')
        if status != 200 or json.loads(body) != {'version': 'codi-binary-upload/1', 'maxBytes': 134217728}:
            raise ValueError('Streaming gateway capability unavailable')

    op.check = check
    action = sys.argv[1]
    if action == 'recover':
        sys.argv = [str(OPERATOR), action]
        op.main()
        return
    candidate = sys.stdin.buffer.read(1048577)
    if sha(candidate) != NEW_MANIFEST:
        raise ValueError('Candidate manifest changed')
    current = op.MANIFEST.read_bytes()
    if sha(current) != OLD_MANIFEST:
        raise ValueError('Baseline manifest changed')
    before = op.common.tomllib.loads(current.decode())
    after = op.common.tomllib.loads(candidate.decode())
    expected = copy.deepcopy(before)
    matches = [site for site in expected['sites'] if site['domain'] == 'ksu.codes']
    if len(matches) != 1 or matches[0].get('codi_large_files', False):
        raise ValueError('Unexpected KSU site baseline')
    matches[0]['codi_large_files'] = True
    if after != expected:
        raise ValueError('Candidate changes more than the KSU large-file flag')
    status, body = op.request('ksu.codes', '/gateway/upload-capabilities')
    if status != 200 or json.loads(body) != {'version': 'codi-binary-upload/1', 'maxBytes': 134217728}:
        raise ValueError('Streaming gateway capability unavailable')
    with tempfile.TemporaryDirectory(prefix='codi-large-file-ingress-') as name:
        path = Path(name)
        (path / 'common.py').write_bytes(op.SOURCE.read_bytes())
        (path / 'sites.toml').write_bytes(candidate)
        sys.argv = [str(OPERATOR), action, '--inputs', str(path)]
        op.main()


if __name__ == '__main__':
    main()
