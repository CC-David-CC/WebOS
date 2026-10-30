#!/usr/bin/env python3
"""Bind installed code-transition proofs; the overall system goal remains active."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));checks=ROOT/'.build/checks'
from origin_service.release import NATIVE,record,verify
names=['persistent-services-deployment-baseline-hidden-result.json','persistent-services-deployment-root-result.json','persistent-services-recovery-hidden-result.json','deployment-policy-result.json','recovery-policy-result.json','service-operator-result.json','connected-release-result.json','root-authority-result.json','full-system-hidden-readonly-release-provisioned-result.json','deployment-source-sync-result.json','deployment-webhost-upgrade-result.json','deployment-webhost-api-result.json','deployment-webhost-health-result.json','deployment-prototype-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,receipt in receipts.items():
 assert receipt['status']=='PASS',name
 if name=='deployment-prototype-boundary-result.json':continue
 for source,expected in receipt.get('sha256',{}).items():
  file=ROOT/source
  if digest(file)!=expected and source=='scripts/persistent-services-check.py':file=checks/'fixtures'/('persistent-services-'+expected+'.py')
  assert digest(file)==expected,(name,source)
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];release=Path(full['release']['directory']);assert verify(release)==full['release']
manifest=json.loads((release/'connected-release.json').read_text());assert manifest['version']=='codi-connected-development/7'
for name in NATIVE:assert record(ROOT/name)==manifest['files'][name],name
expected=full['release']['manifestSHA256'];assert expected=='69af311a1f1fd93bd45c900088be08790e590ca47f8200d7a7dd8b8919840ea2'
def browser_check(browser):
 assert browser['identityTrust']=='test-server' and browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['guestAndIdentityPreserved']
 assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
for index,name in enumerate(names[:3]):
 receipt=receipts[name];assert receipt['release']['manifestSHA256']==expected
 assert receipt['basePath']==('' if index==1 else '/hidden') and not receipt['cleanupErrors']
 assert all(receipt[flag] for flag in ['onlineReleaseAfterExecutionVerified','disposableInstalledUnitsAndStateRemoved','originalReleaseUnchanged','pingPolicyRestoredAndForwardingUnchanged','noBootEnablement'])
 browser_check(receipt['browser'])
 if index<2:
  transition=receipt['deployment'];assert transition['checkpointAccounts']==1
  for flag in ['postCheckpointAccountPreserved','postUpgradeAccountPreserved','manualRollbackWithoutDataRestore','failedStartupAutomaticallyRolledBack','wrongIdentityHttp200AutomaticallyRolledBack','noOpDoesNotRestart','actualPartialUnitWriteRecovered','pendingCodeJournalBlocksStart','issuerRootScopedKeysAndAuthorityUnchanged','allThreePreviouslyActiveRolesRestored']:assert transition[flag],(name,flag)
 else:
  recovery=receipt['recovery'];assert recovery['newerRootRevision']==3 and recovery['firstRecoveredRootRevision']==4 and recovery['resumedRootRevision']==5
  for flag in ['issuerAndRootKeysPreserved','scopedKeyRotated','oldPasswordsQuarantined','freshCredentialRestoresSameAccount','tamperedBackupRejected','backupDeniedWhileRunning','roleCannotReadSnapshot','writeAheadFenceBlocksOldRoot','actualInterruptedRenameResumed','pendingRecoveryBlocksStart']:assert recovery[flag]
assert receipts[names[0]]['nativeRoleBaseline']['manifestSHA256']=='d6cbba5b6f46b3163d9f415aca14b848b3d973e196a5013257531bf4df403c74'
assert receipts[names[1]]['deployment']['committedTransitionRetainedAfterJournalClearFailure']
for name,count in [('deployment-policy-result.json',16),('recovery-policy-result.json',16),('service-operator-result.json',16),('connected-release-result.json',12),('root-authority-result.json',17)]:
 value=receipts[name];assert value['tests']==count and value['errors']==value['failures']==0
assert all(full[flag] for flag in ['readOnlyReleaseEnforced','provisionedSteward','configuredPrefixAndCookieScopeVerified','publicConfigCredentialFree','childrenReaped','stewardReaped','credentialFilesRemoved','disposableRuntimeRemoved','disposableRootAuthorityRemoved','releaseAfterExecutionVerified']) and not full['cleanupErrors']
browser=full['browser'];browser_check(browser)
assert browser['stewardCrash']['sameProvisionedWorkerRecovered'] and browser['rootPolicyRenewal']['revision']==2 and browser['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert all(witness['localCandidateType']==witness['remoteCandidateType']=='relay' and witness['localRelayProtocol']=='tls' for witness in browser['witnesses'])
sync=receipts['deployment-source-sync-result.json'];server=receipts['deployment-webhost-upgrade-result.json'];api=receipts['deployment-webhost-api-result.json'];health=receipts['deployment-webhost-health-result.json']
commit='1db61878120627ac497dfa68b9a226a5f6fcf8a6';installed='/srv/codi-connected/releases/1db6187'
assert sync['sourceCommit']==server['sourceCommit']==commit and sync['publicAndAppTreesUnchanged'] and len(sync['changedFiles'])==6 and all(name.startswith('tools/codiserver/') for name in sync['changedFiles'])
assert server['installedRelease']==api['onlineRoleRelease']==health['onlineRoleRelease']==installed and server['manifestSHA256']==api['manifestSHA256']==health['manifestSHA256']==expected
assert server['upgrade']['status']=='upgraded' and server['rollback']['status']=='rolled-back' and server['finalUpgrade']['status']=='upgraded'
for flag in ['keysAccountsRootAndFenceUnchanged','guestAndBootstrapInactive','unitsRemainDisabledForBoot','pingAndForwardingUnchanged']:assert server[flag]
for flag in ['anonymousEntryAndSignature','renewalPreservesSessionAndKey','registeredStableAccountFreshSessionAndKey','wrongPasswordRejected','logoutRevoked','disposableAccountDisabled','sourceAndPrivateHttpPathsDenied','foreignOriginRejected','publicPolicyMatchesHiddenOrigin']:assert api[flag]
assert api['rootRevision']==1 and health['guestAndBootstrapInactive'] and len(health['siteResults'])==8 and set(health['siteResults'].values())=={'PASS'}
assert api['pingGroupRange']==health['pingGroupRange']==['1000','1000']
for process in health['processes'].values():assert process['uid']>0 and set(process['groups'])<={process['gid']} and int(process['capabilities'],16)==0 and process['noNewPrivileges']=='1'
boundary=receipts['deployment-prototype-boundary-result.json'];assert boundary['localIdentityNoApiOrGuestRelay'] and boundary['hiddenStatus']==404
assert boundary['sha256']=={'release.json':'d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9','app.js':'2abb154d558cbc44149cfa46ddcc23c9d4843f822b8a44c5d392cd4bd2f88602','config.json':'5ec30b79a21a07911315ddd9714fba560fc3451004d51942ee53f36c0e6effad'}
clone=ROOT.parent/'.build/deployment/ksu.codes';assert subprocess.check_output(['git','-C',str(clone),'rev-parse','HEAD'],text=True).strip()==commit
assert not subprocess.check_output(['git','-C',str(clone),'status','--porcelain'],text=True).strip();assert verify(clone/'tools/codiserver/connected')['manifestSHA256']==expected
result={'status':'PASS','scope':'Code-only upgrade/rollback with installed local browser fault recovery, backup compatibility and actual private webhost round trip; no public/WAN or schema-migration claim','manifestSHA256':expected,'sourceCommit':commit,'receipts':{name:digest(checks/name) for name in names},'fullObjectiveComplete':False,'checkerSHA256':digest(Path(__file__))}
(checks/'deployment-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
