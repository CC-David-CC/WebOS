#!/usr/bin/env python3
"""Public three-Linux peer/fallback flow with the real coordinator SIGSTOP.

Ordinary TLS; one owned QA account disabled afterward. A transient90s resume
watchdog prevents this test leaving discovery paused if the test client dies.
No native/room restart, data restore, router port or primary root signing.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
public=module('coordinator_failure_public_support',ROOT/'scripts/hosted-peer-public-check.py')
suite=module('coordinator_failure_actual',ROOT/'scripts/reader-directory-native-check.py')
original=suite.driver.call

def trusted(path,data=None,method=None):
    if path=='/session':
        caps=data['capabilities']['alwaysMatch'];args=caps['goog:chromeOptions']['args'];marker='--ignore-certificate-errors-spki-list='+public.MARKER
        assert args.count(marker)==1;args.remove(marker);assert not any('ignore-certificate' in v for v in args);caps['acceptInsecureCerts']=False
    return original(path,data,method)

def run(release):
    guard='codi-reader-resume-test-'+secrets.token_hex(6);actions=[]
    def control(action):
        assert action in ['pause','resume']
        code='''import json,os,signal,subprocess,time
from pathlib import Path
action=ACTION;guard=GUARD;unit='codi-readers-ksu.service'
pid=int(subprocess.check_output(['systemctl','show',unit,'-p','MainPID','--value'],text=True));assert pid>0
proc=Path('/proc')/str(pid);assert b'serve-reader-coordinator.py' in (proc/'cmdline').read_bytes();assert proc.stat().st_uid!=0
state=lambda:dict(line.split(':',1) for line in (proc/'status').read_text().splitlines() if ':' in line)['State'].strip()
if action=='pause':
 subprocess.run(['systemd-run','--quiet','--unit='+guard,'--on-active=90s','--collect','/usr/bin/systemctl','kill','--kill-whom=main','--signal=CONT',unit],check=True,capture_output=True)
 os.kill(pid,signal.SIGSTOP);deadline=time.monotonic()+2
 while not state().startswith('T'):
  assert time.monotonic()<deadline;time.sleep(.01)
 print(json.dumps({'action':action,'pid':pid,'paused':True,'resumeWatchdog':guard,'automaticResumeSeconds':90}))
else:
 was=state().startswith('T');os.kill(pid,signal.SIGCONT)
 subprocess.run(['systemctl','stop',guard+'.timer'],check=False,capture_output=True)
 print(json.dumps({'action':action,'pid':pid,'wasPaused':was,'resumeWatchdogCancelled':True}))
'''.replace('ACTION',repr(action)).replace('GUARD',repr(guard))
        r=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','python3','-'],input=code,text=True,capture_output=True,timeout=15)
        assert r.returncode==0,r.stderr[-3000:];value=json.loads(r.stdout);actions.append(value);return value
    suite.driver.call=trusted;suite.vm.remote=public.public_remote
    v=suite.run(release,coordinator_control=control)
    v.update(scope=__doc__,defaultPublicTLS=True,actualURL='https://ksu.codes/',publicWANTested=False,coordinatorControlActions=actions,wholeGoalComplete=False,wrapperSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return v

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();v=run(a.release.resolve());a.output.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps({'status':v['status'],'checks':len(v['checks']),'error':v.get('error')}));raise SystemExit(0 if v['status']=='PASS' else 1)
