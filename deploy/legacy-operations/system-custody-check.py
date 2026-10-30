#!/usr/bin/env python3
"""Test private SYSTEM identity, restart, posting and custody refusal."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];script=ROOT/'scripts/official-admin.py'
def call(state,action,text=None,ok=True):
 p=subprocess.run([sys.executable,str(script),'--state',str(state),action],input=text,text=True,capture_output=True)
 if ok and p.returncode:raise AssertionError(p.stderr)
 if not ok and not p.returncode:raise AssertionError('Expected refusal')
 return json.loads(p.stdout) if ok else p.stderr
with tempfile.TemporaryDirectory(prefix='codi-system-custody-') as directory:
 root=Path(directory);root.chmod(0o700);state=root/'state';call(state,'init');first=call(state,'system-init');second=call(state,'system-init');assert first==second
 assert (state/'system-owner.pem').stat().st_mode&0o777==0o600 and (state/'system-channel.json').stat().st_mode&0o777==0o600
 assert call(state,'system-post','first')['height']==1;assert call(state,'system-post','second')['height']==2
 key=state/'system-owner.pem';key.chmod(0o644);assert 'private' in call(state,'system-post','refuse',ok=False);key.chmod(0o600)
 assert call(state,'system-post','third')['height']==3
 processes=[subprocess.Popen([sys.executable,str(script),'--state',str(state),'system-post'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(6)]
 outcomes=[process.communicate('concurrent '+str(i),timeout=30) for i,process in enumerate(processes)]
 assert all(process.returncode==0 for process in processes),outcomes
 assert sorted(json.loads(stdout)['height'] for stdout,_ in outcomes)==list(range(4,10))
 print(json.dumps({'status':'PASS','checks':7}))
