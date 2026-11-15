#!/usr/bin/env python3
"""Bind actual installed worker/quota proof to current desktop and kernel tests."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from guest_service.installation import WORKER_FILES
CHECKS=ROOT/'.build/checks'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def receipt(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,expected in value.get('sha256',{}).items():assert sha(ROOT/path)==expected,(name,path)
    return value

if __name__=='__main__':
    names=['guest-network-integration-milestone-result.json','guest-usage-result.json','guest-worker-export-result.json','guest-installed-worker-result.json','guest-desktop-browser-result.json']
    integration,usage,export,installed,desktop=[receipt(name) for name in names]
    assert integration['aggregateSourceSHA256']==sha(ROOT/'scripts/guest-network-integration-milestone.py')
    for name,expected in integration['receiptSHA256'].items():assert sha(CHECKS/name)==expected,name
    assert integration['combinedKernelWorkerCoordinatorVerified'] and integration['fullDesktopAppIntegrationVerified'] and not integration['liveGuestNetworkRuleInstalled']
    assert usage['tests']==28 and usage['failures']==usage['errors']==0
    assert export['tests']==8 and export['failures']==export['errors']==0
    assert len(installed['checks'])==13 and installed['actualSystemdWorkers'] and installed['durableAccountQuotas'] and installed['rootKernelPreflight']
    assert not installed['continuousKernelGuard'] and not installed['managedOperatorInstalled'] and not installed['liveWebhostChanged']
    assert installed['fixtureCleanupCompleted'] and installed['hostFirewallResolverAndSysctlsUnchanged']
    assert set(installed['copiedRuntimeFiles'])==WORKER_FILES
    for path,record in installed['copiedRuntimeFiles'].items():assert record=={'bytes':(ROOT/path).stat().st_size,'sha256':sha(ROOT/path)},path
    a,r=[installed['witnesses'][role] for role in ['anonymous','registered']]
    assert a['uid']!=r['uid'] and a['gid']==r['gid']==1001 and a['capabilities']==r['capabilities']==0 and a['noNewPrivileges'] and r['noNewPrivileges'] and a['privateNamespaceInode']==r['privateNamespaceInode']
    controlled=[v for v in desktop['witnesses'] if v['mode']=='controlled']
    assert len(controlled)==2
    for value in controlled:assert value['durableUsageEnabled'] and value['quotaDenialKeepsIdentityAndVM'] and value['quotaRestorationResumesRegisteredWire']
    result={'status':'PASS','scope':'Exact local worker runtime: root-pinned inputs and real systemd Unix sockets/LoadCredential/separate UIDs; durable SQLite account quotas, process kill/restart, permission withdrawal and startup drift refusal. Separate current Chrome desktop quota/identity/VM continuity and current combined kernel network fixtures. No production operator or rollout.',
        'runtimeManifestSHA256':installed['runtimeManifestSHA256'],'installedSystemdFixtureVerified':True,'durablePerAccountNetworkUsageVerified':True,'desktopQuotaFallbackAndRestorationVerified':True,
        'atomicKernelLifecycleOperatorVerified':False,'continuousKernelGuardVerified':False,'browserWithInstalledWorkersAndKernelVerified':False,'native12Installed':False,'liveGuestNetworkRuleInstalled':False,
        'privateFilesGUIWithNewNetworkVerified':False,'physicalAndroidVerified':False,'independentWANVerified':False,'fullGoalComplete':False,
        'liveNativeManifestSHA256':integration['liveNativeManifestSHA256'],'liveFrontendManifestSHA256':integration['liveFrontendManifestSHA256'],
        'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'guest-durable-workers-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
