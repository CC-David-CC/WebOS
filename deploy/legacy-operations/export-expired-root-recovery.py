#!/usr/bin/env python3
"""Export a closed public-code-only expired-root recovery operator bundle."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES={'expired_root_steps.py':'origin_service/expired_root_steps.py','expired_root_recovery.py':'origin_service/expired_root_recovery.py','expired_root_managed.py':'origin_service/expired_root_managed.py','run.py':'scripts/run-expired-root-recovery.py'}
def record(path):
 data=path.read_bytes();return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def verify(folder):
 folder=Path(folder)
 if folder.is_symlink() or not folder.is_dir():raise ValueError('Regular bundle required')
 path=folder/'recovery-operator.json';raw=path.read_bytes();value=json.loads(raw)
 if path.is_symlink() or set(value)!={'version','files'} or value['version']!='codi-expired-root-operator/1' or set(value['files'])!=set(SOURCES):raise ValueError('Invalid bundle manifest')
 found=set()
 for p in folder.rglob('*'):
  if p.is_symlink() or not p.is_file() or p.stat().st_nlink!=1:raise ValueError('Only regular unlinked bundle files permitted')
  found.add(str(p.relative_to(folder)))
  if p!=path and value['files'].get(p.name)!=record(p):raise ValueError('Bundle input changed')
 if found!=set(SOURCES)|{'recovery-operator.json'}:raise ValueError('Missing or extra bundle file')
 return {'status':'PASS','manifestSHA256':hashlib.sha256(raw).hexdigest(),'files':value['files']}
def export(target):
 target=Path(target).absolute();base=ROOT/'.build/recovery-operators'
 if '..' in target.parts or target.exists() or not target.is_relative_to(base) or any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('Choose a new local recovery operator directory')
 target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.expired-root-',dir=target.parent))
 try:
  for dest,source in SOURCES.items():
   p=ROOT/source
   if p.is_symlink() or not p.is_file():raise ValueError('Regular recovery source required')
   shutil.copyfile(p,stage/dest);(stage/dest).chmod(0o644)
  value={'version':'codi-expired-root-operator/1','files':{n:record(stage/n) for n in sorted(SOURCES)}};(stage/'recovery-operator.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n');(stage/'recovery-operator.json').chmod(0o644);stage.chmod(0o755);verify(stage);stage.rename(target)
 finally:
  if stage.exists():shutil.rmtree(stage)
 return verify(target)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True);g.add_argument('--output',type=Path);g.add_argument('--verify',type=Path);a=p.parse_args();print(json.dumps(verify(a.verify) if a.verify else export(a.output),indent=2))
