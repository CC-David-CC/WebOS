#!/usr/bin/env python3
"""Stage the tested shared picker against one pinned live static release."""
import hashlib,json,os,shutil
from pathlib import Path
OLD='b78903ccd9f59eeb6d7556bf60ef390c35d4ce76376fd3beadb130d61bcbb83b'
INPUT_SHA='e66486c60b55a901fdbcebd1398dd7eade0bcb69cd9f155ca1c170da6dc6bb5f'
RELEASES=Path('/srv/codi-connected/simplified');INPUT=Path('/tmp/codi-picker-update/desktop-apps.js')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def replace(path,data):
 tmp=path.with_name('.'+path.name+'.new');tmp.write_bytes(data);tmp.chmod(0o644);os.replace(tmp,path)
def main():
 if os.geteuid()!=0:raise ValueError('root required')
 old=RELEASES/OLD;stage=RELEASES/'.picker-update-stage'
 if stage.exists() or stage.is_symlink():raise ValueError('stage already exists')
 if INPUT.is_symlink() or sha(INPUT)!=INPUT_SHA:raise ValueError('input changed')
 expected=json.loads((old/'assets/desktop/cache-manifest.json').read_text())
 if expected['id']!=OLD:raise ValueError('baseline mismatch')
 for name,record in expected['files'].items():
  p=old/name
  if p.is_symlink() or not p.is_file() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:raise ValueError('baseline asset changed: '+name)
 shutil.copytree(old,stage,copy_function=os.link,symlinks=False)
 replace(stage/'desktop-apps.js',INPUT.read_bytes())
 files={}
 for p in sorted(stage.rglob('*')):
  if p.is_symlink():raise ValueError('unexpected symlink')
  if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
   files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
 if set(files)!=set(expected['files']) or {name for name in files if files[name]!=expected['files'][name]}!={'desktop-apps.js'}:raise ValueError('unexpected changes')
 canonical=json.dumps(files,sort_keys=True,separators=(',',':')).encode();manifest={'version':'codi-public-cache/1','id':hashlib.sha256(canonical).hexdigest(),'files':files};encoded=json.dumps(manifest,separators=(',',':')).encode()
 replace(stage/'assets/desktop/cache-manifest.json',encoded)
 worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True)
 if len(lines)<2 or not lines[1].startswith(b'const RELEASE=') or not lines[1].rstrip().endswith(b';'):raise ValueError('unexpected cache worker')
 lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines))
 dest=RELEASES/manifest['id']
 if dest.exists() or dest.is_symlink():raise ValueError('release exists')
 stage.rename(dest);print(json.dumps({'release':manifest['id'],'files':len(files),'changed':['desktop-apps.js','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js']}))
if __name__=='__main__':main()
