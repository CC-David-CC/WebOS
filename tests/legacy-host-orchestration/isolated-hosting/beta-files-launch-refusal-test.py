#!/usr/bin/env python3
"""Real launcher bootstrap refusal in a disposable root-owned bundle.

This only tests protected loading; hostname is substituted for the fixture.
It performs no host route, account, service, or artifact mutation.
"""
import os,subprocess,sys,uuid
from pathlib import Path
ops=Path(__file__).resolve().parents[1]/'ops';tmp='/root/codi-files-launch-test-'+uuid.uuid4().hex
names=('beta_files_launch.py','beta_launcher.py','beta_files_preflight.py')
def sudo(*args):return subprocess.run(['sudo','-n',*args],capture_output=True,text=True)
setup=sudo('mkdir','-m','700',tmp);assert setup.returncode==0,setup.stderr
try:
 for n in names:
  r=sudo('cp',str(ops/n),tmp+'/'+n);assert r.returncode==0,r.stderr
 def invoke(action):
  py='import runpy,socket,sys; socket.gethostname=lambda:"box-webhost"; sys.argv=["launch",'+repr(action)+']; runpy.run_path('+repr(tmp+'/beta_files_launch.py')+',run_name="__main__")'
  return sudo('python3','-I','-B','-c',py)
 assert sudo('chmod','666',tmp+'/beta_launcher.py').returncode==0
 result=invoke('plan');assert result.returncode and 'unprotected launcher path' in result.stderr,result.stderr
 assert sudo('chmod','644',tmp+'/beta_launcher.py').returncode==0
 py='from pathlib import Path; p=Path('+repr(tmp+'/beta_files_preflight.py')+'); p.write_bytes(p.read_bytes()+b"\\n# tamper\\n")'
 assert sudo('python3','-I','-B','-c',py).returncode==0
 result=invoke('recover');assert result.returncode and 'bundle source pin mismatch' in result.stderr,result.stderr
 print('PASS actual protected entrypoint refuses unsafe custody and tampered source')
finally:
 py='from pathlib import Path; p=Path('+repr(tmp)+'); [(p/n).unlink(missing_ok=True) for n in '+repr(names)+']; p.rmdir()'
 result=sudo('python3','-I','-B','-c',py)
 if result.returncode:print('fixture cleanup failed: '+result.stderr,file=sys.stderr)
