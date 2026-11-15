#!/usr/bin/env python3
"""Guarded native10 update for distinct Register/Sign in and optional account UI."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = '7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625'
REMOTE = r'''
import fcntl,hashlib,http.client,json,os,pathlib,pwd,shutil,socket,ssl,stat,subprocess,sys,tempfile,time,tomllib
Path=pathlib.Path;inputs=json.load(sys.stdin);action=inputs['action'];expected=inputs['manifestSHA256'];commit=inputs['commit']
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
assert os.geteuid()==0 and action in ['plan','install','upgrade','recover']
checkout=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');hosting=checkout.parent.parent
assert run(['runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==commit
assert not run(['runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
source=checkout/'tools/codiserver/native-candidates'/expected
raw=(source/'connected-release.json').read_bytes();assert digest(raw)==expected
metadata=json.loads(raw);assert metadata['version']=='codi-connected-development/10' and len(metadata['files'])==189
def read_file(file,record):
 for parent in [file,*file.parents]:assert not parent.is_symlink()
 with os.fdopen(os.open(file,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as stream:
  info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==record['bytes'] and 0<=info.st_size<=134217728
  value=stream.read(info.st_size+1);assert len(value)==info.st_size and digest(value)==record['sha256'];return value
for name,record in metadata['files'].items():
 assert isinstance(name,str) and not Path(name).is_absolute() and all(part not in ['','.','..'] for part in name.split('/'))
 read_file(source/name,record)
assert {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}=={'connected-release.json',*metadata['files']}
script_source=checkout/'tools/codiserver/native-rollout/scripts/native-rollout.py'
script=read_file(script_source,{'bytes':inputs['rolloutBytes'],'sha256':inputs['rolloutSHA256']})
destination=Path('/srv/codi-connected/releases')/('native10-'+expected[:16])
controller=Path('/srv/codi-connected/rollout-controllers')/inputs['rolloutSHA256']
config_path=Path('/etc/codi-connected/ksu/managed.json');current=json.loads(config_path.read_text());python=Path('/srv/codi-connected/venvs/517179c/bin/python')
assert current['instance']=='codi-ksu-hidden' and current['origin']=='https://ksu.codes' and current['basePath']=='/hidden'
assert current['stateRoot']=='/var/lib/codi-connected/ksu' and current['unitDir']=='/etc/systemd/system' and current['python']==str(python)
assert current['ports']=={'issuer':8118,'steward':8119,'guest':8132} and current['version']=='codi-managed-instance/3' and current['maintenance']==1
assert (current['release'],current['manifestSHA256']) in [('/srv/codi-connected/releases/native10-ced620b043b7054c','ced620b043b7054c17e4d943a987f8b3f959c21f63961894091b6088cbbd9058'),(str(destination),expected)]
before_config=current.copy()
pins={'ops/common.py':'8095d2a6387da16f1e64678f6d074e41990af74c3ae9f549869f13ab3daaf430','sites.toml':'bc0af355d73e4f5d9cf5d51aa3376cb989cb59f769d6baa47788c7cb87da127a'}
def unchanged_hosting():
 for name,value in pins.items():assert digest((hosting/name).read_bytes())==value
 assert digest(Path('/etc/caddy/Caddyfile').read_bytes())=='4af0c3a21383b1d64dd11c10bca63228a444f7f06720218f9b28f10393405677'
 assert Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001'] and Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
unchanged_hosting()
website=Path('/srv/webapps/ksu.codes/current').resolve();assert website.is_relative_to(Path('/srv/webapps/ksu.codes/releases'))
prototype={'release.json':'d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9','app.js':'2abb154d558cbc44149cfa46ddcc23c9d4843f822b8a44c5d392cd4bd2f88602','config.json':'5ec30b79a21a07911315ddd9714fba560fc3451004d51942ee53f36c0e6effad'}
for name,value in prototype.items():assert digest((website/'public/desktop'/name).read_bytes())==value
def protected(path,mode=None):
 for parent in [path,*path.parents]:
  info=parent.lstat();assert not stat.S_ISLNK(info.st_mode) and info.st_uid==info.st_gid==0 and not info.st_mode&0o022
 if mode is not None:assert stat.S_IMODE(path.stat().st_mode)==mode
def exact_release(folder):
 protected(folder,0o755);assert digest((folder/'connected-release.json').read_bytes())==expected
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}=={'connected-release.json',*metadata['files']}
 for name,record in metadata['files'].items():protected(folder/name,0o644);read_file(folder/name,record)
def install_release():
 protected(destination.parent)
 if destination.exists():exact_release(destination);return
 stage=Path(tempfile.mkdtemp(prefix='.native10-',dir=destination.parent))
 try:
  for name,record in metadata['files'].items():
   value=read_file(source/name,record);file=stage/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(value);file.chmod(0o644)
  (stage/'connected-release.json').write_bytes(raw);(stage/'connected-release.json').chmod(0o644)
  for directory in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:directory.chmod(0o755)
  exact_release(stage);os.rename(stage,destination)
 finally:
  if stage.exists():shutil.rmtree(stage)
 exact_release(destination)
def install_controller():
 if not controller.parent.exists():controller.parent.mkdir(mode=0o755)
 protected(controller.parent,0o755)
 if not controller.exists():
  stage=Path(tempfile.mkdtemp(prefix='.rollout-',dir=controller.parent))
  try:
   file=stage/'native-rollout.py';file.write_bytes(script);file.chmod(0o644)
   with file.open('rb') as stream:os.fsync(stream.fileno())
   stage.chmod(0o755);os.rename(stage,controller)
   fd=os.open(controller.parent,os.O_RDONLY|os.O_DIRECTORY)
   try:os.fsync(fd)
   finally:os.close(fd)
  finally:
   if stage.exists():shutil.rmtree(stage)
 protected(controller,0o755);protected(controller/'native-rollout.py',0o644)
 assert set(p.name for p in controller.iterdir())=={'native-rollout.py'} and digest((controller/'native-rollout.py').read_bytes())==inputs['rolloutSHA256']
def pids():return {role:run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','--value']) for role in ['issuer','steward','guest']}
def request(path):
 connection=http.client.HTTPSConnection('ksu.codes',timeout=10);connection.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  connection.request('GET',path);response=connection.getresponse();body=response.read(4194305);assert len(body)<=4194304;return response.status,body
 finally:connection.close()
frontend='8acbd0f506fddd04ef02499514e0bfa19144937b47afee699cf8deafcf7b4f3d'
assets=json.loads((Path('/srv/codi-connected/frontends')/frontend/'frontend.json').read_text())['files']
def public_assets():
 for name,record in assets.items():
  status,body=request('/hidden/'+name);assert status==200 and digest(body)==record['sha256']
 for name,value in prototype.items():
  status,body=request('/desktop/'+name);assert status==200 and digest(body)==value
public_assets();before=pids()
if action not in ['recover']:assert all(int(value)>0 for value in before.values()) and not (config_path.parent/'maintenance.json').exists() and not (config_path.parent/'native-rollout.json').exists()
assert run(['systemctl','show','codi-ksu-hidden-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
report={'status':'PASS','action':action,'sourceCommit':commit,'candidateManifestSHA256':expected,'installedRelease':str(destination),'rolloutControllerSHA256':inputs['rolloutSHA256'],'frontendManifestSHA256':frontend,'beforePids':before,'nativePolicyAndHostingUnchanged':True,'prototypeSHA256':prototype}
if action=='plan':
 report['scope']='Read-only validation of exact source/native baseline, public frontend, prototype, current managed routing and ports; no installation or restart'
 print(json.dumps(report));raise SystemExit(0)
install_release();install_controller()
if action in ['upgrade','recover']:
 backups=Path('/var/backups/codi-connected/ksu');protected(backups,0o700)
 command=[python,'-I','-B',controller/'native-rollout.py','recover' if action=='recover' else 'upgrade','--operator',destination/'scripts/manage-services.py','--operator-manifest-sha256',expected,'--config',config_path]
 if action=='upgrade':command+=['--release',destination,'--python',python,'--backup-parent',backups]
 report['rollout']=json.loads(run(command,300))
else:assert pids()==before
unchanged_hosting();public_assets();assert Path('/srv/webapps/ksu.codes/current').resolve()==website
after=json.loads(config_path.read_text());assert {k:v for k,v in before_config.items() if k not in ['release','manifestSHA256']}=={k:v for k,v in after.items() if k not in ['release','manifestSHA256']}
for role in ['issuer','steward','guest']:
 response=subprocess.run(['systemctl','is-enabled','codi-ksu-hidden-'+role+'.service'],capture_output=True,text=True);assert response.returncode in [0,1] and response.stdout.strip()=='disabled'
if action=='upgrade':assert after['release']==str(destination) and after['manifestSHA256']==expected
report['afterPids']=pids();report['nativeConfigVersion']=after['version'];report['onlineRoleRelease']=after['release'];report['issuerTurnPolicyConfigured']=True
report['scope']='Authenticated root-owned code/controller installation and optional recoverable native rollout; account/authority data never restored, current R12/prototype/hosting/ports retained'
receipt=Path('/srv/codi-connected')/('native10-'+action+'-'+str(time.time_ns())+'-result.json')
fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as output:json.dump(report,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
report['rootReceipt']=str(receipt);report['rootReceiptSHA256']=digest(receipt.read_bytes());print(json.dumps(report))
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--action', choices=['plan', 'install', 'upgrade', 'recover'], default='plan')
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.commit):
        parser.error('An exact reviewed source commit is required')
    raw = (ROOT / 'scripts/native-rollout.py').read_bytes()
    inputs = {'action': args.action, 'commit': args.commit, 'manifestSHA256': EXPECTED,
              'rolloutSHA256': hashlib.sha256(raw).hexdigest(), 'rolloutBytes': len(raw)}
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                            'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(REMOTE)],
                           input=json.dumps(inputs), text=True, capture_output=True, timeout=450)
    if child.returncode:
        raise SystemExit(child.stderr or child.stdout)
    report = json.loads(child.stdout)
    (ROOT / '.build/checks' / ('account-menu-native-webhost-' + args.action + '-result.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
