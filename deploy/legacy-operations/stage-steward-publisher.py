#!/usr/bin/env python3
"""Install a pinned publisher only; no release activation or service restart."""
import json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REMOTE=r'''
import fcntl,hashlib,json,os,stat,tempfile
from pathlib import Path
assert os.geteuid()==0
repo=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');src=repo/'tools/codiserver/steward-account-release-r1/publish-steward-account.py';pin='46932dedfdfd5de61a7aa161ffc001824ebd215e6421273490c60dd8303672c9';lock=Path('/home/dflanag3/webhost-sites/.controller.lock');fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
def directory(p):
 if not p.exists():p.mkdir(mode=0o755)
 st=p.lstat();assert stat.S_ISDIR(st.st_mode) and st.st_uid==0 and st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o755 and not p.is_symlink()
def sync(p):
 f=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:os.fsync(f)
 finally:os.close(f)
try:
 st=os.fstat(fd);assert st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import subprocess
 def git(*args):return subprocess.run(['runuser','-u','dflanag3','--','git','-C',str(repo),*args],check=True,capture_output=True,text=True).stdout.strip()
 assert git('rev-parse','HEAD')=='b3e2baad301dacea7a6140a924ce728a5478b3e6' and not git('status','--porcelain')
 assert not src.is_symlink() and src.is_file();data=src.read_bytes();assert hashlib.sha256(data).hexdigest()==pin
 config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_bytes());assert config['manifestSHA256']=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46'
 parent=Path('/srv/codi-connected/steward-account-publishers');directory(parent);target=parent/pin;directory(target);file=target/'publish-steward-account.py'
 if not file.exists():
  raw=os.open(file,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644)
  with os.fdopen(raw,'wb') as stream:os.fchmod(stream.fileno(),0o644);stream.write(data);stream.flush();os.fsync(stream.fileno())
  sync(target);sync(parent)
 st=file.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==0 and st.st_gid==0 and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==0o644 and file.read_bytes()==data
 assert {p.name for p in target.iterdir()}=={file.name}
 print(json.dumps({'status':'PASS','publisher':str(file),'sha256':pin,'servicesRestarted':False,'releaseActivated':False}))
finally:os.close(fd)
'''
def main():
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],capture_output=True,text=True,timeout=45)
 if child.returncode:raise RuntimeError('Publisher staging failed; inspect installed path: '+child.stderr[-3000:])
 result=json.loads(child.stdout);out=ROOT/'.build/checks/steward-publisher-stage-r1-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
