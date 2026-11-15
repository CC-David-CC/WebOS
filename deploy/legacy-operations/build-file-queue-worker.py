#!/usr/bin/env python3
"""Build a pinned private gateway candidate with bounded burst admission."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
BASE='2bd92f334f1a29407d33872396cddd51d12d938caa473d33471a5836a0d29084'
OLD={'gateway_service/http.py':'b83ef4ba5115e73a0fc6653a31b92dd13640d38ef6d2fa83ee880c9c0dc87d47'}
def sha(data):return hashlib.sha256(data).hexdigest()
def verify(root):
 raw=(root/'files-service.json').read_bytes();manifest=json.loads(raw)
 if manifest.get('version')!='codi-private-file-service/1':raise ValueError('Invalid worker version')
 files=set()
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('Linked worker entry')
  if not p.is_file():continue
  name=p.relative_to(root).as_posix()
  if name=='files-service.json':continue
  data=p.read_bytes()
  if manifest['files'].get(name)!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('Worker file mismatch: '+name)
  files.add(name)
 if files!=set(manifest['files']):raise ValueError('Worker files missing')
 return sha(raw),manifest
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--sources',type=Path,required=True);p.add_argument('--source-hashes',type=Path,required=True);a=p.parse_args()
 base=a.base.resolve();out=a.output.absolute()
 if out.exists() or out.is_symlink() or not out.parent.is_dir() or base in out.parents or out in base.parents:raise ValueError('Choose a new disjoint output')
 pin,manifest=verify(base)
 if pin!=BASE:raise ValueError('Unexpected worker baseline')
 hashes=json.loads(a.source_hashes.read_text())
 if set(hashes)!=set(OLD):raise ValueError('Expected exact source hash list')
 for name,old in OLD.items():
  if sha((base/name).read_bytes())!=old or sha((a.sources/name).read_bytes())!=hashes[name]:raise ValueError('Source pin mismatch: '+name)
 stage=Path(tempfile.mkdtemp(prefix='.queue-worker-',dir=out.parent))
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True)
  for name in OLD:
   data=(a.sources/name).read_bytes();(stage/name).write_bytes(data);manifest['files'][name]={'bytes':len(data),'sha256':sha(data)}
  (stage/'files-service.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
  for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
  result,_=verify(stage);stage.rename(out);print(json.dumps({'directory':str(out),'manifestSHA256':result,'changed':list(OLD)},indent=2))
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':main()
