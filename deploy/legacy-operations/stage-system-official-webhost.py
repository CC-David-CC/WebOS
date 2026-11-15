#!/usr/bin/env python3
"""Install the tested official-service package without activating it."""
import hashlib,json,os,shutil,stat,tempfile
from pathlib import Path
source=Path('/tmp/codi-official-system-r2');parent=Path('/srv/codi-connected/official-services');dest=parent/'system-channel-r2';pin='04fd3157bf1fbd094a4324a9654868a76179879cb0d0a6cc4a12988946e18d4b'
assert os.geteuid()==0 and source.is_dir() and not source.is_symlink() and not dest.exists()
raw=(source/'official-service.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;m=json.loads(raw);assert m['version']=='codi-official-service/1'
paths=set(m['files'])|{'official-service.json'};assert {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}==paths
for name,rec in m['files'].items():
 p=source/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts and not p.is_symlink() and p.is_file() and p.stat().st_nlink==1 and len(p.read_bytes())==rec['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
parent.mkdir(mode=0o755,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.system-',dir=parent))
try:
 for name in sorted(paths):
  target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,target);target.chmod(0o644)
 for p in [stage,*stage.rglob('*')]:
  if p.is_dir():p.chmod(0o755)
 for name,rec in m['files'].items():
  p=stage/name;assert p.stat().st_uid==0 and p.stat().st_size==rec['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
 os.rename(stage,dest)
finally:
 if stage.exists():shutil.rmtree(stage)
print(json.dumps({'status':'PASS','release':str(dest),'manifestSHA256':pin,'files':len(m['files'])}))
