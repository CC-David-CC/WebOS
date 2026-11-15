#!/usr/bin/env python3
"""Read current live preview roles, hosting pins and activation smoke evidence."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,pathlib,pwd,subprocess,sys
sys.path.insert(0,"/home/dflanag3/webhost-sites/ops");import common
Path=pathlib.Path;config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text());processes={}
assert (config['release'],config['manifestSHA256']) in [('/srv/codi-connected/releases/f2fbd4d','e6bd7e6df07544c58ce57efe3672f18df793dd5fbea381d05d89f2953f0baace'),('/srv/codi-connected/releases/native10-ced620b043b7054c','ced620b043b7054c17e4d943a987f8b3f959c21f63961894091b6088cbbd9058'),('/srv/codi-connected/releases/native10-7705a87e09c44e22','7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625')]
for name in ['maintenance.json','native-rollout.json']:assert not (Path('/etc/codi-connected/ksu')/name).exists()
def run(args):return subprocess.run(args,check=True,capture_output=True,text=True).stdout
for role in ['issuer','steward','guest']:
 unit=dict(line.split('=',1) for line in run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','-p','ActiveState','-p','FragmentPath','-p','ProtectSystem','-p','NoNewPrivileges','-p','CapabilityBoundingSet']).splitlines());pid=int(unit['MainPID']);assert pid>0 and unit['ActiveState']=='active'
 assert unit['FragmentPath']=='/etc/systemd/system/codi-ksu-hidden-'+role+'.service' and unit['ProtectSystem']=='strict' and unit['NoNewPrivileges']=='yes' and unit['CapabilityBoundingSet']==''
 status=dict(line.split(':',1) for line in (Path('/proc')/str(pid)/'status').read_text().splitlines());user=pwd.getpwnam('codi-'+role)
 program={'issuer':'scripts/serve-connected.py','steward':'scripts/serve-steward.py','guest':'guest-relay/server.py'}[role];assert (config['release']+'/'+program).encode() in (Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
 assert user.pw_uid>0 and set(map(int,status['Uid'].split()))=={user.pw_uid} and set(map(int,status['Gid'].split()))=={user.pw_gid} and set(map(int,status['Groups'].split()))<={user.pw_gid}
 assert int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
 assert subprocess.run(['systemctl','is-enabled','codi-ksu-hidden-'+role+'.service'],capture_output=True,text=True).stdout.strip()=='disabled'
 processes[role]={'pid':pid,'uid':user.pw_uid,'gid':user.pw_gid,'groups':list(map(int,status['Groups'].split())),'capabilities':status['CapEff'].strip(),'noNewPrivileges':status['NoNewPrivs'].strip()}
assert run(['systemctl','show','codi-ksu-hidden-issuer-bootstrap.service','-p','MainPID','--value']).strip()=='0'
data=common.load(Path('/home/dflanag3/webhost-sites/sites.toml'));shared=bool(data.get('codi_shared_ingress'))
pins={name:hashlib.sha256(Path(path).read_bytes()).hexdigest() for name,path in [('generator','/home/dflanag3/webhost-sites/ops/common.py'),('manifest','/home/dflanag3/webhost-sites/sites.toml'),('activeCaddy','/etc/caddy/Caddyfile')]}
key=next(s for s in data['sites'] if s['domain']=='ksu.codes')['codi_frontend']
candidates=[Path('/srv/codi-connected')/('frontend-'+key+'-activation-result.json'),Path('/srv/codi-ingress/ksu-shared-ingress-activation-result.json')]
hosting_activation=None
for path in candidates:
 if not path.is_file():continue
 receipt=json.loads(path.read_text())
 if receipt.get('status')=='PASS' and pins=={'generator':receipt.get('generatorSHA256'),'manifest':receipt.get('manifestSHA256'),'activeCaddy':receipt.get('activeCaddySHA256')}:
  hosting_activation=path;break
assert hosting_activation is not None,'No root activation receipt matches the actual current hosting inputs'

hosting_receipt=json.loads(hosting_activation.read_text());smoke_path=Path(hosting_receipt['allSiteSmoke']);smoke=json.loads(smoke_path.read_text());sites={name:value['result'] for name,value in smoke['sites'].items()};domains={s['domain'] for s in data['sites'] if s['enabled']};assert len(domains)==9 and set(sites)==domains and set(sites.values())=={'PASS'};assert Path('/etc/caddy/Caddyfile').read_text()==common.caddy(data,'production')
pins={name:hashlib.sha256(Path(path).read_bytes()).hexdigest() for name,path in [('generator','/home/dflanag3/webhost-sites/ops/common.py'),('manifest','/home/dflanag3/webhost-sites/sites.toml'),('activeCaddy','/etc/caddy/Caddyfile')]}
key=next(s for s in data['sites'] if s['domain']=='ksu.codes')['codi_frontend'];activation=json.loads((Path('/srv/codi-connected')/('frontend-'+key+'-activation-result.json')).read_text());assert activation['status']==hosting_receipt['status']=='PASS' and pins=={'generator':hosting_receipt['generatorSHA256'],'manifest':hosting_receipt['manifestSHA256'],'activeCaddy':hosting_receipt['activeCaddySHA256']}
frontend=Path('/srv/codi-connected/frontends')/key;raw=(frontend/'frontend.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==frontend.name
for name,record in json.loads(raw)['files'].items():assert record=={'bytes':(frontend/name).stat().st_size,'sha256':hashlib.sha256((frontend/name).read_bytes()).hexdigest()}
speech=Path('/srv/codi-connected/speech/df759266dbd1cc339c4cd96df8265e274b9b9042abef275d00fc0809deed1f3b');speech_raw=(speech/'speech.json').read_bytes();assert hashlib.sha256(speech_raw).hexdigest()==speech.name
speech_records=json.loads(speech_raw)['files'];assert len(speech_records)==22
for name,record in speech_records.items():
 file=speech/name;assert not file.is_symlink() and file.stat().st_uid==file.stat().st_gid==0 and record=={'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
ping=Path('/proc/sys/net/ipv4/ping_group_range').read_text().split();assert ping==['1000','1001'] and Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
policy=Path('/etc/sysctl.d/90-codi-guest-preview.conf');assert policy.stat().st_uid==0 and 'net.ipv4.ping_group_range = 1000 1001' in policy.read_text()
result={'status':'PASS','scope':'Live preview three-role process isolation, hosting/frontend pins, dedicated ping policy and nine-site activation smoke; no independent WAN claim','onlineRoleRelease':config['release'],'manifestSHA256':config['manifestSHA256'],'frontendManifestSHA256':frontend.name,'speechManifestSHA256':speech.name,'processes':processes,'siteResults':sites,'smokeObservedUTC':smoke['time'],'hostingSHA256':pins,'sharedIngressConfigured':shared,'publicTurnListenerConfigured':shared,'issuerTurnPolicyConfigured':config.get('turn') is not None,'hostingActivationReceiptPath':str(hosting_activation),'hostingActivationReceiptSHA256':hashlib.sha256(hosting_activation.read_bytes()).hexdigest(),'pingGroupRange':ping,'forwardingOff':True,'bootstrapInactive':True,'normalUnitsDisabledForBoot':True,'currentWebsite':str(Path('/srv/webapps/ksu.codes/current').resolve())}
website=Path(result['currentWebsite']);assert website.is_relative_to(Path('/srv/webapps/ksu.codes/releases')) and website.stat().st_uid==0 and not website.stat().st_mode&0o022
for name,expected in activation['desktopSHA256'].items():
 file=website/'public/desktop'/name;assert not file.is_symlink() and file.stat().st_uid==0 and not file.stat().st_mode&0o022 and hashlib.sha256(file.read_bytes()).hexdigest()==expected
result['currentWebsitePrototypeBytesPreserved']=True
result['bootstrapHTMLSHA256']=hashlib.sha256((Path(config['release'])/'index.html').read_bytes()).hexdigest()
if 'native10-' in config['release']:
 candidates=sorted(Path('/srv/codi-connected').glob('native10-upgrade-*-result.json'),key=lambda p:p.stat().st_mtime_ns,reverse=True)
 matches=[]
 for path in candidates:
  info=path.stat();assert not path.is_symlink() and info.st_uid==info.st_gid==0 and __import__('stat').S_IMODE(info.st_mode)==0o600
  value=json.loads(path.read_text())
  if value.get('status')=='PASS' and value.get('onlineRoleRelease')==config['release'] and value.get('rollout',{}).get('status')=='upgraded':matches.append((path,value))
 assert matches,'Missing applied native rollout proof'
 path,value=matches[0];assert value['rollout']['guestCookiePreserved'] and value['rollout']['keysAuthorityAndExistingAccountsPreserved']
 # A separately installed frontend may follow the native rollout. Its own
 # root activation must bind the current role PIDs and unchanged native config.
 if value['frontendManifestSHA256']!=key:
  assert activation['nativeConfigUnchanged'] and activation['nativePidsUnchanged']=={role:str(record['pid']) for role,record in processes.items()}
 result['nativeUpgradeReceiptPath']=str(path);result['nativeUpgradeReceiptSHA256']=hashlib.sha256(path.read_bytes()).hexdigest()
 source=Path('/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret');info=source.stat();assert info.st_uid==info.st_gid==0 and __import__('stat').S_IMODE(info.st_mode)==0o600 and source.parent.stat().st_mode&0o777==0o700
 from http.cookies import SimpleCookie
 import http.client
 connection=http.client.HTTPConnection('127.0.0.1',config['ports']['guest'],timeout=5)
 try:
  connection.request('GET','/',headers={'Host':'ksu.codes'});response=connection.getresponse();values=SimpleCookie();values.load(response.getheader('Set-Cookie'));assert response.status==200 and values['codi_guest_relay'].value.encode()==source.read_bytes()
 finally:connection.close()
 result['persistentCookieMatchesRunningGuest']=True
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':
 process=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-'],input=REMOTE,capture_output=True,text=True,timeout=45)
 if process.returncode:raise SystemExit(process.stderr or process.stdout)
 report=json.loads(process.stdout);(ROOT/'.build/checks/preview-touch-live-health-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
