#!/usr/bin/env python3
"""Compose the reviewed Worker guest over the current sealed desktop release."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/worker-async-apps-r1';OUT=ROOT/'.build/releases/guest-worker-r3';PIN='164ef85a8ce43c839d44b9cdd8c7bef6b1c4d005efcbf5b847e8ff62f44ecdbd'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
def key(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists()
stage=Path(tempfile.mkdtemp(prefix='.guest-worker-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set();removed=set()
 def put(name,raw):
  assert contract.public_name(name),name;p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']}
 def section(source,start,end):
  assert source.count(start)==1 and source.count(end)==1;a=source.index(start);b=source.index(end,a);return source[a:b]
 for name,start,end in [('app.js','async function startGuest(){','async function endSession(){'),('desktop-apps.js','const guestFiles = {','function downloadGuestFile(')]:
  old=core[name].decode();source=(ROOT/name).read_text();before=section(old,start,end);after=section(source,start,end);assert old.count(before)==1;core[name]=old.replace(before,after).encode()
 for name in ('guest-worker-client.mjs','guest-worker-runtime.js'):put('assets/desktop/'+name,(ROOT/'assets/desktop'/name).read_bytes())
 graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=folder
 for name,raw in core.items():put(folder+'/'+name,raw)
 for p in (stage/previous).rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)))
 shutil.rmtree(stage/previous);put('assets/desktop/network-release.json',enc(graph));index=(BASE/'index.html').read_text();assert previous in index;put('index.html',index.replace(previous,folder).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|changed)};(stage/'release.json').write_bytes(enc(public))
 full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'core':folder,'removedOldCoreFiles':len(removed)}))
finally:
 if stage.exists():shutil.rmtree(stage)
