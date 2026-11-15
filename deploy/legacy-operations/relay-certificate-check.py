#!/usr/bin/env python3
"""Actual protected certificate refresh job, provider custody and timer checks."""
import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import pwd
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from relay_service import certificates
from relay_service import manager as relay


def main():
    name = 'codi-relay-cert-' + secrets.token_hex(6)
    stage = Path('/srv') / name
    checks, units = [], []
    result = {'status': 'FAIL', 'scope': 'Actual disposable private TURN certificate provider and root scheduled job; no public ingress or CA trust claim'}
    def passed(label):
        checks.append(label)
    def denied(fn):
        try:
            fn()
        except (ValueError, OSError):
            return
        raise AssertionError('Invalid certificate operation accepted')
    def pair(days=10, hostname='turn.fixture.invalid'):
        key = ec.generate_private_key(ec.SECP256R1())
        now = datetime.datetime.now(datetime.timezone.utc)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
        cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject).public_key(key.public_key())
                .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(days=7))
                .not_valid_after(now + datetime.timedelta(days=days)).add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname)]), critical=False).sign(key, hashes.SHA256()))
        return cert.public_bytes(serialization.Encoding.PEM), key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    try:
        stage.mkdir(mode=0o755)
        binary = stage / 'turnserver'
        shutil.copyfile(ROOT / '.build/tools/coturn-4.18.0-build-r1/runtime/turnserver', binary)
        binary.chmod(0o755)
        spec = importlib.util.spec_from_file_location('relay_export', ROOT / 'scripts/export-relay-operator.py')
        exporter = importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
        operator = stage / 'operator'
        exported = exporter.export(operator)
        # Copy only the installed speech-independent crypto dependencies into a
        # fresh root-controlled venv. No privileged job imports user-owned code.
        python = stage / 'venv/bin/python'
        subprocess.run(['/usr/bin/python3', '-m', 'venv', str(stage / 'venv')], check=True, capture_output=True, timeout=45)
        site = next((stage / 'venv/lib').glob('python*/site-packages'))
        for module in ['cryptography', 'cffi', 'pycparser', '_cffi_backend']:
            found = importlib.util.find_spec(module)
            source = Path(found.origin).parent if found.submodule_search_locations else Path(found.origin)
            destination = site / source.name
            shutil.copytree(source, destination) if source.is_dir() else shutil.copyfile(source, destination)
        for distribution in ['cryptography', 'cffi', 'pycparser']:
            meta = Path(importlib.metadata.distribution(distribution)._path)
            shutil.copytree(meta, site / meta.name)
        for entry in [stage / 'venv', *(stage / 'venv').rglob('*')]:
            if not entry.is_symlink():
                entry.chmod(0o755 if entry.is_dir() or entry.parent == python.parent else 0o644)
        uid = pwd.getpwnam('nobody').pw_uid
        provider = stage / 'provider';provider.mkdir(mode=0o700);os.chown(provider, uid, uid)
        def publish(cert, key):
            for suffix, content in [('crt', cert), ('key', key)]:
                file = provider / ('turn.fixture.invalid.' + suffix)
                file.write_bytes(content);file.chmod(0o600);os.chown(file, uid, uid)
        first_cert, first_key = pair()
        publish(first_cert, first_key)
        manager = relay.Manager(stage / 'config')
        with manager.locked():
            initial = manager.configure(instance=name, hostname='turn.fixture.invalid', binary=binary, cert=first_cert, key=first_key, port=17479, unit_dir='/run/systemd/system')
            if '--text-profile' in sys.argv:
                manager.bandwidth_profile('text-32k/1')
            value = manager.load();secret = relay.digest(manager.secret())
            units.extend(manager.names(value))
            keyfile = provider / 'turn.fixture.invalid.key'
            keyfile.chmod(0o644)
            denied(lambda: certificates.bind(manager, provider, uid))
            assert not (manager.directory / 'certificate-source.json').exists()
            keyfile.chmod(0o600)
            certfile = provider / 'turn.fixture.invalid.crt'
            certfile.rename(provider / 'actual.crt');certfile.symlink_to(provider / 'actual.crt')
            denied(lambda: certificates.bind(manager, provider, uid))
            certfile.unlink();(provider / 'actual.crt').rename(certfile)
            certificates.bind(manager, provider, uid)
            assert relay.read(manager.directory / 'certificate-source.json')
            passed('provider-owned0700 directory and0600 key bind; readable key and symbolic link refused before policy write')
            provider.chmod(0o722)
            denied(lambda: certificates.refresh(manager));provider.chmod(0o700)
            assert manager.load() == value
            passed('writable provider directory refused without relay mutation')
            rendered = certificates.refresh_units(manager, operator, python)
            assert not rendered['enabledForBoot'] and not rendered['installed']
            job, timer = name + '-certificate-refresh.service', name + '-certificate-refresh.timer'
            units.extend([job, timer])
            for unit, body in rendered['units'].items():
                assert '[Install]' not in body
                relay.atomic(Path('/run/systemd/system') / unit, body.encode(), 0o644)
            relay.run('systemd-analyze', 'verify', *[Path('/run/systemd/system') / unit for unit in units])
            relay.run('systemctl', 'daemon-reload')
            def run_job(success=True):
                response = relay.run('systemctl', 'start', job, check=False)
                assert (response.returncode == 0) == success
                values = dict(line.split('=', 1) for line in relay.run('systemctl', 'show', job, '-p', 'Result', '-p', 'ExecMainStatus').stdout.splitlines())
                assert (values['Result'] == 'success' and values['ExecMainStatus'] == '0') == success
                return values
            # Release the CLI lock before running a separate process/job.
        run_job()
        with manager.locked():
            assert manager.load() == value and not manager.active(value)
            props = dict(line.split('=', 1) for line in relay.run('systemctl', 'show', job, '-p', 'CapabilityBoundingSet', '-p', 'ProtectSystem', '-p', 'NoNewPrivileges', '-p', 'UnitFileState').stdout.splitlines())
            assert props == {'CapabilityBoundingSet': 'cap_dac_read_search', 'ProtectSystem': 'strict', 'NoNewPrivileges': 'yes', 'UnitFileState': 'static'}
            passed('actual sandboxed root job reads another owner private key with DAC_READ_SEARCH only; stopped no-op stays stopped')
            manager.start();before = manager.states(value)
            next_cert, next_key = pair();publish(next_cert, next_key)
        run_job()
        with manager.locked():
            fresh = manager.load()
            assert fresh != value and manager.ready(fresh)['unauthenticatedAllocation401'] and manager.states(fresh) != before
            assert relay.digest(manager.secret()) == secret
            passed('actual refresh job rotates certificate, restarts active private relay and preserves shared secret')
            stable = manager.states(fresh)
        run_job()
        with manager.locked():
            assert manager.load() == fresh and manager.states(fresh) == stable
            passed('unchanged provider certificate preserves running relay/proxy PIDs')
            bad_cert, bad_key = pair(hostname='wrong.fixture.invalid');publish(bad_cert, bad_key)
        run_job(False)
        with manager.locked():
            assert manager.load() == fresh and manager.states(fresh) == stable and not manager.journal.exists()
            passed('wrong-hostname provider causes failed scheduled job without interrupting active relay')
            publish(next_cert, next_key)
            # Represent an installed generation whose validity elapsed. The
            # fixture constructs protected historical metadata; production never
            # accepts an expired certificate through configure.
            manager.stop()
            expired_cert, expired_key = pair(days=-1)
            old = dict(fresh)
            content = {'turn.conf': manager.turn_config(old), 'cert.pem': expired_cert, 'key.pem': expired_key}
            manifest = relay.encoded({'version': 'codi-turn-credentials/1', 'files': {name: {'bytes': len(raw), 'sha256': relay.digest(raw)} for name, raw in content.items()}})
            old['bundle'] = relay.digest(manifest)
            folder = manager.directory / 'bundles' / old['bundle'];folder.mkdir(mode=0o700)
            for name, raw in {**content, 'bundle.json': manifest}.items():relay.atomic(folder / name, raw)
            manager.apply(old)
            assert not manager.status()['certificate']['validNow']
            denied(manager.start)
            # Emulate a relay left running as a leaf expires, without changing
            # host time or weakening the production start validity check.
            relay.run('systemctl', 'start', manager.names(old)[0], manager.names(old)[2])
        run_job()
        with manager.locked():
            assert manager.load() == fresh and manager.ready(fresh)['unauthenticatedAllocation401']
            assert relay.digest(manager.secret()) == secret
            passed('expired installed certificate remains inspectable and start is refused; refresh repairs a still-running expired generation')
            relay.run('systemctl', 'start', timer)
            timer_props = dict(line.split('=', 1) for line in relay.run('systemctl', 'show', timer, '-p', 'ActiveState', '-p', 'UnitFileState', '-p', 'NextElapseUSecMonotonic').stdout.splitlines())
            assert timer_props['ActiveState'] == 'active' and timer_props['UnitFileState'] == 'static' and timer_props['NextElapseUSecMonotonic'] not in ('0', 'infinity', '')
            passed('actual hourly timer arms with a next deadline and no boot enablement; oneshot dispatch tested separately')
            manager.stop()
        assert exporter.verify(operator) == exported
        result.update(status='PASS', checks=checks, bandwidthProfile=fresh.get('bandwidthProfile','legacy'), operatorManifestSHA256=exported['manifestSHA256'], operatorFiles=exported['files'], providerOwnerUID=uid, refreshJobProperties=props, timerProperties=timer_props, runtimeRelease='4.18.0', secretPrintedOrExported=False, publicIngressConfigured=False, enabledForBoot=False)
    except BaseException as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        result['checks'] = checks
    finally:
        cleanup = []
        for unit in sorted(units, key=lambda name: not name.endswith('.timer')):
            relay.run('systemctl', 'stop', unit, check=False)
            fields = dict(line.split('=', 1) for line in relay.run('systemctl', 'show', unit, '-p', 'MainPID', '-p', 'ActiveState', check=False).stdout.splitlines())
            if fields.get('MainPID', '0') != '0' or fields.get('ActiveState') not in (None, 'inactive', 'failed'):cleanup.append(unit)
        if not cleanup:
            for unit in units:
                (Path('/run/systemd/system') / unit).unlink(missing_ok=True);relay.run('systemctl', 'reset-failed', unit, check=False)
            relay.run('systemctl', 'daemon-reload');shutil.rmtree(stage, ignore_errors=True)
        result['cleanupErrors'] = cleanup
        result['fixtureUnitsAndStateRemoved'] = not cleanup and not stage.exists()
        if not result['fixtureUnitsAndStateRemoved']:result['status'] = 'FAIL'
        result['sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in ['relay_service/manager.py', 'relay_service/certificates.py', 'scripts/manage-relay.py', 'scripts/export-relay-operator.py', 'scripts/relay-certificate-check.py']}
    print(json.dumps(result))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    if os.geteuid() == 0:raise SystemExit(main())
    child = subprocess.run(['sudo', '-n', sys.executable, '-B', str(Path(__file__).resolve()),*sys.argv[1:]], capture_output=True, text=True, timeout=240)
    if child.stderr:sys.stderr.write(child.stderr)
    report = json.loads(child.stdout)
    (ROOT / '.build/checks/relay-certificate-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(child.returncode)
