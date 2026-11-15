#!/usr/bin/env python3
"""Bind managed sign-in activation to current public browser and hosting evidence."""
import hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks';records={}
def read(name):
 raw=(CHECKS/name).read_bytes();records[name]=hashlib.sha256(raw).hexdigest();d=json.loads(raw);assert d['status']=='PASS',name;return d
code=read('signin-public-code-result.json');policy=read('signin-public-policy-result.json');hosting=read('unified-assets-apply-result.json');health=read('webhost-signin-health-result.json');final=read('native15-live-final-inspection-result.json')
assert code['codeRollout']['status']=='upgraded' and code['codeRollout']['guestCookiePreserved'] and code['codeRollout']['checkpointGuestPidPreserved'] and code['codeRollout']['keysAuthorityAndExistingAccountsPreserved'] and not code['codeRollout']['dataRestored']
assert policy['registeredOnlyGuestInternet'] and policy['policyRollout']['status']=='guest-signin-migrated' and policy['keysAccountsCookieFilesAndCountersPreserved'] and policy['privateFileServicesPreserved']
assert policy['guestPolicy']['active'] and policy['guestPolicy']['kernelMatches'] and not policy['guestPolicy']['guardFault']
assert hosting['sixPublicAssetsEqualNative'] and not hosting['publicAssetBytesChanged'] and not hosting['nativeServicesRestarted'] and len(hosting['siteDomains'])==10
assert health['nativeManifestSHA256']==code['nativeManifestSHA256']==final['nativeManifestSHA256']=='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed'
assert health['nativeConfigSHA256']==policy['configSHA256']==final['configSHA256']=='22eec0f5b47841e8994b72954e3cfa119bad8177333319bc5c93b915f9cb3403'
assert health['nativePIDs']==policy['afterPIDs']==final['nativePIDs']
assert health['prototypeDeclaredFilesVerified']==133 and len(health['siteDomains'])==10 and health['unauthorizedFileAccessDenied'] and health['workerScopeRestrictedToHidden'] and health['defaultPublicTLSVerified']
assert final['noPendingNativeJournals'] and final['noticeCleared'] and final['frontendOverlayRetired']
account=read('public-signin-account-result.json');assert account['allAnonymousGuestInternetDenied'] and account['privateServerFilesVerified'] and account['generatedPrivateFileRemoved'] and account['generatedAccountDisabled'] and account['defaultCertificateTrust'] and len(account['checks'])==20
peer=read('public-signin-peer-result.json');assert peer['defaultCertificateTrust'] and not peer['certificateExceptionUsed'] and len(peer['checks'])==7 and '1. e4 e5' in peer['pgn'] and 'ordinary' not in peer['pgn']
cache=read('public-signin-cache-result.json');assert len(cache['checks'])==11 and cache['defaultCertificateTrust'] and cache['rebuildAfterSiteDataClear'] and not cache['runningVMWasSaved']
pool=read('native15-public-pool-result.json');first=read('native15-public-pool-first-result.json')
for d in [pool,first]:assert d['url']=='https://ksu.codes/hidden/' and d['browsers']==3 and len(d['checks'])==8 and d['defaultCertificateTrust'] and d['sourceSHA256']==hashlib.sha256((ROOT/'scripts/pool-check.py').read_bytes()).hexdigest()
assert first['actionTrace']!=pool['actionTrace'],'Separate fresh three-browser runs required'
maintenance=read('signin-public-maintenance-observer.json');assert maintenance['controlsBlockedAtDeadline'] and maintenance['originalMemoryAndGuestFileRetainedAcrossRestart'] and maintenance['freshReloadUsesStrictPolicy'] and maintenance['priorRAMFileNotRestoredAfterReload'] and maintenance['ownedBrowserClosed'] and not maintenance['automaticWorkSaveClaimed']
for proof in [account,health]:
 for name,pin in proof['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==pin,name
with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=15) as response:config=json.load(response)
assert config['guestNetwork']['authorization']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049' and config['guestNetwork']['previewPolicy']['anonymousInternet']=='deny'
assert config['rtc']['preference']=={'version':'codi-session-ice/1','allowed':['relay','all'],'preferred':'all'}
with urllib.request.urlopen('https://ksu.codes/hidden/api/v1/desktop-status',timeout=15) as response:status=json.load(response)
assert status['maintenance'] is None or status['maintenance']['phase']=='cancelled'
result={'status':'PASS','scope':__doc__,'nativeManifestSHA256':final['nativeManifestSHA256'],'configSHA256':final['configSHA256'],'nativePIDs':final['nativePIDs'],'hostingSHA256':health['hostingSHA256'],'registeredOnlyGuestInternetLive':True,'allSiteSmokeDomains':health['siteDomains'],'prototypeDeclaredFilesVerified':133,'publicUniqueChecks':46,'freshThreeBrowserRuns':2,'actualMaintenanceWarningAndLockVerified':True,'reloadRequiredForOldPinnedClients':True,'oldCachedClientsMayNeedAllTabsClosed':True,'automaticWorkSaveClaimed':False,'privateFilesAndAccountStatePreserved':True,'independentWANVerified':False,'physicalAndroidVerified':False,'xtermRealTerminalMigrated':False,'appAPI2Live':False,'initialInvitationTimeoutCauseEstablished':False,'fullGoalComplete':False,'receiptSHA256':records,'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(CHECKS/'native15-live-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','publicUniqueChecks':46,'freshThreeBrowserRuns':2,'registeredOnlyGuestInternetLive':True}))
