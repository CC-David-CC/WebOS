#!/usr/bin/env python3
"""Stage only a Git-pinned source checkout; do not install or restart services."""
import json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];COMMIT='b3e2baad301dacea7a6140a924ce728a5478b3e6'
REMOTE=r'''
import fcntl,hashlib,json,os,subprocess
from pathlib import Path
repo=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');lock=Path('/home/dflanag3/webhost-sites/.controller.lock');commit='b3e2baad301dacea7a6140a924ce728a5478b3e6';old='bd8cdf691dd6192919009a1ac302e0a37dedcfe9';assert os.geteuid()==0
def git(*args):return subprocess.run(['runuser','-u','dflanag3','--','git','-C',str(repo),*args],check=True,capture_output=True,text=True).stdout.strip()
fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 st=os.fstat(fd);assert st.st_uid==0 and st.st_nlink==1 and not st.st_mode&0o022;fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert not git('status','--porcelain');head=git('rev-parse','HEAD');assert head in (old,commit);subprocess.run(['runuser','-u','dflanag3','--','git','-C',str(repo),'merge-base','--is-ancestor',old,commit],check=True)
 config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_bytes());assert config['manifestSHA256']=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46' and config['basePath']==''
 if head!=commit:git('checkout','--detach',commit)
 pattern='/tools/codiserver/steward-account-release-r1/'
 patterns=git('sparse-checkout','list').splitlines()
 if pattern not in patterns:git('sparse-checkout','add','--no-cone',pattern)
 assert git('rev-parse','HEAD')==commit and not git('status','--porcelain')
 packet=repo/'tools/codiserver/steward-account-release-r1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert sha(packet/'publish-steward-account.py')=='46932dedfdfd5de61a7aa161ffc001824ebd215e6421273490c60dd8303672c9'
 assert sha(packet/'release/connected-release.json')=='b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e'
 print(json.dumps({'status':'PASS','before':head,'commit':commit,'packet':str(packet),'servicesRestarted':False,'liveReleaseChanged':False}))
finally:os.close(fd)
'''
def main():
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],capture_output=True,text=True,timeout=180)
 if child.returncode:raise RuntimeError('Source stage failed; inspect checkout before retry: '+child.stderr[-3000:])
 result=json.loads(child.stdout);out=ROOT/'.build/checks/steward-source-stage-r1-result.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
