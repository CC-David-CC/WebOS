#!/usr/bin/env python3
"""Package the tested password policy and account UI onto the scout-fix release."""
import hashlib,importlib.util,json,shutil,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/mobile-scout-profile26-r1';OUT=ROOT/'.build/releases/simple-password-profile26-r1';PIN='5a8cf3eaab393acca76eb5c3acd248a10dad08db1ec6f1bc35fecd2261c5f468'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
def key(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists();stage=Path(tempfile.mkdtemp(prefix='.simple-password-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 lifecycle=(ROOT/'origin_service/lifecycle.py').read_bytes();(stage/'origin_service/lifecycle.py').write_bytes(lifecycle)
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']};old=core['app.js'].decode();new=(ROOT/'app.js').read_text();start='  showAccountForm(mode,anchor){';end='  async showDeviceStorage(anchor){';oldpart=old[old.index(start):old.index(end)];newpart=new[new.index(start):new.index(end)];assert old.count(oldpart)==1 and "Password: 15–128 characters." in oldpart and "Password: 4–32 characters." in newpart;core['app.js']=old.replace(oldpart,newpart).encode()
 graph['core']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in core.items()};newcore=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=newcore
 for n,raw in core.items():put(newcore+'/'+n,raw)
 put('assets/desktop/network-release.json',enc(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,newcore).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));put('assets/desktop/offline-worker.js',(ROOT/'scripts/templates/device-cache-worker.js').read_text().replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'core':newcore}))
finally:
 if stage.exists():shutil.rmtree(stage)
