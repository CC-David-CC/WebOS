#!/usr/bin/env python3
"""Replace the official-history polling service in the active sealed release."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/fast-server-apps-r1';OUT=ROOT/'.build/releases/fast-poll-r1';SERVICE=ROOT/'.build/shared-services/catchup-hash-r45';PIN='a798ebbabe25068f1f01fe3dbfaf89ef1e174f28d5951855c7a1b13913bdbaf7'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def key(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists();stage=Path(tempfile.mkdtemp(prefix='.server-poll-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set();removed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 registry=json.loads((BASE/'assets/desktop/shared-services.json').read_bytes());entry=next(x for x in registry['services'] if x['name']=='device-history');old=entry['path'];new=json.loads((SERVICE/'shared-service.json').read_bytes());assert new['name']=='device-history' and new['sourceAlias']==entry['sourceAlias'];entry.update(new)
 for name,expected in new['files'].items():
  path=str(Path(new['path']).parent/name);assert record(SERVICE/path)==expected;put(path,(SERVICE/path).read_bytes())
 olddir=stage/Path(old).parent
 for p in olddir.rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)))
 shutil.rmtree(olddir);put('assets/desktop/shared-services.json',enc(registry));graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']};assert sum(v.count(old.encode()) for v in core.values())>0
 core={n:v.replace(old.encode(),new['path'].encode()) for n,v in core.items()};graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=folder
 for n,raw in core.items():put(folder+'/'+n,raw)
 oldcore=stage/previous
 for p in oldcore.rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)))
 shutil.rmtree(oldcore);put('assets/desktop/network-release.json',enc(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,folder).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(p for p in stage.rglob('*') if p.is_file() and p.name!='connected-release.json')};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'service':new['path'],'core':folder,'removedObsoleteFiles':len(removed)}))
finally:
 if stage.exists():shutil.rmtree(stage)
