#!/usr/bin/env python3
"""Disable only exact generated file-QA accounts whose subjects were witnessed."""
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,pathlib,re,sqlite3,subprocess,sys,uuid
Path=pathlib.Path;ledger=json.load(sys.stdin)
assert len(ledger['names'])==2 and len(set(ledger['names']))==2
assert all(re.fullmatch(r'fqa_[0-9a-f]{12}',n) for n in ledger['names'])
assert set(ledger['subjects'])<=set(ledger['names'])
state=Path('/var/lib/codi-connected/ksu/issuer/state');database=state/'accounts.sqlite3'
config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text())
assert config['manifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
release=Path(config['release']);script=release/'origin_service/lifecycle.py'
assert hashlib.sha256(script.read_bytes()).hexdigest()==json.loads((release/'connected-release.json').read_text())['files']['origin_service/lifecycle.py']['sha256']
def snapshot():
 with sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True) as db:
  assert db.execute('PRAGMA quick_check(1)').fetchall()==[('ok',)]
  return {name:(subject,disabled,generation) for name,subject,disabled,generation in db.execute('SELECT username,subject,disabled,generation FROM accounts JOIN account_policy USING(subject)')}
before=snapshot();others={k:v for k,v in before.items() if k not in ledger['names']};result=[]
for name in ledger['names']:
 if name not in before:
  assert name not in ledger['subjects'];result.append({'name':name,'created':False});continue
 subject=ledger['subjects'].get(name);assert before[name][0]==subject,'Unwitnessed or different account; refuse to alter it'
 uuid.UUID(subject.removeprefix('user:'))
 code='import json,sys;sys.path.insert(0,sys.argv[1]);from origin_service.lifecycle import set_disabled;print(json.dumps(set_disabled(sys.argv[2],sys.argv[3],True)))'
 command=['runuser','-u','codi-issuer','--',config['python'],'-I','-B','-c',code,str(release),str(state),name]
 response=subprocess.run(command,check=True,capture_output=True,text=True,timeout=15)
 value=json.loads(response.stdout);assert value['subject']==subject and value['disabled'] is True
 folder=Path('/var/lib/codi-user-files/ksu/users')/uuid.UUID(subject[5:]).hex
 if folder.exists() and any(folder.iterdir()):
  assert name==ledger['names'][0] and ledger.get('maximumBinaryTransfer'),'Only the exact owned successful QA tree may be removed'
  contents={'Saved/note.txt':hashlib.sha256(b'Saved with phone touch').hexdigest(),'from-guest.txt':hashlib.sha256(b'Temporary Linux content').hexdigest(),'late.txt':hashlib.sha256(b'private delayed response').hexdigest(),'maximum.bin':ledger['maximumBinaryTransfer']['sha256']}
  if ledger.get('actualImportAndDownloadSHA256'):contents['imported.bin']=ledger['actualImportAndDownloadSHA256']
  files=list(folder.rglob('*'));assert not folder.is_symlink() and folder.stat().st_uid==978
  for file in files:
   relative=str(file.relative_to(folder));assert not file.is_symlink() and file.stat().st_uid==978
   if file.is_dir():assert relative=='Saved'
   else:assert relative in contents and file.stat().st_size<=8388608 and hashlib.sha256(file.read_bytes()).hexdigest()==contents[relative]
  for file in sorted(files,key=lambda p:len(p.parts),reverse=True):
   if file.is_dir():file.rmdir()
   else:file.unlink()
 empty=not folder.exists() or not any(folder.iterdir())
 result.append({'name':name,'subject':subject,'disabled':True,'testHomeEmpty':empty,'homeRetained':folder.exists()})
after=snapshot();assert others=={k:v for k,v in after.items() if k not in ledger['names']}
assert all(name not in after or after[name][1]==1 for name in ledger['names'])
assert all(v.get('testHomeEmpty',True) for v in result)
print(json.dumps({'status':'PASS','scope':'Only exact witnessed disposable file-QA accounts disabled; real accounts unchanged; empty homes and audit records retained','fixtures':result,'allOtherAccountPoliciesUnchanged':True,'accountDatabaseIntegrity':True}))
'''
if __name__=='__main__':
    file=ROOT/'.build/checks/public-files-fixtures.json'
    ledger=json.loads(file.read_text())
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(ledger),capture_output=True,text=True,timeout=60)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    report=json.loads(child.stdout)
    ledger['accountsDisabled']=True;file.write_text(json.dumps(ledger,indent=2)+'\n')
    (ROOT/'.build/checks/public-files-cleanup-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
