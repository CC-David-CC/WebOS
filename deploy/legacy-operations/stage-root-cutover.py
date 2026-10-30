#!/usr/bin/env python3
"""Git-first immutable root candidate/operator install; never activates services."""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,json,os,pathlib,shutil,stat,subprocess,sys,tempfile,time
P=pathlib.Path;v=json.load(sys.stdin);assert v['action'] in ['plan','install'];base=P('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';cfg=P('/etc/codi-connected/ksu/managed.json')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def read(p,mode=None):
 p=P(p)
 for q in [p,*p.parents]:assert not q.is_symlink()
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=134217728
  if mode is not None:assert stat.S_IMODE(s.st_mode)==mode and s.st_uid==s.st_gid==0
  b=f.read(s.st_size+1);assert len(b)==s.st_size;return b
def protected(p):
 for q in [P(p),*P(p).parents]:
  s=q.lstat();assert not q.is_symlink() and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
def run(*args):return subprocess.check_output(list(map(str,args)),text=True,timeout=60).strip()
def install(destination,values):
 protected(destination.parent)
 def verify(folder):
  protected(folder);assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(values)
  for p in folder.rglob('*'):protected(p)
  for n,b in values.items():assert read(folder/n,0o644)==b
 if destination.exists():verify(destination);return
 stage=P(tempfile.mkdtemp(prefix='.root-candidate-',dir=destination.parent))
 try:
  for n,b in values.items():
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('wb') as f:os.fchmod(f.fileno(),0o644);f.write(b);f.flush();os.fsync(f.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  verify(stage);stage.rename(destination);fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
 verify(destination)
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 def git(*args):return run('runuser','-u','dflanag3','--','git','-C',repo,*args)
 assert git('rev-parse','HEAD')==v['commit'] and not git('status','--porcelain')
 original=read(cfg,0o600);assert sha(original)=='39d88cd8fd56d223d88efaa8291cbf0693f0105660f937e9c022765b136d2c51';c=json.loads(original)
 assert c['release']=='/srv/codi-connected/releases/native16-3071d17fa17666e2' and c['manifestSHA256']=='3071d17fa17666e2d9317e96e2e9a79d629e2a16be2e44b9afb0ed9947efd211' and c['basePath']=='/hidden'
 assert not any((cfg.parent/n).exists() for n in ['native-rollout.json','maintenance.json','guest-signin-migration.json','site-cutover.json'])
 old=P(c['release']);protected(old);old_raw=read(old/'connected-release.json',0o644);assert sha(old_raw)==c['manifestSHA256'];old_meta=json.loads(old_raw);old_public=json.loads(read(old/'release.json',0o644))['files']
 source=repo/'tools/codiserver/native-candidates'/v['nativeSHA256'];raw=read(source/'connected-release.json');assert sha(raw)==v['nativeSHA256'];metadata=json.loads(raw);public=json.loads(read(source/'release.json'))['files']
 assert {k:b for k,b in metadata.items() if k!='files'}=={k:b for k,b in old_meta.items() if k!='files'}
 native=set(old_meta['files'])-set(old_public)-{'release.json'};assert set(metadata['files'])==set(public)|native|{'release.json'}
 for n in native:assert metadata['files'][n]==old_meta['files'][n]
 mutable={'index.html','assets/desktop/network-release.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
 for n,r in old_public.items():
  if n not in mutable:assert public[n]==r
 graph=json.loads(read(source/'assets/desktop/network-release.json'));previous=json.loads(read(old/'assets/desktop/network-release.json'));assert graph['modules']==previous['modules'] and graph['directory']==previous['directory']
 client='assets/desktop/device-cache-v2/23df9ee07327b089a5d491684921e9a72d14a661f35692d8a4d7981d2b7eb44c.mjs';assert sha(read(source/client))=='23df9ee07327b089a5d491684921e9a72d14a661f35692d8a4d7981d2b7eb44c'
 for n in graph['core']:
  before=read(old/previous['coreDirectory']/n);after=read(source/graph['coreDirectory']/n)
  if n=='app.js':
   anchor=b"new URL('assets/desktop/device-cache.mjs',document.baseURI)";assert before.count(anchor)==1;assert after==before.replace(anchor,("new URL('"+client+"',document.baseURI)").encode())
  else:assert before==after
 assert set(public)-set(old_public)=={client,*(graph['coreDirectory']+'/'+n for n in graph['core'])}
 values={'connected-release.json':raw}
 for n,r in metadata['files'].items():
  assert not P(n).is_absolute() and '..' not in P(n).parts;b=read(source/n);assert r=={'bytes':len(b),'sha256':sha(b)};values[n]=b
 assert len(git('ls-files','--',str(source.relative_to(repo))).splitlines())==len(values)
 operator=repo/'tools/codiserver/mount-operators'/v['operatorSHA256'];raw=read(operator/'mount-operator.json');assert sha(raw)==v['operatorSHA256'];m=json.loads(raw)
 expected={'mount_operator/'+n+'.py' for n in ['__init__','authority','backends','coordinator']}|{'scripts/migrate-desktop-mount.py'}
 assert set(m)=={'version','files'} and m['version']=='codi-mount-operator/1' and set(m['files'])==expected
 operator_values={'mount-operator.json':raw}
 for n,r in m['files'].items():
  b=read(operator/n);assert r=={'bytes':len(b),'sha256':sha(b)};operator_values[n]=b
 assert len(git('ls-files','--',str(operator.relative_to(repo))).splitlines())==len(operator_values)
 hosting={str(p):sha(read(p)) for p in [base/'ops/common.py',base/'sites.toml',P('/etc/caddy/Caddyfile')]}
 assert hosting=={str(base/'ops/common.py'):'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4',str(base/'sites.toml'):'c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715','/etc/caddy/Caddyfile':'694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'}
 website=P('/srv/webapps/ksu.codes/current').resolve();home=sha(read(website/'public/index.html'));assert home=='55f2928da214010b2ed7d647a354c0052ae03e9d06bafc09c1ea3b67e8608a38';prototype=json.loads(read(website/'public/desktop/release.json'))['files'];assert len(prototype)==133
 for n,r in prototype.items():
  b=read(website/'public/desktop'/n);assert r=={'bytes':len(b),'sha256':sha(b)}
 def pids():return {r:int(run('systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value')) for r in ['issuer','steward','guest']}
 before=pids();assert all(before.values())
 destination=P('/srv/codi-connected/releases')/('native16-'+v['nativeSHA256'][:16]);operator_destination=P('/srv/codi-connected/mount-operators')/v['operatorSHA256']
 if v['action']=='install':
  if not operator_destination.parent.exists():protected(operator_destination.parent.parent);operator_destination.parent.mkdir(mode=0o755)
  install(destination,values);install(operator_destination,operator_values)
 assert pids()==before and read(cfg)==original and {p:sha(read(P(p))) for p in hosting}==hosting and P('/srv/webapps/ksu.codes/current').resolve()==website and sha(read(website/'public/index.html'))==home
 result={'status':'PASS','action':v['action'],'nativeDestination':str(destination),'nativeManifestSHA256':v['nativeSHA256'],'operatorDestination':str(operator_destination),'operatorManifestSHA256':v['operatorSHA256'],'prototypeFilesVerified':133,'nativePIDsUnchanged':before,'servicesRestarted':False,'configAndHostingAndHomepageUnchanged':True,'activated':False}
 if v['action']=='install':
  receipt=P('/srv/codi-connected')/('root-cutover-install-'+str(time.time_ns())+'-result.json')
  with os.fdopen(os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  result['rootReceipt']=str(receipt)
 print(json.dumps(result))
'''


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install'],default='plan');p.add_argument('--commit',required=True);p.add_argument('--native-sha256',required=True);p.add_argument('--operator-sha256',required=True);a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit) and all(re.fullmatch('[0-9a-f]{64}',s) for s in [a.native_sha256,a.operator_sha256])
    payload={'action':a.action,'commit':a.commit,'nativeSHA256':a.native_sha256,'operatorSHA256':a.operator_sha256}
    r=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(payload),capture_output=True,text=True,timeout=180)
    if r.returncode:raise ValueError(r.stderr[-5000:] or r.stdout[-5000:])
    result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('root-cutover-'+a.action+'-result.json')
    if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
