#!/usr/bin/env python3
"""Raise the desktop's default accounted networking allowance to 512 MiB."""
import hashlib,importlib.util,json,shutil,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'.build/releases/system-channel-profile26-r2';out=ROOT/'.build/releases/network-512-profile26-r1';pin='894b758887f3b426944e668c81e089377549011856a2a1452d78d13167ca6893'
def sha(v):return hashlib.sha256(v).hexdigest()
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
def key(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def record(p):b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',base/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(base)['manifestSHA256']==pin and not out.exists()
graph=json.loads((base/'assets/desktop/network-release.json').read_bytes());old=graph['coreDirectory'];core={n:(base/old/n).read_bytes() for n in graph['core']};needle=b'let metadataMiB=128,releaseStoragePermission=()=>{};';assert core['networking.js'].count(needle)==1 and 'let metadataMiB=512,releaseStoragePermission=()=>{};' in (ROOT/'networking.js').read_text();core['networking.js']=core['networking.js'].replace(needle,needle.replace(b'128',b'512'));graph['core']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in core.items()};new=str(Path(old).parent/key(graph['core']));graph['coreDirectory']=new
stage=Path(tempfile.mkdtemp(prefix='.network-default-',dir=out.parent))
try:
 shutil.copytree(base,stage,dirs_exist_ok=True);changed=set();removed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 for n,raw in core.items():put(new+'/'+n,raw)
 assert (base/'index.html').read_text().count(old)>=1;put('index.html',(base/'index.html').read_text().replace(old,new).encode());put('assets/desktop/network-release.json',enc(graph))
 for p in (stage/old).rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)));p.unlink()
 cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));put('assets/desktop/offline-worker.js',(ROOT/'scripts/templates/device-cache-worker.js').read_text().replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((base/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((base/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(out);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'release':str(out)}))
finally:
 if stage.exists():shutil.rmtree(stage)
