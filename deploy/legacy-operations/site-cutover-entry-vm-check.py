#!/usr/bin/env python3
"""Run the sealed CLI itself against real VM backends and noisy hosting commands."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
ENTRY = r'''
import hashlib,importlib.util,json,pathlib,runpy,subprocess,sys
P=pathlib.Path;v=json.load(sys.stdin);sys.path[:0]=[v['operator'],v['mount'],'/srv/codi-network-fixture/candidate-c23b1b73df68ffb2']
assert hashlib.sha256(P(v['driver']).read_bytes()).hexdigest()==v['driverSHA256']
s=importlib.util.spec_from_file_location('owned_site_cli_fixture',v['driver']);fixture=importlib.util.module_from_spec(s);s.loader.exec_module(fixture)
import site_cutover.managed as managed
Driver=fixture.fixture_class(managed.Managed,managed.records,managed.read);Driver.binary=P(v['binary']);original=Driver.apply_caddy
def noisy(self,data):
 original(self,data)
 subprocess.run(['/usr/bin/printf','fixture Caddy fd1 output\n'],check=True)
 print('fixture buffered Python output')
Driver.apply_caddy=noisy;managed.Managed=Driver
script=P(v['operator'])/'scripts/site-cutover.py'
sys.argv=[str(script),v['operation'],'--plan',v['plan'],'--plan-sha256',v['planSHA256'],'--operator-sha256',v['operatorSHA256']]
runpy.run_path(str(script),run_name='__main__')
'''


def run():
    spec = importlib.util.spec_from_file_location('entry_vm', ROOT/'scripts/prepare-native-network-vm.py')
    vm = importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
    cp = ROOT/'.build/checks/site-cutover-vm-context.json';previous = json.loads(cp.read_text())
    exported = json.loads((ROOT/'.build/checks/site-cutover-operator-r3-export-result.json').read_text());key = exported['manifestSHA256'];folder = Path(exported['directory'])
    context = {**previous, 'operator': '/srv/codi-site-fixture/operator-'+key, 'operatorSHA256': key}
    stage = r'''import json,pathlib,sys
P=pathlib.Path;v=json.load(sys.stdin);folder=P(v['folder']);assert not folder.exists();folder.mkdir(mode=0o755)
for n,raw in v['files'].items():
 p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw);p.chmod(0o644)
print('staged')'''
    r = subprocess.run([*vm.ssh_args(), '/usr/bin/python3 -I -B -c '+shlex.quote(stage)],
                       input=json.dumps({'folder': context['operator'], 'files': {str(p.relative_to(folder)): p.read_text() for p in folder.rglob('*') if p.is_file()}}), capture_output=True, text=True, timeout=30)
    if r.returncode:raise ValueError(r.stderr[-4000:])
    cp.with_name('site-cutover-vm-context-before-entry-test.json').write_text(json.dumps(previous, indent=2)+'\n');cp.write_text(json.dumps(context, indent=2)+'\n')

    def action(name, **fields):
        r = subprocess.run([*vm.ssh_args(), '/srv/codi-network-fixture/venv/bin/python -I -B '+shlex.quote(context['driver'])],
                           input=json.dumps({**context, 'action': name, **fields}), capture_output=True, text=True, timeout=300)
        if r.returncode:raise ValueError(r.stderr[-5000:])
        return json.loads(r.stdout)

    def snapshot():
        r = subprocess.run([*vm.ssh_args(), '/srv/codi-network-fixture/venv/bin/python -I -B /srv/codi-network-fixture/tools/native-network-vm-lifecycle-check.py --snapshot'], capture_output=True, text=True, timeout=60)
        if r.returncode:raise ValueError(r.stderr[-3000:])
        return json.loads(r.stdout)

    initial = action('inspect');assert initial['basePath'] == '' and initial['rootRevision'] == 22 and not initial['pending']
    saved = snapshot();action('resume-runtime');blog = Path(initial['website']).name;results = []
    for base in ['/hidden', '']:
        plan = action('plan', targetBasePath=base, websiteTarget=blog if base == '' else None)
        receipts = {}
        for operation in ['plan', 'apply']:
            payload = {**context, **plan, 'operation': operation}
            r = subprocess.run([*vm.ssh_args(), '/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(ENTRY)],
                               input=json.dumps(payload), capture_output=True, text=True, timeout=300)
            diagnostic = ROOT/'.build/checks'/('site-cutover-entry-'+('root' if base == '' else 'hidden')+'-'+operation+'.log')
            diagnostic.write_text(r.stdout+'\nSTDERR\n'+r.stderr)
            if r.returncode:raise ValueError(r.stderr[-5000:] or r.stdout[-3000:])
            value = json.loads(r.stdout)
            if operation == 'apply':
                assert value['status'] == 'site-cutover-completed' and 'fixture Caddy fd1 output' in r.stderr and 'fixture buffered Python output' in r.stderr
                assert 'fixture Caddy' not in r.stdout and 'fixture buffered' not in r.stdout
            else:assert value['status'] == 'site-cutover-prepared-readonly'
            receipts[operation] = value
        current = action('inspect');assert current['basePath'] == base and not current['pending']
        results.append({'basePath': base, 'state': current, 'receipts': receipts})
    after = snapshot()
    for name in ['keysAndAccountDBSHA256', 'privateFixtureFileSHA256']:assert saved[name] == after[name]
    cleanup = action('cleanup')
    return {'status': 'PASS', 'operatorSHA256': key, 'context': context, 'transitions': results,
            'checks': ['sealed CLI readonly and actual inverse/apply at hidden', 'sealed CLI readonly and actual apply at root',
                       'fd1 subprocess and buffered Python logs go to stderr; stdout is one JSON receipt',
                       'existing keys/accounts/cookie/private files unchanged; no pending journals'],
            'initialRootRevision': 22, 'finalRootRevision': current['rootRevision'], 'cleanup': cleanup,
            'fixtureAdaptersExplicit': True, 'ordinaryPublicTLS': False, 'productionChanged': False}


if __name__ == '__main__':
    result = {'status': 'FAIL'}
    try:result.update(run())
    finally:
        result['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        p = ROOT/'.build/checks/site-cutover-entry-vm-result.json'
        if p.exists():p.rename(p.with_name(p.stem+'-before-'+str(time.time_ns())+'.json'))
        p.write_text(json.dumps(result, indent=2)+'\n');print(json.dumps(result, indent=2))
