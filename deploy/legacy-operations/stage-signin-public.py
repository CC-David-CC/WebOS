#!/usr/bin/env python3
"""Reconstruct/seal exact native15 R7 from two reviewed private Git bundles.

Plan/install only. No live configuration, unit, policy or service changes.
"""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
NATIVE='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed'
REMOTE=r'''
import fcntl,hashlib,json,os,shutil,stat,subprocess,sys,tempfile
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0 and v['action'] in ('plan','install')
base=Path('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';source=repo/'tools/codiserver';cfg=Path('/etc/codi-connected/ksu/managed.json')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),text=True,timeout=30).strip()
def read(p,record=None):
 for f in [p,*p.parents]:assert not f.is_symlink()
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=134217728;raw=f.read(s.st_size+1);assert len(raw)==s.st_size
 if record is not None:assert record=={'bytes':len(raw),'sha256':digest(raw)}
 return raw
def package(folder,name,pin,version,count):
 raw=read(folder/name);assert digest(raw)==pin;m=json.loads(raw);assert m['version']==version and len(m['files'])==count
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(m['files'])|{name}
 values={name:raw}
 for n,r in m['files'].items():
  assert not Path(n).is_absolute() and all(c not in ('','.','..') for c in n.split('/'));values[n]=read(folder/n,r)
 return values
def protected(p,mode=None):
 for f in [p,*p.parents]:
  s=f.lstat();assert not f.is_symlink() and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
 if mode is not None:assert stat.S_IMODE(p.stat().st_mode)==mode
def install(destination,values):
 protected(destination.parent,0o755)
 def verify(folder):
  protected(folder,0o755);assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(values)
  for n,raw in values.items():protected(folder/n,0o644);assert read(folder/n)==raw
 if destination.exists():verify(destination);return
 stage=Path(tempfile.mkdtemp(prefix='.signin-public-',dir=destination.parent))
 try:
  for n,raw in values.items():
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('wb') as out:os.fchmod(out.fileno(),0o644);out.write(raw);out.flush();os.fsync(out.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  verify(stage);stage.rename(destination);fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
 verify(destination)
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 assert run(['runuser','-u','dflanag3','--','git','-C',repo,'rev-parse','HEAD'])==v['commit'] and not run(['runuser','-u','dflanag3','--','git','-C',repo,'status','--porcelain'])
 before=cfg.read_bytes();assert digest(before)=='8fc7929f40629edb4e089a0601289cd54de3203468c3ff925a6e0f519e718b5c';c=json.loads(before)
 assert c['release']=='/srv/codi-connected/releases/native14-8810761ee7e47e15'
 pids={r:run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value']) for r in ['issuer','steward','guest']};assert all(int(p)>0 for p in pids.values())
 pins={str(p):digest(p.read_bytes()) for p in [cfg,Path(c['guestNetwork']['configFile']),Path('/etc/codi-user-files/ksu/managed.json'),base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile')]}
 assert pins[str(base/'ops/common.py')]=='718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4' and pins[str(base/'sites.toml')]=='da1383b2b4f7fa25911c204c212981d54b05355f53e07ff8284242971b387bd9' and pins['/etc/caddy/Caddyfile']=='09763673ee7b6bcc6ade992a931e3c409aebd0daafeeb5ba46181178d81a5a7f'
 values=package(source/'guest-signin-r1/native','connected-release.json','5fad3b77a5b3f982345c7bd959789509634076059c0b94403f2148146744fcb8','codi-connected-development/15',226)
 ui=package(source/'guest-signin-ui-r1','signin-ui.json','a59b210c39f2f0992dcb114e3cb95762aba1e7f634a4bb064434074fce5c387d','codi-guest-signin-ui-source-proof/1',26)
 delta={n.removeprefix('native-delta/'):raw for n,raw in ui.items() if n.startswith('native-delta/')}
 assert set(delta)=={'connected-release.json','release.json','app.js','desktop-apps.js','assets/desktop/apps.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js','assets/desktop/apps/help/d44f5f298eafd09889524e36d13a4e884c1d673ef0380e6be9867329dbad4300.mjs'}
 values.update(delta);assert digest(values['connected-release.json'])==v['native'];m=json.loads(values['connected-release.json']);assert m['version']=='codi-connected-development/15' and len(m['files'])==227 and set(values)==set(m['files'])|{'connected-release.json'}
 for n,r in m['files'].items():assert r=={'bytes':len(values[n]),'sha256':digest(values[n])}
 destination=Path('/srv/codi-connected/releases')/('native15-'+v['native'][:16])
 if v['action']=='install':install(destination,values)
 # Existing protected strict worker/operator/controller were installed separately.
 for folder,name,pin,count,version in [('workers','guest-wire.json','9f9106e682e51bd5284273fd093994353db6274f887834a12af97828a6907096',13,'codi-guest-wire-runtime/2'),('operators','guest-operator.json','5c51d2c86c214519c21237c41252d41b20a2536d6cdd46f96af37719e9a076fc',11,'codi-guest-network-operator/2')]:
  p=Path('/srv/codi-guest-network')/folder/pin;protected(p,0o755);package(p,name,pin,version,count)
 controller=Path('/srv/codi-connected/rollout-controllers/f51b11cc8ce2af83aa209fedc4b34e2b34aa88251879494608270182a8e8e6e0/native-rollout.py');protected(controller,0o644);assert digest(read(controller))==controller.parent.name
 prototype=Path('/srv/webapps/ksu.codes/current').resolve()/'public/desktop';manifest=json.loads((prototype/'release.json').read_text());assert digest((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9'
 for n,r in manifest['files'].items():read(prototype/n,r)
 assert len(manifest['files'])==133 and pins=={p:digest(Path(p).read_bytes()) for p in pins} and cfg.read_bytes()==before
 assert pids=={r:run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value']) for r in pids}
 print(json.dumps({'status':'PASS','action':v['action'],'sourceCommit':v['commit'],'manifestSHA256':v['native'],'destination':str(destination),'files':227,'nativePIDs':pids,'liveConfigSHA256':digest(before),'prototypeFilesVerified':133,'runtimeChanged':False}))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install'],default='plan');p.add_argument('--commit',required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit)
 r=subprocess.run(['ssh','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'action':a.action,'commit':a.commit,'native':NATIVE}),capture_output=True,text=True,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr[-4000:] or r.stdout[-4000:])
 result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('signin-public-webhost-'+a.action+'-result.json')
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
