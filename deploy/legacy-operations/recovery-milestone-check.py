#!/usr/bin/env python3
"""Bind actual checkpoint/recovery evidence; leaves the full objective active."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));checks=ROOT/'.build/checks'
from origin_service.release import NATIVE,record,verify
names=['persistent-services-recovery-root-result.json','persistent-services-recovery-hidden-result.json','persistent-services-recovery-baseline-hidden-result.json','root-authority-result.json','recovery-policy-result.json','service-operator-result.json','connected-release-result.json','full-system-hidden-readonly-release-provisioned-result.json','recovery-source-sync-result.json','recovery-webhost-backup-result.json','recovery-webhost-health-result.json','persistent-services-webhost-api-result.json','recovery-prototype-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
for name,receipt in receipts.items():
 assert receipt['status']=='PASS',name
 if name!='recovery-prototype-boundary-result.json':
  for source,digest in receipt.get('sha256',{}).items():
   if source=='scripts/persistent-services-check.py' and hashlib.sha256((ROOT/source).read_bytes()).hexdigest()!=digest:
    archived=checks/'fixtures'/('persistent-services-'+digest+'.py');assert hashlib.sha256(archived.read_bytes()).hexdigest()==digest
   else:assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==digest,(name,source)
for index,name in enumerate(names[:3]):
 receipt=receipts[name];assert receipt['basePath']==('' if index==0 else '/hidden')
 assert not receipt['cleanupErrors'] and receipt['onlineReleaseAfterExecutionVerified'] and receipt['disposableInstalledUnitsAndStateRemoved'] and receipt['originalReleaseUnchanged'] and receipt['pingPolicyRestoredAndForwardingUnchanged']
 recovery=receipt['recovery'];assert recovery['snapshot']['files']==13 and recovery['snapshot']['binding']['rootRevision']==2 and recovery['newerRootRevision']==3 and recovery['firstRecoveredRootRevision']==4 and recovery['resumedRootRevision']==5
 for flag in ['issuerAndRootKeysPreserved','scopedKeyRotated','oldPasswordsQuarantined','freshCredentialRestoresSameAccount','tamperedBackupRejected','backupDeniedWhileRunning','roleCannotReadSnapshot','writeAheadFenceBlocksOldRoot','actualInterruptedRenameResumed','pendingRecoveryBlocksStart']:assert recovery[flag],(name,flag)
 browser=receipt['browser'];assert browser['identityTrust']=='test-server' and browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['guestAndIdentityPreserved']
 assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
assert receipts[names[2]]['nativeRoleBaseline']['manifestSHA256']=='d6cbba5b6f46b3163d9f415aca14b848b3d973e196a5013257531bf4df403c74'
for name,count,key in [('root-authority-result.json',17,'tests'),('recovery-policy-result.json',16,'tests'),('service-operator-result.json',16,'tests'),('connected-release-result.json',12,'tests')]:assert receipts[name][key]==count and receipts[name]['errors']==receipts[name]['failures']==0
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];browser=full['browser']
assert full['releaseAfterExecutionVerified'] and full['childrenReaped'] and full['stewardReaped'] and not full['cleanupErrors'] and full['credentialFilesRemoved'] and full['disposableRuntimeRemoved'] and full['disposableRootAuthorityRemoved']
assert browser['stewardCrash']['sameProvisionedWorkerRecovered'] and browser['rootPolicyRenewal']['revision']==2 and browser['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert all(w['localCandidateType']==w['remoteCandidateType']=='relay' and w['localRelayProtocol']=='tls' for w in browser['witnesses'])
assert len(browser['guestInternet'])==2 and all(g['pingReplies']==2 and g['dnsAndHttp'] for g in browser['guestInternet'])
release=Path(full['release']['directory']);assert verify(release)==full['release'];manifest=json.loads((release/'connected-release.json').read_text());assert manifest['version']=='codi-connected-development/6'
for name in NATIVE:assert record(ROOT/name)==manifest['files'][name],name
assert all(receipts[name]['release']['manifestSHA256']==full['release']['manifestSHA256'] for name in names[:3])
sync=receipts['recovery-source-sync-result.json'];server=receipts['recovery-webhost-backup-result.json'];health=receipts['recovery-webhost-health-result.json']
assert sync['sourceCommit']=='6b99ae4477492c05e86e991460944dbea883f819' and sync['publicAndAppTreesUnchanged']
assert server['controllerManifestSHA256']==full['release']['manifestSHA256'] and server['verified'] and server['issuerRootAndScopedKeysUnchanged']
assert server['configVersion']=='codi-managed-instance/2' and server['allSnapshotFilesRootPrivate'] and server['legacyControllerRejectsAdoptedMetadata'] and server['externalFenceExists'] and not any(server['onlineRolesCannotReadBackup'].values())
assert server['backup']['files']==13 and server['backup']['manifestSHA256']=='8ade3bfc602a77391f4ba190506d27564f513f99ce7a04c8e76c0835a704aa25'
assert health['guestAndBootstrapInactive'] and len(health['siteResults'])==8 and set(health['siteResults'].values())=={'PASS'}
assert server['pingGroupRange']==health['pingGroupRange']==['1000','1000'] and health['configVersion']=='codi-managed-instance/2'
for process in health['processes'].values():assert process['uid']!=0 and set(process['groups'])<={process['gid']} and int(process['capabilities'],16)==0 and process['noNewPrivileges']=='1'
api=receipts['persistent-services-webhost-api-result.json'];assert api['anonymousEntryAndSignature'] and api['registeredStableAccountFreshSessionAndKey'] and api['renewalPreservesSessionAndKey'] and api['wrongPasswordRejected'] and api['logoutRevoked'] and api['disposableAccountDisabled'] and api['rootRevision']==1
assert receipts['recovery-prototype-boundary-result.json']['localIdentityNoApiOrGuestRelay'] and receipts['recovery-prototype-boundary-result.json']['hiddenStatus']==404
result={'status':'PASS','scope':'Native fenced checkpoint/disaster recovery on local installed roles, verified on-host private server backup and resumed API/site health; no live restore, off-host custody, code rollback or public/WAN claim','manifestSHA256':full['release']['manifestSHA256'],'sourceCommit':sync['sourceCommit'],'receipts':{name:hashlib.sha256((checks/name).read_bytes()).hexdigest() for name in names},'fullObjectiveComplete':False,'checkerSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(checks/'recovery-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
