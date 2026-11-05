#!/usr/bin/env python3
import hashlib,importlib.util,json,os,pathlib,tempfile
p=pathlib.Path(__file__).resolve().parents[1]/'research/cad-source-access/registry.py';s=importlib.util.spec_from_file_location('cad_source_registry',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
# Run as root under /var/lib to exercise real immutable ancestor custody.
assert os.geteuid()==0
with tempfile.TemporaryDirectory(dir='/var/lib',prefix='codi-cad-source-registry-') as t:
 root=pathlib.Path(t);os.chmod(root,0o755);data=b'example source bytes';(root/'source.zip').write_bytes(data);os.chmod(root/'source.zip',0o644)
 manifest={'version':'codi-cad-source-registry/1','files':{'source.zip':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}}};raw=json.dumps(manifest).encode();(root/'manifest.json').write_bytes(raw);os.chmod(root/'manifest.json',0o644);
 try:m.SourceRegistry(root,'0'*64)
 except ValueError:pass
 else:raise AssertionError('wrong manifest accepted')
 registry=m.SourceRegistry(root,hashlib.sha256(raw).hexdigest())
 try:
  fd,size,digest=registry.open('source.zip');assert os.read(fd,100)==data and size==len(data) and digest==manifest['files']['source.zip']['sha256'];os.close(fd)
  for n in ('../source.zip','manifest.json','unknown'):
   try:registry.open(n)
   except ValueError:pass
   else:raise AssertionError('unknown source accepted')
  (root/'source.zip').write_bytes(b'tampered')
  try:registry.open('source.zip')
  except ValueError:pass
  else:raise AssertionError('tamper accepted')
  (root/'source.zip').unlink();(root/'source.zip').symlink_to('/etc/passwd')
  try:registry.open('source.zip')
  except OSError:pass
  else:raise AssertionError('symlink accepted')
 finally:registry.close()
print('PASS pinned immutable source registry, unknown/traversal/tamper/symlink rejection; authentication not tested')
