#!/usr/bin/env python3
"""Stage the Git-pinned live renewal bundle on box-webhost without signing."""
import base64,hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CLONE=ROOT.parent/'.build/deployment/ksu.codes'
COMMIT='6b4208ae7575795e372014ebeda2d80c6ec1c8db';PACKET='tools/codiserver/live-root-bundle-r1/bundle';PIN='f1b5fd9e3eff2d75805c554fcba79130ba3e5ee87831bcd3ea268e01a12ad214'
CONFIG='19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092';RELEASE='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46'
NAMES=['expired_root_steps.py','expired_root_recovery.py','expired_root_managed.py','live_root_renewal.py','live_root_journal.py','live_root_managed.py','run.py','recovery-operator.json']
REMOTE=r'''
import base64,fcntl,hashlib,json,os,shutil,stat,sys,tempfile
from pathlib import Path
P=Path;assert os.geteuid()==0
value=json.load(sys.stdin);assert set(value)=={'pin','config','release','files'}
files={k:base64.b64decode(v,validate=True) for k,v in value['files'].items()};assert set(files)=={'expired_root_steps.py','expired_root_recovery.py','expired_root_managed.py','live_root_renewal.py','live_root_journal.py','live_root_managed.py','run.py','recovery-operator.json'}
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads(files['recovery-operator.json']);assert sha(files['recovery-operator.json'])==value['pin'] and set(manifest)=={'version','files'} and manifest['version']=='codi-live-root-operator/1' and set(manifest['files'])==set(files)-{'recovery-operator.json'}
for name,expected in manifest['files'].items():assert expected=={'bytes':len(files[name]),'sha256':sha(files[name])}
def directory(p,mode):
 p=P(p)
 if not p.exists():p.mkdir(mode=mode)
 st=p.lstat();assert stat.S_ISDIR(st.st_mode) and not p.is_symlink() and st.st_uid==0 and stat.S_IMODE(st.st_mode)==mode
 return p
def sync(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)
lock=P('/home/dflanag3/webhost-sites/.controller.lock');fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 st=os.fstat(fd);assert stat.S_ISREG(st.st_mode) and st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 config=P('/etc/codi-connected/ksu/managed.json');assert not config.is_symlink();raw=config.read_bytes();c=json.loads(raw);assert sha(raw)==value['config'] and c['manifestSHA256']==value['release'] and c['origin']=='https://ksu.codes' and c['basePath']==''
 parent=directory('/srv/codi-connected',0o755);operators=directory(parent/'recovery-operators',0o755);target=operators/value['pin']
 if target.exists():
  assert not target.is_symlink() and target.is_dir() and target.stat().st_uid==0 and stat.S_IMODE(target.stat().st_mode)==0o755 and {p.name for p in target.iterdir()}==set(files)
  for name,data in files.items():
   p=target/name;st=p.lstat();assert stat.S_ISREG(st.st_mode) and not p.is_symlink() and st.st_uid==0 and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o644 and p.read_bytes()==data
 else:
  stage=P(tempfile.mkdtemp(prefix='.live-',dir=operators));stage.chmod(0o755)
  try:
   for name,data in files.items():
    f=os.open(stage/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644)
    with os.fdopen(f,'wb') as stream:os.fchmod(stream.fileno(),0o644);stream.write(data);stream.flush();os.fsync(stream.fileno())
   sync(stage);os.rename(stage,target);sync(operators)
  finally:
   if stage.exists():shutil.rmtree(stage)
 private=directory(config.parent/'live-root-renewal',0o700);sync(config.parent)
 assert not (private/'journal.json').exists() and not (private/'journal.json').is_symlink()
 print(json.dumps({'status':'PASS','bundle':str(target),'manifestSHA256':value['pin'],'journalDirectory':str(private),'liveServicesChanged':False,'signingPerformed':False}))
finally:os.close(fd)
'''
def main():
 remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/desktop-preview'],cwd=CLONE,text=True).split()[0]
 subprocess.run(['git','merge-base','--is-ancestor',COMMIT,remote],cwd=CLONE,check=True)
 files={}
 for name in NAMES:
  data=subprocess.check_output(['git','show',COMMIT+':'+PACKET+'/'+name],cwd=CLONE);files[name]=base64.b64encode(data).decode()
 assert hashlib.sha256(base64.b64decode(files['recovery-operator.json'])).hexdigest()==PIN
 payload=json.dumps({'pin':PIN,'config':CONFIG,'release':RELEASE,'files':files})
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=payload,text=True,capture_output=True,timeout=45)
 if child.returncode:raise RuntimeError('Staging failed; inspect remote state before retry: '+child.stderr[-4000:])
 result=json.loads(child.stdout);result.update(gitCommit=COMMIT,remoteBranch=remote);out=ROOT/'.build/checks/live-root-bundle-stage-r1-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
