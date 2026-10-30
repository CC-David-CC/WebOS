#!/usr/bin/env python3
"""Bind actual three-role Internet/browser evidence; not full objective completion."""
import datetime,hashlib,importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;checks=ROOT/'.build/checks'
names=['managed-roles-root-result.json','managed-roles-hidden-result.json','service-accounts-result.json','guest-relay-result.json','connected-release-result.json','full-system-hidden-readonly-release-provisioned-result.json','managed-roles-prototype-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
for name,record in receipts.items():
 assert record['status']=='PASS',name
 if name!='managed-roles-prototype-boundary-result.json':
  for source,digest in record.get('sha256',{}).items():assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==digest,(name,source)
for index,name in enumerate(names[:2]):
 record=receipts[name];assert record['basePath']==('' if index==0 else '/hidden')
 assert not record['cleanupErrors'] and record['onlineReleaseAfterExecutionVerified'] and record['originalReleaseUnchanged'] and record['disposablePrivateStateRemoved']
 assert record['completeIssuerUnitRestart'] and record['registeredAccountSurvivesIssuerRestartWithFreshSessionAndKey'] and record['wrongPasswordRejectedAfterRestart']
 assert record['issuerAccountLoginWorksWithStewardStopped'] and record['operatorUsesOnlyIssuerPublicMetadata'] and record['explicitRenewalThroughPublicBundle']
 assert record['missingPingPermissionRefusesStartup'] and record['pingPolicyRestoredAndForwardingUnchanged'] and record['observedQemuChildrenReaped']
 roles=record['roles'];assert set(roles)=={'issuer','steward','guest'}
 assert len({role['uid'] for role in roles.values()})==len({role['gid'] for role in roles.values()})==3
 for name_role,role in roles.items():
  assert role['uid'] not in (0,os.geteuid()) and role['User']==role['Group']=='codi-'+name_role
  assert role['ProtectSystem']=='strict' and role['ProtectHome']=='yes' and role['NoNewPrivileges']=='yes' and not role['CapabilityBoundingSet'] and not role['AmbientCapabilities']
  assert len(record['unixCredentialAccessProbes'][name_role])==19 and all(probe['allowed']==probe['expected'] for probe in record['unixCredentialAccessProbes'][name_role])
  sockets=record['nativeSocketPermissions'][name_role];assert sockets['uid']==role['uid'] and sockets['gid']==role['gid'] and not sockets['groups'] and not sockets['raw'] and sockets['ping']==(name_role=='guest')
  account=record['accounts']['accounts'][name_role];assert account['locked'] and account['uid']==role['uid'] and account['gid']==role['gid']
 assert roles['issuer']['nativeUid']==roles['issuer']['uid']
 assert len(record['qemuChildrenUnderGuestAccount'])>=2
 for child in record['qemuChildrenUnderGuestAccount']:
  assert child['uid']==roles['guest']['uid'] and child['gid']==roles['guest']['gid'] and set(child['groups'])<={roles['guest']['gid']}
  assert int(child['effectiveCapabilities'],16)==0 and child['noNewPrivileges']=='1'
 policy=record['pingGroupPolicy'];assert policy['before']==policy['after'] and not policy['persistentSettingWritten']
 assert set(range(*[int(policy['during'][0]),int(policy['during'][1])+1]))=={int(policy['before'][0]),roles['guest']['gid']}
 browser=record['browser'];assert browser['bidirectionalRTC'] and browser['separateRoomChatAndMoves'] and browser['guestAndIdentityPreserved'] and browser['identityTrust']=='test-server'
 assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
 assert record['identity']['realGuestBoot'] and record['identity']['wrongPasswordRejected']
assert receipts['service-accounts-result.json']['unitTests']==14 and receipts['service-accounts-result.json']['realOccupiedGidRefusedBeforeMutation'] and receipts['service-accounts-result.json']['existingAccountsNotChanged']
assert len(receipts['guest-relay-result.json']['checks'])==65 and receipts['connected-release-result.json']['tests']==12
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];browser=full['browser']
assert full['releaseAfterExecutionVerified'] and full['childrenReaped'] and full['stewardReaped'] and not full['cleanupErrors'] and full['credentialFilesRemoved'] and full['disposableRuntimeRemoved'] and full['disposableRootAuthorityRemoved']
assert browser['stewardCrash']['sameProvisionedWorkerRecovered'] and browser['rootPolicyRenewal']['revision']==2 and browser['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert len(browser['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in browser['guestInternet'])
assert all(witness['localCandidateType']==witness['remoteCandidateType']=='relay' and witness['localRelayProtocol']=='tls' for witness in browser['witnesses'])
assert full['release']['manifestSHA256']==receipts[names[0]]['release']['manifestSHA256']==receipts[names[1]]['release']['manifestSHA256']
spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
release=Path(full['release']['directory']);assert exporter.verify(release)==full['release']
manifest=json.loads((release/'connected-release.json').read_text());assert manifest['version']=='codi-connected-development/4'
for name in exporter.NATIVE:assert exporter.record(ROOT/name)==manifest['files'][name],name
assert receipts['managed-roles-prototype-boundary-result.json']['localIdentityNoApiOrGuestRelay']
assert Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==receipts[names[0]]['pingGroupPolicy']['before']
result={'status':'PASS','observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Three locally locked persistent account roles, real guest Internet/RTC and existing combined TURN compatibility; no permanent deployed service, public TLS or WAN claim','receipts':{name:hashlib.sha256((checks/name).read_bytes()).hexdigest() for name in names},'manifestSHA256':full['release']['manifestSHA256'],'unixAccessProbesAcrossBothLayouts':114,'fullObjectiveComplete':False,'checkerSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(checks/'managed-roles-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
