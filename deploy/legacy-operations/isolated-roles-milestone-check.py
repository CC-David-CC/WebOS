#!/usr/bin/env python3
"""Bind real role/browser receipts and source versions; not an overall goal gate."""
import datetime,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
checks=ROOT/'.build/checks'
names=['isolated-roles-root-result.json','isolated-roles-hidden-result.json','discovery-source-result.json','connected-release-result.json','publisher-result.json','root-authority-result.json','provisioned-connected-result.json','full-system-hidden-readonly-release-provisioned-result.json','isolated-roles-prototype-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
for name,record in receipts.items():
 if name=='publisher-result.json':assert record['passed'] is True and record['tests']==25 and record['errors']==record['failures']==0
 else:assert record['status']=='PASS',name
 if name!='isolated-roles-prototype-boundary-result.json':
  for source,digest in record.get('sha256',record.get('sourceHashes',{})).items():
   assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==digest,(name,source)
for index,name in enumerate(names[:2]):
 record=receipts[name]
 assert record['basePath']==('' if index==0 else '/hidden')
 assert not record['cleanupErrors'] and record['onlineReleaseAfterExecutionVerified'] and record['originalReleaseUnchanged'] and record['disposablePrivateStateRemoved']
 assert record['registeredAccountSurvivesIssuerRestartWithFreshSessionAndKey'] and record['wrongPasswordRejectedAfterRestart'] and record['issuerAccountLoginWorksWithStewardStopped']
 assert record['operatorUsesOnlyIssuerPublicMetadata'] and record['explicitRenewalThroughPublicBundle']
 issuer,steward=record['roles']['issuer'],record['roles']['steward']
 assert issuer['nativeUid']==issuer['uid']!=steward['uid'] and issuer['uid']!=0 and steward['uid']!=0
 for role in [issuer,steward]:assert role['DynamicUser']=='yes' and role['ProtectSystem']=='strict' and role['ProtectHome']=='yes' and role['NoNewPrivileges']=='yes'
 assert sum(len(probes) for probes in record['unixCredentialAccessProbes'].values())==32
 for probes in record['unixCredentialAccessProbes'].values():assert all(probe['allowed']==probe['expected'] for probe in probes)
 assert record['identity']['realGuestBoot'] and record['identity']['wrongPasswordRejected']
 browser=record['browser'];assert browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['guestAndIdentityPreserved'] and browser['identityTrust']=='test-server'
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];browser=full['browser']
assert full['releaseAfterExecutionVerified'] and not full['cleanupErrors'] and full['childrenReaped'] and full['stewardReaped'] and full['credentialFilesRemoved'] and full['disposableRuntimeRemoved'] and full['disposableRootAuthorityRemoved']
assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
assert browser['stewardCrash']['sameProvisionedWorkerRecovered'] and browser['rootPolicyRenewal']['revision']==2 and browser['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert all(witness['localCandidateType']==witness['remoteCandidateType']=='relay' and witness['localRelayProtocol']=='tls' for witness in browser['witnesses'])
assert full['release']['manifestSHA256']==receipts[names[0]]['release']['manifestSHA256']==receipts[names[1]]['release']['manifestSHA256']
spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
assert exporter.verify(Path(full['release']['directory']))==full['release']
assert receipts['isolated-roles-prototype-boundary-result.json']['localIdentityNoApiOrGuestRelay']
result={'status':'PASS','observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Local independently owned issuer/steward milestone and existing combined-stack compatibility; no public deployment, independently owned guest relay, production identity or WAN claim','receipts':{name:hashlib.sha256((checks/name).read_bytes()).hexdigest() for name in names},'manifestSHA256':full['release']['manifestSHA256'],'unixAccessProbesAcrossBothLayouts':64,'fullObjectiveComplete':False,'checkerSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(checks/'isolated-roles-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
