#!/usr/bin/env python3
"""Verify/install the bounded document-operation worker and code-upgrade helper."""
import argparse,hashlib,json,re,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,json,os,shutil,stat,subprocess,sys,tempfile
from pathlib import Path
v=json.load(sys.stdin);b=Path('/home/dflanag3/webhost-sites');repo=b/'sites/ksu.codes'
def sha(data):return hashlib.sha256(data).hexdigest()
def protected(p):
 for f in [p,*p.parents]:
  i=f.lstat();assert not f.is_symlink() and i.st_uid==0 and not i.st_mode&0o022

def source(p):
 for f in [p,*p.parents]:assert not f.is_symlink()
 i=p.stat();assert stat.S_ISREG(i.st_mode) and i.st_nlink==1 and i.st_size<=262144;return p.read_bytes()
def install(destination,values):
 protected(destination.parent)
 if destination.exists():
  protected(destination);assert {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()}==set(values)
  for n,data in values.items():protected(destination/n);assert (destination/n).read_bytes()==data
  return
 stage=Path(tempfile.mkdtemp(prefix='.document-code-',dir=destination.parent))
 try:
  for n,data in values.items():
   p=stage/n;p.parent.mkdir(parents=True,exist_ok=True)
   with p.open('wb') as f:os.fchmod(f.fileno(),0o644);f.write(data);f.flush();os.fsync(f.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  stage.rename(destination);fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
with (b/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 def git(*args):return subprocess.check_output(['runuser','-u','dflanag3','--','git','-C',str(repo),*args],text=True).strip()
 assert git('rev-parse','HEAD')==v['commit'] and not git('status','--porcelain')
 cfg=Path('/etc/codi-connected/ksu/managed.json');before=cfg.read_bytes();c=json.loads(before);old=json.loads(Path(c['userFiles']['configFile']).read_text());old_manifest=json.loads((Path(old['release'])/'files-service.json').read_text())
 folder=repo/'tools/codiserver/file-service-candidates'/v['worker'];raw=source(folder/'files-service.json');assert sha(raw)==v['worker'];m=json.loads(raw);assert m['version']==old_manifest['version']=='codi-private-file-service/1' and set(m['files'])==set(old_manifest['files'])
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}==set(m['files'])|{'files-service.json'};values={'files-service.json':raw}
 for n,r in m['files'].items():
  assert not Path(n).is_absolute() and '..' not in Path(n).parts;data=source(folder/n);assert r=={'bytes':len(data),'sha256':sha(data)};values[n]=data
  if n not in ['gateway_service/user_store.py','gateway_service/http.py','gateway_service/client.mjs']:assert r==old_manifest['files'][n]
 helper=source(repo/'tools/codiserver/document-workflow-r1/source/active-system/scripts/upgrade-private-file-code.py');assert sha(helper)==v['helper']
 destination=Path('/srv/codi-gateway/releases')/v['worker'];helper_parent=Path('/srv/codi-gateway/code-upgrades')
 if v['action']=='install':
  install(destination,values)
  if not helper_parent.exists():protected(helper_parent.parent);helper_parent.mkdir(mode=0o755)
  install(helper_parent/v['helper'],{'upgrade-private-file-code.py':helper})
 assert cfg.read_bytes()==before
 print(json.dumps({'status':'PASS','action':v['action'],'workerManifestSHA256':v['worker'],'destination':str(destination),'helperSHA256':v['helper'],'helper':str(helper_parent/v['helper']/'upgrade-private-file-code.py'),'nativeConfigSHA256':sha(before),'runtimeChanged':False}))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--action',choices=['plan','install'],default='plan');p.add_argument('--commit',required=True);p.add_argument('--worker-manifest-sha256',required=True);a=p.parse_args();helper=hashlib.sha256((ROOT/'scripts/upgrade-private-file-code.py').read_bytes()).hexdigest();r=subprocess.run(['ssh','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'action':a.action,'commit':a.commit,'worker':a.worker_manifest_sha256,'helper':helper}),capture_output=True,text=True,timeout=90)
 if r.returncode:raise RuntimeError(r.stderr or r.stdout)
 d=json.loads(r.stdout);(ROOT/'.build/checks'/('document-worker-'+a.action+'-result.json')).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
