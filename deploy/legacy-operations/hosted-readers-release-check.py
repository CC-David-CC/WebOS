#!/usr/bin/env python3
"""Check closed native22 graph, historical contracts, retained bytes and refusals."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'.build/releases/connected-hosted-window-native-r1'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(candidate, rebuilt):
    checks = []

    def check(name, ok):
        assert ok, name
        checks.append(name)

    contract = load('reader_release_current', candidate/'origin_service/release.py')
    old = load('reader_release_previous', BASE/'origin_service/release.py')
    verified = contract.verify(candidate)
    check('native22 verifies the sealed candidate manifest', json.loads((candidate/'connected-release.json').read_bytes())['version'] == 'codi-connected-development/22')
    check('new validator still accepts the current live native21 artifact', contract.verify(BASE)['manifestSHA256'] == 'a5d5a90767f4d8cc68054470a39394853835670bdc8decd11ad4afe3f9ae0d07')
    try:
        old.verify(candidate)
        raise AssertionError('Old native21 validator accepted profile22')
    except ValueError:
        checks.append('old native21 validator refuses the unknown native22 profile')
    historical = lambda path: {n.name: ast.dump(n) for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name != 'verify'}
    before, after = historical(BASE/'origin_service/release.py'), historical(candidate/'origin_service/release.py')
    check('all preexisting profile verification functions are unchanged', all(after.get(name) == value for name, value in before.items()))
    a, b = json.loads((BASE/'connected-release.json').read_bytes()), json.loads((candidate/'connected-release.json').read_bytes())
    allowed = {'origin_service/release.py', 'origin_service/deployment.py', 'origin_service/turn_management.py', 'scripts/manage-services.py'}
    changed = {n for n in old.V19_NATIVE if a['files'][n] != b['files'][n]}
    check('only the four explicit profile validators change among57 native files', changed == allowed)
    check('all existing application bundles remain byte-identical', all(b['files'][n] == value for n, value in a['files'].items() if '/apps/' in n))
    check('independent rebuild has the same manifest and every declared byte', (candidate/'connected-release.json').read_bytes() == (rebuilt/'connected-release.json').read_bytes() and all((candidate/n).read_bytes() == (rebuilt/n).read_bytes() for n in b['files']))
    graph = json.loads((candidate/'assets/desktop/network-release.json').read_bytes())
    check('reader organization is an explicit exact closed39-module graph', graph['readerOrganization'] == 'codi-hosted-readers/1' and len(graph['modules']) == 39 and 'hosted-reader-peers.mjs' in graph['modules'])
    check('the desktop opts into reader organization on the existing shared pool', 'stateWindows:true,readerOrganization:true' in (candidate/graph['coreDirectory']/'networking.js').read_text())
    frontend = json.loads((candidate/'release.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='codi-reader-graph-refusal-') as folder:
        copied = Path(folder)/'release'
        shutil.copytree(candidate, copied)
        path = copied/'assets/desktop/network-release.json'
        for name, mutate in [
            ('unsupported reader protocol', lambda g: g.update(readerOrganization='unknown/1')),
            ('missing reader module', lambda g: g['modules'].pop('hosted-reader-peers.mjs')),
            ('extra unreviewed module', lambda g: g['modules'].update({'unknown.mjs': g['modules']['peer.mjs']})),
            ('wrong network directory', lambda g: g.update(directory='../private')),
            ('wrong graph version', lambda g: g.update(version='codi-network-release/6')),
        ]:
            altered = json.loads(json.dumps(graph))
            mutate(altered)
            path.write_text(json.dumps(altered))
            try:
                contract.verify_hosted_readers_graph(copied, frontend)
                raise AssertionError('Accepted '+name)
            except ValueError:
                checks.append('closed graph refuses '+name)
    return dict(status='PASS', checks=checks, manifestSHA256=verified['manifestSHA256'], installed=False, privateVMChanged=False, productionChanged=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--rebuilt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    try:
        result = run(args.release.resolve(), args.rebuilt.resolve())
    except Exception as error:
        import traceback
        result = dict(status='FAIL', error=str(error), traceback=traceback.format_exc())
    result['sourceSHA256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), ROOT/'scripts/build-hosted-readers-native.py']}
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
