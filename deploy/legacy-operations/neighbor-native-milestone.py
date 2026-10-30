#!/usr/bin/env python3
"""Bind the native18 private-VM proof without claiming public or scale acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / '.build/checks'
RELEASE = ROOT / '.build/releases/connected-neighbor-native-r1'
PIN = '5ee491cc01f314580ec85ccf940f9e6e1944159c1a29e907e66dd738283fd024'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    assert digest(RELEASE / 'connected-release.json') == PIN
    manifest = json.loads((RELEASE / 'connected-release.json').read_bytes())
    assert manifest['version'] == 'codi-connected-development/18'
    expected = {'release': 23, 'vm-network': 19, 'vm-mesh': 23,
                'vm-terminal': 38, 'vm-documents': 19, 'vm-lifecycle': 13,
                'vm-accounts': 35, 'vm-rollout': 4, 'vm-production-code-rollback': 4,
                'vm-custody': 2, 'vm-mesh-after-rollout': 23,
                'rollout-floor-contract': 9}
    names = list(expected) + ['vm-upgrade', 'vm-voice', 'reproducibility',
                             'failed-account-file-cleanup', 'final-fixture-health']
    receipts, hashes = {}, {}
    for name in names:
        path = CHECKS / ('neighbor-native-' + name + '-result.json')
        value = json.loads(path.read_bytes())
        assert value['status'] == 'PASS', name
        if name in expected:
            assert len(value['checks']) == expected[name], name
        if 'nativeManifestSHA256' in value:
            assert value['nativeManifestSHA256'] == PIN, name
        assert value.get('productionChanged', False) is False, name
        receipts[name] = value
        hashes[path.name] = digest(path)
    assert receipts['vm-network']['actualLinuxGuests'] == 10
    assert receipts['vm-network']['ownedBrowserContextsClosed'] == 10
    assert receipts['vm-network']['actualV86Tested']
    assert receipts['vm-network']['nativeRuntimeUnchanged']
    assert receipts['vm-mesh']['actualV86Desktops'] == 3
    assert receipts['vm-accounts']['ownedFixtureLedger']['ownedFilesRemoved']
    assert receipts['failed-account-file-cleanup']['fileRemoved']
    assert receipts['reproducibility']['allBytesIdentical']
    assert receipts['reproducibility']['manifestSHA256'] == PIN
    voice = receipts['vm-voice']
    assert voice['actualLocalWhisperWasmInference'] and not voice['audioUploaded']
    spec = importlib.util.spec_from_file_location('neighbor_milestone_rollout', ROOT / 'scripts/mesh-native-vm-rollout-check.py')
    rollout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rollout)
    for name in ['vm-rollout', 'vm-production-code-rollback']:
        assert not receipts[name]['dataRestored']
        rollout.retained_durable(receipts[name]['durableBefore'], receipts[name]['durableAfter'])
    assert receipts['rollout-floor-contract']['contractSHA256'] == digest(ROOT / 'scripts/mesh-native-vm-rollout-check.py')
    assert receipts['vm-rollout']['rollbackManifestSHA256'].startswith('8a90a16e')
    assert receipts['vm-production-code-rollback']['rollbackManifestSHA256'].startswith('c23b1b73')
    health = receipts['final-fixture-health']
    assert health['runtime']['manifestSHA256'] == PIN and not health['pendingJournals']
    assert health['ownedBrowserContextsRemaining'] == 0
    assert all(x['disabled'] and x['remainingFiles'] == 0 for x in health['ownedAccounts'])
    # Source pins describe the precise fixtures, not a substitute for the sealed graph.
    for path, pin in receipts['vm-network']['sourceSHA256'].items():
        assert digest(ROOT / path) == pin, path
    for path, pin in voice['sha256'].items():
        assert digest(ROOT / path) == pin, path
    return {'status': 'PASS', 'scope': __doc__, 'nativeManifestSHA256': PIN,
            'declaredReleaseFiles': 424, 'checkCounts': expected, 'receiptSHA256': hashes,
            'actualLinuxGuestsInNetworkFaultScenario': 10,
            'actualCPUWhisperTested': True, 'byteIdenticalRebuild': True,
            'ownedQAAccountsDisabledAndEmpty': len(health['ownedAccounts']),
            'ownedBrowserContextsRemaining': 0, 'productionChanged': False,
            'publicWANProfile3Tested': False, 'actual8kTested': False,
            'durableCheckpointSyncImplemented': False, 'wholeGoalComplete': False,
            'sourceSHA256': digest(Path(__file__))}


if __name__ == '__main__':
    result = run()
    output = CHECKS / 'neighbor-native-milestone-result.json'
    assert not output.exists(), 'Preserve existing evidence; select another version'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
