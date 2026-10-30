#!/usr/bin/env python3
"""Bind installed lifecycle, Git-first server setup and private API evidence."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));checks=ROOT/'.build/checks'
from origin_service.release import NATIVE,record,verify
names=['persistent-services-root-result.json','persistent-services-hidden-result.json','service-operator-result.json','connected-release-result.json','full-system-hidden-readonly-release-provisioned-result.json','persistent-services-source-sync-result.json','persistent-services-webhost-install-result.json','persistent-services-webhost-api-result.json','persistent-services-webhost-process-result.json','persistent-services-prototype-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
for name,receipt in receipts.items():
 assert receipt['status']=='PASS',name
 for source,digest in receipt.get('sha256',{}).items():
  if name!='persistent-services-prototype-boundary-result.json':assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==digest,(name,source)
for index,name in enumerate(names[:2]):
 receipt=receipts[name];assert receipt['basePath']==('' if index==0 else '/hidden')
 for flag in ['unitsInstalledAndSyntaxVerified','prepareIdempotent','globalInstanceLockCoversOtherConfigDirectories','conflictingSetupAndUnitDriftRefusedWithoutOverwrite','existingProvisionNotReinitialized','operatorRenewalAndCommittedExportPreserveLiveLedger','missingLedgerFailsBeforeRootAdvance','missingIssuerKeyRefusesStartWithoutRegeneration','completeIssuerRestartPreservesAccountAndSigningKey','noBootEnablement','pingPolicyRestoredAndForwardingUnchanged','onlineReleaseAfterExecutionVerified','disposableInstalledUnitsAndStateRemoved','originalReleaseUnchanged']:assert receipt[flag],(name,flag)
 assert not receipt['cleanupErrors']
 browser=receipt['browser'];assert browser['identityTrust']=='test-server' and browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['guestAndIdentityPreserved']
 assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
 assert receipt['identity']['realGuestBoot'] and receipt['identity']['wrongPasswordRejected']
assert receipts['service-operator-result.json']['tests']==16 and receipts['connected-release-result.json']['tests']==12
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];browser=full['browser']
assert full['releaseAfterExecutionVerified'] and full['childrenReaped'] and full['stewardReaped'] and not full['cleanupErrors'] and full['credentialFilesRemoved'] and full['disposableRuntimeRemoved'] and full['disposableRootAuthorityRemoved']
assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
assert browser['stewardCrash']['sameProvisionedWorkerRecovered'] and browser['rootPolicyRenewal']['revision']==2 and browser['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert all(witness['localCandidateType']==witness['remoteCandidateType']=='relay' and witness['localRelayProtocol']=='tls' for witness in browser['witnesses'])
release=Path(full['release']['directory']);assert verify(release)==full['release']
manifest=json.loads((release/'connected-release.json').read_text());assert manifest['version']=='codi-connected-development/5'
for name in NATIVE:assert record(ROOT/name)==manifest['files'][name],name
assert full['release']['manifestSHA256']==receipts[names[0]]['release']['manifestSHA256']==receipts[names[1]]['release']['manifestSHA256']
source=receipts['persistent-services-source-sync-result.json'];server=receipts['persistent-services-webhost-install-result.json'];install=server['installation'];api=receipts['persistent-services-webhost-api-result.json']
assert source['sourceCommit']==install['sourceCommit']=='517179c549203ba7dfb0cc69cc13e99a24ecfe1f' and source['publicAndAppTreesUnchanged'] and source['sourceClean'] and source['changedFiles']==164
assert source['package']['manifestSHA256']==install['manifestSHA256']==full['release']['manifestSHA256']
assert install['runningWebsiteRelease']==source['runningReleaseUnchanged']
assert set(server['backendListeners'])=={'127.0.0.1:8118','127.0.0.1:8119'}
assert server['bootEnablement']=={'issuer':'disabled','steward':'disabled','guest':'disabled','issuer-bootstrap':'static'}
assert server['nativeCurrentStatus']['units']['guest']['MainPID']==server['nativeCurrentStatus']['bootstrap']['MainPID']=='0'
assert len(server['productionSmoke']['sites'])==8 and all(site['result']=='PASS' and site['https_get']==200 for site in server['productionSmoke']['sites'].values())
assert server['productionSmoke']['unknown_http_host']=={'status':404,'tenant_content':False}
for flag in ['anonymousEntryAndSignature','renewalPreservesSessionAndKey','registeredStableAccountFreshSessionAndKey','wrongPasswordRejected','logoutRevoked','disposableAccountDisabled','sourceAndPrivateHttpPathsDenied','foreignOriginRejected','publicPolicyMatchesHiddenOrigin']:assert api[flag],flag
assert api['authorityExpiresAt']>time.time() and api['rootRevision']==1 and api['pingGroupRange']==['1000','1000']
for role in ['issuer','steward','guest']:
 probes=api['nativeOwnershipProbes'][role];assert probes['uid']!=0
 assert [item['allowed'] for item in probes['privateReads']]=={'issuer':[True,True,False,False,False],'steward':[False,False,True,True,False],'guest':[False,False,False,False,False]}[role]
 if role!='guest':
  process=receipts['persistent-services-webhost-process-result.json']['processes'][role]
  assert process['uid']==probes['uid'] and process['gid']==probes['gid'] and set(process['groups'])<={process['gid']} and int(process['effectiveCapabilities'],16)==0 and process['noNewPrivileges']=='1'
boundary=receipts['persistent-services-prototype-boundary-result.json'];assert boundary['localIdentityNoApiOrGuestRelay'] and boundary['hiddenPublicStatus']==404
result={'status':'PASS','scope':'Actual local persistent-unit lifecycle plus Git-first private box-webhost issuer/steward installation and API evidence; guest/public route/WAN/production identity remain unachieved','manifestSHA256':full['release']['manifestSHA256'],'sourceCommit':source['sourceCommit'],'receipts':{name:hashlib.sha256((checks/name).read_bytes()).hexdigest() for name in names},'fullObjectiveComplete':False,'checkerSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(checks/'persistent-services-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
