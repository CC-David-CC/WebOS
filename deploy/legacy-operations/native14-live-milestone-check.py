#!/usr/bin/env python3
"""Bind public native14 deployment proofs without claiming the full plan complete."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
CHECKS=ROOT/'.build/checks'
records={}
def read(name):
    raw=(CHECKS/name).read_bytes()
    records[name]=hashlib.sha256(raw).hexdigest()
    value=json.loads(raw)
    assert value['status']=='PASS',name
    return value

upgrade=read('ice-preference-native-webhost-upgrade-result.json')
assert upgrade['candidateManifestSHA256']=='8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce'
assert upgrade['rollout']['status']=='upgraded' and upgrade['rollout']['guestCookiePreserved'] and upgrade['rollout']['checkpointGuestPidPreserved']
assert upgrade['rollout']['keysAuthorityAndExistingAccountsPreserved'] and not upgrade['rollout']['dataRestored']
assert upgrade['privateWorkerCustodyAndPidsPreserved']
activation=read('touch-frontend-activation-result.json')
assert activation['frontendManifestSHA256']=='97b80a77ce3f377aecdea64928730d35c947ce13c3c6e8a968123fa218778381'
policy=read('direct-ice-policy-apply-result.json')
assert policy['afterTransportPolicy']=='all' and policy['legacyTransportPolicy']=='relay' and policy['issuerOnlyRestarted']
assert policy['keysAccountsCookieAndOtherProcessesPreserved'] and policy['noticeCleared'] and not policy['routerFirewallPortsAndBootChanged']
health=read('webhost-desktop-health-result.json')
assert health['nativeConfigSHA256']==policy['afterConfigSHA256'] and health['frontendManifestSHA256']==activation['frontendManifestSHA256']
assert health['prototypeDeclaredFilesVerified']==133 and len(health['siteDomains'])==10
assert health['unauthorizedFileAccessDenied'] and health['workerScopeRestrictedToHidden'] and health['guestPolicy']['active'] and health['guestPolicy']['kernelMatches']
renewal=read('explicit-live-root-renewal-native13-result.json')
assert renewal['authorityKeysPreserved'] and renewal['guestCookiePreserved'] and renewal['operatorResult']['revision']==2
continuity=read('public-ice-continuity-result.json')
for name in ['defaultCertificateTrust','actualIssuerEpochChange','maintenanceControlsBlocked','automaticRecovery','sameLinuxAndFilesystem','sameShellAndGuestFile','sameEditorDraftAndSelection','noReload']:
    assert continuity[name],name
assert not continuity['workAutomaticallySaved'] and continuity['nativePolicyAfter']=='all'
account=read('public-network-account-result.json')
assert account['defaultCertificateTrust'] and account['liveRegisteredOwnWANAndAnonymousDenyVerified'] and account['privateServerFilesVerified'] and account['generatedPrivateFileRemoved'] and account['generatedAccountDisabled']
release=json.loads((ROOT/'.build/releases/connected-ice-preference-r2/connected-release.json').read_text())['files']
def peer_proof(proof,preferred,kind):
    assert proof['status']=='PASS' and proof['publicPreferredIcePolicy']==preferred and proof['publicLegacyIcePolicy']=='relay'
    assert proof['defaultCertificateTrust'] and proof['onlyOwnedPeersInvited'] and not proof['clientForcedRelay'] and proof['testOnlyNativePolicyOverride'] is None
    for name in ['bidirectionalRTC','separateRoomChatAndMoves','pgnExportMatchesAcrossPeersAndExcludesChat','rtcSurvivesWssStop','guestAndIdentityPreserved','serverPolicyRolloutVerified']:
        assert proof[name],name
    assert proof['disposed']==[True,True]
    for witness in proof['witnesses']:
        assert witness['nativeIcePolicies']==[preferred]
        assert witness['localCandidateType']==witness['remoteCandidateType']==kind
        if kind=='relay':assert witness['localRelayProtocol']=='tls'
    for name,value in proof['servedAssetsSHA256'].items():assert value==release[name]['sha256'],name

peer_proof(read('native14-public-relay-result.json'),'relay','relay')
peer_proof(read('native14-public-direct-result.json'),'all','host')
blocked=read('ice-blocked-direct-vm-result.json')
assert blocked['publicPolicyAllVerified'] and not blocked['preflightOnly'] and blocked['kernelBlockedPackets']>0 and blocked['vmRulesAndOwnedDriverCleaned'] and blocked['vmNativeReleaseAndProcessesUnchanged']
peer_proof(blocked['proof'],'all','relay')
prior_blocked=[]
for file in CHECKS.glob('ice-blocked-direct-vm-result-before-*.json'):
    value=json.loads(file.read_text())
    if value.get('status')=='PASS' and value.get('publicPolicyAllVerified') and value.get('vmRulesAndOwnedDriverCleaned'):
        prior_blocked.append(file)
assert prior_blocked,'A second successful real blocked-direct run is required after the initial timeout'
previous=read(sorted(prior_blocked)[-1].name)
peer_proof(previous['proof'],'all','relay')
# Preserve and disclose the initial unexplained timeout, rather than erasing it.
assert (CHECKS/'native14-blocked-direct-first-diagnostics.txt').is_file()
records['native14-blocked-direct-first-diagnostics.txt']=hashlib.sha256((CHECKS/'native14-blocked-direct-first-diagnostics.txt').read_bytes()).hexdigest()
with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=20) as response:
    config=json.load(response)
assert config['rtc']['iceTransportPolicy']=='relay' and config['rtc']['preference']=={'version':'codi-session-ice/1','allowed':['relay','all'],'preferred':'all'}
with urllib.request.urlopen('https://ksu.codes/hidden/api/v1/desktop-status',timeout=20) as response:
    status=json.load(response)
assert status['maintenance'] is None or status['maintenance']['phase']=='cancelled'
report={'status':'PASS','scope':__doc__,'nativeManifestSHA256':upgrade['candidateManifestSHA256'],'frontendManifestSHA256':activation['frontendManifestSHA256'],'nativeConfigSHA256':health['nativeConfigSHA256'],'nativePIDs':health['nativePIDs'],'hostingSHA256':health['hostingSHA256'],'developmentRootRevision':2,'developmentRootExpiresAt':renewal['operatorResult']['expiresAt'],'legacyRelayModernAll':True,'realDirectAndBlockedDirectTurnTLSVerified':True,'subsequentBlockedDirectPasses':2,'initialBlockedDirectTimeoutRetained':True,'initialTimeoutCauseEstablished':False,'automaticMemoryRecoveryVerified':True,'automaticWorkSavingClaimed':False,'independentWANVerified':False,'physicalAndroidVerified':False,'fullGoalComplete':False,'receiptSHA256':records}
report['sha256']={'scripts/native14-live-milestone-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(CHECKS/'native14-live-milestone-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
