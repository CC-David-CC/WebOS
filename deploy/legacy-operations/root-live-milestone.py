#!/usr/bin/env python3
"""Bind actual root deployment/browser/WAN receipts, without closing the full goal."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT/'.build/checks'
PIN = 'c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1'


def run():
    evidence = {}

    def receipt(name, status='PASS'):
        raw = (CHECKS/name).read_bytes();value = json.loads(raw)
        assert value['status'] == status, name
        evidence[name] = hashlib.sha256(raw).hexdigest()
        return value

    apply = receipt('site-cutover-production-apply-result.json', 'site-cutover-completed')
    assert apply['basePath'] == '' and apply['mount']['rootRevision'] == 3 and not apply['dataRestored'] and not apply['workSaved']
    health = receipt('root-live-health-result.json')
    assert health['nativeManifestSHA256'] == PIN and health['basePath'] == '' and health['rootRevision'] == 3
    assert health['existingAccountsPreserved'] == 35 and health['keysRealmServiceIdentityUnchanged'] and health['noPendingJournals']
    assert health['prototypeFilesVerified'] == 133 and health['prototypeBackendFree'] and health['all10SiteSmoke'] == 'PASS' and health['rootBranchTestedByLiveSmoke']
    for kind, count in [('terminal', 38), ('documents', 19), ('lifecycle', 13)]:
        result = receipt('root-public-'+kind+'-result.json')
        assert len(result['checks']) == count and result['defaultPublicTLS'] and result['releaseSHA256'] == PIN and result['basePath'] == ''
        if kind == 'lifecycle':
            assert result['ordinaryOpensAndCloses'] == 182 and all(s['resources'] == result['samples'][0]['resources'] and s['budget'] == result['samples'][0]['budget'] for s in result['samples'])
    cache = receipt('root-public-cache-result.json')
    assert len(cache['checks']) == 11 and cache['defaultPublicTLS'] and cache['releaseSHA256'] == PIN and cache['rebuildAfterSiteDataClear']
    assert not cache['runningVMWasSaved'] and not cache['offlineReloadRestoresVM'] and not cache['userFilesOrCredentialsCached']
    account = receipt('root-public-account-result.json')
    assert len(account['checks']) == 20 and account['nativeManifestSHA256'] == PIN and account['basePath'] == '' and account['defaultCertificateTrust']
    assert account['allAnonymousGuestInternetDenied'] and account['liveRegisteredOwnWANAndAnonymousDenyVerified'] and account['generatedPrivateFileRemoved'] and account['generatedAccountDisabled']
    cleanup = receipt('root-document-public-cleanup-result.json')
    assert cleanup['otherAccountPoliciesUnchanged'] and all(a['disabled'] and a['homeEmpty'] for a in cleanup['accounts'])
    for kind, count in [('group', 36), ('history', 23), ('scope', None)]:
        value = receipt('root-wan-'+kind+'-result.json')
        assert value['basePath'] == '' and value['nativeManifestSHA256'] == PIN and value['publicTLSValidation'] and value['independentWANVerified'] and value['actualBrowserContexts'] == 3 and not value['HTTPChatRelayUsed']
        assert len(set(value['hosts'].values())) == 2 and {p['host'] for p in value['crossHostCandidatePairs']} == {'development', 'moonpie'}
        assert all(p['localType'] == p['remoteType'] == 'relay' and p['relayProtocol'] == 'tls' and p['turnURL'].startswith('turns:turn.ksu.codes:443') for p in value['crossHostCandidatePairs'])
        if count is not None:assert len(value['checks']) == count
        else:
            for key in ['validOriginCannotBeTransplantedBetweenTwoAdmittedGroups', 'rejectedScopeDidNotAdvanceOriginalReplayFloor', 'correctDestinationDeliversExactlyOnce', 'legacyUnnegotiatedRoutingRejectedBeforeDelivery', 'existingTwoPeerChatAndSeparateLegalChessOnSamePool', 'matchingLegacyPgnExcludesChat']:
                assert value[key], key
    outside = receipt('moonpie-root-cleanup-result.json')
    assert outside['driverStopped'] and outside['fixtureFolderRemoved'] and outside['forwardStopped']
    return {'status': 'PASS', 'scope': 'Root/blog publication and current bounded-system acceptance; full goal remains active',
            'nativeManifestSHA256': PIN, 'basePath': '', 'desktop': 'https://ksu.codes/', 'blog': 'https://ksu.codes/blog/',
            'evidenceSHA256': evidence, 'wholeGoalCompleted': False,
            'limits': {'network': 'fixed3..8member controller stars, maximum300second grants; full gossip/bridge failover not implemented',
                       'history': 'bounded recent signed repair, not durable chunk/checkpoint convergence',
                       'WAN': 'two public Internet egresses,3real browsers per suite; public TURN/TLS443 fallback, not8k capacity',
                       'memory': 'shared128MiB networking accounting default; not reserved or whole-browser/Linux/voice memory',
                       'persistence': 'explicit registered server saves persist; browser RAM/unsaved drafts are not automatically saved',
                       'operations': 'native units remain disabled for boot; bounded root3 delegation expires2026-10-25 11:06:16UTC; no auto-renewal'},
            'retainedFailure': 'First outside history startup reported Moonpie tab crashed; fresh repeat passes, cause unproven, original diagnostics/log retained',
            'requiredRemaining': ['complete request/package/roadmap audit', 'self-organizing partial meshes/islands/layers and bounded server fallback',
                                  'resumable content-addressed checkpoint/branch convergence and valid missed operations',
                                  'bounded cancellable browser PoW admission', 'two player roles with spectator chat',
                                  'actual staged solo through8k logical-channel load/fault/resource tests']}


if __name__ == '__main__':
    value = run()
    value['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (CHECKS/'root-live-milestone-result.json').write_text(json.dumps(value, indent=2)+'\n')
    print(json.dumps(value, indent=2))
