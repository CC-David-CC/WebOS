#!/usr/bin/env python3
"""Bind tested root lifecycle and actual inactive preparation to live preservation."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
OPERATOR='8411c84aab2b284418951371b2ee9822797a70599c016c375bb409cb40f641d1'
WORKER='7f5de0c7525b81391448069708ee972cca304792baaf274b4aa1151e181a9759'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,digest in value.get('sha256',{}).items():assert sha(ROOT/path)==digest,(name,path)
    return value

if __name__=='__main__':
    names=['guest-durable-workers-milestone-result.json','guest-operator-result.json','guest-operator-export-result.json','guest-operator-package-result.json','guest-network-standby-plan-result.json','guest-network-standby-install-result.json','webhost-files-preview-health-result.json']
    durable,actual,export,package,plan,install,health=[load(name) for name in names]
    assert durable['aggregateSourceSHA256']==sha(ROOT/'scripts/guest-durable-workers-milestone.py')
    for name,digest in durable['receiptSHA256'].items():assert sha(CHECKS/name)==digest,name
    assert durable['runtimeManifestSHA256']==actual['workerRuntimeSHA256']==install['workerManifestSHA256']==WORKER
    assert package['manifestSHA256']==actual['operatorManifestSHA256']==install['operatorManifestSHA256']==OPERATOR
    assert len(actual['checks'])==20 and actual['actualSystemdLifecycle'] and actual['actualQEMUAndSignedGrants'] and actual['continuousKernelGuard'] and actual['atomicRecoveryBoundaries']
    assert actual['unrelatedFixtureTablePreserved'] and actual['fixtureCleanupCompleted'] and actual['hostFirewallResolverAndSysctlsUnchanged']
    assert export['tests']==8 and export['failures']==export['errors']==0
    for path,digest in actual['copiedSourceSHA256'].items():
        kind,relative=path.split('/',1);assert kind in ('operator','worker') and sha(ROOT/relative)==digest,path
    guard=actual['processWitnesses']['guard'];assert guard=={'uid':0,'gid':0,'effectiveCapabilities':4096,'noNewPrivileges':True}
    for role in ['anonymous','registered']:
        value=actual['processWitnesses'][role];assert value['uid']>0 and value['gid']==1001 and value['effectiveCapabilities']==0 and value['noNewPrivileges']
    assert install['action']=='install' and plan['action']=='plan' and install['ownPublicIPv4']==plan['ownPublicIPv4']==['104.180.210.33']
    for value in [plan,install]:
        assert value['wrapperSHA256']==sha(ROOT/'scripts/stage-guest-network.py')
        assert not value['kernelRulesActivated'] and not value['native12Installed'] and not value['servicesRestarted'] and value['hostFirewallAndSysctlsUnchanged']
        assert value['prototypeDeclaredFilesVerified']==133
    assert install['usageLedgersEmpty'] and install['configure']['status']=='configured' and not install['configure']['started'] and not install['configure']['bootEnabled']
    assert set(install['preparedIdentities'])=={'anonymous','registered'} and len(set(install['preparedIdentities'].values()))==2
    for value in install['units'].values():assert value['ActiveState']=='inactive' and value.get('MainPID','0')=='0' and value['UnitFileState']=='static'
    assert health['nativeManifestSHA256']==install['nativeManifestSHA256']==durable['liveNativeManifestSHA256'] and health['nativeConfigVersion']=='codi-managed-instance/4'
    assert health['frontendManifestSHA256']==install['liveFrontendManifestSHA256']==durable['liveFrontendManifestSHA256']
    assert health['defaultPublicTLSVerified'] and len(health['siteDomains'])==10 and health['prototypeDeclaredFilesVerified']==133
    assert not health['servicesRestarted'] and not health['personalFileContentsRead']
    for role,pid in health['nativePIDs'].items():assert str(pid)==install['nativeAndFilesPIDs']['codi-ksu-hidden-'+role+'.service']
    for name,value in health['privateWorker']['processes'].items():assert str(value['pid'])==install['nativeAndFilesPIDs'][name]
    assert health['hostingSHA256']=={'generator':install['protectedSHA256']['/home/dflanag3/webhost-sites/ops/common.py'],'manifest':install['protectedSHA256']['/home/dflanag3/webhost-sites/sites.toml'],'activeCaddy':install['protectedSHA256']['/etc/caddy/Caddyfile']}
    result={'status':'PASS','scope':'Exact local installed-systemd root controller/guard, crash/rollback/readiness/ownership proof plus actual box-webhost inactive code/accounts/config/units preparation and fresh native11/R15/all-site/prototype preservation; public guest network access control is not activated',
        'operatorManifestSHA256':OPERATOR,'workerRuntimeSHA256':WORKER,'localAtomicLifecycleAndGuardVerified':True,'preparedOnWebhost':True,
        'operatorActiveOnWebhost':False,'liveGuestNetworkRuleInstalled':False,'native12Installed':False,'browserInstalledWholeChainVerified':False,
        'privateFilesGUIWithNewNetworkVerified':False,'physicalAndroidVerified':False,'independentWANVerified':False,'fullGoalComplete':False,
        'standbyManagedConfigSHA256':install['managedConfigSHA256'],'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'guest-operator-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
