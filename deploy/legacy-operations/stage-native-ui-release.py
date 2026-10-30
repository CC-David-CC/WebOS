#!/usr/bin/env python3
"""Plan/install a public-asset-only native15 upgrade from reviewed private Git.

Uses existing native15 runtime/operator; never configures or restarts services.
"""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,json,os,shutil,stat,subprocess,sys,tempfile
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0 and v['action'] in ['plan','install'];base=Path('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';key=v['manifestSHA256'];source=repo/'tools/codiserver/native-candidates'/key;destination=Path('/srv/codi-connected/releases')/('native15-'+key[:16]);cfg=Path('/etc/codi-connected/ksu/managed.json')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),text=True,timeout=60).strip()
def protected(path,mode=None):
 for p in [path,*path.parents]:
  s=p.lstat();assert not p.is_symlink() and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
 if mode is not None:assert stat.S_IMODE(path.stat().st_mode)==mode

def read(path):
 for p in [path,*path.parents]:assert not p.is_symlink()
 with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<=s.st_size<=134217728;raw=f.read(s.st_size+1);assert len(raw)==s.st_size;return raw
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 def git(*args):return run(['runuser','-u','dflanag3','--','git','-C',repo,*args])
 assert git('rev-parse','HEAD')==v['commit'] and not git('status','--porcelain')
 before=read(cfg);assert sha(before)==v['configSHA256'];c=json.loads(before);old=Path(c['release']);m=json.loads(read(old/'connected-release.json'));old_public=json.loads(read(old/'release.json'))['files']
 assert c['manifestSHA256']==v['baseManifestSHA256'] and c['guestNetwork']['policySHA256']=='436096d722a1bfb42935ca817dcaaf74cec7b2856bf229a4f775cc0c7cd2c049'
 raw=read(source/'connected-release.json');assert sha(raw)==key;candidate=json.loads(raw);public=json.loads(read(source/'release.json'))['files'];assert candidate['version']==m['version']=='codi-connected-development/15' and {k:w for k,w in m.items() if k!='files'}=={k:w for k,w in candidate.items() if k!='files'}
 native=set(m['files'])-set(old_public)-{'release.json'};assert set(candidate['files'])==set(public)|native|{'release.json'}
 for name in native:assert candidate['files'][name]==m['files'][name]
 for name,r in old_public.items():
  if name not in ['index.html','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js']:assert public[name]==r
 for name in set(public)-set(old_public):assert name.startswith(('assets/desktop/','assets/terminal/v2/','assets/desktop-style-v2-'))
 assert {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}==set(candidate['files'])|{'connected-release.json'} and len(git('ls-files','--','tools/codiserver/native-candidates/'+key).splitlines())==len(candidate['files'])+1
 values={'connected-release.json':raw}
 for name,r in candidate['files'].items():
  assert not Path(name).is_absolute() and all(p not in ('','.','..') for p in name.split('/'));data=read(source/name);assert r=={'bytes':len(data),'sha256':sha(data)};values[name]=data
 pids={r:int(run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value'])) for r in ['issuer','steward','guest']};assert all(p>0 for p in pids.values())
 hosting={str(p):sha(read(p)) for p in [base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile')]};assert hosting[str(base/'sites.toml')]=='c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715'
 prototype=Path('/srv/webapps/ksu.codes/current').resolve()/'public/desktop';pm=json.loads(read(prototype/'release.json'));assert sha(read(prototype/'release.json'))=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9' and len(pm['files'])==133
 for n,r in pm['files'].items():
  raw=read(prototype/n);assert r=={'bytes':len(raw),'sha256':sha(raw)}
 def verify(folder):
  protected(folder,0o755);assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(values)
  for n,data in values.items():protected(folder/n,0o644);assert read(folder/n)==data
 if v['action']=='install':
  protected(destination.parent,0o755)
  if not destination.exists():
   stage=Path(tempfile.mkdtemp(prefix='.native-ui-',dir=destination.parent))
   try:
    for n,data in values.items():
     p=stage/n;p.parent.mkdir(parents=True,exist_ok=True)
     with p.open('wb') as out:os.fchmod(out.fileno(),0o644);out.write(data);out.flush();os.fsync(out.fileno())
    for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
    verify(stage);stage.rename(destination);fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
   finally:
    if stage.exists():shutil.rmtree(stage)
  verify(destination)
 assert cfg.read_bytes()==before and hosting=={p:sha(read(Path(p))) for p in hosting} and pids=={r:int(run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value'])) for r in pids}
 print(json.dumps({'status':'PASS','action':v['action'],'manifestSHA256':key,'destination':str(destination),'files':len(candidate['files']),'sourceCommit':v['commit'],'nativeBackendBytesUnchanged':True,'legacyAssetsRetained':True,'prototypeFilesVerified':133,'nativePIDs':pids,'runtimeChanged':False}))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install'],default='plan');p.add_argument('--commit',required=True);p.add_argument('--manifest-sha256',required=True);p.add_argument('--base-manifest-sha256',default='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed');p.add_argument('--config-sha256',default='22eec0f5b47841e8994b72954e3cfa119bad8177333319bc5c93b915f9cb3403');a=p.parse_args();assert re.fullmatch('[0-9a-f]{40}',a.commit) and re.fullmatch('[0-9a-f]{64}',a.manifest_sha256)
 r=subprocess.run(['ssh','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'action':a.action,'commit':a.commit,'manifestSHA256':a.manifest_sha256,'baseManifestSHA256':a.base_manifest_sha256,'configSHA256':a.config_sha256}),capture_output=True,text=True,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr[-4000:] or r.stdout[-4000:])
 value=json.loads(r.stdout);value['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('native-ui-'+a.action+'-result.json')
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
