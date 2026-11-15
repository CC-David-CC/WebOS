#!/usr/bin/env python3
"""Private recovery archive of explicitly selected public build inputs, never account state."""
import hashlib,json,os,stat,sys,tarfile
from pathlib import Path
root=Path('/mnt/data10tb/codi-handoffs/CAD1-20261110');target=root/'runtime-inputs.tar.gz'
paths=[
'/mnt/data10tb/codi-acad-build-20261107-r2/node_modules',
'/mnt/data10tb/codi-acad-build-20261107-r2/.build/arrangement-native-inputs',
'/mnt/data10tb/codi-occ-finite-curve-native-portable-20261109-r1',
'/mnt/data10tb/codi-occ-circular-root-build-20261108-r3',
'/mnt/data10tb/codi-occ-mechanical-native-portable-20261109-r1',
'/mnt/data10tb/codi-occ-analytic-degenerate-portable-20261110-r4',
'/mnt/data10tb/codi-3mf-qualification-SrUmue/node',
'/mnt/data10tb/codi-agent-bracket-desktop-20261105/active-system/tools/app-builder/node_modules',
'/mnt/data10tb/codi-acad-acceptance-deps-20261109/node_modules/puppeteer-core',
'/mnt/data10tb/codi-mirror-sync-venv',
'/mnt/data10tb/codi-evidence-reader-20261110-r1',
'/mnt/data10tb/codi-acad-assembled-pins-20261110-r8.json',
'/mnt/data10tb/codi-acad-assembled-pins-20261110-r8-unicode.json',
'/mnt/data10tb/codi-acad-multiprofile-pins-20261109-r1.json',
'/mnt/data10tb/codi-restart-runtime-20261110/chrome-linux64.zip',
'/mnt/data10tb/codi-restart-runtime-20261110/chrome-provenance.json']
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
files=[];links=[]
def walk(p,ancestors=()):
 actual=p.resolve(strict=True); assert str(actual).startswith(('/mnt/data10tb/','/usr/','/lib/')),str(actual)
 st=actual.stat();key=(st.st_dev,st.st_ino)
 if p.is_symlink():links.append({'path':str(p),'target':os.readlink(p),'resolved':str(actual)})
 if stat.S_ISDIR(st.st_mode):
  assert key not in ancestors,'cyclic input link'
  for c in sorted(p.iterdir()):
   if c.name=='__pycache__':continue
   walk(c,(*ancestors,key))
 else:
  assert stat.S_ISREG(st.st_mode),str(p)
  files.append({'path':str(p),'archive':str(p).lstrip('/'),'resolved':str(actual),'bytes':st.st_size,'sha256':digest(p),'mtime_ns':st.st_mtime_ns})
for name in paths:walk(Path(name))
assert not target.exists(),'exclusive backup output'
with tarfile.open(target,'w:gz',compresslevel=1,dereference=True) as tar:
 for r in files:
  tar.add(r['path'],arcname=r['archive'],recursive=False)
expected={r['archive']:r for r in files};seen=set()
with tarfile.open(target,'r:gz') as tar:
 for member in tar:
  assert member.isfile() and member.name in expected and member.name not in seen
  r=expected[member.name];assert member.size==r['bytes'];h=hashlib.sha256()
  with tar.extractfile(member) as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  assert h.hexdigest()==r['sha256'];seen.add(member.name)
assert len(seen)==len(expected)
for r in files:
 p=Path(r['path']);assert p.stat().st_mtime_ns==r['mtime_ns'] and digest(p)==r['sha256'],'input changed'
result={'status':'PASS','scope':'Private public-code build/runtime input recovery, not a release or CAD gate proof','files':files,'linksMaterialized':links,'roots':paths,'filesVerified':len(files),'inputBytes':sum(r['bytes'] for r in files),'archive':str(target),'archiveBytes':target.stat().st_size,'archiveSha256':digest(target),'allArchiveMembersIndependentlyRead':True,'sourceInputsUnchanged':True}
(root/'runtime-inputs-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('files','linksMaterialized','roots')}))
