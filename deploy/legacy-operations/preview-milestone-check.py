#!/usr/bin/env python3
"""Bind the bounded live preview evidence without claiming WAN/full completion."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));checks=ROOT/'.build/checks'
from origin_service.release import NATIVE,record,verify
names=['guest-relay-result.json','persistent-services-deployment-baseline-hidden-result.json','full-system-hidden-readonly-release-provisioned-result.json','connected-release-result.json','service-operator-result.json','preview-source-sync-result.json','preview-webhost-upgrade-result.json','preview-webhost-api-result.json','preview-webhost-proxy-validation-result.json','preview-webhost-activation-result.json','preview-public-browser-result.json','preview-public-identity-result.json','preview-live-health-result.json','preview-live-boundary-result.json']
receipts={name:json.loads((checks/name).read_text()) for name in names}
def digest(file):return hashlib.sha256(file.read_bytes()).hexdigest()
archives={'scripts/persistent-services-check.py':'persistent-services','scripts/identity-check.py':'identity','scripts/tls-discovery-check.py':'tls-discovery','scripts/full-system-check.py':'full-system'}
def sources(value):
 if isinstance(value,dict):
  for source,expected in value.get('sha256',{}).items():
   file=ROOT/source
   if digest(file)!=expected and source in archives:file=checks/'fixtures'/(archives[source]+'-'+expected+'.py')
   assert digest(file)==expected,source
  for child in value.values():sources(child)
 elif isinstance(value,list):
  for child in value:sources(child)
for name,receipt in receipts.items():assert receipt['status']=='PASS',name;sources(receipt)
manifest_sha='e6bd7e6df07544c58ce57efe3672f18df793dd5fbea381d05d89f2953f0baace';commit='f2fbd4d0497e71c82d24b29b277e155dbac2365d';installed='/srv/codi-connected/releases/f2fbd4d'
full=receipts['full-system-hidden-readonly-release-provisioned-result.json'];release=Path(full['release']['directory']);assert verify(release)==full['release'] and full['release']['manifestSHA256']==manifest_sha
manifest=json.loads((release/'connected-release.json').read_text());assert manifest['version']=='codi-connected-development/8'
for name in NATIVE:assert record(ROOT/name)==manifest['files'][name],name
relay=receipts['guest-relay-result.json']
for check in ['preview TCP port 80','preview TCP port 443','preview TCP port 22','preview arbitrary external UDP denied','session byte cap survives rate window reset','sequential sessions share a non-resetting cap','exhausted service refuses new QEMU','blocked packets consume traffic quota']:assert check in relay['checks']
baseline=receipts['persistent-services-deployment-baseline-hidden-result.json'];assert baseline['release']['manifestSHA256']==manifest_sha and baseline['nativeRoleBaseline']['manifestSHA256']=='69af311a1f1fd93bd45c900088be08790e590ca47f8200d7a7dd8b8919840ea2'
assert baseline['basePath']=='/hidden' and not baseline['cleanupErrors'] and baseline['disposableInstalledUnitsAndStateRemoved'] and baseline['pingPolicyRestoredAndForwardingUnchanged']
for key,value in baseline['deployment'].items():assert value,(key,value)
def browser(value):
 assert value['identityTrust']=='test-server' and value['bidirectionalRTC'] and value['separateRoomChatAndMoves'] and value['guestAndIdentityPreserved']
 assert len(value['guestInternet'])==2 and all(guest['pingReplies']==2 and guest['dnsAndHttp'] for guest in value['guestInternet'])
browser(baseline['browser']);browser(full['browser'])
assert full['readOnlyReleaseEnforced'] and full['releaseAfterExecutionVerified'] and full['childrenReaped'] and full['stewardReaped'] and not full['cleanupErrors'] and full['credentialFilesRemoved'] and full['disposableRuntimeRemoved'] and full['disposableRootAuthorityRemoved']
assert full['browser']['stewardCrash']['sameProvisionedWorkerRecovered'] and full['browser']['rootPolicyRenewal']['sameEstablishedPeerConnections']
assert all(w['localCandidateType']==w['remoteCandidateType']=='relay' and w['localRelayProtocol']=='tls' for w in full['browser']['witnesses'])
for name,count in [('connected-release-result.json',12),('service-operator-result.json',16)]:assert receipts[name]['tests']==count and receipts[name]['failures']==receipts[name]['errors']==0
sync=receipts['preview-source-sync-result.json'];upgrade=receipts['preview-webhost-upgrade-result.json'];api=receipts['preview-webhost-api-result.json'];activation=receipts['preview-webhost-activation-result.json'];health=receipts['preview-live-health-result.json']
assert sync['sourceCommit']==upgrade['sourceCommit']==commit and sync['publicAndAppTreesUnchanged'] and len(sync['changedFiles'])==7 and all(name.startswith('tools/codiserver/') for name in sync['changedFiles'])
assert upgrade['installedRelease']==api['onlineRoleRelease']==activation['nativeRelease']==health['onlineRoleRelease']==installed
assert upgrade['manifestSHA256']==api['manifestSHA256']==activation['nativeManifestSHA256']==health['manifestSHA256']==manifest_sha
assert upgrade['keysAccountsRootAndFenceUnchanged'] and upgrade['rollback']['status']=='rolled-back' and upgrade['finalUpgrade']['status']=='upgraded'
assert activation['publicPreviewEnabled'] and activation['forwardingUnchanged'] and activation['normalUnitsRemainDisabledForBoot'] and activation['pingGroupRange']==['1000','1001']
assert len(activation['eightSiteSmoke'])==8 and all(line.endswith(' PASS') for line in activation['eightSiteSmoke'])
assert len(health['siteResults'])==8 and set(health['siteResults'].values())=={'PASS'} and set(health['processes'])=={'issuer','steward','guest'}
for process in health['processes'].values():assert process['uid']>0 and set(process['groups'])<={process['gid']} and int(process['capabilities'],16)==0 and process['noNewPrivileges']=='1'
public=receipts['preview-public-browser-result.json'];browser(public);assert public['url']=='https://ksu.codes/hidden/' and public['defaultCertificateTrust'] and not public['untrustedCertificateRejected'] and public['privatePathsNotServed'] and public['foreignWssOriginRejected']
identity=receipts['preview-public-identity-result.json'];assert identity['cleanup']['disabled'] and identity['identity']['defaultCertificateTrust']
for flag in ['anonymousEntry','desktopRenewal','renewalSameKeyAndSession','stableAccountFreshSession','wrongPasswordRejected','logoutRevoked','foreignOriginRejected','foreignHostNotRoutedToIssuer','privatePathsNotServed']:assert identity['identity'][flag],flag
boundary=receipts['preview-live-boundary-result.json'];assert boundary['prototypeLocalIdentityNoApiOrGuestRelay'] and boundary['hiddenStatus']==200 and boundary['hiddenDevelopmentIdentityAndBoundedRelay'] and boundary['hiddenNoStoreAndScopedCsp'] and boundary['prototypeSHA256']==activation['desktopSHA256']
assert boundary['hiddenAppSHA256']==digest(ROOT/'app.js')
candidate=ROOT.parent/'.build/deployment/hosting-preview/candidate-r1';prepared=json.loads((candidate/'candidate-result.json').read_text());assert prepared['status']=='PASS'
assert digest(candidate/'common.preview.py')==activation['generatorSHA256']==health['hostingSHA256']['generator']==prepared['candidateGeneratorSHA256']
assert digest(candidate/'sites.preview.toml')==activation['manifestSHA256']==health['hostingSHA256']['manifest']==prepared['candidateManifestSHA256']
assert activation['activeCaddySHA256']==health['hostingSHA256']['activeCaddy']
clone=ROOT.parent/'.build/deployment/ksu.codes';assert subprocess.check_output(['git','-C',str(clone),'rev-parse','HEAD'],text=True).strip()==commit and not subprocess.check_output(['git','-C',str(clone),'status','--porcelain'],text=True).strip();assert verify(clone/'tools/codiserver/connected')['manifestSHA256']==manifest_sha
result={'status':'PASS','scope':'Bounded live hidden preview, public default-trusted Chrome identity/RTC/chess/v86/guest Internet from development network and preserved prototype; independent WAN/NAT and production approval remain open','nativeManifestSHA256':manifest_sha,'sourceCommit':commit,'previewURL':'https://ksu.codes/hidden/','receipts':{name:digest(checks/name) for name in names},'fullObjectiveComplete':False,'independentWanVerified':False,'publicTurnConfigured':False,'checkerSHA256':digest(Path(__file__))}
(checks/'preview-milestone-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key!='receipts'},indent=2))
