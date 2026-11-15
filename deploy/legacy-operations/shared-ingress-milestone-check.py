#!/usr/bin/env python3
"""Bind installed/public ingress, recovery and current desktop/relay proofs."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / '.build/checks'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


names = ['managed-ingress-result.json', 'shared-ingress-exercise-rollback-result.json',
         'shared-ingress-stage-recovery-test-result.json', 'shared-ingress-prepared-recover-result.json',
         'shared-ingress-recover-result.json', 'shared-ingress-apply-result.json',
         'public-ingress-result.json', 'webhost-private-relay-health-result.json',
         'preview-touch-live-health-result.json', 'touch-milestone-result.json',
         'speech-milestone-result.json', 'persistent-relay-milestone-result.json']
receipts = {name: json.loads((CHECKS / name).read_text()) for name in names}
for name, value in receipts.items():
    assert value['status'] == 'PASS', name
    for source, expected in value.get('sha256', {}).items():
        assert digest(ROOT / source) == expected, source
local, exercise, staged, prepared, committed, activation, public, relay, live, touch, speech, persistent = [receipts[name] for name in names]
controller = digest(ROOT / 'scripts/activate-shared-ingress.py')
for value in [exercise, staged, prepared, committed, activation]:
    assert value['controllerSHA256'] == controller
assert public['checkerSHA256'] == digest(ROOT / 'scripts/public-ingress-check.py')
assert local['rollback']['exactControllerRestoreFunctionExecuted']
assert {item['afterCutoverIngressRunning'] for item in local['rollback']['checks']} == {False, True}
assert all(item['oldListenerActuallyRestored'] and item['stagedUnitAndDependencyRemoved'] for item in local['rollback']['checks'])
assert local['rollback']['unrelatedHostingEditRefused']
assert local['installedFixtureUnitRemoved'] and local['protectedFixtureRuntimeRemoved'] and local['allChildrenReaped'] and local['disposableCaKeysRemoved']
assert len(local['websiteHosts']) == 9 and local['managedUnitSandbox']['uid'] > 0 and int(local['managedUnitSandbox']['capabilities'], 16) == 1024
assert exercise['unitAndDependencyRemoved'] and exercise['hostingAndNativeInputsUnchanged'] and exercise['indexAndGuestCookieUnchanged']
assert staged['pendingRecoveryRequired'] and prepared['action'] == 'prior-hosting-restored'
assert committed['action'] == 'committed-state-preserved' and {k: v for k, v in activation.items() if k != 'controllerSHA256'} == committed['activation']
candidate = ROOT / '.build/hosting/shared-ingress-20261023-r2/candidate'
for name, expected in activation['candidateFilesSHA256'].items():
    assert digest(candidate / name) == expected
runtime = ROOT / '.build/tools/haproxy-2.8.31-build-r1/runtime'
key = digest(runtime / 'runtime.json')
meta = json.loads((runtime / 'runtime.json').read_text())
assert key == activation['runtimeManifestSHA256'] == public['after']['runtimeManifestSHA256']
assert meta['builderSHA256'] == digest(ROOT / 'scripts/build-haproxy.py') and meta['upstreamRelease'] == local['haproxyRelease'] == '2.8.31'
for name, record in meta['files'].items():
    assert record == {'bytes': (runtime / name).stat().st_size, 'sha256': digest(runtime / name)}
assert meta['files']['haproxy']['sha256'] == activation['runtimeBinarySHA256'] == local['haproxyBinarySHA256']
assert activation['defaultTrustedTurnTLS'] and activation['publicUnauthenticatedAllocation401'] and activation['publicTurnListenerConfigured']
assert not activation['issuerTurnPolicyConfigured'] and not activation['routerFirewallAndPublicPortsChanged']
assert public['turn']['defaultTrustedTLS'] and public['turn']['unauthenticatedAllocation401'] and public['turn']['realm'] == 'turn.ksu.codes'
assert public['turn']['leafSHA256'] == relay['certificate']['leafSHA256']
assert public['acmeALPNRoutedToCaddy'] and public['publicH2Negotiated'] and public['prototypeAndHiddenAssetsPreserved']
assert public['before']['clientAddressFromProductionCaddyLog'] == '127.0.0.3'
for audit in [public['before'], public['after']]:
    assert audit['pid'] == activation['ingressPid'] and audit['uid'] == activation['ingressUID'] and audit['noNewPrivileges']
    assert audit['noPendingJournal'] and audit['caddyBackendsLoopbackOnly'] and audit['activationReceiptSHA256'] == live['hostingActivationReceiptSHA256']
assert set(public['websites']) == set(activation['siteDomains']) == set(live['siteResults']) and len(public['websites']) == 9
assert live['hostingSHA256'] == {'generator': activation['generatorSHA256'], 'manifest': activation['manifestSHA256'], 'activeCaddy': activation['activeCaddySHA256']}
assert live['sharedIngressConfigured'] and live['publicTurnListenerConfigured'] and not live['issuerTurnPolicyConfigured']
assert relay['publicTurnConfigured'] and relay['scheduledCertificateJobActuallyTriggered'] and persistent['installedOnWebhost']
assert touch['publicTurnConfigured'] and not touch['issuerTurnPolicyConfigured']
assert speech['frontendSourceCommit'] == '08c8af907a21f5805a317c6ad3d85c5a10a5908d'
assert not public['independentWanVerified'] and not public['actualCaChallengeIssuanceVerified']
result = {'status': 'PASS', 'scope': 'Installed/public shared80/443 ingress, real local rollback, webhost prepared/committed recovery, nine-site preservation and current public Chrome desktop/voice proof; authenticated public relay and independent WAN remain open',
          'verifiedAtUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'receipts': {name: digest(CHECKS / name) for name in names},
          'runtimeManifestSHA256': key, 'nativeRelease': live['onlineRoleRelease'],
          'publicTurnListenerConfigured': True, 'issuerTurnPolicyConfigured': False,
          'realWebhostUnitDependenciesVerified': True, 'actualMachineRebootVerified': False,
          'independentWanVerified': False, 'actualCaChallengeIssuanceVerified': False,
          'fullObjectiveComplete': False, 'checkerSHA256': digest(Path(__file__))}
(CHECKS / 'shared-ingress-milestone-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
