#!/usr/bin/env python3
"""Plan/install immutable security code only; never configure or activate it.

Requires exact private-Git source commit and existing native14/R18 pins. This
prepares the reviewed native15/worker2/operator2/controller alongside live code.
No route, unit, config, account, permission, key, file or kernel state is changed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
NATIVE='5fad3b77a5b3f982345c7bd959789509634076059c0b94403f2148146744fcb8'
WORKER='9f9106e682e51bd5284273fd093994353db6274f887834a12af97828a6907096'
OPERATOR='5c51d2c86c214519c21237c41252d41b20a2536d6cdd46f96af37719e9a076fc'
REMOTE=r'''
import fcntl,hashlib,json,os,shutil,stat,subprocess,sys,tempfile
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0 and v['action'] in ('plan','install')
base=Path('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';source=repo/'tools/codiserver/guest-signin-r1'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),text=True).strip()
def protected(p,mode=None):
 for f in [p,*p.parents]:
  s=f.lstat();assert not f.is_symlink() and s.st_uid==0 and not s.st_mode&0o022
 if mode is not None:assert stat.S_IMODE(p.stat().st_mode)==mode

def package(folder,manifest,pin,version,count):
 raw=(folder/manifest).read_bytes();assert digest(raw)==pin;m=json.loads(raw);assert m['version']==version and len(m['files'])==count
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(m['files'])|{manifest}
 values={manifest:raw}
 for name,r in m['files'].items():
  assert not Path(name).is_absolute() and all(p not in ('','.','..') for p in name.split('/'))
  p=folder/name
  for ancestor in [p,*p.parents]:assert not ancestor.is_symlink()
  with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
   s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size==r['bytes'] and s.st_size<=134217728;data=f.read(s.st_size+1)
  assert len(data)==r['bytes'] and digest(data)==r['sha256'];values[name]=data
 return values

def install(destination,values):
 protected(destination.parent,0o755)
 def verify(folder):
  protected(folder,0o755);assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(values)
  for name,data in values.items():protected(folder/name,0o644);assert (folder/name).read_bytes()==data
 if destination.exists():verify(destination);return
 stage=Path(tempfile.mkdtemp(prefix='.signin-code-',dir=destination.parent))
 try:
  for name,data in values.items():
   p=stage/name;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('wb') as out:os.fchmod(out.fileno(),0o644);out.write(data);out.flush();os.fsync(out.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  verify(stage);stage.rename(destination)
  fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
 verify(destination)

with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert run(['runuser','-u','dflanag3','--','git','-C',repo,'rev-parse','HEAD'])==v['commit']
 assert not run(['runuser','-u','dflanag3','--','git','-C',repo,'status','--porcelain'])
 cfg=Path('/etc/codi-connected/ksu/managed.json');before=cfg.read_bytes();assert digest(before)=='8fc7929f40629edb4e089a0601289cd54de3203468c3ff925a6e0f519e718b5c'
 c=json.loads(before);assert c['release']=='/srv/codi-connected/releases/native14-8810761ee7e47e15' and c['manifestSHA256']=='8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce'
 binding=Path(c['guestNetwork']['configFile']);guest= binding.read_bytes();b=json.loads(guest)
 assert b['policy']=={'version':'codi-guest-egress-policy/1','ownPublicIPv4':['104.180.210.33'],'dnsIPv4':['1.1.1.1','9.9.9.9']}
 assert b['stateRoot']=='/var/lib/codi-guest-network/ksu' and c['instance']=='codi-ksu-hidden' and c['origin']=='https://ksu.codes' and c['basePath']=='/hidden'
 assert c['turn']['iceTransportPolicy']=='all' and c['version']=='codi-managed-instance/5'
 pids={role:run(['systemctl','show',c['instance']+'-'+role+'.service','-p','MainPID','--value']) for role in ['issuer','steward','guest']};assert all(int(p)>0 for p in pids.values())
 files={str(p):digest(p.read_bytes()) for p in [cfg,binding,Path('/etc/codi-user-files/ksu/managed.json'),base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile')]}
 assert files[str(base/'ops/common.py')]=='718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4'
 assert files[str(base/'sites.toml')]=='da1383b2b4f7fa25911c204c212981d54b05355f53e07ff8284242971b387bd9'
 assert files['/etc/caddy/Caddyfile']=='09763673ee7b6bcc6ade992a931e3c409aebd0daafeeb5ba46181178d81a5a7f'
 site=Path('/srv/webapps/ksu.codes/current').resolve();prototype=site/'public/desktop';manifest=json.loads((prototype/'release.json').read_text())
 assert digest((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for name,r in manifest['files'].items():assert {'bytes':(prototype/name).stat().st_size,'sha256':digest((prototype/name).read_bytes())}==r
 assert len(manifest['files'])==133
 packages=[]
 for kind,meta,pin,version,count,destination in [
  ('native','connected-release.json',v['native'],'codi-connected-development/15',226,Path('/srv/codi-connected/releases')/('native15-'+v['native'][:16])),
  ('worker','guest-wire.json',v['worker'],'codi-guest-wire-runtime/2',13,Path('/srv/codi-guest-network/workers')/v['worker']),
  ('operator','guest-operator.json',v['operator'],'codi-guest-network-operator/2',11,Path('/srv/codi-guest-network/operators')/v['operator'])]:
  values=package(source/kind,meta,pin,version,count);packages.append((destination,values))
 controller=(source/'scripts/native-rollout.py').read_bytes();assert digest(controller)==v['controller']
 packages.append((Path('/srv/codi-connected/rollout-controllers')/v['controller'],{'native-rollout.py':controller}))
 if v['action']=='install':
  for destination,values in packages:install(destination,values)
 assert cfg.read_bytes()==before and binding.read_bytes()==guest
 assert pids=={role:run(['systemctl','show',c['instance']+'-'+role+'.service','-p','MainPID','--value']) for role in pids}
 assert files=={p:digest(Path(p).read_bytes()) for p in files} and Path('/srv/webapps/ksu.codes/current').resolve()==site
 assert Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0' and Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001']
 result={'status':'PASS','action':v['action'],'sourceCommit':v['commit'],'packages':{str(dest):len(values) for dest,values in packages},'nativePIDs':pids,'liveConfigSHA256':digest(before),'prototypeFilesVerified':133,'nativePolicyAndHostingUnchanged':True,'servicesRestarted':False,'guestPolicyActivated':False,'personalFileContentsRead':False,'newPortsOrBootChanges':False}
 print(json.dumps(result))
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install'],default='plan');p.add_argument('--commit',required=True);a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('Exact reviewed private-Git commit required')
    values={'action':a.action,'commit':a.commit,'native':NATIVE,'worker':WORKER,'operator':OPERATOR,'controller':hashlib.sha256((ROOT/'scripts/native-rollout.py').read_bytes()).hexdigest()}
    r=subprocess.run(['ssh','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(values),capture_output=True,text=True,timeout=180)
    if r.returncode:raise RuntimeError(r.stderr[-3000:] or r.stdout[-3000:])
    result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('guest-signin-webhost-'+a.action+'-result.json');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
