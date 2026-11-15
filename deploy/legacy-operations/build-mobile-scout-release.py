#!/usr/bin/env python3
"""Patch the current sealed service's measured mobile scout limits only."""
import hashlib,importlib.util,json,shutil,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/network-512-profile26-r1';OUT=ROOT/'.build/releases/mobile-scout-profile26-r1';PIN='7f6b827263bfb36b530e1e26c46b4bd4f274e6ef8faa8a995a551faf8d0092aa'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
def key(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists()
stage=Path(tempfile.mkdtemp(prefix='.mobile-scout-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 registry=json.loads((BASE/'assets/desktop/shared-services.json').read_bytes());entry=next(e for e in registry['services'] if e['name']=='device-history');old=entry['path'];files={name:(BASE/Path(old).parent/name).read_bytes() for name in entry['files']};raw=files['index.mjs'].decode()
 for expression in ['enc.encode(JSON.stringify(b.offer)).length <= 8192, "Invalid scout introduction"','enc.encode(JSON.stringify(answer)).length <= 8192, "Scout answer exceeds allowance"','enc.encode(JSON.stringify(b.answer)).length <= 8192, "Invalid scout introduction reply"']:
  assert raw.count(expression)==1;raw=raw.replace(expression,expression.replace('<= 8192','<= 12288'))
 files['index.mjs']=raw.encode();records={name:{'sha256':sha(v),'bytes':len(v)} for name,v in files.items()};bundle=sha(json.dumps(records,separators=(',',':')).encode());folder='assets/desktop/services/device-history/'+bundle;entry['path']=folder+'/index.mjs';entry['files']=records
 for name,raw in files.items():put(folder+'/'+name,raw)
 put('assets/desktop/shared-services.json',enc(registry))
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']};assert sum(v.count(old.encode()) for v in core.values())>0
 core={n:v.replace(old.encode(),entry['path'].encode()) for n,v in core.items()};graph['core']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in core.items()};newcore=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=newcore
 for n,raw in core.items():put(newcore+'/'+n,raw)
 put('assets/desktop/network-release.json',enc(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,newcore).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));put('assets/desktop/offline-worker.js',(ROOT/'scripts/templates/device-cache-worker.js').read_text().replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'service':entry['path'],'core':newcore}))
finally:
 if stage.exists():shutil.rmtree(stage)
