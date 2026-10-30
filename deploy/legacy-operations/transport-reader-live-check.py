#!/usr/bin/env python3
"""Exercise the pinned SDK-only reader upgrade and rollback on live development."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import traceback

COMMIT='8258f5586f960e0835f37d687a008de932376ae8'
PUB='a98cb6bfd47b652a631fcd219169d3b4274661b1977fe9e2acf9d0ede1a199ee'
PRUNE='dafe8b40857264ed6d40a24a7d51bb8eae0523f10bf6277a7c75e35d1cf4e2e6'
BOOT="import os,sys;p='/srv/codi-connected/venvs/517179c/bin/python';os.execv(p,[p,'-I','-B','-c',sys.stdin.read()])"

def root(code):
    r=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(BOOT)],input=code,text=True,capture_output=True,timeout=240)
    if r.returncode:raise RuntimeError(r.stderr[-8000:] or r.stdout[-8000:])
    return json.loads(r.stdout)

def run():
    result={'status':'FAIL','sourceCommit':COMMIT,'steps':[],'wholeGoalComplete':False,'scope':__doc__}
    try:
        installed=root('''import hashlib,json,os,stat,subprocess
from pathlib import Path
repo=Path('/home/dflanag3/webhost-sites/sites/ksu.codes')
git=lambda *a:subprocess.check_output(['runuser','-u','dflanag3','--','git','-C',str(repo),*a],text=True).strip()
assert git('rev-parse','HEAD')=='''+repr(COMMIT)+''' and not git('status','--porcelain')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,pin in [('reader-recovery-proof-r1','4e79c9f611fa255177251c3a99717762df6c2805f4a3c69082704feeeda0f0dd'),('reader-transport-update-r1','cfaff2ea65aa3b99e487f9d21aa24acfbda43202936a7a5e8ab234ed4251895a')]:
 folder=repo/'tools/codiserver'/name;assert sha(folder/'source-proof.json')==pin;records=json.loads((folder/'source-proof.json').read_bytes())['files']
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}==set(records)|{'source-proof.json'}
 for n,r in records.items():
  p=folder/n;assert not p.is_symlink() and p.is_file() and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],n
def protected(p):
 for q in [p,*p.parents]:
  st=q.lstat();assert not q.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,str(q)
def install(source,category,pin):
 parent=Path('/srv/codi-connected')/category
 if not parent.exists():protected(parent.parent);parent.mkdir(mode=0o755)
 protected(parent);folder=parent/pin
 if not folder.exists():folder.mkdir(mode=0o755)
 protected(folder);target=folder/source.name;raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==pin
 if not target.exists():
  fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
  with os.fdopen(fd,'wb') as f:f.write(raw)
 protected(target);assert sha(target)==pin;return str(target)
pub=install(repo/'tools/codiserver/reader-transport-update-r1/operator/publish-transport-reader.py','transport-readers','''+repr(PUB)+''')
prune=install(repo/'tools/codiserver/reader-recovery-proof-r1/scripts/prune-recovery-reader-release.py','cleanup-tools','''+repr(PRUNE)+''')
print(json.dumps({'status':'PASS','publisher':pub,'pruner':prune,'sourcePacketsVerified':2}))
''')
        result['installation']=installed
        value=root('import runpy;runpy.run_path('+repr(installed['pruner'])+',run_name="__main__")')
        assert value['status']=='PASS';result['obsolete680Cleanup']=value
        print(json.dumps({'step':'obsolete680Cleanup','status':value['status']}),flush=True)
        for action in ['stage','activate','verify','rollback','verify','activate','verify']:
            value=root('import runpy,sys;sys.argv=['+repr(installed['publisher'])+','+repr(action)+',"--commit",'+repr(COMMIT)+'];runpy.run_path(sys.argv[0],run_name="__main__")')
            result['steps'].append(value);assert value['status']=='PASS',value
            print(json.dumps(value),flush=True)
        result['status']='PASS'
    except Exception as e:result.update(error=str(e),traceback=traceback.format_exc())
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();value=run();a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'steps':len(value['steps']),'error':value.get('error')}));raise SystemExit(0 if value['status']=='PASS' else 1)
