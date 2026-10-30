#!/usr/bin/env python3
"""Read-only audit of all witnessed file-QA accounts and their empty homes."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE='''import json,pathlib,sqlite3,sys,uuid
subjects=json.load(sys.stdin);database=pathlib.Path('/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3')
with sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True) as db:
 for name,subject in subjects.items():
  assert db.execute('SELECT subject,disabled FROM accounts JOIN account_policy USING(subject) WHERE username=?',(name,)).fetchone()==(subject,1)
  folder=pathlib.Path('/var/lib/codi-user-files/ksu/users')/uuid.UUID(subject[5:]).hex
  assert folder.is_dir() and not any(folder.iterdir())
 assert db.execute("SELECT disabled FROM accounts JOIN account_policy USING(subject) WHERE username='dflanag3'").fetchone()==(0,)
print(json.dumps({'status':'PASS','generatedFileQAAccounts':len(subjects),'allDisabled':True,'allTestHomesEmpty':True,'realAccountRemainsEnabled':True,'accountSecretsRead':False}))
'''
if __name__=='__main__':
    subjects={};ledgers={}
    for file in (ROOT/'.build/checks').glob('public-files-fixtures*.json'):
        value=json.loads(file.read_text());assert value['accountsDisabled']
        ledgers[str(file.relative_to(ROOT))]=hashlib.sha256(file.read_bytes()).hexdigest()
        for name,subject in value['subjects'].items():
            assert re.fullmatch('fqa_[0-9a-f]{12}',name) and (name not in subjects or subjects[name]==subject)
            subjects[name]=subject
    assert subjects
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(subjects),capture_output=True,text=True,timeout=30)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    result=json.loads(child.stdout);result['ledgerSHA256']=ledgers
    result['sha256']={'scripts/verify-public-files-fixtures.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'.build/checks/public-files-all-fixtures-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
