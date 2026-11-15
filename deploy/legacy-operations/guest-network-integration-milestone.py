#!/usr/bin/env python3
"""Bind local guest identity/kernel/desktop proofs without claiming live rollout."""
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks'
NATIVE='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
FRONTEND='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,expected in value.get('sha256',{}).items():assert sha(ROOT/path)==expected,(name,path)
    return value

if __name__=='__main__':
    names=['guest-authorization-result.json','guest-egress-kernel-result.json','guest-worker-result.json','guest-coordinator-result.json','guest-combined-result.json','guest-client-browser-result.json','guest-desktop-browser-result.json','webhost-files-preview-health-result.json','connected-release-result.json']
    auth,kernel,worker,coordinator,combined,client,desktop,health,release=[load(name) for name in names]
    assert release['tests']==16 and release['failures']==release['errors']==0
    assert auth['tests']==28 and auth['failures']==auth['errors']==0
    assert kernel['packetDecisions']==161 and sum(len(w['results']) for w in kernel['actualKernelWitnesses'].values())==84
    assert kernel['policySHA256']==worker['policySHA256']==coordinator['policySHA256']==combined['policySHA256']
    assert kernel['fixtureNamespaceAndProcessesCleaned'] and not kernel['hostFirewallChanged'] and kernel['actualNftCountersAdvanced']
    assert len(worker['checks'])==63 and worker['actualQEMU']
    assert len(coordinator['checks'])==18 and coordinator['publicWireRetainedAcrossRoleChanges'] and coordinator['controlMessagesOutsideNIC'] and coordinator['allFixtureChildrenCleaned']
    assert len(combined['checks'])==35
    for key in ['separateUIDsAndSharedPingGID','internalUnixSocketOwnershipVerified','workerResolverBindVerified','actualUIDConfinedCoordinator','publicConnectionRetainedAfterExpiry','actualKernelWorkerIntegration','fixtureNamespacesAndStageRemoved','hostFirewallAndResolverUnchanged']:assert combined[key],key
    assert not combined['browserV86Integration'] and not combined['livePreviewChanged']
    for role in ['anonymous','registered']:
        witness=combined['qemuProcessWitnesses'][role]
        assert witness['uid']=={'anonymous':60231,'registered':60232}[role] and witness['gid']==1001 and witness['noCapabilities'] and witness['noNewPrivileges']
        result=combined['actualLinuxGuestResults'][role]
        for key in ['own_ping','own_http','own_tls']:assert result[key]['ok']==(role=='registered'),(role,key)
        for key in ['other_ping','other_http','other_tls','dns']:assert result[key]['ok'],(role,key)
        for key in ['lan10','lan172','lan192','metadata','public_other_port']:assert not result[key]['ok'],(role,key)
    assert len(client['witnesses'])==2
    for value in client['witnesses']:
        assert value['actualV86LinuxBoot'] and value['actualLinuxNICReceivesReply'] and value['realHTTPWebCryptoGrants']
        assert value['samePublicSocketAcrossAccountSwitch'] and value['linuxShellAndSharedFilePreserved'] and value['cookieRenewedWithoutVMReload'] and value['staleIdentityResponseDiscarded'] and value['controlTextNeverDeliveredToNIC']
    assert [(v['basePath'],v['mode'],v['mobile']) for v in desktop['witnesses']]==[('','controlled',False),('/hidden','controlled',True),('','legacy',False),('/hidden','offline',True),('/hidden','invalid',False)]
    for value in desktop['witnesses']:
        if value['mode']=='invalid':assert value['invalidMetadataFailsClosed'] and value['legacyFallbackNotAttempted'] and value['failedVMStopped']
        else:
            for key in ['actualDesktopLinuxReady','actualAccountMenu','sameVMAndFilesystem','independentShellsPreserved','workspaceAndEditorPreserved']:assert value[key],key
            assert not value['browserErrors']
            if value['mode']=='controlled':assert value['sameNetworkSocketAcrossAccounts'] and value['registeredCookieReconnect']
            else:assert value['legacySDKNotRequested'] and value['sdkRequests']==0
    assert health['nativeManifestSHA256']==NATIVE and health['frontendManifestSHA256']==FRONTEND and health['nativeConfigVersion']=='codi-managed-instance/4'
    assert health['prototypeDeclaredFilesVerified']==133 and len(health['siteDomains'])==10 and health['defaultPublicTLSVerified'] and not health['servicesRestarted'] and not health['personalFileContentsRead']
    baseline=ROOT/'.build/releases/connected-files-r2'
    assert sha(baseline/'connected-release.json')==NATIVE
    for path,record in health['frontendFiles'].items():assert sha(baseline/path)==record['sha256']
    assert sha(ROOT/'app.js')!=health['frontendFiles']['app.js']['sha256'],'Candidate must be distinguished from the still-live R15 app'
    with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=20) as response:
        config=json.load(response);assert config['guestNetwork'].get('authorization') is None and config['gateway']['version']=='codi-user-files/1'
    request=urllib.request.Request('https://ksu.codes/hidden/api/v1/guest-network/challenge',data=b'{}',method='POST',headers={'Content-Type':'application/json','Origin':'https://ksu.codes'})
    try:
        with urllib.request.urlopen(request,timeout=20) as response:status=response.status
    except urllib.error.HTTPError as error:status=error.code
    assert status==404,status
    result={'status':'PASS','scope':'Local real signed grants; actual separate-UID QEMU/coordinator and nft enforcement together; separate real Chrome/v86 and full desktop root/hidden integration, account switching and mixed versions. Live native11/R15 preserved; no managed network rollout or WAN proof.',
        'combinedKernelWorkerCoordinatorVerified':True,'v86AdapterVerified':True,'fullDesktopAppIntegrationVerified':True,
        'v86WithKernelAndManagedServicesVerified':False,'registeredFileGUIWithNewNetworkVerified':False,
        'managedNetworkOperatorInstalled':False,'native12Installed':False,'liveGuestNetworkRuleInstalled':False,
        'physicalAndroidVerified':False,'independentWANVerified':False,'fullGoalComplete':False,
        'liveNativeManifestSHA256':NATIVE,'liveFrontendManifestSHA256':FRONTEND,'candidateAppSHA256':sha(ROOT/'app.js'),'policyFixtureSHA256':combined['policySHA256'],
        'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'guest-network-integration-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
