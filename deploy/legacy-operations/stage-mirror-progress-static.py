#!/usr/bin/env python3
"""Stage the reviewed mirror module in a verified immutable static release."""
import hashlib,json,os,shutil
from pathlib import Path
OLD='7f0798683edc5e41e4515d62505d120fa883fadc90d1dc68aa26d848a14fd72c'
CANDIDATE='3eefc87ae89c7be21a0c1a18b339c52c889bd855773d91e38237f7ac5fc193d1'
ROOT=Path('/srv/codi-connected/simplified');INPUT=Path('/tmp/codi-mirror-progress-input.mjs')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def replace(p,data):
 tmp=p.with_name('.'+p.name+'.new');tmp.write_bytes(data);tmp.chmod(0o644);os.replace(tmp,p)
def main():
 if os.geteuid()!=0 or INPUT.is_symlink() or sha(INPUT)!=CANDIDATE:raise ValueError('Invalid candidate or privileges')
 old=ROOT/OLD;stage=ROOT/'.mirror-progress-stage'
 if stage.exists() or stage.is_symlink():raise ValueError('Stage already exists')
 previous=json.loads((old/'assets/desktop/cache-manifest.json').read_text());assert previous['id']==OLD
 for name,record in previous['files'].items():
  p=old/name
  if p.is_symlink() or not p.is_file() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:raise ValueError('Old asset changed: '+name)
 shutil.copytree(old,stage,copy_function=os.link,symlinks=False);replace(stage/'storage/browser/mirror.mjs',INPUT.read_bytes())
 files={}
 for p in sorted(stage.rglob('*')):
  if p.is_symlink():raise ValueError('Unexpected symlink')
  if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
   files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
 changed=[p for p in set(files)|set(previous['files']) if files.get(p)!=previous['files'].get(p)]
 if changed!=['storage/browser/mirror.mjs']:raise ValueError('Unexpected asset changes: '+repr(changed))
 canonical=json.dumps(files,sort_keys=True,separators=(',',':')).encode();manifest={'version':'codi-public-cache/1','id':hashlib.sha256(canonical).hexdigest(),'files':files};encoded=json.dumps(manifest,separators=(',',':')).encode()
 replace(stage/'assets/desktop/cache-manifest.json',encoded);worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True)
 if not lines[1].startswith(b'const RELEASE=') or not lines[1].rstrip().endswith(b';'):raise ValueError('Unexpected cache worker')
 lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines));dest=ROOT/manifest['id']
 if dest.exists() or dest.is_symlink():raise ValueError('Release already exists')
 stage.rename(dest);print(json.dumps({'release':manifest['id'],'files':len(files),'mirror':CANDIDATE}))
if __name__=='__main__':main()
