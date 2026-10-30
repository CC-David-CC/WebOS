#!/usr/bin/env python3
"""Compose opt-in receipt windows over the native21 graph; retain live apps/security."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT/'.build/releases/connected-hosted-peer-native-r4'
LIVE_PIN = '5ad8cefa2de56378b76fafdbdd3c35f4dfc738104d286577adcf8b6b6accd1b0'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def build(destination):
    assert hashlib.sha256((LIVE/'connected-release.json').read_bytes()).hexdigest() == LIVE_PIN
    destination = destination.resolve()
    builder = module('window_network_build', ROOT/'scripts/build-hosted-peer-native.py')
    network = builder.build(destination.with_name(destination.name+'-base'))
    apps = module('window_app_composition', ROOT/'scripts/build-native-app-update.py')
    composed = apps.build(ROOT/'.build/hosted-peer-app-assets-r1', destination, Path(network['directory']), network['manifestSHA256'])
    old = json.loads((LIVE/'assets/desktop/network-release.json').read_bytes())
    new = json.loads((destination/'assets/desktop/network-release.json').read_bytes())
    changed = [n for n in old['modules'] if old['modules'][n] != new['modules'][n]]
    assert set(changed) == {'hosted-peer-sync.mjs', 'hosted-room-authority.mjs', 'hosted-room-client.mjs', 'peer.mjs', 'peer-pool.mjs'}
    assert len(new['modules']) == 38 and old['core']['desktop-apps.js'] == new['core']['desktop-apps.js']
    contract = module('window_final_contract', destination/'origin_service/release.py')
    assert all((LIVE/n).read_bytes() == (destination/n).read_bytes() for n in contract.V19_NATIVE)
    before = json.loads((LIVE/'connected-release.json').read_bytes())['files']
    after = json.loads((destination/'connected-release.json').read_bytes())['files']
    assert all(before[n] == after[n] for n in before if '/apps/' in n)
    peer = (destination/new['directory']/'peer.mjs').read_text()
    networking = (destination/new['coreDirectory']/'networking.js').read_text()
    assert "'codi-hosted/1:state-window/1'" in peer and 'callbacks.hostedWindow=true' in networking and 'stateWindows:true' in networking
    return {'status': 'PASS', 'manifestSHA256': composed['manifestSHA256'], 'files': composed['files'], 'networkModules': 38, 'nativeFiles': 57, 'changedNetworkModules': changed, 'nativeBytesUnchangedFromLive': True, 'liveAppHostAndBundlesPreserved': True, 'negotiatedFeature': 'codi-hosted/1:state-window/1', 'baseManifestSHA256': network['manifestSHA256'], 'directory': str(destination), 'installed': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
