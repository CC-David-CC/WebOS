#!/usr/bin/env python3
"""Stage reviewed desktop changes from the exact live static tree; no activation."""
import hashlib,json,os,shutil,socket,sys,tempfile
from pathlib import Path
BASE='98c9e1ea94d513b291ff00b591745b8d6aadad9969e8565c77ead69cff9e5c90'
ROOT=Path('/srv/codi-connected/simplified')
PINS={'app.js':'1b5bebedcc387101c6892b4d8a329e31a5b0f7008641d92e3d5facdd61eb77e5','desktop-apps.js':'d708ebed449ebc100fad0db31d371930ce909fedbf1d08e15108bbd06d685d62','style.css':'80d664c6c54c34c849bb0f59943213552326b01ccd4a2d93351bb5053c57eedc','network/identity.mjs':'f79b6df53044e4371dbeeaafd0703c9d29309dc8023092d235c387faf2ee367a','apps.json':'b5e4016f9776bbf73026d765add151e18b77b2f70e0ace5adaf1c8b8d5d89b06'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def replace(p,raw):
 tmp=p.with_name('.'+p.name+'.new');tmp.write_bytes(raw);tmp.chmod(0o644);os.replace(tmp,p)
def main():
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or len(sys.argv)!=2:raise ValueError('Root on box-webhost and input directory required')
 inputs=Path(sys.argv[1]);base=ROOT/BASE
 if inputs.is_symlink() or not inputs.is_dir() or base.is_symlink():raise ValueError('Invalid input')
 for name,pin in PINS.items():
  p=inputs/name
  if p.is_symlink() or not p.is_file() or sha(p)!=pin:raise ValueError('Candidate changed: '+name)
 manifest=json.loads((base/'assets/desktop/cache-manifest.json').read_text())
 if manifest['id']!=BASE:raise ValueError('Baseline release changed')
 for name,entry in manifest['files'].items():
  p=base/name
  if p.is_symlink() or not p.is_file() or p.stat().st_size!=entry['bytes'] or sha(p)!=entry['sha256']:raise ValueError('Baseline asset changed: '+name)
 apps=json.loads((inputs/'apps.json').read_text())['apps']
 if {a['id'] for a in apps}!={'files','text'} or len(apps)!=2:raise ValueError('Unexpected applications')
 for app in apps:
  if not all(c in '0123456789abcdef' for c in app['bundleSHA256']) or len(app['bundleSHA256'])!=64:raise ValueError('Invalid bundle')
  root=inputs/'apps'/app['id']/app['bundleSHA256']
  found={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
  if found!=set(app['files']):raise ValueError('Bundle file set changed')
  for name,entry in app['files'].items():
   p=root/name
   if p.is_symlink() or not p.is_file() or p.stat().st_size!=entry['bytes'] or sha(p)!=entry['sha256']:raise ValueError('Bundle changed: '+name)
 stage=Path(tempfile.mkdtemp(prefix='.classroom-frontend-',dir=ROOT))
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True,copy_function=os.link,symlinks=False)
  for name in PINS:
   if name!='apps.json':replace(stage/name,(inputs/name).read_bytes())
  catalog_path=stage/'assets/desktop/apps.json';catalog=json.loads(catalog_path.read_text())
  for app in apps:
   target=stage/'assets/desktop/apps'/app['id'];shutil.rmtree(target);shutil.copytree(inputs/'apps'/app['id']/app['bundleSHA256'],target/app['bundleSHA256'])
   for path in [target,*target.rglob('*')]:
    if path.is_symlink():raise ValueError('Unexpected bundle symlink')
    path.chmod(0o755 if path.is_dir() else 0o644)
   index=next(i for i,x in enumerate(catalog['apps']) if x['id']==app['id']);catalog['apps'][index]=app
  replace(catalog_path,(json.dumps(catalog,indent=2)+'\n').encode())
  files={}
  for p in sorted(stage.rglob('*')):
   if p.is_symlink():raise ValueError('Unexpected symlink')
   if p.is_file() and p.relative_to(stage).as_posix() not in ('assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'):files[p.relative_to(stage).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
  release=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest();new={'version':'codi-public-cache/1','id':release,'files':files};encoded=json.dumps(new,separators=(',',':')).encode()
  replace(stage/'assets/desktop/cache-manifest.json',encoded);worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True)
  if not lines[1].startswith(b'const RELEASE='):raise ValueError('Unexpected worker')
  lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines));dest=ROOT/release
  if dest.exists() or dest.is_symlink():raise ValueError('Candidate already exists')
  stage.chmod(0o755);stage.rename(dest);print(json.dumps({'status':'staged','release':release,'apps':[a['id'] for a in apps]}))
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':main()
