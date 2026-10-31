#!/usr/bin/env python3
"""Create a static candidate changing only the file-mirror module and cache pins."""
import argparse,hashlib,json,os,shutil,tempfile
from pathlib import Path
BASE='87f37964f1b08edec68d71acaffe2e0a6fe3358f81581c2f894b4cd4203cf113'
OLD_MIRROR='4c24c5e1013463b56711234e9aff60b974ccd05c23a9f6daa7d004088b7415e4'
NAME='storage/browser/mirror.mjs'
def sha(data):return hashlib.sha256(data).hexdigest()
def put(path,data):path.unlink(missing_ok=True);path.write_bytes(data);path.chmod(0o644)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--mirror',type=Path,required=True);p.add_argument('--mirror-sha256',required=True);p.add_argument('--worker-template',type=Path,required=True);a=p.parse_args();base=a.base.resolve();root=base.parent
 if base.name!=BASE or sha((base/NAME).read_bytes())!=OLD_MIRROR or sha(a.mirror.read_bytes())!=a.mirror_sha256:raise ValueError('Unexpected frontend or mirror source')
 old=json.loads((base/'assets/desktop/cache-manifest.json').read_text())
 if old['id']!=BASE or old['files'][NAME]['sha256']!=OLD_MIRROR:raise ValueError('Unexpected frontend manifest')
 template=a.worker_template.read_text().replace("'networking.js',", "'bootstrap.js',").replace("if(event.data?.type!=='cache-loaded'||!event.ports[0])return;", "if(event.data?.type==='codi-cache-version'&&event.ports[0]){event.ports[0].postMessage({protocol:'codi-simplified-cache/1',release:RELEASE.id});return;}\n  if(event.data?.type!=='cache-loaded'||!event.ports[0])return;")
 if template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(old,separators=(',',':')))!=(base/'assets/desktop/offline-worker.js').read_text():raise ValueError('Unexpected cache worker template')
 stage=Path(tempfile.mkdtemp(prefix='.inventory-frontend-',dir=root))
 try:
  shutil.copytree(base,stage,copy_function=os.link,dirs_exist_ok=True);data=a.mirror.read_bytes();put(stage/NAME,data)
  files=dict(old['files']);files[NAME]={'bytes':len(data),'sha256':sha(data)};files=dict(sorted(files.items()));release=sha(json.dumps(files,sort_keys=True,separators=(',',':')).encode());new={'version':old['version'],'id':release,'files':files}
  put(stage/'assets/desktop/cache-manifest.json',(json.dumps(new,indent=2)+'\n').encode());put(stage/'assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(new,separators=(',',':'))).encode())
  dest=root/release
  if dest.exists():raise ValueError('Candidate already exists')
  stage.rename(dest);print(json.dumps({'directory':str(dest),'release':release,'changed':[NAME]},indent=2))
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':main()
