#!/usr/bin/env python3
"""Bind actual private worker activation without claiming a live account Files UI."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    names=['persistent-files-result.json','file-operator-export-result.json','private-files-webhost-plan-result.json',
           'private-files-webhost-apply-result.json','webhost-files-health-result.json','gateway-live-preservation-result.json',
           'gateway-files-milestone-result.json']
    reports={name:json.loads((CHECKS/name).read_text()) for name in names}
    for name,value in reports.items():
        assert value['status']=='PASS',name
        for source,pin in value.get('sha256',{}).items():assert sha(ROOT/source)==pin,(name,source)
    local=reports['persistent-files-result.json'];health=reports['webhost-files-health-result.json'];activation=reports['private-files-webhost-apply-result.json']
    worker='aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d';operator='8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7'
    for report in [local,health,activation]:assert report['workerManifestSHA256']==worker and report['operatorManifestSHA256']==operator
    assert len(local['checks'])==12 and local['fixtureCleanupCompleted']
    assert reports['file-operator-export-result.json']['tests']==10
    assert activation['activationSourceSHA256']==sha(ROOT/'scripts/activate-private-files.py')
    assert activation['migration']['existingBindingsAndACLsPreserved'] and not activation['migration']['dataRestored']
    assert activation['existingUserFileMetadataPreserved'] and activation['hostingNativeAndPrototypeUnchanged']
    assert activation['staticUnits'] and health['staticUnits'] and health['onlyLoopbackInterface']
    assert health['privateDatabasesSeparated'] and health['publicGatewayRoutesAbsent'] and health['defaultPublicTLSVerified']
    assert health['retainedRegisteredFolders']==1 and health['permissionRows']==7 and health['anonymousFolders']==0
    live=reports['gateway-live-preservation-result.json'];assert live['prototypeBytesPreserved'] and len(live['enabledSites'])==10
    assert {name:str(pid) for name,pid in live['nativePIDs'].items()}==activation['nativePids']
    for folder,filename,pin in [(ROOT/'.build/gateways/user-files-r4','files-service.json',worker),(ROOT/'.build/file-operators/private-files-r6','file-operator.json',operator)]:
        assert sha(folder/filename)==pin
        for source,value in json.loads((folder/filename).read_text())['files'].items():
            assert value=={'bytes':(folder/source).stat().st_size,'sha256':sha(folder/source)}
            assert (folder/source).read_bytes()==(ROOT/source).read_bytes()
    result={'status':'PASS','scope':'Actual installed private isolated file worker plus local file transport/UI candidate; live account Files/API integration remains absent',
            'workerManifestSHA256':worker,'operatorManifestSHA256':operator,'privateWorkerInstalled':True,'publicFileAPIInstalled':False,'liveFilesUIUsesServer':False,
            'guestNetworkIdentityRuleInstalled':False,'independentWANVerified':False,'physicalPhoneVerified':False,
            'rootActivationReceipt':activation['rootReceipt'],'rootActivationReceiptSHA256':activation['rootReceiptSHA256'],
            'receiptSHA256':{name:sha(CHECKS/name) for name in names},'aggregateSourceSHA256':sha(Path(__file__))}
    (CHECKS/'persistent-files-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
