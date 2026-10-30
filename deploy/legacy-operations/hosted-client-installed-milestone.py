#!/usr/bin/env python3
"""Bind native20 private full-desktop and actual-tab acceptance, not production/8k."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / '.build/checks'
PIN = '1d520e96ba5a7778ee6b43d472fc1ab8abb32b2a4ded612a610e775353f1d54d'
WORKER = '3907eac6785bc4ad6ca02436949539d0d06de9cdbf78b51f0b96e2d40d6a7a85'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    receipts = {}
    def load(stem, status='PASS'):
        path = CHECKS / (stem + '-result.json')
        value = json.loads(path.read_bytes())
        if status is not None:
            assert value['status'] == status, stem
        receipts[path.name] = digest(path)
        return value
    source = load('hosted-client-source-r5')
    assert len(source['checks']) == 26 and not source['sourceChangedDuringTest']
    assert source['actualPageReload'] and source['creationRetriesDidNotDuplicateRooms']
    assert source['exactCommittedMessageCount'] == 4 and source['ownedBrowserContextsClosed'] == 1
    for name, pin in source['sourceSHA256'].items():
        assert digest(ROOT.parent / name) == pin, name
    control = load('hosted-client-floor-control-r3', 'FAIL')
    assert not control['sourceChangedDuringTest'] and control['ownedBrowserContextsClosed'] == 1
    assert len(control['phaseOne']['checks']) == 9 and len(control['phaseTwo']['checks']) == 8
    assert 'atomic browser storage refuses a stale tab' in control['error']
    retired = load('hosted-client-retire-before-r1', 'FAIL')
    assert len(retired['phaseOne']['checks']) == 7 and retired['ownedBrowserContextsClosed'] == 1
    assert 'throwing retire callback cannot prevent' in retired['error']
    archive_before = load('hosted-native-browser-archive-before-r1', 'FAIL')
    assert len(archive_before['checks']) == 14 and archive_before['ownedAccountPolicy']['disabled']
    assert archive_before['error'] == 'sign-out retains the unsent saved-chat draft in the read-only identity archive'
    native = load('hosted-client-native-release-r4')
    assert len(native['checks']) == 15 and native['manifestSHA256'] == PIN
    assert native['sourceSHA256'] == digest(ROOT / 'scripts/hosted-client-native-check.py')
    assert native['networkModules'] == 37 and native['nativeFiles'] == 57
    for stem in ['hosted-client-native-repro-r4', 'hosted-client-native-app-compose-r4']:
        value = load(stem, None)
        assert value['manifestSHA256'] == PIN and value['files'] == 519
    scope = load('hosted-client-native-archive-scope-r1')
    assert scope['newManifestSHA256'] == PIN and scope['changedCoreModules'] == ['app.js']
    assert scope['all37NetworkModulesUnchanged'] and scope['all57NativeFilesUnchanged']
    assert scope['sameAppCatalogAndRoomBundle']
    mesh = load('hosted-client-native-vm-mesh-r1')
    assert len(mesh['checks']) == 23 and mesh['nativeManifestSHA256'] == scope['oldManifestSHA256']
    assert all(a['disabled'] for a in mesh['ownedTestAccountsDisabled'])
    worker = load('hosted-client-worker-vm-r2')
    assert worker['workerManifestSHA256'] == WORKER and worker['allPriorKeysAccountsCookieFilesFloorsAndUsagePreserved']
    assert not worker['productionChanged'] and not worker['dataRestored']
    upgrade = load('hosted-client-native-vm-upgrade-r2')
    assert upgrade['nativeManifestSHA256'] == PIN and upgrade['actualManagedCodeUpgrade']
    assert upgrade['keysAccountsCookieFilesAndCountersPreserved'] and not upgrade['liveWebhostChanged']
    ui = load('hosted-native-browser-client-ui-r3')
    assert ui['nativeManifestSHA256'] == PIN and len(ui['checks']) == 17
    assert ui['sourceSHA256'] == digest(ROOT / 'scripts/hosted-native-ui-check.py')
    assert archive_before['sourceSHA256'] == ui['sourceSHA256']
    assert ui['actualPageReload'] and ui['fullRoomsReopenCycles'] == 12
    assert ui['workspaceDOMAndDraftsPreserved'] and ui['acceptedRecordsInOwnedRoom'] == 2
    assert ui['ownedBrowserContextsClosed'] == 1 and ui['ownedAccountPolicy']['disabled']
    tabs = load('hosted-native-browser-tabs-r2')
    assert tabs['nativeManifestSHA256'] == PIN and len(tabs['checks']) == 9
    assert tabs['sourceSHA256'] == digest(ROOT / 'scripts/hosted-native-tabs-check.py')
    assert tabs['actualConcurrentTabs'] == tabs['actualV86Desktops'] == 2
    assert tabs['genuineDelayedSnapshot'] and tabs['sharedAccountFloorNeverRegressed']
    assert tabs['acceptedRecordsInOwnedRoom'] == 3 and tabs['ownedAccountPolicy']['disabled']
    assert tabs['ownedBrowserContextsClosed'] == 1 and tabs['ownedTabsClosed'] == 2
    health = load('hosted-client-installed-final-health-r1')
    assert health['runtime'] == upgrade['runtime']
    assert health['ownedBrowserContextsRemaining'] == 0 and not health['pendingJournals']
    assert health['roomHealth']['status'] == 'PASS' and health['defaultPublicTLS']
    assert health['roomHealth']['privateNetworkNamespace'] and health['roomHealth']['emptyCapabilities']
    assert not health['roomHealth']['bootEnabled']
    assert not health['productionChanged']
    for suite in [ui, tabs]:
        assert any(a['subject'] == suite['subject'] and a['disabled'] and a['remainingFiles'] == 0
                   for a in health['ownedAccounts'])
    release = ROOT / '.build/releases/connected-hosted-client-native-r4'
    assert digest(release / 'connected-release.json') == PIN
    return dict(status='PASS', scope=__doc__, nativeManifestSHA256=PIN,
                privateWorkerManifestSHA256=WORKER, privateNative20Installed=True,
                componentBrowserChecks=26, fullDesktopBrowserChecks=17,
                actualConcurrentTabChecks=9, actualConcurrentV86Desktops=2,
                staleActualTabSnapshotRefused=True, unsentSignOutDraftArchivedReadOnly=True,
                priorArtifactMeshChecks=23, meshProtocolBytesUnchanged=True,
                nativeReleaseChecks=15, exactRebuildFiles=519,
                ownedBrowserContextsRemaining=0, productionChanged=False,
                sharedHostedClientLiveInProduction=False, P2PHostedDeliveryImplemented=False,
                hostedChessStateImplemented=False, actual8kNetworkTested=False,
                physicalPhoneTested=False, wholeGoalComplete=False,
                receiptSHA256=receipts, sourceSHA256=digest(Path(__file__)))

if __name__ == '__main__':
    output = CHECKS / 'hosted-client-installed-milestone-r1-result.json'
    assert not output.exists(), 'Preserve prior evidence'
    value = run()
    output.write_text(json.dumps(value, indent=2) + '\n')
    print(json.dumps(value, indent=2))
