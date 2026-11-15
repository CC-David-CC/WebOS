#!/usr/bin/env python3
"""Reviewed private webhost code upgrade/rollback round trip; no public activation."""
import argparse,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,os,pathlib,shutil,stat,subprocess,sys
from pathlib import Path
commit,expected=sys.argv[1:];checkout=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');source=checkout/'tools/codiserver/connected'
def run(argv,timeout=60):return subprocess.run([str(x) for x in argv],check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
assert run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==commit
assert not run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
config_path=Path('/etc/codi-connected/ksu/managed.json');before=json.loads(config_path.read_text());state=Path(before['stateRoot']);python=Path(before['python'])
assert before['version']=='codi-managed-instance/2' and before['maintenance']==1 and before['instance']=='codi-ksu-hidden' and before['origin']=='https://ksu.codes' and before['basePath']=='/hidden'
assert before['release']=='/srv/codi-connected/releases/1db6187' and before['manifestSHA256']=='69af311a1f1fd93bd45c900088be08790e590ca47f8200d7a7dd8b8919840ea2'
assert state==Path('/var/lib/codi-connected/ksu') and python==Path('/srv/codi-connected/venvs/517179c/bin/python')
assert not (config_path.parent/'maintenance.json').exists()
website=Path('/srv/webapps/ksu.codes/current').resolve();assert str(website)=='/srv/webapps/ksu.codes/releases/20261021T125622370238Z-279f978f'
ping=Path('/proc/sys/net/ipv4/ping_group_range').read_text();forward=Path('/proc/sys/net/ipv4/ip_forward').read_text()
assert ping.split()==['1000','1000'] and forward.strip()=='0'
destination=Path('/srv/codi-connected/releases')/commit[:7]
assert not destination.exists()
# Authenticate every byte before importing/executing any new release code.
raw=(source/'connected-release.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
manifest=json.loads(raw);assert manifest['version']=='codi-connected-development/8' and len(manifest['files'])==164
def exact_tree(directory,root_owned=False):
 assert hashlib.sha256((directory/'connected-release.json').read_bytes()).hexdigest()==expected
 found=set()
 for file in [directory,*directory.rglob('*')]:
  info=file.lstat();assert not stat.S_ISLNK(info.st_mode)
  assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
  if root_owned:assert info.st_uid==0 and info.st_gid==0 and not info.st_mode&0o022
  if file.is_dir():continue
  assert info.st_nlink==1;name=str(file.relative_to(directory))
  if name=='connected-release.json':continue
  record=manifest['files'][name];assert info.st_size==record['bytes'] and hashlib.sha256(file.read_bytes()).hexdigest()==record['sha256'];found.add(name)
 assert found==set(manifest['files'])
exact_tree(source)
for parent in [destination.parent,*destination.parent.parents]:
 info=parent.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
shutil.copytree(source,destination,symlinks=True)
for file in [destination,*destination.rglob('*')]:
 assert not file.is_symlink();os.chown(file,0,0);file.chmod(0o755 if file.is_dir() else 0o644)
exact_tree(destination,True)
def tool(action,*options):
 output=run([python,'-B',destination/'scripts/manage-services.py',action,'--config',config_path,*options],180);return json.loads(output)
def preserved():
 files=[state/'issuer/state/issuer.pem',state/'issuer/state/accounts.sqlite3',state/'operator/root/root.pem',state/'operator/root/authority.sqlite3',state/'steward/service.pem',config_path.parent/'recovery-fence.json']
 return {str(file):hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
stable=preserved();initial=tool('status')
assert all(initial['units'][role]['ActiveState']=='active' for role in ['issuer','steward']) and initial['units']['guest']['MainPID']=='0' and initial['bootstrap']['MainPID']=='0'
upgraded=tool('upgrade','--release',destination,'--python',python);assert upgraded['status']=='upgraded' and upgraded['activeRoles']==['issuer','steward'] and stable==preserved()
rolled=tool('rollback');assert rolled['status']=='rolled-back' and rolled['release']==before['release'] and stable==preserved()
final_upgrade=tool('upgrade','--release',destination,'--python',python);assert final_upgrade['status']=='upgraded' and stable==preserved()
current=json.loads(config_path.read_text());status=tool('status');assert current=={**before,'release':str(destination),'manifestSHA256':expected}
assert all(status['units'][role]['ActiveState']=='active' for role in ['issuer','steward']) and status['units']['guest']['MainPID']=='0' and status['bootstrap']['MainPID']=='0'
for role in ['issuer','steward','guest','issuer-bootstrap']:
 response=subprocess.run(['systemctl','is-enabled','codi-ksu-hidden-'+role+'.service'],capture_output=True,text=True)
 assert response.stdout.strip()==('static' if role=='issuer-bootstrap' else 'disabled')
assert Path('/srv/webapps/ksu.codes/current').resolve()==website and Path('/proc/sys/net/ipv4/ping_group_range').read_text()==ping and Path('/proc/sys/net/ipv4/ip_forward').read_text()==forward
assert stable==preserved() and not (config_path.parent/'maintenance.json').exists();exact_tree(destination,True)
report={'status':'PASS','scope':'Actual private box-webhost code upgrade/rollback/re-upgrade; no public deployment or WAN claim','sourceCommit':commit,'installedRelease':str(destination),'manifestSHA256':expected,'beforeRelease':before['release'],'upgrade':upgraded,'rollback':rolled,'finalUpgrade':final_upgrade,'keysAccountsRootAndFenceUnchanged':True,'guestAndBootstrapInactive':True,'unitsRemainDisabledForBoot':True,'pingAndForwardingUnchanged':True,'runningWebsiteUnchanged':str(website),'statusAfter':status}
report_path=Path('/srv/codi-connected')/('upgrade-'+commit[:7]+'-result.json')
fd=os.open(report_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as output:json.dump(report,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
print(json.dumps(report,indent=2))
'''
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--commit',required=True);parser.add_argument('--manifest-sha256',required=True);args=parser.parse_args()
 if not re.fullmatch('[0-9a-f]{40}',args.commit) or not re.fullmatch('[0-9a-f]{64}',args.manifest_sha256):parser.error('Exact reviewed Git and manifest digests are required')
 command=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-',args.commit,args.manifest_sha256]
 process=subprocess.run(command,input=REMOTE,text=True,capture_output=True,timeout=600)
 if process.returncode:raise SystemExit(process.stderr or process.stdout)
 report=json.loads(process.stdout);(ROOT/'.build/checks/deployment-webhost-upgrade-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
