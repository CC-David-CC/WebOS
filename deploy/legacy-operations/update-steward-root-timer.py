#!/usr/bin/env python3
"""Update only root renewal service pins after a committed code change."""
import base64,hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];CLONE=ROOT.parent/'.build/deployment/ksu.codes';COMMIT='225efcc';NAME='tools/codiserver/steward-root-timer-r1/codi-ksu-live-root-renew.service';PIN='8786bbde83c960220e6e549346f857370c7609e8e6ddcad4017deb3b1ab04eae'
REMOTE=r'''
import base64,fcntl,hashlib,json,os,stat,subprocess,sys,tempfile,time
from pathlib import Path
assert os.geteuid()==0;new=base64.b64decode(json.load(sys.stdin)['service'],validate=True);sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(new)=='8786bbde83c960220e6e549346f857370c7609e8e6ddcad4017deb3b1ab04eae'
lock=Path('/home/dflanag3/webhost-sites/.controller.lock');fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 st=os.fstat(fd);assert st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 config=Path('/etc/codi-connected/ksu/managed.json');assert sha(config.read_bytes())=='a1690e2c883d03836a95e5c89ca8a3cd1c56b50370254d13f28c5571fa67ea45';assert json.loads(config.read_bytes())['manifestSHA256']=='b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e'
 path=Path('/etc/systemd/system/codi-ksu-live-root-renew.service');st=path.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==st.st_gid==0 and stat.S_IMODE(st.st_mode)==0o644 and st.st_nlink==1
 old=path.read_bytes();expected=old.replace(b'19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092',b'a1690e2c883d03836a95e5c89ca8a3cd1c56b50370254d13f28c5571fa67ea45').replace(b'36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46',b'b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e');assert expected==new and old!=new
 with tempfile.TemporaryDirectory(prefix='codi-root-pin-',dir='/run') as tmp:
  candidate=Path(tmp)/path.name;candidate.write_bytes(new);subprocess.run(['systemd-analyze','verify',str(candidate)],check=True,capture_output=True)
 backup=Path('/var/backups')/('codi-root-service-before-'+str(time.time_ns())+'.service');raw=os.open(backup,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 with os.fdopen(raw,'wb') as f:f.write(old);f.flush();os.fsync(f.fileno())
 tmp=path.with_name('.codi-root-renew-'+str(os.getpid()));raw=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o644)
 with os.fdopen(raw,'wb') as f:os.fchmod(f.fileno(),0o644);f.write(new);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path);d=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY);os.fsync(d);os.close(d);subprocess.run(['systemctl','daemon-reload'],check=True)
 assert path.read_bytes()==new and subprocess.run(['systemctl','is-active','--quiet','codi-ksu-live-root-renew.timer']).returncode==0
 print(json.dumps({'status':'PASS','backup':str(backup),'oldSHA256':sha(old),'newSHA256':sha(new),'timerActive':True,'signingPerformed':False}))
finally:os.close(fd)
'''
def main():
 head=subprocess.check_output(['git','ls-remote','origin','refs/heads/desktop-preview'],cwd=CLONE,text=True).split()[0];subprocess.run(['git','merge-base','--is-ancestor',COMMIT,head],cwd=CLONE,check=True);data=subprocess.check_output(['git','show',COMMIT+':'+NAME],cwd=CLONE);assert hashlib.sha256(data).hexdigest()==PIN
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'service':base64.b64encode(data).decode()}),text=True,capture_output=True,timeout=45)
 if child.returncode:raise RuntimeError(child.stderr[-3000:])
 result=json.loads(child.stdout);out=ROOT/'.build/checks/steward-root-timer-pin-r1-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
