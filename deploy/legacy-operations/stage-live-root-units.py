#!/usr/bin/env python3
"""Install pinned static renewal units without starting or enabling them."""
import base64,hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CLONE=ROOT.parent/'.build/deployment/ksu.codes'
COMMIT='c5ee4b6';PACKET='tools/codiserver/live-root-host-units-r1/ops'
NAMES=['codi-ksu-live-root-renew.service','codi-ksu-live-root-renew.timer']
REMOTE=r'''
import base64,fcntl,hashlib,json,os,pathlib,stat,subprocess,sys,tempfile
P=pathlib.Path; assert os.geteuid()==0
value=json.load(sys.stdin); files={k:base64.b64decode(v,validate=True) for k,v in value.items()}; names={'codi-ksu-live-root-renew.service','codi-ksu-live-root-renew.timer'};assert set(files)==names
sha=lambda b:hashlib.sha256(b).hexdigest()
config=P('/etc/codi-connected/ksu/managed.json');assert sha(config.read_bytes())=='19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092'
bundle=P('/srv/codi-connected/recovery-operators/f1b5fd9e3eff2d75805c554fcba79130ba3e5ee87831bcd3ea268e01a12ad214/recovery-operator.json');assert sha(bundle.read_bytes())=='f1b5fd9e3eff2d75805c554fcba79130ba3e5ee87831bcd3ea268e01a12ad214'
lock=P('/home/dflanag3/webhost-sites/.controller.lock');fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);created=[]
try:
 info=os.fstat(fd);assert stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1 and not info.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 for name in names:assert not (P('/etc/systemd/system')/name).exists() and not (P('/etc/systemd/system')/name).is_symlink()
 with tempfile.TemporaryDirectory(prefix='codi-renew-units-',dir='/run') as tmp:
  for name,raw in files.items():(P(tmp)/name).write_bytes(raw)
  subprocess.run(['systemd-analyze','verify',*[str(P(tmp)/name) for name in sorted(names)]],check=True,stdout=subprocess.DEVNULL)
 try:
  for name,raw in files.items():
   path=P('/etc/systemd/system')/name;out=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o644);created.append(path)
   with os.fdopen(out,'wb') as f:os.fchmod(f.fileno(),0o644);f.write(raw);f.flush();os.fsync(f.fileno())
  subprocess.run(['systemctl','daemon-reload'],check=True)
 except BaseException:
  for path in created:path.unlink(missing_ok=True)
  subprocess.run(['systemctl','daemon-reload'],check=False);raise
 print(json.dumps({'status':'PASS','files':{k:sha(v) for k,v in files.items()},'enabled':False,'started':False,'signingPerformed':False}))
finally:os.close(fd)
'''
def main():
 remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/desktop-preview'],cwd=CLONE,text=True).split()[0];subprocess.run(['git','merge-base','--is-ancestor',COMMIT,remote],cwd=CLONE,check=True)
 files={name:base64.b64encode(subprocess.check_output(['git','show',COMMIT+':'+PACKET+'/'+name],cwd=CLONE)).decode() for name in NAMES}
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(files),text=True,capture_output=True,timeout=60)
 if child.returncode:raise RuntimeError('Unit staging failed; inspect unit state before retry: '+child.stderr[-4000:])
 value=json.loads(child.stdout);value.update(gitCommit=COMMIT,remoteBranch=remote);out=ROOT/'.build/checks/live-root-units-stage-r1-result.json';assert not out.exists();out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
if __name__=='__main__':main()
