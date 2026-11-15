#!/usr/bin/env python3
"""Stage a pinned code-only chess runner package, without starting services."""
import hashlib,json,os,pathlib,shutil,stat,tempfile
P=pathlib.Path;source=P('/tmp/codi-official-chat-busy-r1');parent=P('/srv/codi-connected/official-services');dest=parent/'chat-busy-r1';pin='9526dd94469ad6eee847ed0518b1ca8f4894c62637fb0c5a3a68ed76256828da'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if os.geteuid()!=0 or source.is_symlink() or not source.is_dir() or dest.exists() or digest(source/'official-service.json')!=pin:raise ValueError('Package staging pin differs')
manifest=json.loads((source/'official-service.json').read_bytes())
if set(manifest)!={'version','files'} or manifest['version']!='codi-official-service/1':raise ValueError('Invalid package manifest')
names=set(manifest['files'])|{'official-service.json'}
if {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}!=names:raise ValueError('Unexpected package inventory')
for name,rec in manifest['files'].items():
 p=source/name
 if P(name).is_absolute() or '..' in P(name).parts or any(x.is_symlink() for x in [p,*p.parents] if x!=P('/')):raise ValueError('Unsafe package path')
 info=p.stat()
 if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size!=rec['bytes'] or digest(p)!=rec['sha256']:raise ValueError('Package file changed')
stage=P(tempfile.mkdtemp(prefix='.chess-rotation-',dir=parent))
try:
 for name in sorted(names):
  target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,target);target.chmod(0o644)
 for directory in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:directory.chmod(0o755)
 for name,rec in manifest['files'].items():
  target=stage/name
  if target.stat().st_uid!=0 or target.stat().st_size!=rec['bytes'] or digest(target)!=rec['sha256']:raise ValueError('Staged package differs')
 if digest(stage/'official-service.json')!=pin:raise ValueError('Staged manifest differs')
 os.rename(stage,dest)
finally:
 if stage.exists():shutil.rmtree(stage)
print(json.dumps({'status':'PASS','action':'stage-only','package':str(dest),'manifestSHA256':pin}))
