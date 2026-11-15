#!/usr/bin/env python3
"""Stage only the reviewed sign-in retry change against a pinned frontend."""
import hashlib,json,os,shutil,socket,sys,tempfile
from pathlib import Path
ROOT=Path('/srv/codi-connected/simplified');BASE='70a9306b59bee93a129acdc609cbf808aef5bb70ae79a7cc6e1e5e2a5dcc0647';NAME='network/identity.mjs';OLD='f79b6df53044e4371dbeeaafd0703c9d29309dc8023092d235c387faf2ee367a';NEW='64d71b17a26d1d7900798ee9989fcc3d4f43c1ac1b908949240cd4f7b78a64ca'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def replace(p,raw):
 tmp=p.with_name('.'+p.name+'.new');tmp.write_bytes(raw);tmp.chmod(0o644);os.replace(tmp,p)
def main():
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or len(sys.argv)!=2:raise ValueError('Root on box-webhost and candidate path required')
 base=ROOT/BASE;source=Path(sys.argv[1]);raw=source.read_bytes();old=json.loads((base/'assets/desktop/cache-manifest.json').read_text())
 if source.is_symlink() or sha(raw)!=NEW or old['id']!=BASE or old['files'][NAME]['sha256']!=OLD or sha((base/NAME).read_bytes())!=OLD:raise ValueError('Unexpected source or baseline')
 stage=Path(tempfile.mkdtemp(prefix='.signin-retry-',dir=ROOT))
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True,copy_function=os.link,symlinks=False);replace(stage/NAME,raw);files=dict(old['files']);files[NAME]={'bytes':len(raw),'sha256':sha(raw)};files=dict(sorted(files.items()));release=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode());manifest={'version':old['version'],'id':release,'files':files};encoded=json.dumps(manifest,separators=(',',':')).encode();replace(stage/'assets/desktop/cache-manifest.json',encoded);worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True)
  if not lines[1].startswith(b'const RELEASE='):raise ValueError('Unexpected worker')
  lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines));dest=ROOT/release
  if dest.exists() or dest.is_symlink():raise ValueError('Destination exists')
  stage.chmod(0o755);stage.rename(dest);print(json.dumps({'status':'staged','release':release,'changed':[NAME]}))
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':main()
