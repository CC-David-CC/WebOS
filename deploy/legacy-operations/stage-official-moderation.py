#!/usr/bin/env python3
"""Install a pinned, inactive operator-only moderation package."""
import hashlib,json,os,pathlib,shutil,tempfile
P=pathlib.Path;source=P('/tmp/codi-official-moderation-r2');parent=P('/srv/codi-connected/official-services');dest=parent/'moderation-r2';pin='92e5b2488304cc267dc3d0c0f61d3f6c664d04127027b738fd91afe7adb9cdee';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if os.geteuid()!=0 or not source.is_dir() or source.is_symlink() or dest.exists() or sha(source/'official-service.json')!=pin:raise ValueError('Moderation staging pins differ')
manifest=json.loads((source/'official-service.json').read_bytes());files=set(manifest['files'])|{'official-service.json'}
if manifest.get('version')!='codi-official-service/1' or {str(p.relative_to(source)) for p in source.rglob('*') if not p.is_dir()}!=files:raise ValueError('Moderation inventory differs')
for name,rec in manifest['files'].items():
 p=source/name
 if P(name).is_absolute() or '..' in P(name).parts or any(x.is_symlink() for x in [p,*p.parents] if x!=P('/')) or not p.is_file() or p.stat().st_nlink!=1 or p.stat().st_size!=rec['bytes'] or sha(p)!=rec['sha256']:raise ValueError('Moderation file differs')
stage=P(tempfile.mkdtemp(prefix='.moderation-',dir=parent))
try:
 for name in sorted(files):
  target=stage/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,target);target.chmod(0o644)
 for path in (stage,*(p for p in stage.rglob('*') if p.is_dir())):path.chmod(0o755)
 if sha(stage/'official-service.json')!=pin:raise ValueError('Installed package differs')
 os.rename(stage,dest);print(json.dumps({'status':'PASS','package':str(dest),'manifestSHA256':pin,'runningServicesChanged':False}))
finally:
 if stage.exists():shutil.rmtree(stage)
