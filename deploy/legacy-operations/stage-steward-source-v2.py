#!/usr/bin/env python3
"""Stage only a Git-pinned source checkout; do not install or restart services."""
import json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];COMMIT='c0690b7f597a2e45ec815fcc5d3209c39b772f76'
REMOTE=r'''
import fcntl,hashlib,json,os,subprocess
from pathlib import Path
repo=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');lock=Path('/home/dflanag3/webhost-sites/.controller.lock');commit='c0690b7f597a2e45ec815fcc5d3209c39b772f76';old='b3e2baad301dacea7a6140a924ce728a5478b3e6';assert os.geteuid()==0
def git(*args):return subprocess.run(['runuser','-u','dflanag3','--','git','-C',str(repo),*args],check=True,capture_output=True,text=True).stdout.strip()
fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 st=os.fstat(fd);assert st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not git('status','--porcelain');head=git('rev-parse','HEAD');assert head in (old,commit);subprocess.run(['runuser','-u','dflanag3','--','git','-C',str(repo),'merge-base','--is-ancestor',old,commit],check=True)
 config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_bytes());assert config['manifestSHA256']=='b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e' and config['basePath']==''
 if head!=commit:git('checkout','--detach',commit)
 pattern='/tools/codiserver/steward-account-release-r2/'
 patterns=git('sparse-checkout','list').splitlines()
 if pattern not in patterns:git('sparse-checkout','add','--no-cone',pattern)
 assert git('rev-parse','HEAD')==commit and not git('status','--porcelain')
 packet=repo/'tools/codiserver/steward-account-release-r2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha(packet/'publish-steward-account-v2.py')=='a31ce785663fc4e6b6d262bf664ffd75bc235ee105794d42e384e0d1b490ba1f'
 assert sha(packet/'release/connected-release.json')=='b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e'
 print(json.dumps({'status':'PASS','before':head,'commit':commit,'packet':str(packet),'servicesRestarted':False,'liveReleaseChanged':False}))
finally:os.close(fd)
'''
def main():
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],capture_output=True,text=True,timeout=180)
 if child.returncode:raise RuntimeError('Source stage failed; inspect checkout before retry: '+child.stderr[-3000:])
 result=json.loads(child.stdout);out=ROOT/'.build/checks/steward-source-stage-r2-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
