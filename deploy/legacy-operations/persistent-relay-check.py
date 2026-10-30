#!/usr/bin/env python3
"""Exercise real isolated native relay installation, rotation and crash recovery."""
import datetime
import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from relay_service import manager as relay


def main():
    name = 'codi-relay-check-' + secrets.token_hex(6)
    stage = Path('/srv') / name
    checks = []
    result = {'status': 'FAIL', 'scope': 'Actual disposable native private relay lifecycle; pinned local TLS only, not public trust/WAN/shared ingress', 'instance': name}
    manager = None
    network = None
    def passed(label):
        checks.append(label)
    def denied(fn):
        try:
            fn()
        except (ValueError, OSError):
            return
        raise AssertionError('Unsafe operation was accepted')
    def pair(days=4, hostname='turn.fixture.invalid'):
        key = ec.generate_private_key(ec.SECP256R1())
        now = datetime.datetime.now(datetime.timezone.utc)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
        certificate = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
                       .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=1))
                       .not_valid_after(now + datetime.timedelta(days=days)).add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False).sign(key, hashes.SHA256()))
        return certificate.public_bytes(serialization.Encoding.PEM), key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    try:
        stage.mkdir(mode=0o755)
        binary = stage / 'turnserver'
        shutil.copyfile(ROOT / '.build/tools/coturn-4.18.0-build-r1/runtime/turnserver', binary)
        binary.chmod(0o755)
        manager = relay.Manager(stage / 'config')
        first_cert, first_key = pair()
        next_cert, next_key = pair()
        kwargs = {'instance': name, 'hostname': 'turn.fixture.invalid', 'binary': binary, 'port': 16479, 'unit_dir': '/run/systemd/system'}
        with manager.locked():
            initial = manager.configure(**kwargs, cert=first_cert, key=first_key)
            assert initial['status'] == 'relay-configured' and not initial['running']
            first = manager.load()
            assert first['coturnRelease'] == '4.18.0'
            secret_pin = relay.digest(manager.secret())
            assert all(state.get('ActiveState') == 'inactive' for state in manager.states(first).values())
            passed('persistent configuration installs three static units without starting or enabling them')
            manager.start()
            assert manager.ready(first)['unauthenticatedAllocation401']
            logs = list((Path('/run') / name).glob('turn*.log'))
            assert logs and not any(token in '\n'.join(p.read_text() for p in logs).lower() for token in ['bad configuration', 'unknown option', 'unrecognized', 'deprecated'])
            passed('real TLS relay starts through socket proxy and refuses unauthenticated allocation')
            change = manager.bandwidth_profile('text-128/1')
            wide = manager.load()
            assert change['effectiveBandwidthAllocationSlots'] == 128
            config = manager.turn_config(wide)
            assert all(setting in config for setting in (b'total-quota=128\n', b'bps-capacity=4194304\n', b'max-port=14011\n', b'denied-peer-ip=0.0.0.0-255.255.255.255\n'))
            assert manager.ready(wide)['unauthenticatedAllocation401']
            change = manager.bandwidth_profile('text-256/1')
            large = manager.load()
            assert change['effectiveBandwidthAllocationSlots'] == 256
            config = manager.turn_config(large)
            assert all(setting in config for setting in (b'total-quota=256\n', b'user-quota=32\n', b'bps-capacity=8388608\n', b'max-port=14523\n', b'denied-peer-ip=0.0.0.0-255.255.255.255\n'))
            assert manager.ready(large)['unauthenticatedAllocation401']
            manager.bandwidth_profile('legacy')
            assert manager.load() == first and manager.ready(first)['unauthenticatedAllocation401']
            passed('128-slot profile starts and rolls back with private relay isolation preserved')
            def inspect():
                states = manager.states(manager.load())
                witnesses = {}
                for unit in manager.names(first)[:2]:
                    pid = int(states[unit]['MainPID'])
                    assert pid > 0
                    raw = dict(line.split(':', 1) for line in Path('/proc', str(pid), 'status').read_text().splitlines())
                    namespace = os.readlink('/proc/' + str(pid) + '/ns/net')
                    uid = set(map(int, raw['Uid'].split()))
                    assert len(uid) == 1 and 0 not in uid and int(raw['CapEff'], 16) == 0 and raw['NoNewPrivs'].strip() == '1'
                    assert namespace != os.readlink('/proc/self/ns/net')
                    assert states[unit]['UnitFileState'] == 'static'
                    witnesses[unit] = {'pid': pid, 'uid': next(iter(uid)), 'namespace': namespace, 'capabilities': raw['CapEff'].strip(), 'noNewPrivileges': True}
                assert len({w['namespace'] for w in witnesses.values()}) == 1 and len({w['uid'] for w in witnesses.values()}) == 2
                pid = next(iter(witnesses.values()))['pid']
                probe = '''import errno,json,socket
def check(host,port):
 with socket.socket() as s:s.settimeout(1);return s.connect_ex((host,port))
internet=check('1.1.1.1',443);host=check('127.0.0.1',8118)
assert internet==errno.ENETUNREACH and host==errno.ECONNREFUSED
print(json.dumps({'internetError':internet,'hostIssuerError':host}))
'''
                probes = json.loads(subprocess.run(['nsenter', '-t', str(pid), '-n', '/usr/bin/python3', '-B', '-c', probe], capture_output=True, text=True, check=True).stdout)
                interfaces = json.loads(subprocess.run(['nsenter', '-t', str(pid), '-n', 'ip', '-j', 'address', 'show'], capture_output=True, text=True, check=True).stdout)
                assert [item['ifname'] for item in interfaces] == ['lo']
                listeners = subprocess.run(['nsenter', '-t', str(pid), '-n', 'ss', '-H', '-lntu'], capture_output=True, text=True, check=True).stdout.splitlines()
                assert len(listeners) == 1 and listeners[0].startswith('tcp') and '127.0.0.1:' + str(kwargs['port']) in listeners[0], listeners
                return {'processes': witnesses, 'onlyLoopbackInterface': True, 'probes': probes}
            network = inspect()
            passed('separate dynamic users share only a private loopback namespace, no host/Internet reachability')
            before_pids = manager.states(first)
            assert manager.configure(**kwargs, cert=first_cert, key=first_key)['status'] == 'relay-already-current'
            assert manager.states(first) == before_pids
            passed('unchanged certificate configuration does not restart services')
            for cert, key in [pair(days=1), pair(hostname='wrong.fixture.invalid'), (next_cert, first_key)]:
                denied(lambda: manager.configure(**kwargs, cert=cert, key=key))
            assert manager.states(first) == before_pids and manager.load() == first
            passed('expiring certificate, wrong hostname and mismatched key refused before restart')
            secret_file = manager.directory / 'turn.secret'
            original_secret = relay.read(secret_file)
            relay.atomic(secret_file, b'z' * 43)
            try:
                denied(manager.start)
                denied(lambda: manager.configure(**kwargs, cert=next_cert, key=next_key))
                assert manager.states(first) == before_pids
            finally:
                relay.atomic(secret_file, original_secret)
            passed('secret drift refused before touching running services')
            unit = Path(first['unitDir']) / manager.names(first)[0]
            original_unit = relay.read(unit, 0o644)
            relay.atomic(unit, original_unit + b'\n# outside edit\n', 0o644)
            try:
                denied(manager.start)
                denied(lambda: manager.configure(**kwargs, cert=next_cert, key=next_key))
            finally:
                relay.atomic(unit, original_unit, 0o644)
            assert manager.states(first) == before_pids
            passed('out-of-controller unit changes refused without restart')
            original_start = manager.start_units
            calls = [0]
            def failed_ready(value):
                output = original_start(value)
                calls[0] += 1
                if calls[0] == 1:
                    raise ValueError('SIMULATED_READINESS_FAILURE_AFTER_REAL_START')
                return output
            with patch.object(manager, 'start_units', failed_ready):
                denied(lambda: manager.configure(**kwargs, cert=next_cert, key=next_key))
            assert manager.load() == first and not manager.journal.exists()
            assert manager.ready(first)['unauthenticatedAllocation401']
            inspect()
            passed('failed readiness after real certificate replacement restores previous units/certificate and starts relay')
            class AbruptDeath(BaseException):
                pass
            original_apply = manager.apply
            def interrupted(value):
                original_apply(value)
                raise AbruptDeath()
            try:
                with patch.object(manager, 'apply', interrupted):
                    manager.configure(**kwargs, cert=next_cert, key=next_key)
            except AbruptDeath:
                pass
            else:
                raise AssertionError('Fault injection did not run')
            assert manager.journal.exists() and manager.load() != first
            for operation in [manager.start, manager.stop, lambda: manager.configure(**kwargs, cert=first_cert, key=first_key)]:
                denied(operation)
            assert manager.recover()['status'] == 'interrupted-relay-rolled-back'
            assert manager.load() == first and manager.ready(first)['unauthenticatedAllocation401']
            inspect()
            passed('actual interrupted unit/config write retains journal, blocks lifecycle and recovers old running relay')
            with patch.object(manager, 'clear', side_effect=OSError('SIMULATED_FAILURE_AFTER_COMMIT')):
                denied(lambda: manager.configure(**kwargs, cert=next_cert, key=next_key))
            committed = manager.load()
            assert committed != first and json.loads(relay.read(manager.journal))['phase'] == 'committed'
            assert manager.recover()['status'] == 'committed-relay-recovered'
            assert manager.load() == committed and manager.ready(committed)['unauthenticatedAllocation401']
            network = inspect()
            assert relay.digest(manager.secret()) == secret_pin
            assert (manager.directory / 'bundles' / first['bundle'] / 'key.pem').exists()
            passed('durable commit recovery retains new certificate, original shared secret and prior credential bundle')
            manager.stop()
            with socket.socket() as occupied:
                occupied.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                occupied.bind(('127.0.0.1', kwargs['port']))
                occupied.listen()
                denied(manager.start)
                assert not manager.active(committed)
            manager.start()
            passed('host socket conflict cleans newly started private processes; explicit start succeeds afterward')
            manager.stop()
            pids = manager.states(committed)
            assert not manager.active(committed)
            for p in [manager.directory, manager.directory / 'bundles', manager.directory / 'bundles' / committed['bundle']]:
                assert p.stat().st_uid == 0 and p.stat().st_mode & 0o777 == 0o700
            for p in (manager.directory / 'bundles').rglob('*'):
                if p.is_file():
                    assert p.stat().st_mode & 0o777 == 0o600
            passed('explicit stop reaps processes; retained certificates/config/shared secret have root-only custody')
            result.update(status='PASS', checks=checks, network=network, coturnRelease='4.18.0', coturnBinarySHA256=relay.digest(binary.read_bytes()), enabledForBoot=False, publicIngressConfigured=False, secretPrintedOrExported=False)
    except BaseException as error:
        result['error'] = str(error)
        result['checks'] = checks
    finally:
        cleanup = []
        names = [name + '-proxy.socket', name + '-proxy.service', name + '.service']
        for unit in names:
            subprocess.run(['systemctl', 'stop', unit], capture_output=True, timeout=15)
            response = subprocess.run(['systemctl', 'show', unit, '-p', 'MainPID', '-p', 'ActiveState'], capture_output=True, text=True)
            fields = dict(line.split('=', 1) for line in response.stdout.splitlines() if '=' in line)
            if fields.get('MainPID', '0') != '0' or fields.get('ActiveState') not in ('inactive', 'failed', None):
                cleanup.append('Unit remains active: ' + unit)
        if not cleanup:
            for unit in names:
                (Path('/run/systemd/system') / unit).unlink(missing_ok=True)
                subprocess.run(['systemctl', 'reset-failed', unit], capture_output=True)
            subprocess.run(['systemctl', 'daemon-reload'], check=True, capture_output=True)
            shutil.rmtree(stage, ignore_errors=True)
            if stage.exists():
                cleanup.append('Private fixture retained')
        result['cleanupErrors'] = cleanup
        result['fixtureUnitsAndPrivateStateRemoved'] = not cleanup and not stage.exists()
        if cleanup:
            result['status'] = 'FAIL'
        result['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['relay_service/__init__.py', 'relay_service/manager.py', 'scripts/manage-relay.py', 'scripts/persistent-relay-check.py']}
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    if os.geteuid() == 0:
        raise SystemExit(main())
    child = subprocess.run(['sudo', '-n', sys.executable, '-B', str(Path(__file__).resolve())], capture_output=True, text=True, timeout=240)
    if child.stderr:
        sys.stderr.write(child.stderr)
    report = json.loads(child.stdout)
    (ROOT / '.build/checks/persistent-relay-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(child.returncode)
