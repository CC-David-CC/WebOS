#!/usr/bin/env python3
"""Retest real inverse/recovery with fresh CLI import paths after production refusal."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent


def run():
    spec = importlib.util.spec_from_file_location('site_import_vm', ROOT/'scripts/prepare-native-network-vm.py')
    vm = importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
    context_file = ROOT/'.build/checks/site-cutover-vm-context.json'
    before = json.loads(context_file.read_text())
    export = json.loads((ROOT/'.build/checks/site-cutover-operator-r2-export-result.json').read_text())
    source = Path(export['directory']);key = export['manifestSHA256']
    helper = (ROOT/'scripts/site-cutover-vm-driver.py').read_text();helper_key = hashlib.sha256(helper.encode()).hexdigest()
    context = {**before, 'operator': '/srv/codi-site-fixture/operator-'+key, 'operatorSHA256': key,
               'driver': '/srv/codi-site-fixture/driver-'+helper_key+'.py', 'driverSHA256': helper_key}
    code = r'''import hashlib,json,pathlib,sys
P=pathlib.Path;v=json.load(sys.stdin);folder=P(v['folder']);assert not folder.exists();folder.mkdir(mode=0o755)
for n,raw in v['files'].items():
 p=folder/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(raw);p.chmod(0o644)
helper=P(v['driver']);assert not helper.exists();helper.write_text(v['helper']);helper.chmod(0o644)
print(json.dumps({'operator':str(folder),'driver':str(helper)}))'''
    files = {str(p.relative_to(source)): p.read_text() for p in source.rglob('*') if p.is_file()}
    stage = subprocess.run([*vm.ssh_args(), '/usr/bin/python3 -I -B -c '+shlex.quote(code)],
                           input=json.dumps({'folder': context['operator'], 'files': files, 'driver': context['driver'], 'helper': helper}), capture_output=True, text=True, timeout=30)
    if stage.returncode:raise ValueError(stage.stderr[-4000:])
    context_file.with_name('site-cutover-vm-context-before-import-fix.json').write_text(json.dumps(before, indent=2)+'\n')
    context_file.write_text(json.dumps(context, indent=2)+'\n')

    def action(name, check=True, **fields):
        payload = {**context, 'action': name, **fields}
        r = subprocess.run([*vm.ssh_args(), '/srv/codi-network-fixture/venv/bin/python -I -B '+shlex.quote(context['driver'])],
                           input=json.dumps(payload), capture_output=True, text=True, timeout=300)
        if check and r.returncode:raise ValueError(r.stderr[-6000:] or r.stdout[-3000:])
        return json.loads(r.stdout) if check else r

    initial = action('inspect');assert initial['basePath'] == '' and initial['rootRevision'] == 20 and not initial['pending']
    action('resume-runtime')
    blog = Path(initial['website']).name
    checks = [];transitions = []
    for base, fault in [('/hidden', 'hosting-common.py'), ('', 'receipt')]:
        plan = action('plan', targetBasePath=base, websiteTarget=blog if base == '' else None)
        # Driver asserts no hosting helper directory is pre-injected here.
        validated = action('validate', **plan);assert validated['status'] == 'site-cutover-prepared-readonly'
        prior = action('inspect');killed = action('apply', check=False, fault=fault, **plan)
        assert killed.returncode == 87, killed.stderr[-4000:]
        middle = action('inspect');assert middle['rootRevision'] == prior['rootRevision']+1
        recovered = action('recover', **plan);after = action('inspect')
        assert after['basePath'] == base and after['rootRevision'] == middle['rootRevision'] and after['rootFloor'] == after['rootRevision'] and not after['pending']
        checks.append('fresh CLI paths: actual '+fault+' inverse/recovery without another root mint')
        transitions.append({'fault': fault, 'plan': plan, 'before': prior, 'middle': middle, 'after': after, 'result': recovered})
    cleanup = action('cleanup')
    return {'status': 'PASS', 'checks': checks, 'transitions': transitions, 'context': context,
            'initialRootRevision': 20, 'finalRootRevision': after['rootRevision'], 'cleanup': cleanup,
            'freshCLIImportPathsTested': True, 'productionChanged': False, 'dataRestored': False}


if __name__ == '__main__':
    result = {'status': 'FAIL'}
    try:result.update(run())
    finally:
        result['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        path = ROOT/'.build/checks/site-cutover-import-vm-result.json'
        if path.exists():path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
        path.write_text(json.dumps(result, indent=2)+'\n');print(json.dumps(result, indent=2))
