#!/usr/bin/env python3
"""Bind local guest-network identity, kernel sockets and QEMU wire evidence."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,expected in value.get('sha256',{}).items():assert sha(ROOT/path)==expected,path
    return value

if __name__=='__main__':
    names=['guest-authorization-result.json','guest-egress-kernel-result.json','guest-worker-result.json','guest-live-feature-off-result.json','webhost-files-preview-health-result.json','public-files-milestone-result.json']
    auth,kernel,worker,off,health,files=[load(name) for name in names]
    assert auth['tests']==28 and auth['failures']==auth['errors']==0
    assert kernel['fixtureNamespaceAndProcessesCleaned'] and not kernel['hostFirewallChanged'] and not kernel['liveWebhostChanged']
    assert kernel['policySHA256']==worker['policySHA256']
    for role,expected_uid in [('anonymous',60231),('registered',60232),('frontend',60233),('unrelated',60234)]:
        witness=kernel['actualKernelWitnesses'][role]
        assert witness['uid']==expected_uid and witness['effectiveCapabilities']==0 and witness['noNewPrivileges']
        for name in ['own_ping','own_http','own_https']:
            assert witness['results'][name]['ok']==(role in ('registered','unrelated'))
        for name in ['lan10','lan172','lan192','metadata','cgnat','ipv6_loopback']:
            assert witness['results'][name]['ok']==(role=='unrelated')
    assert kernel['actualNftCountersAdvanced'] and kernel['replyOnlyControlServersWork'] and kernel['unrelatedUIDUnchanged']
    assert worker['actualQEMU'] and not worker['externalTrafficTested'] and not worker['kernelWorkerIntegrationTested'] and not worker['livePreviewChanged']
    for name in ['anonymous own-WAN and LAN frames dropped before QEMU','anonymous grant cannot start registered QEMU','refresh retains actual QEMU process','same QEMU NIC works after live grant refresh','different account cannot inherit an established registered wire','lease expiry reaps QEMU and established wire','all actual QEMU children and worker slots cleaned']:
        assert name in worker['checks'],name
    assert off['newGuestAuthorizationEndpointAbsent'] and off['newGuestPolicyNotAdvertised'] and not off['livePreviewChanged']
    assert health['nativeManifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
    assert health['frontendManifestSHA256']=='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787'
    assert health['nativeConfigVersion']=='codi-managed-instance/4' and files['registeredPrivateFilesLive']
    assert len(health['siteDomains'])==10 and health['prototypeDeclaredFilesVerified']==133
    baseline=ROOT/'.build/releases/connected-files-r2';raw=(baseline/'connected-release.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==health['nativeManifestSHA256']
    declared=json.loads(raw)['files'];dependencies={}
    for path in ['origin_service/lifecycle.py','codiserver-server-v0.3.0/codiauth/jose.py','codiserver-server-v0.3.0/codiauth/service.py']:
        actual=sha(ROOT/path);assert actual==sha(baseline/path)==declared[path]['sha256'];dependencies[path]=actual
    fixture_path='codiserver-server-v0.3.0/tests/test_service.py'
    assert sha(ROOT/fixture_path)==sha(ROOT.parent/fixture_path)
    fixture_dependencies={fixture_path:sha(ROOT/fixture_path)}
    result={'status':'PASS','scope':'Local typed live-session network grants, isolated actual nftables/direct sockets and separate actual HTTP/WSS/QEMU wire lifecycle; combined kernel/worker, v86 frontend, managed install and public rollout remain undone',
            'liveGuestNetworkRuleInstalled':False,'combinedKernelWorkerVerified':False,'v86FrontendWired':False,'independentWANVerified':False,'fullGoalComplete':False,
            'liveNativeManifestSHA256':health['nativeManifestSHA256'],'liveFrontendManifestSHA256':health['frontendManifestSHA256'],'policyFixtureSHA256':kernel['policySHA256'],
            'native11DependencySHA256':dependencies,'localFixtureSHA256':fixture_dependencies,'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'guest-network-foundation-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
