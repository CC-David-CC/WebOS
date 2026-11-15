import hashlib,json,os,shutil,socket,tempfile
from pathlib import Path
ROOT=Path('/srv/codi-connected/simplified');BASE=ROOT/'7841c461b24a18f6fa667a609667964ef12d0b4e71cccd8be6c2898e35ba41da';INPUT=Path('/tmp/codi-reg-input-1101/identity.mjs');OLD='64d71b17a26d1d7900798ee9989fcc3d4f43c1ac1b908949240cd4f7b78a64ca';NEW='7b8f6d710e220a686401d8756864cc8f25d41ba743d378c213f69b55ed723953'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def replace(p,raw):
 t=p.with_name('.'+p.name+'.new');t.write_bytes(raw);t.chmod(0o644);os.replace(t,p)
assert os.geteuid()==0 and socket.gethostname()=='box-webhost' and not BASE.is_symlink() and not INPUT.is_symlink() and sha(INPUT)==NEW and sha(BASE/'network/identity.mjs')==OLD
old=json.loads((BASE/'assets/desktop/cache-manifest.json').read_text());assert old['id']==BASE.name
for name,entry in old['files'].items():
 p=BASE/name;assert not p.is_symlink() and p.is_file() and p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256']
stage=Path(tempfile.mkdtemp(prefix='.registration-frontend-',dir=ROOT))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True,copy_function=os.link,symlinks=False);replace(stage/'network/identity.mjs',INPUT.read_bytes());files={}
 for p in sorted(stage.rglob('*')):
  assert not p.is_symlink()
  if p.is_file() and (n:=p.relative_to(stage).as_posix()) not in ('assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'):files[n]={'bytes':p.stat().st_size,'sha256':sha(p)}
 assert {n for n in set(files)|set(old['files']) if files.get(n)!=old['files'].get(n)}=={'network/identity.mjs'}
 release=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest();manifest={'version':'codi-public-cache/1','id':release,'files':files};encoded=json.dumps(manifest,separators=(',',':')).encode();replace(stage/'assets/desktop/cache-manifest.json',encoded);worker=stage/'assets/desktop/offline-worker.js';lines=worker.read_bytes().splitlines(keepends=True);assert lines[1].startswith(b'const RELEASE=') and BASE.name.encode() in lines[1];lines[1]=b'const RELEASE='+encoded+b';\n';replace(worker,b''.join(lines));dest=ROOT/release;assert not dest.exists() and not dest.is_symlink();stage.chmod(0o755);stage.rename(dest);print(json.dumps({'release':release,'changed':['network/identity.mjs']}))
finally:
 if stage.exists():shutil.rmtree(stage)
