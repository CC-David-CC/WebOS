#!/usr/bin/env python3
"""Build a content-addressed native26 release with official discovery enabled."""
import hashlib,importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/official-recovery-profile26-candidate-r4';OUT=ROOT/'.build/releases/official-discovery-profile26-r1';PIN='9f76e0007353025326950220175ad1aac33fbf2b4b2920487323abab3fbbb64e'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(value):return (json.dumps(value,indent=2)+'\n').encode()
def key(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
def record(path):
 raw=path.read_bytes();return {'bytes':len(raw),'sha256':sha(raw)}
spec=importlib.util.spec_from_file_location('official_release_contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists()
stage=Path(tempfile.mkdtemp(prefix='.official-discovery-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set()
 def put(name,data):
  assert contract.public_name(name),name
  p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);changed.add(name)
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={name:(BASE/previous/name).read_bytes() for name in graph['core']};old=b"version:'codi-device-channels/1',channelDiscovery:true,channelIndex:true";assert core['networking.js'].count(old)==1;core['networking.js']=core['networking.js'].replace(old,old+b',officialDiscovery:true')
 graph['core']={name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in core.items()};folder=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=folder
 for name,raw in core.items():put(folder+'/'+name,raw)
 put('assets/desktop/network-release.json',enc(graph));index=(BASE/'index.html').read_text();assert previous in index;put('index.html',index.replace(previous,folder).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={name:record(stage/name) for name in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={name:record(stage/name) for name in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public))
 full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','release':str(OUT),'manifestSHA256':result['manifestSHA256'],'coreDirectory':folder}))
finally:
 if stage.exists():shutil.rmtree(stage)
