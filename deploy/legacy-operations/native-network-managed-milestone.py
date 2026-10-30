#!/usr/bin/env python3
"""Bind native12 model, installed VM/browser/kernel/recovery and live preservation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
NATIVE='6965594615c296061ddea6cc16fe61654cb0d99c2d577860b5c1e7ffa1fd9a63'
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def load(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,digest in value.get('sha256',{}).items():assert sha(ROOT/path)==digest,(name,path)
    return value
if __name__=='__main__':
    names=['connected-release-result.json','service-operator-result.json','native-network-policy-result.json','native-files-result.json','native-network-vm-browser-result.json','native-network-vm-boundary-result.json','native-network-vm-lifecycle-result.json','webhost-files-preview-health-result.json']
    release,units,model,files,browser,kernel,lifecycle,health=[load(name) for name in names]
    for value,count in [(release,18),(units,20),(model,20)]:assert value['tests']==count and value['failures']==value['errors']==0
    assert model['kernelEffectsModeled'] and not model['installedLifecycleVerified']
    assert len(files['checks'])==11 and files['nativeProfile']=='codi-connected-development/12' and files['fixtureCleanupCompleted'] and files['nativeManifestSHA256']==NATIVE
    assert len(browser['checks'])==28 and len(browser['probes'])==17 and browser['actualBrowserWorkerKernelChain'] and browser['realPrivateFilesGUI'] and not browser['browserErrors']
    assert browser['fixtureCertificatePinUsed'] and not browser['publicDefaultTLSVerified'] and not browser['independentWANVerified']
    assert browser['installed']['nativeSHA256']==NATIVE
    assert len(kernel['rootControlledListenerReferences'])==18 and all(kernel['rootControlledListenerReferences'].values())
    assert kernel['unfilteredReferenceContext']=={'uid':65534,'gid':1001,'effectiveCapabilities':0,'noNewPrivileges':True}
    for role in ['anonymous','registered','frontend']:
        value=kernel['uidWitnesses'][role];assert len(value['results'])==18 and value['gid']==1001 and value['effectiveCapabilities']==0 and value['noNewPrivileges']
        assert all(p['connected']==p['expectedAllowed'] for p in value['results']) and kernel['actualRejectCounters'][role]>0
    assert len(lifecycle['checks'])==13 and lifecycle['nativeManifestSHA256']==NATIVE and lifecycle['actualProcessExitAndGuardDeath']
    assert lifecycle['keyAccountCookieAndPrivateFileStatePreserved'] and lifecycle['usageCountersNeverReset'] and lifecycle['finalConfigVersion']=='codi-managed-instance/5'
    assert len(lifecycle['committedWireContinuity'])==2 and all(v['sameQEMUChildren'] and v['samePublicWebSocketAndActualARP'] for v in lifecycle['committedWireContinuity'])
    assert lifecycle['finalWorkerStatus']['active'] and lifecycle['finalWorkerStatus']['kernelMatches'] and not lifecycle['finalWorkerStatus']['guardFault']
    assert health['nativeManifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0' and health['nativeConfigVersion']=='codi-managed-instance/4'
    assert health['frontendManifestSHA256']=='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787' and health['prototypeDeclaredFilesVerified']==133 and len(health['siteDomains'])==10
    assert health['defaultPublicTLSVerified'] and not health['servicesRestarted'] and not health['personalFileContentsRead']
    spec=importlib.util.spec_from_file_location('native12_release',ROOT/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    artifact=ROOT/'.build/releases/connected-network-r1';verified=contract.verify(artifact);assert verified['manifestSHA256']==NATIVE and verified['files']==206
    native=json.loads((artifact/'connected-release.json').read_text());assert native['version']=='codi-connected-development/12'
    for name,record in native['files'].items():
        if name!='release.json' and (ROOT/name).is_file():assert sha(ROOT/name)==record['sha256'],name
    spec=importlib.util.spec_from_file_location('native12_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm);live=vm.status()
    helper_names=['setup-native-network-vm.py','native-network-vm-services.py','native-network-vm-boundary-check.py','native-network-vm-lifecycle-check.py']
    code="import hashlib,json;from pathlib import Path;p=Path('/srv/codi-network-fixture/tools');names="+repr(helper_names)+";print(json.dumps({n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in names}))"
    import shlex
    copied=json.loads(subprocess.run([*vm.ssh_args(),'/usr/bin/python3 -I -B -c '+shlex.quote(code)],check=True,capture_output=True,text=True,timeout=30).stdout)
    assert copied=={name:sha(ROOT/'scripts'/name) for name in helper_names}
    value={'status':'PASS','scope':__doc__,'nativeManifestSHA256':NATIVE,'actualInstalledBrowserWorkerKernelVerified':True,'privateFilesGUIWithNewNetworkVerified':True,'actualNativeCrashRollbackAndGuardRecoveryVerified':True,'independentNativeSocketKernelProbesVerified':True,'phoneFullChainVerified':False,'voiceRTCChessFullCandidateRegressionVerified':False,'cachedSDKAcrossPolicyOffOnVerified':False,'webhostNative12Installed':False,'webhostGuestPolicyActivated':False,'independentWANVerified':False,'physicalAndroidVerified':False,'fullGoalComplete':False,'privateVMConfirmedLive':live,'copiedVMHelperSHA256':copied,'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'native-network-managed-milestone-result.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
