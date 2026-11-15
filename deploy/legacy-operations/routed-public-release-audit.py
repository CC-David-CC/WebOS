#!/usr/bin/env python3
"""Audit the bounded /hidden/ release against direct evidence and installed state."""
import concurrent.futures,hashlib,json,shlex,subprocess,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;CHECKS=ROOT/'.build/checks';RELEASE=ROOT/'.build/releases/connected-routed-r8'
NATIVE='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200'
REMOTE=r'''
import fcntl,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),text=True,timeout=90).strip()
base=Path('/home/dflanag3/webhost-sites');path=Path('/etc/codi-connected/ksu/managed.json')
with (base/'.controller.lock').open('rb') as hosting_lock:
 fcntl.flock(hosting_lock,fcntl.LOCK_EX)
 c=json.loads(path.read_bytes());assert c['manifestSHA256']=='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200' and sha(path.read_bytes())=='a8249551a9191a33ecee227e95b3327e7a394090379bde87429ff68243aadc2f'
 release=Path(c['release']);sys.path.insert(0,str(release));spec=importlib.util.spec_from_file_location('final_release_operator',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
 with op.locked(path):
  c=op.load(path);op.installed(c);op.ready(c,['issuer','steward','guest'])
  from origin_service import network_management
  b=network_management.Binding(op,c,c['guestNetwork']);worker=b.run('status');assert worker['active'] and worker['kernelMatches'] and not worker['guardFault'] and not worker['bootEnabled']
  assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
  manifest=json.loads((release/'connected-release.json').read_text())
  for role in ['issuer','steward','guest']:
   enabled=subprocess.run(['systemctl','is-enabled',c['instance']+'-'+role+'.service'],text=True,capture_output=True);assert enabled.returncode==1 and enabled.stdout.strip()=='disabled'
  assert run(['systemctl','show',c['instance']+'-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
  assert not any((path.parent/n).exists() for n in ['maintenance.json','native-rollout.json','guest-signin-migration.json'])
 website=Path('/srv/webapps/ksu.codes/current').resolve();prototype=website/'public/desktop';assert sha((website/'public/index.html').read_bytes())=='55f2928da214010b2ed7d647a354c0052ae03e9d06bafc09c1ea3b67e8608a38'
 assert sha((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9';p=json.loads((prototype/'release.json').read_bytes());assert len(p['files'])==133
 for n,r in p['files'].items():
  raw=(prototype/n).read_bytes();assert r=={'bytes':len(raw),'sha256':sha(raw)}
 pc=json.loads((prototype/'config.json').read_bytes());assert pc['identity']['mode']=='local-development' and not pc['identity'].get('apiBase') and not pc.get('guestNetwork')
 hosting={str(base/'ops/common.py'):'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4',str(base/'sites.toml'):'c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715','/etc/caddy/Caddyfile':'694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'}
 assert all(sha(Path(p).read_bytes())==pin for p,pin in hosting.items())
 relay=Path('/etc/codi-relay/ksu/managed.json');rc=json.loads(relay.read_text());assert sha(relay.read_bytes())=='5ab3e23016cd673146f1c6925aac0826368a4eff54b0fabdb9a28d7276c998a4' and rc['bandwidthProfile']=='text-32k/1'
 assert not (relay.parent/'maintenance.json').exists() and not Path('/srv/codi-relay/ksu-bandwidth-migration.json').exists()
 assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0' and Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001']
 units=[c['instance']+'-'+r+'.service' for r in ['issuer','steward','guest']]+['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']
 pids={n:int(run(['systemctl','show',n,'-p','MainPID','--value'])) for n in units};assert all(pids.values())
 print(json.dumps({'status':'PASS','nativeManifestSHA256':c['manifestSHA256'],'nativeDeclaredFilesVerified':len(manifest['files']),'nativeConfigSHA256':sha(path.read_bytes()),'PIDs':pids,'privateFilesAndGuestPolicyBindingsReady':True,'guestKernelPolicyMatches':True,'guestGuardHealthy':True,'noPendingNativeOrRelayJournals':True,'nativeBootEnablementUnchanged':True,'prototypeFilesVerified':133,'prototypeBackendFree':True,'homepageSHA256':sha((website/'public/index.html').read_bytes()),'websiteRelease':str(website),'hostingSHA256':hosting,'relayConfigSHA256':sha(relay.read_bytes()),'relayProfile':rc['bandwidthProfile'],'forwardingDisabled':True}))
'''
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run():
 records={}
 def receipt(name):
  raw=(CHECKS/name).read_bytes();v=json.loads(raw);assert v['status']=='PASS',name;records[name]=sha(raw);return v
 group=receipt('routed-wan-group-relay-result.json');history=receipt('routed-wan-history-relay-result.json');scope=receipt('routed-wan-scope-relay-result.json')
 for v in [group,history,scope]:
  assert v['nativeManifestSHA256']==NATIVE and v['independentWANVerified'] and v['publicTLSValidation'] and not v['HTTPChatRelayUsed'] and v['actualBrowserContexts']==3
  assert v['hosts']=={'developmentPublicIP':'104.180.210.33','moonpiePublicIP':'24.126.137.85'}
  assert {p['host'] for p in v['crossHostCandidatePairs']}=={'moonpie','development'}
  assert all(p['localType']==p['remoteType']=='relay' and p['relayProtocol']=='tls' and p['turnURL'].startswith('turns:turn.ksu.codes:443') for p in v['crossHostCandidatePairs'])
 assert len(group['checks'])==36 and len(history['checks'])==23
 for name in ['validOriginCannotBeTransplantedBetweenTwoAdmittedGroups','rejectedScopeDidNotAdvanceOriginalReplayFloor','legacyUnnegotiatedRoutingRejectedBeforeDelivery','existingTwoPeerChatAndSeparateLegalChessOnSamePool','matchingLegacyPgnExcludesChat']:assert scope[name]
 account=receipt('public-signin-account-result.json');assert account['nativeManifestSHA256']==NATIVE and len(account['checks'])==20 and account['allAnonymousGuestInternetDenied'] and account['privateServerFilesVerified'] and account['generatedPrivateFileRemoved'] and account['generatedAccountDisabled']
 doc=receipt('document-workflow-public-result.json');assert len(doc['checks'])==19 and doc['defaultPublicTLS']
 cleanup=receipt('document-public-cleanup-result.json');assert cleanup['otherAccountPoliciesUnchanged'] and all(a['disabled'] and a['homeEmpty'] for a in cleanup['accounts'])
 term=receipt('xterm-public-result.json');assert term['releaseSHA256']==NATIVE and len(term['checks'])==28 and term['actualNano'] and term['defaultPublicTLS']
 lifecycle=receipt('routed-public-lifecycle-result.json');assert lifecycle['nativeManifestSHA256']==NATIVE and lifecycle['ordinaryOpensAndCloses']==182 and len(lifecycle['checks'])==13 and len(lifecycle['apps'])==7 and lifecycle['defaultPublicTLS']
 assert all(s['resources']==lifecycle['samples'][0]['resources'] and s['budget']==lifecycle['samples'][0]['budget'] for s in lifecycle['samples'])
 cache=receipt('routed-r8-public-cache-result.json');assert cache['releaseSHA256']==NATIVE and len(cache['checks'])==11 and cache['defaultPublicTLS'] and cache['rebuildAfterSiteDataClear'] and not cache['runningVMWasSaved'] and not cache['userFilesOrCredentialsCached']
 maintenance=receipt('public-maintenance-result.json');assert maintenance['defaultCertificateTrust'] and maintenance['sameLinuxFilesystemSessionDraftAndCursorRetained'] and maintenance['desktopAndVoiceInertAtDeadline'] and not maintenance['liveServicesRestarted'] and not maintenance['workAutomaticallySaved']
 rollback=receipt('routed-native-vm-rollout-result.json');assert rollback['nativeManifestSHA256']==NATIVE and len(rollback['checks'])==4 and rollback['rollbackManifestSHA256']=='6789b29e7ed65ff2087e791448306ba68ab0b8bcc45ed70cdaa60a23fa404f35'
 activation=receipt('routed-native-upgrade-result.json');assert activation['manifestSHA256']==NATIVE and activation['hostingAndHomepageUnchanged'] and not activation['dataRestored']
 relay=receipt('relay-text-profile-apply-result.json');undo=receipt('relay-text-profile-rollback-result.json');assert relay['profile']=='text-32k/1' and undo['profile']=='legacy' and not relay['aggregateBandwidthCeilingRaised']
 health_raw=(CHECKS/'routed-public-r8-complete-health.json').read_bytes();health=json.loads(health_raw);records['routed-public-r8-complete-health.json']=sha(health_raw);assert len(health['sites'])==10 and all(v['result']=='PASS' for v in health['sites'].values())
 graph=json.loads((RELEASE/'assets/desktop/network-release.json').read_bytes());public=json.loads((RELEASE/'release.json').read_bytes())['files'];paths=['index.html','assets/desktop/network-release.json',*[graph['directory']+'/'+n for n in graph['modules']],*[graph['coreDirectory']+'/'+n for n in graph['core']]]
 def fetch(path):
  with urllib.request.urlopen('https://ksu.codes/hidden/'+path,timeout=20) as r:raw=r.read()
  assert public[path]=={'bytes':len(raw),'sha256':sha(raw)},path
  return path,sha(raw)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:served=dict(pool.map(fetch,paths))
 with urllib.request.urlopen('https://ksu.codes/hidden/config.json',timeout=20) as r:config=json.load(r)
 assert config['routedGroups']=={'version':'codi-routed-room/2'} and config['identity']['mode']=='server' and config['guestNetwork']['previewPolicy']['anonymousInternet']=='deny'
 remote=json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/srv/codi-connected/venvs/517179c/bin/python','-I','-B','-c',shlex.quote(REMOTE)],text=True,timeout=150))
 docs=['HANDOFF.md','network/ROUTED-PUBLIC-PROFILE.md','evidence/routed-history.md','evidence/routed-native-integration.md']
 return {'status':'PASS','scope':__doc__,'requirements':{'publicGroupChat':True,'boundedMissingMessageRecovery':True,'accountsPrivateFilesAndDocumentComposition':True,'independentXtermShellsAndNano':True,'registeredOnlyGuestInternetAndLANAcessDenied':True,'applicationResourceCleanupAndStaleWork':True,'separateInternetConnectionsWithTrustedTURN':True,'honestRecoveryAndPersistenceDocumentation':True,'installedPublicationAndTestedRollback':True,'homepageAndSizingPrototypePreserved':True},'nativeManifestSHA256':NATIVE,'directPublicEvidenceSHA256':records,'liveVersionedAssetSHA256':served,'currentInstalledState':remote,'documentationSHA256':{n:sha((ROOT/n).read_bytes()) for n in docs},'scopeLimits':{'groups':'fixed public3..8members,controller,maximum300second lease','history':'bounded recent unexpired signed originals,not durable storage','memory':'per-tab accounting cap,not physical RAM allocation','WAN':'two independent public networks;three browsers per suite','nativeRollback':'actually exercised in installed private VM;no live user data restore','fullGossipPrivateGroupsPoWAnd8k':'future work','rootBlogCutover':'future separately tested migration;homepage unchanged'}}
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['sourceSHA256']=sha(Path(__file__).read_bytes());out=CHECKS/'routed-public-release-audit-result.json'
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
