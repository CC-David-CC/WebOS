#!/usr/bin/env python3
"""Bind live per-account template evidence without claiming a live file API."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
if __name__=='__main__':
    names=['user-apps-result.json','user-apps-public-result.json','touch-public-result.json',
           'general-voice-public-result.json','preview-touch-live-health-result.json',
           'touch-frontend-activation-result.json','user-apps-cleanup-result.json',
           'gateway-auth-result.json','user-storage-webhost-apply-result.json']
    reports={name:json.loads((CHECKS/name).read_text()) for name in names}
    for name,value in reports.items():
        assert value['status']=='PASS',name
        for path,expected in value.get('sha256',{}).items():assert digest(ROOT/path)==expected,(name,path)
    health=reports['preview-touch-live-health-result.json'];activation=reports['touch-frontend-activation-result.json']
    frontend=ROOT/'.build/frontends/user-apps-r14';metadata=json.loads((frontend/'frontend.json').read_text())
    assert digest(frontend/'frontend.json')==health['frontendManifestSHA256']==activation['frontendManifestSHA256']
    assert health['onlineRoleRelease']=='/srv/codi-connected/releases/native10-7705a87e09c44e22'
    assert activation['nativePidsUnchanged']=={role:str(record['pid']) for role,record in health['processes'].items()}
    assert activation['nativeConfigUnchanged'] and activation['indexAndGuestCookieUnchanged']
    assert len(health['siteResults'])==9 and set(health['siteResults'].values())=={'PASS'}
    assert health['currentWebsitePrototypeBytesPreserved'] and health['persistentCookieMatchesRunningGuest']
    for name,record in metadata['files'].items():
        assert record=={'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)}
        for report in ['user-apps-result.json','user-apps-public-result.json','touch-public-result.json']:
            assert reports[report]['servedAssetsSHA256'][name]==record['sha256']
    assert reports['user-apps-cleanup-result.json']['disabled']==4
    assert reports['user-storage-webhost-apply-result.json']['registry']['retainedRegisteredFolders']==1
    assert reports['user-storage-webhost-apply-result.json']['registry']['anonymousFolders']==0
    result={'status':'PASS','scope':'Current live R14 account-specific RAM template apps and public touch/voice/native/prototype health; local authorization candidate separately tested',
            'frontendManifestSHA256':health['frontendManifestSHA256'],'nativeManifestSHA256':health['manifestSHA256'],
            'templateServerPersistence':False,'gatewayFileAPIInstalled':False,'identityBoundGuestWANPolicyInstalled':False,
            'physicalPhoneNotVerified':True,'independentWANNotVerified':True,
            'receiptsSHA256':{name:digest(CHECKS/name) for name in names},'aggregateSourceSHA256':digest(Path(__file__))}
    (CHECKS/'user-apps-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
