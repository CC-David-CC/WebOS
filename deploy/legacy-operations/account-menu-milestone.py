#!/usr/bin/env python3
"""Bind optional accounts, current public UI, native rollout and storage setup."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def receipt(name):
    value=json.loads((CHECKS/name).read_text());assert value['status']=='PASS',name
    for path,expected in value.get('sourceSHA256',value.get('sha256',{})).items():
        assert digest(ROOT/path)==expected,(name,path)
    return value

if __name__=='__main__':
    names=['account-menu-result.json','account-menu-public-result.json','origin-lifecycle-result.json',
           'touch-public-result.json','general-voice-public-result.json','independent-shells-public-result.json',
           'account-menu-native-webhost-upgrade-result.json','touch-frontend-activation-result.json',
           'preview-touch-live-health-result.json','user-storage-result.json',
           'user-storage-webhost-apply-result.json','account-menu-cleanup-result.json']
    values={name:receipt(name) for name in names}
    health=values['preview-touch-live-health-result.json'];native=values['account-menu-native-webhost-upgrade-result.json'];activation=values['touch-frontend-activation-result.json']
    frontend=ROOT/'.build/frontends/account-menu-r13';metadata=json.loads((frontend/'frontend.json').read_text())
    assert digest(frontend/'frontend.json')==health['frontendManifestSHA256']==activation['frontendManifestSHA256']
    assert values['account-menu-result.json']['executedReleaseManifestSHA256']==native['candidateManifestSHA256']==health['manifestSHA256']
    assert health['onlineRoleRelease']==native['onlineRoleRelease']==native['installedRelease']
    assert health['nativeUpgradeReceiptSHA256']==native['rootReceiptSHA256']
    assert {role:str(record['pid']) for role,record in health['processes'].items()}==native['afterPids']==activation['nativePidsUnchanged']
    for name,record in metadata['files'].items():
        assert record=={'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)}
        for report in ['account-menu-result.json','account-menu-public-result.json','touch-public-result.json']:
            assert values[report]['servedAssetsSHA256'][name]==record['sha256']
    assert native['rollout']['guestCookiePreserved'] and native['rollout']['keysAuthorityAndExistingAccountsPreserved'] and not native['rollout']['dataRestored']
    assert health['persistentCookieMatchesRunningGuest'] and health['currentWebsitePrototypeBytesPreserved']
    assert len(health['siteResults'])==9 and set(health['siteResults'].values())=={'PASS'}
    assert values['account-menu-cleanup-result.json']['disabled']==2
    foundation=values['user-storage-webhost-apply-result.json'];assert foundation['issuerDatabaseUnreadableByGateway'] and foundation['privateDatabaseUnreadableByOtherServices'] and not foundation['publicServiceStarted']
    storage=ROOT/'.build/storage/private-storage-r1';assert digest(storage/'storage.json')==foundation['manifestSHA256']
    for name,record in json.loads((storage/'storage.json').read_text())['files'].items():
        assert record=={'bytes':(ROOT/name).stat().st_size,'sha256':digest(ROOT/name)}
    report={'status':'PASS','scope':'Current native/R13 public optional accounts, mobile/desktop regressions, CPU voice, independent PTYs, nine-site/prototype health and private storage foundation',
            'frontendManifestSHA256':health['frontendManifestSHA256'],'nativeManifestSHA256':health['manifestSHA256'],
            'privateStorageHTTPOrFilesIntegration':False,'independentWANNotVerified':True,'physicalPhoneKeyboardAndMicrophoneNotVerified':True,
            'receiptsSHA256':{name:digest(CHECKS/name) for name in names},'aggregateSourceSHA256':digest(Path(__file__))}
    (CHECKS/'account-menu-milestone-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
