#!/usr/bin/env python3
"""Run the complete automatic-neighbor fault scenario on the installed native18.

Uses real Chrome/v86 desktops and the VM's existing issuer, same-origin routes,
WSS and protected artifact; fixture SPKI only, not public/WAN or8k evidence.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import time

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def run(release):
    vm = module('neighbor_installed_vm', ROOT / 'scripts/upgrade-signin-native-vm.py')
    pin = hashlib.sha256((release / 'connected-release.json').read_bytes()).hexdigest()
    before = vm.runtime()
    assert before['manifestSHA256'] == pin
    installed = json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'))
    command = ['curl', '--fail', '--silent', '--insecure', '--pinnedpubkey', 'sha256//' + installed['fixtureSPKI']]
    index = vm.remote(shlex.join([*command, 'https://127.0.0.1:8443/']))
    assert index.encode() == (release / 'index.html').read_bytes()
    expected = json.loads((release / 'assets/desktop/network-release.json').read_bytes())
    graph = json.loads(vm.remote(shlex.join([*command, 'https://127.0.0.1:8443/assets/desktop/network-release.json'])))
    assert graph == expected and graph['version'] == 'codi-network-release/3' and graph['automaticNeighbors'] == 'codi-peer-introductions/1'
    suite = module('neighbor_installed_network', ROOT / 'scripts/mesh-neighbors-browser-check.py')
    result = suite.run(installed['publicOrigin'] + '/', installed['fixtureSPKI'])
    assert before == vm.runtime(), 'Browser test changed native runtime'
    result.update(nativeManifestSHA256=pin, actualSealedGraph=graph, fixtureSPKIOnly=True,
                  nativeRuntimeUnchanged=True, productionChanged=False, publicWANTested=False,
                  wrapperSourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        args.output.rename(args.output.with_name(args.output.stem + '-before-' + str(time.time_ns()) + '.json'))
    result = {'status': 'FAIL'}
    try:
        result.update(run(args.release.resolve()))
    finally:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'status': result['status'], 'checks': len(result.get('checks', [])), 'error': result.get('error'), 'cleanupErrors': result.get('cleanupErrors')}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
