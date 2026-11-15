#!/usr/bin/env python3
"""Prepare only cache-pinned public inputs and verified forward assets for loopback tests."""
import hashlib, importlib.util, json, os, pathlib, shutil, tarfile
P=pathlib.Path('/tmp/codi-beta-opfs-transition-candidate'); C=pathlib.Path('/tmp/codi-beta-files-forward-20261104-r1'); O=pathlib.Path('/tmp/codi-files-forward-independent-inputs'); A=pathlib.Path('/tmp/codi-beta-opfs-public-archive.tar.gz')
spec=importlib.util.spec_from_file_location('builder','research/beta-files-forward/build.py'); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
b.sealed(P,b.PARENT,'codi-beta-opfs-candidate/1'); b.sealed(C,'e359a081ee09027ce0247daaeabadea3d3d2c766e7b176d6bb422f7b85003a0f',b.FORMAT)
cache=json.loads((P/'assets/desktop/cache-manifest.json').read_bytes())['files']; base=O/'public-base'; old=O/'public-3ad'; new=O/'public-e359'
for d in (base,old,new):
 if d.exists(): raise ValueError('output already exists: '+str(d))
base.mkdir(); matched=[]; replaced=[]; excluded=[]; prefix='codi-beta-opfs-test-baseline-2/'
with tarfile.open(A,'r:gz') as tar:
 seen=set()
 for m in tar:
  if not m.name.startswith(prefix) or m.isdir(): continue
  rel=m.name[len(prefix):]; path=pathlib.PurePosixPath(rel)
  if not m.isfile() or not path.parts or any(x in ('','.','..') for x in rel.split('/')) or rel in seen: raise ValueError('unsafe archive member '+rel)
  seen.add(rel); data=tar.extractfile(m).read(); rec=cache.get(rel)
  if rec and len(data)==rec['bytes'] and hashlib.sha256(data).hexdigest()==rec['sha256']:
   target=base/rel; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data); matched.append(rel)
  elif (P/rel).is_file(): replaced.append(rel)
  else: excluded.append(rel)
# Overlays are already closed-inventory verified. Only their public URLs are installed.
for target,overlay in ((old,P),(new,C)):
 shutil.copytree(base,target)
 for section in ('assets','storage'):
  shutil.copytree(overlay/section,target/section,dirs_exist_ok=True)
 for source,dest in (('shell/app.js','app.js'),('shell/desktop-apps.js','desktop-apps.js')):
  shutil.copyfile(overlay/source,target/dest)
 # gateway client comes from the independently full-inventory-verified dd8 release.
 sdk=pathlib.Path('/tmp/codi-beta-client-44da-built/gateway_service/client.mjs').read_bytes()
 if hashlib.sha256(sdk).hexdigest()!='44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869':raise ValueError('SDK mismatch')
 (target/'gateway').mkdir(exist_ok=True); (target/'gateway/client.mjs').write_bytes(sdk)
print(json.dumps({'matched':len(matched),'parentReplacement':replaced,'excluded':excluded,'old':str(old),'new':str(new)},indent=2))
