#!/usr/bin/env python3
"""Bind private installed hosted-room recovery and browser/API acceptance.

No Rooms-drawer/P2P hosted integration, state-snapshot, replica, chess, WAN or8k
completion is inferred. The public native16 release is unchanged.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / '.build/checks'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    receipts, values = {}, {}
    expected = {
        'hosted-room-operator-vm': 15,
        'hosted-native-release-r2': 15,
        'hosted-native-browser-r1': 11,
        'hosted-native-vm-binding-recovery-r1': 14,
        'hosted-native-vm-mesh': 23,
        'hosted-native-source-core-r1': 38,
    }
    for stem, count in expected.items():
        path = CHECKS / (stem + '-result.json')
        value = json.loads(path.read_bytes())
        assert value['status'] == 'PASS' and len(value['checks']) == count, stem
        receipts[path.name] = digest(path)
        values[stem] = value
    for stem in ['hosted-native-vm-upgrade', 'hosted-native-vm-binding',
                 'hosted-native-vm-ingress', 'hosted-native-final-health-r1']:
        path = CHECKS / (stem + '-result.json')
        value = json.loads(path.read_bytes())
        assert value['status'] == 'PASS', stem
        receipts[path.name] = digest(path)
        values[stem] = value
    release = ROOT / '.build/releases/connected-hosted-native-r2'
    manifest = json.loads((release / 'connected-release.json').read_bytes())
    assert manifest['version'] == 'codi-connected-development/19' and len(manifest['files']) == 468
    for name, record in manifest['files'].items():
        path = release / name
        assert path.is_file() and not path.is_symlink()
        assert record == {'bytes': path.stat().st_size, 'sha256': digest(path)}, name
    pin = digest(release / 'connected-release.json')
    health = values['hosted-native-final-health-r1']
    recovery = values['hosted-native-vm-binding-recovery-r1']
    browser = values['hosted-native-browser-r1']
    mesh = values['hosted-native-vm-mesh']
    assert health['runtime']['manifestSHA256'] == recovery['nativeManifestSHA256'] == mesh['nativeManifestSHA256'] == pin
    assert health['roomState']['rooms'] == recovery['workerState']['rooms']
    assert health['roomState']['replayFloors'] == recovery['workerState']['replayFloors']
    assert browser['acceptedRecords'] == 2 and browser['ownedAccountPolicy']['disabled']
    assert recovery['operatorDeaths'] == 4 and recovery['actualNativeRollbackAndReupgrade']
    assert recovery['nativeKeysAccountsCookieFilesAndFloorsPreserved']
    assert mesh['automaticIntroductionsEnabled'] and mesh['leasedMembershipEnabled']
    assert health['ownedBrowserContextsRemaining'] == 0 and not health['pendingJournals']
    assert health['defaultPublicTLS'] and not health['productionChanged']
    for account in health['ownedAccounts']:
        assert account['disabled'] and account['remainingFiles'] == 0
    core = values['hosted-native-source-core-r1']
    assert not core['sourceChangedDuringTest']
    for name, expected_pin in core['sourceSHA256'].items():
        assert digest(ROOT / name) == expected_pin, name
    return dict(status='PASS', scope=__doc__, receiptSHA256=receipts,
                nativeManifestSHA256=pin, declaredReleaseFiles=468, nativeRuntime=health['runtime'],
                installedServiceLifecycleChecks=15, installedNonemptyHistoryRecoveryChecks=14,
                directBrowserAPIChecks=11, actualV86DesktopMeshChecks=23, sourceCoreChecks=38,
                ownedBrowserContextsRemaining=0, ownedQAAccountsDisabledAndEmpty=len(health['ownedAccounts']),
                browserAPISourceCommit=recovery['committedFixtureSource'],
                productionChanged=False, publicNativeVersion=16, installedPrivateNativeVersion=19,
                hostedRoomsDrawerIntegrated=False, hostedP2PTransportIntegrated=False,
                materializedStateSnapshotsImplemented=False, replicatedFailoverImplemented=False,
                hostedChessImplemented=False, actual8kNetworkTested=False, normalPublicHostedWANTested=False,
                terminalDocumentsLifecycleAccountRegressionOnNative19Pending=True,
                wholeGoalComplete=False, sourceSHA256=digest(Path(__file__)))


if __name__ == '__main__':
    out = CHECKS / 'hosted-native-milestone-r1-result.json'
    assert not out.exists(), 'Preserve earlier evidence'
    value = run()
    out.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(value, indent=2))
