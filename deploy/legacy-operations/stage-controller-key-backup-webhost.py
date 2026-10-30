#!/usr/bin/env python3
"""Install the exact sealed peer-pending candidate as inactive root-owned code."""
import hashlib,json,os,pathlib,shutil,stat,tempfile
P=pathlib.Path; source=P('/tmp/codi-controller-backup-TE1ymnzM'); parent=P('/srv/codi-connected/releases'); dest=parent/'native26-controller-backup-r1'; expected='7034ae0e2f2c4e4b4ad8a04c7219835cc93b0fc0be4433da5b10d295d8878bbf'
assert os.geteuid()==0 and source.is_dir() and not source.is_symlink() and parent.is_dir() and not dest.exists()
raw=(source/'connected-release.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
manifest=json.loads(raw);assert manifest['version']=='codi-connected-development/26';assert len(manifest['files'])>0
expected_paths=set(manifest['files'])|{'connected-release.json'};assert {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}==expected_paths
for name,rec in manifest['files'].items():
 p=source/name;assert not P(name).is_absolute() and '..' not in P(name).parts and all(not x.is_symlink() for x in [p,*p.parents] if x!=P('/'))
 info=p.stat();assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==rec['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
install=P(tempfile.mkdtemp(prefix='.peer-pending-',dir=parent))
try:
 for name in sorted(expected_paths):
  src=source/name;target=install/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);target.chmod(0o644)
 for directory in [install,*(p for p in install.rglob('*') if p.is_dir())]:directory.chmod(0o755)
 assert hashlib.sha256((install/'connected-release.json').read_bytes()).hexdigest()==expected
 for name,rec in manifest['files'].items():
  p=install/name;assert p.stat().st_uid==0 and p.stat().st_size==rec['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
 os.rename(install,dest)
finally:
 if install.exists():shutil.rmtree(install)
print(json.dumps({'status':'PASS','action':'stage-only','release':str(dest),'manifestSHA256':expected,'files':len(manifest['files'])}))
