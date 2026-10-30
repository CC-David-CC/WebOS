#!/usr/bin/env python3
"""Read installed root bindings, preserved identity/account records and public bytes."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import fcntl,hashlib,importlib.util,json,pathlib,sqlite3,subprocess,sys,datetime
P=pathlib.Path;b=P('/home/dflanag3/webhost-sites');path=P('/etc/codi-connected/ksu/managed.json');sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
with (b/'.controller.lock').open('rb') as hosting:
 fcntl.flock(hosting,fcntl.LOCK_EX|fcntl.LOCK_NB);c=json.loads(path.read_text());assert c['basePath']=='' and c['origin']=='https://ksu.codes' and c['manifestSHA256']=='c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1'
 release=P(c['release']);sys.path[:0]=[str(release),str(b/'ops')];s=importlib.util.spec_from_file_location('root_health_native',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(s);sys.modules[s.name]=op;s.loader.exec_module(op)
 with op.locked(path):
  op.load(path);op.ready(c,op.ROLES)
  from origin_service import maintenance,network_management
  assert not any((path.parent/n).exists() for n in ['site-cutover.json','maintenance.json','native-rollout.json','guest-signin-migration.json'])
  receipt=json.loads(op.read_owned(path.parent/'site-cutover-last.json',0,0o600));assert receipt['status']=='site-cutover-completed' and not receipt['dataRestored'] and receipt['basePath']==''
  code=json.loads(op.read_owned(path.parent/'native-rollout-last.json',0,0o600));backup=maintenance.verify_backup(op,P(code['checkpoint']['directory']),code['checkpoint']['manifestSHA256'])
  saved=backup['binding'];current=maintenance.binding(P(c['stateRoot']))
  for n in ['issuerKeyId','rootKeyId','realm','serviceKeyId']:assert saved[n]==current[n]
  assert current['rootRevision']==3 and current['publisherRevision']>=saved['publisherRevision']
  for name in ['issuer/state/issuer.pem','operator/root/root.pem','steward/service.pem']:assert sha(P(c['stateRoot'])/name)==backup['files'][name]['sha256']
  def rows(file):
   with sqlite3.connect(file.as_uri()+'?mode=ro',uri=True) as db:return {hashlib.sha256(json.dumps(r,separators=(',',':')).encode()).hexdigest() for r in db.execute('SELECT username,subject,password_hash,created FROM accounts')}
  before=rows(P(code['checkpoint']['directory'])/'state/issuer/state/accounts.sqlite3');after=rows(P(c['stateRoot'])/'issuer/state/accounts.sqlite3');assert before<=after
  worker=network_management.Binding(op,c,c['guestNetwork']).run('status');assert worker['active'] and worker['kernelMatches'] and not worker['guardFault'] and not worker['bootEnabled']
  assert c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
  pids={}
  for role in op.ROLES:
   unit=op.unit(c,role);pid=int(op.systemctl('show',unit,'-p','MainPID','--value'));assert pid>0 and op.systemctl('show',unit,'-p','UnitFileState','--value').strip()=='disabled';pids[role]=pid
   status=dict(line.split(':',1) for line in P('/proc',str(pid),'status').read_text().splitlines());assert int(status['Uid'].split()[0])>0 and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
  assert op.systemctl('show',op.unit(c,'issuer-bootstrap'),'-p','MainPID','--value').strip()=='0'
  provision=json.loads((P(c['stateRoot'])/'steward/provision.json').read_text());from steward.protocol import jose
  seed=jose.inspect(provision['seed'],'codi-seed/1',32768)[1];assert seed['revision']==3
 website=P('/srv/webapps/ksu.codes/current').resolve();assert website.name==receipt['website']['current'];prototype=website/'public/desktop';m=json.loads((prototype/'release.json').read_text());assert len(m['files'])==133 and sha(prototype/'release.json')=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for n,r in m['files'].items():assert r=={'bytes':(prototype/n).stat().st_size,'sha256':sha(prototype/n)}
 cfg=json.loads((prototype/'config.json').read_text());assert cfg['identity']['mode']=='local-development' and not cfg['identity'].get('apiBase') and not cfg.get('guestNetwork')
 import common;assert common.caddy(common.load(),'production')==P('/etc/caddy/Caddyfile').read_text()
 hosting_sha={n:sha(p) for n,p in [('generator',b/'ops/common.py'),('manifest',b/'sites.toml'),('Caddy',P('/etc/caddy/Caddyfile')),('smoke',b/'ops/production-smoke.py')]}
 assert hosting_sha['generator']=='c3181a47ed0b9489bf2b6093ce2f54e62bab089560eb57eec86c6f0ec0c290e7' and hosting_sha['manifest']=='f583f6f43f5b03d1e48afd71567f0c508373a7073c1bfc5add1dd75a591bee12' and hosting_sha['Caddy']=='4cf23397bd3d1885e8f2c386072633c9ffec36459811753bce68866b50252bb5'
 smoke=json.loads((b/'reports/private/root-cutover-smoke.json').read_text());assert len(smoke['sites'])==10 and all(v['result']=='PASS' for v in smoke['sites'].values()) and smoke['sites']['ksu.codes']['root_desktop_verified'] and smoke['sites']['ksu.codes']['homepage_path']=='/blog/'
 assert sha('/etc/codi-relay/ksu/managed.json')=='5ab3e23016cd673146f1c6925aac0826368a4eff54b0fabdb9a28d7276c998a4' and P('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
 print(json.dumps({'status':'PASS','nativeManifestSHA256':c['manifestSHA256'],'nativeConfigSHA256':sha(path),'release':str(release),'basePath':'','nativePIDs':pids,'nativeUnitsDisabledForBoot':True,'verifiedReleaseFiles':len(json.loads((release/'connected-release.json').read_text())['files']),'noPendingJournals':True,'rootRevision':3,'rootExpiresAt':datetime.datetime.fromtimestamp(seed['exp'],datetime.timezone.utc).isoformat(),'publisherRevision':current['publisherRevision'],'keysRealmServiceIdentityUnchanged':True,'existingAccountsPreserved':len(before),'currentAccountCount':len(after),'guestCookiePreservedByCodeRollout':code['guestCookiePreserved'],'prototypeFilesVerified':133,'prototypeBackendFree':True,'websiteRelease':str(website),'blogSHA256':sha(website/'public/index.html'),'hostingSHA256':hosting_sha,'all10SiteSmoke':'PASS','rootBranchTestedByLiveSmoke':True,'guestKernelGuardHealthy':True,'registeredOnlyEgressPolicyUnchanged':True,'relayConfigUnchanged':True,'forwardingDisabled':True,'siteRootReceipt':str(path.parent/'site-cutover-last.json'),'servicesRestarted':False}))
'''


if __name__ == '__main__':
    bootstrap = "import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_text());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', 'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(bootstrap)], input=REMOTE, capture_output=True, text=True, timeout=180)
    if child.returncode:raise ValueError(child.stderr[-5000:] or child.stdout[-3000:])
    result = json.loads(child.stdout)
    release = ROOT/'.build/releases/connected-root-cache-r2'
    for name in ['index.html', 'assets/desktop/network-release.json', 'assets/desktop/offline-worker.js']:
        with urllib.request.urlopen('https://ksu.codes/'+name, timeout=20) as response:assert response.read() == (release/name).read_bytes()
    result.update(defaultPublicTLS=True, publicAssetsMatched=3, sourceSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    output = ROOT/'.build/checks/root-live-health-result.json'
    if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(time.time_ns())+'.json'))
    output.write_text(json.dumps(result, indent=2)+'\n');print(json.dumps(result, indent=2))
