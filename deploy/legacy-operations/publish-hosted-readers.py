#!/usr/bin/env python3
"""Pinned code-only live reader-organization update through the native22 controller.

Root on box-webhost only. No routing, account policy, authority renewal, private
backend install or data restore. Source must be clean at the explicit Git commit.
"""
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import time

OLD = 'a5d5a90767f4d8cc68054470a39394853835670bdc8decd11ad4afe3f9ae0d07'
NEW = '9537a6b6d4ab7074512d48e13c46121282980e7197a7aaf3b1c3f7ddc8199f6a'
OLD_DIR = Path('/srv/codi-connected/releases/native21-'+OLD[:16])
DEST = Path('/srv/codi-connected/releases/native22-'+NEW[:16])
PUBLISHER = Path('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
ROOT_RECEIPT = Path('/srv/codi-connected/hosted-peer-inspect-1792890782972029188-result.json')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main(action, commit):
    assert os.geteuid() == 0 and socket.gethostname() == 'box-webhost'
    assert re.fullmatch('[a-f0-9]{40}', commit)
    assert sha(PUBLISHER) == 'd08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
    m = module('timeout_retention_support', PUBLISHER)
    m.protected(PUBLISHER)
    # Target profile22 validates both current21 and next22. The old pinned
    # publisher remains a byte-identical retention/install helper only.
    m.NATIVE_DIR = DEST
    def config():
        m.protected(m.CONTROL)
        assert stat.S_IMODE(m.CONTROL.stat().st_mode) == 0o600
        c = json.loads(m.CONTROL.read_bytes())
        assert c['version'] == 'codi-managed-instance/5' and c['basePath'] == '' and c['origin'] == 'https://ksu.codes' and c['instance'] == 'codi-ksu-hidden'
        assert c['stateRoot'] == '/var/lib/codi-connected/ksu' and c['python'] == str(m.PYTHON)
        assert (c['manifestSHA256'], c['release']) in [(OLD, str(OLD_DIR)), (NEW, str(DEST))]
        assert c.get('hostedRooms') and c['guestNetwork']['policySHA256'] == '436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
        assert not any((m.CONTROL.parent/n).exists() for n in ['maintenance.json', 'native-rollout.json', 'site-cutover.json'])
        assert sha(Path(c['release'])/'connected-release.json') == c['manifestSHA256']
        return c
    def rooms():
        manager = m.room_manager()
        with manager.locked():
            return manager.health(manager.load())
    def verify_bytes():
        contract = module('timeout_installed_contract', DEST/'origin_service/release.py')
        value = contract.verify(DEST)
        assert value['manifestSHA256'] == NEW and value['files'] == 615
        allowed = {'origin_service/release.py', 'origin_service/deployment.py', 'origin_service/turn_management.py', 'scripts/manage-services.py'}
        changed = {name for name in contract.V19_NATIVE if (DEST/name).read_bytes() != (OLD_DIR/name).read_bytes()}
        assert changed == allowed
        old = json.loads((OLD_DIR/'connected-release.json').read_bytes())['files']
        current = json.loads((DEST/'connected-release.json').read_bytes())['files']
        assert all(current[name] == record for name, record in old.items() if '/apps/' in name)
        return value
    with (m.HOST/'.controller.lock').open('rb') as hosting:
        fcntl.flock(hosting, fcntl.LOCK_EX | fcntl.LOCK_NB)
        git = lambda *args: m.run(['runuser', '-u', 'dflanag3', '--', 'git', '-C', m.REPO, *args])
        assert git('rev-parse', 'HEAD') == commit and not git('status', '--porcelain')
        assert m.hosting_pins() == m.NEW_PINS
        c = config()
        before = m.capture(c)
        backend = rooms()
        result = {'status': 'PASS', 'action': action, 'sourceCommit': commit, 'beforeManifestSHA256': c['manifestSHA256']}
        if action == 'stage':
            assert c['manifestSHA256'] == OLD
            m.install(m.REPO/'tools/codiserver/hosted-readers-native-r1/release', DEST, 'connected-release.json', NEW)
            verify_bytes()
            result['nativeNotActivated'] = True
        elif action == 'activate':
            assert c['manifestSHA256'] == OLD
            verify_bytes()
            notice = Path(c['release'])/'scripts/desktop-maintenance.py'
            notice_args = [m.PYTHON, '-I', '-B', notice, '--directory', Path(c['stateRoot'])/'public']
            result['notice'] = json.loads(m.run([*notice_args, 'scheduled', '--in-seconds', '10', '--duration', '180', '--message', 'Development update in 10 seconds. Please save your work. Unsaved browser work is not backed up; server-saved files remain available.']))
            time.sleep(10)
            try:
                result['upgrade'] = m.native('upgrade', '--release', DEST, '--python', m.PYTHON)
                assert result['upgrade']['status'] == 'upgraded'
            finally:
                message = 'Development update finished. Reload to load the new version. Unsaved browser work was not backed up.' if result.get('upgrade', {}).get('status') == 'upgraded' else 'Development update did not finish. Reload if needed; unsaved browser work was not backed up.'
                result['noticeFinished'] = json.loads(m.run([*notice_args, 'cancelled', '--duration', '120', '--message', message]))
        elif action == 'verify':
            assert c['manifestSHA256'] == NEW
            result['releaseVerification'] = verify_bytes()
            result['nativeStatus'] = m.native('status')
            assert sha(ROOT_RECEIPT) == '43fb53090747c89c43f9b64012416a75a54a21fdf5ad36a1b3f184e860b98e5f'
            m.preserved(json.loads(ROOT_RECEIPT.read_bytes())['state'], c)
            for role in ['issuer', 'steward', 'guest']:
                unit = c['instance']+'-'+role+'.service'
                assert m.run(['systemctl', 'show', unit, '-p', 'UnitFileState', '--value']) == 'disabled'
                pid = int(m.run(['systemctl', 'show', unit, '-p', 'MainPID', '--value']))
                status = dict(line.split(':', 1) for line in Path('/proc', str(pid), 'status').read_text().splitlines())
                assert int(status['Uid'].split()[0]) > 0 and int(status['CapEff'], 16) == 0 and status['NoNewPrivs'].strip() == '1'
            assert m.run(['systemctl', 'show', c['instance']+'-issuer-bootstrap.service', '-p', 'MainPID', '--value']) == '0'
        else:
            raise ValueError('Unknown action')
        after = config()
        result['state'] = m.preserved(before, after)
        assert rooms() == backend and m.hosting_pins() == m.NEW_PINS
        result.update(afterManifestSHA256=after['manifestSHA256'], nativeConfigSHA256=sha(m.CONTROL), hostingUnchanged=True, backendNotRestarted=True, statePreserved=True, routerPortsChanged=False, bootPolicyChanged=False, dataRestored=False)
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['stage', 'activate', 'verify'])
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    value = main(args.action, args.commit)
    receipt = Path('/srv/codi-connected')/('hosted-readers-'+args.action+'-'+str(time.time_ns())+'-result.json')
    fd = os.open(receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': value['status'], 'action': args.action, 'rootReceipt': str(receipt), 'rootReceiptSHA256': sha(receipt), 'nativeManifestSHA256': value['afterManifestSHA256']}))
