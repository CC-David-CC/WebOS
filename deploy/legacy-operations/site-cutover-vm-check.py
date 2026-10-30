#!/usr/bin/env python3
"""Actual code/website/signed-mount/Caddy fault recovery in the retained VM."""
import argparse
import ast
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import tarfile
import time

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent/'.build/deployment/ksu.codes'
FOLDER = '/srv/codi-site-fixture'
PIN = 'c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1'
OLD = '3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211'
NATIVE = '/srv/codi-network-fixture/candidate-c23b1b73df68ffb2'
CONFIG = '/etc/codi-native-fixture/managed.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run(prepare_only=False, resume=False):
    vm = module('site_full_vm', ROOT/'scripts/upgrade-signin-native-vm.py')
    vm.vm.status()

    def remote(command, input=None, check=True, timeout=360):
        r = subprocess.run([*vm.vm.ssh_args(), command], input=input, capture_output=True,
                           text=True, timeout=timeout)
        if check and r.returncode:
            raise ValueError(r.stderr[-6000:] or r.stdout[-3000:])
        return r

    def payload(code, value):
        return json.loads(remote('/usr/bin/python3 -I -B -c '+shlex.quote(code), json.dumps(value)).stdout)

    context_path = ROOT/'.build/checks/site-cutover-vm-context.json'
    if not resume:
        assert remote('test ! -e '+FOLDER, check=False).returncode == 0, 'Preserve/recover the existing owned fixture; do not recreate it'
        # Capture public hosting code only, under the controller lock. Private
        # auth imports/config/keys/user state never leave the production host.
        code = r'''import fcntl,hashlib,json,pathlib
P=pathlib.Path;b=P('/home/dflanag3/webhost-sites')
with (b/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 names=['common.py','webctl.py','scaffold.py','hardware_hosting.py','cardboard_hosting.py','production-smoke.py']
 files={n:(b/'ops'/n).read_text() for n in names};files['sites.toml']=(b/'sites.toml').read_text()
 assert hashlib.sha256(files['common.py'].encode()).hexdigest()=='718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4'
 assert hashlib.sha256(files['sites.toml'].encode()).hexdigest()=='c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715'
 print(json.dumps(files))'''
        r = subprocess.run(['ssh', '-o', 'BatchMode=yes', 'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(code)], capture_output=True, text=True, timeout=60)
        if r.returncode:
            raise ValueError(r.stderr[-3000:])
        inputs = json.loads(r.stdout)
        frozen = ROOT/'.build/hosting/site-cutover-inputs-r1'
        assert not frozen.exists();frozen.mkdir()
        for n, raw in inputs.items():(frozen/n).write_text(raw)
        values = {n: (ROOT/n).read_bytes() for n in ['site_cutover/__init__.py', 'site_cutover/coordinator.py', 'site_cutover/managed.py', 'scripts/site-cutover.py', 'scripts/native-rollout.py']}
        for n, raw in values.items():ast.parse(raw.decode())
        manifest = (json.dumps({'version': 'codi-site-cutover-operator/1', 'files': {n: {'bytes': len(b), 'sha256': sha(b)} for n, b in values.items()}}, indent=2, sort_keys=True)+'\n').encode()
        key = sha(manifest);operator = FOLDER+'/operator-'+key
        values['site-cutover-operator.json'] = manifest
        mount_key = '6e4ebb33e945ea8712dd72c56f5a9928a955af5b340ceaff6ef0221112ebe0dc'
        mount_source = REPO/'tools/codiserver/mount-operators'/mount_key
        mount = FOLDER+'/mount-'+mount_key
        context = {'operator': operator, 'operatorSHA256': key, 'mount': mount}
        helper = (ROOT/'scripts/site-cutover-vm-driver.py').read_bytes();helper_key = sha(helper)
        context['driver'] = FOLDER+'/driver-'+helper_key+'.py';context['driverSHA256'] = helper_key
        binary = ROOT.parent/'.build/tools/caddy';binary_key = sha(binary.read_bytes())
        context.update(binary='/srv/codi-network-fixture/tools/root-route-caddy-'+binary_key, binarySHA256=binary_key)
        write_code = r'''import json,os,pathlib,sys
P=pathlib.Path;v=json.load(sys.stdin);folder=P('/srv/codi-site-fixture');assert not folder.exists();folder.mkdir(mode=0o755)
for n,raw in v['files'].items():
 p=folder/n;assert not P(n).is_absolute() and '..' not in P(n).parts;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw);p.chmod(0o644)
(folder/'hosting/.controller.lock').write_text('');(folder/'hosting/.controller.lock').chmod(0o600)
print(json.dumps({'created':True}))'''
        all_files = {str(Path(operator).relative_to(FOLDER)/n): raw.decode() for n, raw in values.items()}
        all_files.update({str(Path(mount).relative_to(FOLDER)/str(p.relative_to(mount_source))): p.read_text() for p in mount_source.rglob('*') if p.is_file()})
        all_files[Path(context['driver']).name] = helper.decode()
        for n, raw in inputs.items():
            all_files['baseline/'+n] = raw
            all_files['hosting/'+('sites.toml' if n == 'sites.toml' else 'ops/'+n)] = raw
        all_files['root-common.py'] = (ROOT/'hosting_root/common.py').read_text()
        all_files['root-production-smoke.py'] = (ROOT/'hosting_root/production-smoke.py').read_text()
        all_files['root-sites.toml'] = (ROOT/'.build/hosting/root-mount-r1-candidate/sites.toml').read_text()
        payload(write_code, {'files': all_files})
        context_path.write_text(json.dumps(context, indent=2)+'\n')
        # Only reviewed public app/assets and declared dependencies enter the VM.
        def archive(commit, destination):
            data = subprocess.check_output(['git', '-C', str(REPO), 'archive', '--format=tar', commit, 'app', 'public', 'requirements.in', 'requirements.lock.txt'])
            mkdir = remote('mkdir -p '+shlex.quote(destination));assert mkdir.returncode == 0
            with io.BytesIO(data) as stream:
                child = subprocess.run([*vm.vm.ssh_args(), 'tar -xf - -C '+shlex.quote(destination)], input=stream.read(), capture_output=True, timeout=120)
                if child.returncode:raise ValueError(child.stderr.decode()[-2000:])
        archive('bc8ba8c223ea24f151d03afa0b0eaa185720f1a7', FOLDER+'/hosting/sites/ksu.codes')
        # Explicit fixture rollback advances authority instead of restoring it.
        cli = ['/srv/codi-network-fixture/venv/bin/python', '-I', '-B', mount+'/scripts/migrate-desktop-mount.py', 'apply', '--config', CONFIG, '--native-release', NATIVE, '--native-manifest-sha256', PIN, '--base-path', '/hidden', '--seconds', '86400']
        json.loads(remote(shlex.join(cli)).stdout)
        remote('mkdir -m 0700 '+FOLDER+'/code-checkpoints')
        args = ['/srv/codi-network-fixture/venv/bin/python', '-I', '-B', operator+'/scripts/native-rollout.py', 'upgrade', '--operator', NATIVE+'/scripts/manage-services.py', '--operator-manifest-sha256', PIN, '--config', CONFIG, '--release', '/srv/codi-network-fixture/candidate-'+OLD[:16], '--python', '/srv/codi-network-fixture/venv/bin/python', '--backup-parent', FOLDER+'/code-checkpoints']
        changed = json.loads(remote(shlex.join(args)).stdout);assert changed['status'] == 'upgraded'
    else:
        context = json.loads(context_path.read_text())

    def action(name, check=True, **fields):
        value = {**context, 'action': name, **fields}
        r = remote('/srv/codi-network-fixture/venv/bin/python -I -B '+shlex.quote(context['driver']), json.dumps(value), check=check)
        if not check:return r
        return json.loads(r.stdout)

    prepared_report = ROOT/'.build/checks/site-cutover-vm-prepared-result.json'
    if not resume or not prepared_report.exists():
        current = vm.runtime()
        if current['manifestSHA256'] != OLD:
            assert current['manifestSHA256'] == PIN
            remote('test -d '+FOLDER+'/code-checkpoints || mkdir -m 0700 '+FOLDER+'/code-checkpoints')
            args = ['/srv/codi-network-fixture/venv/bin/python', '-I', '-B', context['operator']+'/scripts/native-rollout.py', 'upgrade', '--operator', NATIVE+'/scripts/manage-services.py', '--operator-manifest-sha256', PIN, '--config', CONFIG, '--release', '/srv/codi-network-fixture/candidate-'+OLD[:16], '--python', '/srv/codi-network-fixture/venv/bin/python', '--backup-parent', FOLDER+'/code-checkpoints']
            changed = json.loads(remote(shlex.join(args)).stdout);assert changed['status'] == 'upgraded'
        setup_exists = remote('test -e '+FOLDER+'/prepared.json', check=False)
        assert setup_exists.returncode in (0, 1)
        prepared = action('resume-prepare' if setup_exists.returncode == 0 else 'prepare')
        data = subprocess.check_output(['git', '-C', str(REPO), 'archive', '--format=tar', '9531506c9ed3254d6946df2cbc0f9d296e0e9b78', 'app', 'public', 'requirements.in', 'requirements.lock.txt'])
        child = subprocess.run([*vm.vm.ssh_args(), 'tar -xf - -C '+FOLDER+'/hosting/sites/ksu.codes'], input=data, capture_output=True, timeout=120)
        if child.returncode:raise ValueError(child.stderr.decode()[-2000:])
        action('commit-source')
        prepared_report.write_text(json.dumps({'status': 'PASS', 'context': context, **prepared}, indent=2)+'\n')
    if prepare_only:
        return {'status': 'PREPARED', 'context': context, 'state': action('inspect'), 'productionChanged': False}

    def snapshot():
        return json.loads(remote('/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py --snapshot').stdout)
    before = snapshot();initial = action('inspect');assert initial['basePath'] == '/hidden' and initial['nativeManifestSHA256'] == OLD and not initial['pending']
    checks = [];transitions = [];blog = None
    cases = [('', 'code'), ('/hidden', 'website'), ('', 'mount-authority'), ('/hidden', 'hosting-common.py'), ('', 'hosting-applied'), ('/hidden', 'committed'), ('', 'receipt')]
    for base, fault in cases:
        planned = action('plan', targetBasePath=base, noticeSeconds=2 if not transitions else 0, websiteTarget=blog if base == '' else None)
        validated = action('validate', **planned);assert validated['status'] == 'site-cutover-prepared-readonly'
        prior = action('inspect');killed = action('apply', check=False, fault=fault, **planned)
        assert killed.returncode == 87, killed.stderr[-6000:]
        middle = action('inspect');assert 'site-cutover.json' in middle['pending']
        if fault in ('mount-authority', 'hosting-common.py', 'hosting-applied', 'committed'):
            assert 'maintenance.json' in middle['pending'] and middle['rootRevision'] == prior['rootRevision']+1
            for operation in ['start', 'renew']:
                denied = remote(shlex.join(['/srv/codi-network-fixture/venv/bin/python', '-I', '-B', NATIVE+'/scripts/manage-services.py', operation, '--config', CONFIG]), check=False)
                assert denied.returncode != 0
            checks.append('pending '+fault+' keeps ordinary native start/signing blocked')
        recovered = action('recover', **planned);after = action('inspect')
        assert recovered['status'] == 'site-cutover-completed' and recovered['dataRestored'] is False
        assert after['basePath'] == base and after['nativeManifestSHA256'] == PIN and not after['pending'] and after['rootRevision'] == after['rootFloor']
        if fault == 'receipt':assert after['rootRevision'] == middle['rootRevision']
        else:assert after['rootRevision'] == prior['rootRevision']+1
        if base == '':blog = recovered['website']['current']
        current = snapshot()
        for key in ['keysAndAccountDBSHA256', 'privateFixtureFileSHA256']:assert current[key] == before[key]
        for role, rows in before['usage'].items():
            counters = {(r[0], r[1]): r[2:] for r in current['usage'][role]}
            for row in rows:assert (row[0], row[1]) in counters and all(a >= b for a, b in zip(counters[(row[0], row[1])], row[2:]))
        assert current['worker']['active'] and current['worker']['kernelMatches'] and not current['worker']['guardFault']
        transitions.append({'fault': fault, 'before': prior, 'interrupted': middle, 'after': after, 'recovered': recovered})
        checks.append('actual '+fault+' death/recovery preserves keys/accounts/files/cookie and nondecreasing usage')
        (ROOT/'.build/checks/site-cutover-vm-progress.json').write_text(json.dumps({'checks': checks, 'transitions': transitions}, indent=2)+'\n')
    assert action('inspect')['basePath'] == ''
    cleanup = action('cleanup')
    return {'status': 'PASS', 'checks': checks, 'transitions': transitions, 'context': context,
            'initialRootRevision': initial['rootRevision'], 'finalRootRevision': after['rootRevision'],
            'cleanup': cleanup, 'productionChanged': False, 'dataRestored': False,
            'actualCodeWebsiteNativeAndCaddy': True, 'ordinaryPublicTLS': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--resume-prepared', action='store_true')
    args = parser.parse_args();result = {'status': 'FAIL'}
    try:result.update(run(args.prepare_only, args.resume_prepared))
    finally:
        result['sourceSHA256'] = sha(Path(__file__).read_bytes())
        output = ROOT/'.build/checks/site-cutover-vm-result.json'
        if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
        output.write_text(json.dumps(result, indent=2)+'\n');print(json.dumps(result, indent=2))
