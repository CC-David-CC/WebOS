#!/usr/bin/env python3
"""Disable only witnessed disposable document-QA accounts after their files are removed."""
import argparse,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,pwd,re,sqlite3,subprocess,sys,uuid
from pathlib import Path
v=json.load(sys.stdin);assert v['ownedFilesRemoved'] is True and len(v['names'])==2 and set(v['subjects'])<=set(v['names']);assert all(re.fullmatch('qa_doc_[a-f0-9]{12}',n) for n in v['names'])
c=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text());release=Path(c['release']);db=Path(c['stateRoot'])/'issuer/state/accounts.sqlite3';files=json.loads(Path(c['userFiles']['configFile']).read_text())
def policies():
 with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as s:return {n:(sub,d,g) for n,sub,d,g in s.execute('SELECT username,subject,disabled,generation FROM accounts JOIN account_policy USING(subject)')}
before=policies();others={n:r for n,r in before.items() if n not in v['names']};rows=[]
for name,subject in v['subjects'].items():
 assert before[name][0]==subject;home=Path(files['dataRoot'])/'users'/uuid.UUID(subject[5:]).hex;assert not home.is_symlink() and home.is_dir() and not any(home.iterdir())
 code='import sys,json;sys.path.insert(0,sys.argv[1]);from origin_service.lifecycle import set_disabled;print(json.dumps(set_disabled(sys.argv[2],sys.argv[3],True)))'
 r=subprocess.run(['runuser','-u','codi-issuer','--',c['python'],'-I','-B','-c',code,str(release),str(Path(c['stateRoot'])/'issuer/state'),name],check=True,capture_output=True,text=True,timeout=20);result=json.loads(r.stdout);assert result['subject']==subject and result['disabled'] is True;rows.append({'name':name,'subject':subject,'disabled':True,'homeEmpty':True})
after=policies();assert others=={n:r for n,r in after.items() if n not in v['names']};print(json.dumps({'status':'PASS','accounts':rows,'otherAccountPoliciesUnchanged':True,'userFilesRead':False}))
'''
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ledger',type=Path,default=ROOT/'.build/checks/document-public-fixtures.json');parser.add_argument('--output',type=Path,default=ROOT/'.build/checks/document-public-cleanup-result.json');args=parser.parse_args()
 p=args.ledger;v=json.loads(p.read_text());r=subprocess.run(['ssh','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(v),capture_output=True,text=True,timeout=90)
 if r.returncode:raise RuntimeError(r.stderr or r.stdout)
 d=json.loads(r.stdout);v['accountsDisabled']=True;p.write_text(json.dumps(v,indent=2)+'\n');args.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
