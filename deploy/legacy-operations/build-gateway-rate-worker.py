#!/usr/bin/env python3
"""Build a private request-limit candidate from the exact live gateway baseline.

This only creates a candidate. It does not install, restart or change data.
"""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
BASE='8b9ea654f1c8f954c8fbade8c83046c388955d70eb2ed9d70991500bc6a854af'
OLD='f2ba234e04f456940532c488ad945b9897a3337092ffa500e6f261d8921884dd'
NAME='scripts/serve-user-files.py'
def digest(data):return hashlib.sha256(data).hexdigest()
def verify(root):
 raw=(root/'files-service.json').read_bytes();manifest=json.loads(raw)
 if manifest.get('version')!='codi-private-file-service/1' or not isinstance(manifest.get('files'),dict):raise ValueError('Invalid worker manifest')
 files=set()
 for path in root.rglob('*'):
  if path.is_symlink():raise ValueError('Linked worker entry refused')
  if path.is_dir():continue
  if not path.is_file():raise ValueError('Unexpected worker entry')
  name=path.relative_to(root).as_posix()
  if name=='files-service.json':continue
  data=path.read_bytes()
  if manifest['files'].get(name)!={'bytes':len(data),'sha256':digest(data)}:raise ValueError('Worker file mismatch: '+name)
  files.add(name)
 if files!=set(manifest['files']):raise ValueError('Worker files missing')
 return digest(raw),manifest

def build(base,out,source,source_hash):
 base=base.absolute();out=out.absolute();source=source.absolute()
 if base.is_symlink() or not base.is_dir() or out.exists() or out.is_symlink() or not out.parent.is_dir() or base in out.parents or out in base.parents:raise ValueError('Choose a new disjoint output and regular baseline')
 if source.is_symlink() or not source.is_file():raise ValueError('Expected regular source')
 pin,manifest=verify(base)
 if pin!=BASE or digest((base/NAME).read_bytes())!=OLD:raise ValueError('Unexpected gateway baseline')
 data=source.read_bytes()
 if digest(data)!=source_hash or len(data)>262144:raise ValueError('Source pin mismatch')
 stage=Path(tempfile.mkdtemp(prefix='.gateway-rate-',dir=out.parent))
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True);(stage/NAME).write_bytes(data);manifest['files'][NAME]={'bytes':len(data),'sha256':digest(data)}
  (stage/'files-service.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
  for path in [stage,*stage.rglob('*')]:path.chmod(0o755 if path.is_dir() else 0o644)
  result,_=verify(stage);stage.rename(out);return {'directory':str(out),'manifestSHA256':result,'changed':[NAME],'installed':False}
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha256',required=True);a=p.parse_args()
 try:print(json.dumps(build(a.base,a.output,a.source,a.source_sha256),indent=2))
 except (ValueError,OSError) as error:p.error(str(error))
