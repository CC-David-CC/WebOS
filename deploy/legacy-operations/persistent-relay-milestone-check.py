#!/usr/bin/env python3
"""Bind the exact relay operator to actual services, recovery and browser proof."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / '.build/checks'
sys.path.insert(0, str(ROOT))
from origin_service.release import verify as verify_connected

spec = importlib.util.spec_from_file_location('relay_export', ROOT / 'scripts/export-relay-operator.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)
artifact = ROOT / '.build/relay-operators/persistent-turn-20261023-r2'
operator = exporter.verify(artifact)
assert operator['manifestSHA256'] == '53ad5058662dbb0113caf43b900bcb77cbfdf0923e62477f899abe006d56c52b'
names = ['persistent-relay-result.json', 'relay-operator-result.json', 'full-system-hidden-readonly-release-provisioned-private-turn-network-result.json', 'preview-touch-live-health-result.json', 'relay-certificate-result.json', 'coturn-runtime-result.json', 'webhost-private-relay-install-result.json', 'webhost-private-relay-health-result.json']
receipts = {name: json.loads((CHECKS / name).read_text()) for name in names}
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
for name, receipt in receipts.items():
    assert receipt['status'] == 'PASS', name
local, exported, full, live, certs, runtime, installed, health = [receipts[name] for name in names]
for receipt in [local, exported, certs]:
    for name, pin in receipt['sha256'].items():
        assert digest(ROOT / name) == pin, name
assert len(local['checks']) == 12 and not local['cleanupErrors'] and local['fixtureUnitsAndPrivateStateRemoved']
assert len(exported['checks']) == 7 and exported['fixtureRemoved']
assert len(certs['checks'])==8 and certs['fixtureUnitsAndStateRemoved'] and not certs['cleanupErrors']
assert certs['operatorManifestSHA256']==operator['manifestSHA256'] and certs['operatorFiles']==operator['files']
assert certs['refreshJobProperties']['CapabilityBoundingSet']=='cap_dac_read_search'
assert certs['timerProperties']['ActiveState']=='active' and not certs['enabledForBoot']
assert local['coturnRelease']=='4.18.0'
assert full['managedTurnNetwork'] and full['readOnlyReleaseEnforced'] and full['releaseAfterExecutionVerified']
assert verify_connected(Path(full['release']['directory'])) == full['release']
assert full['release']['manifestSHA256'] == 'dea2b7d770b3ddd8f9dc07282d1f5f2ca98c395469b7eee361c2bff4f3cc627e'
for flag in ['childrenReaped', 'stewardReaped', 'credentialFilesRemoved', 'disposableRuntimeRemoved', 'disposableRootAuthorityRemoved']:
    assert full[flag], flag
assert not full['cleanupErrors'] and full['privateTurnCleanup'] == {'removed': True, 'unitsRemoved': True, 'credentialsRemoved': True}
network = full['privateTurnNetwork']
assert network['status'] == 'PASS' and network['onlyLoopbackInterface'] and network['publicOrForwardedUdpPorts'] == []
metadata=json.loads((ROOT/'.build/tools/coturn-4.18.0-build-r1/runtime/runtime.json').read_text())
assert metadata['upstreamRelease']==network['coturnRelease']==local['coturnRelease']=='4.18.0'
assert metadata['files']['turnserver']['sha256']==network['coturnBinarySHA256']==local['coturnBinarySHA256']==digest(ROOT/'.build/tools/coturn-4.18.0-build-r1/runtime/turnserver')
assert network['probes'] == {'internetError': 101, 'hostIssuerError': 111, 'cannotReachHostOrInternet': True}
for name, pin in network['operatorSourceSHA256'].items():
    assert digest(ROOT / name) == pin == operator['files'][name]['sha256']
for name in ['scripts/full-system-check.py', 'scripts/tls-discovery-check.py', 'scripts/managed-private-turn-fixture.py', 'scripts/private-turn-fixture.py', 'scripts/prepare-tls-preview.py']:
    assert digest(ROOT / name) == full['sha256'][name], name
browser = full['browser']
for flag in ['bidirectionalRTC', 'separateRoomChatAndMoves', 'guestAndIdentityPreserved']:
    assert browser[flag], flag
assert browser['legalMoves'] == ['e4', 'e5', 'Nf3'] and browser['identityTrust'] == 'test-server'
assert len(browser['guestInternet']) == 2 and all(guest['pingReplies'] == 2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
assert browser['rootPolicyRenewal']['sameEstablishedPeerConnections'] and browser['stewardCrash']['sameProvisionedWorkerRecovered']
for witness in browser['witnesses']:
    assert witness['localCandidateType'] == witness['remoteCandidateType'] == 'relay' and witness['localRelayProtocol'] == 'tls'
    assert witness['privateRelayAllocations']
    for pair in witness['privateRelayAllocations']:
        assert pair['local'] == pair['remote'] == '127.0.0.2' and pair['localType'] == pair['remoteType'] == 'relay' and pair['relayProtocol'] == 'tls'
        assert 13500 <= pair['localPort'] <= 13627 and 13500 <= pair['remotePort'] <= 13627
assert live['onlineRoleRelease'] == '/srv/codi-connected/releases/f2fbd4d'
assert live['frontendManifestSHA256'] == 'd6b62247203795f680d549d8064a27c37f0ed12f25e3b8ead0b4b069eb4dbc4a'
assert len(live['siteResults']) == 9 and set(live['siteResults'].values()) == {'PASS'}
assert installed['operatorManifestSHA256']==health['operatorManifestSHA256']==operator['manifestSHA256']
assert installed['runtimeManifestSHA256']==health['runtimeManifestSHA256']=='69ce8817cef7b4a1d99a30be1d5548e92eb0bfeaa2ee6ae6fb165180a5ea4e4b'
assert installed['runtimeBinarySHA256']==metadata['files']['turnserver']['sha256']
assert health['installationReceiptSHA256']==digest(CHECKS/'webhost-private-relay-install-result.json')
assert health['checkerSHA256']==digest(ROOT/'scripts/webhost-relay-health.py')
assert installed['defaultTrustedTLS'] and installed['unauthenticatedAllocation401'] and installed['indexAndGuestCookieUnchanged'] and installed['nativeConfigUnchanged']
assert installed['processes']==health['processes']
assert health['scheduledCertificateJobActuallyTriggered'] and health['relayPidsUnchangedAfterScheduledJob'] and health['onlyLoopbackInterface']
assert health['namespaceProbes']=={'internetError':101,'hostIssuerError':111} and not health['normalUnitsEnabledForBoot']
assert installed['frontendSHA256']=={name:r['sha256'] for name,r in json.loads((CHECKS/'touch-frontend-activation-result.json').read_text())['frontendFiles'].items()}
assert installed['siteDomains']==list(live['siteResults'])
report = {'status': 'PASS', 'scope': 'Installed persistent private TURN: real systemd lifecycle/rotation/recovery, isolated relay/relay Chrome chat/chess/v86 and preserved live frontend. Browser integration uses the separately pinned profile9 native artifact, not a claim that every current frontend source ran in that fixture.', 'certificateJobAndTimerVerified':True, 'coturnRelease':network['coturnRelease'],'coturnBinarySHA256':network['coturnBinarySHA256'], 'operatorManifestSHA256': operator['manifestSHA256'], 'receipts': {name: digest(CHECKS / name) for name in names}, 'installedOnWebhost': True, 'publicTurnConfigured': health['publicTurnConfigured'], 'independentWanVerified': False, 'fullObjectiveComplete': False, 'checkerSHA256': digest(Path(__file__))}
(CHECKS / 'persistent-relay-milestone-result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
