#!/usr/bin/env python3
"""Build a paired, narrowly pinned networking and history-service candidate."""
import hashlib,importlib.util,json,shutil,tempfile,sys
sys.dont_write_bytecode=True
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R/'.build/releases/official-fast-profile26-r1';O=R/'.build/releases/submission-fair-profile26-r1';T=R/'.build/shared-services/submission-fair-network-probe-r1/apps/replica-core/test/index.mjs'
PIN='2827a9879cd5e3d1577eda51e0c90d81c24f4275ab6808d5f3d5ff1d27640f10';TEST='5998c5e7bd780d1b614b149cea51b9bd900d12d459b1b42ffc4f757a564bf65a'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def key(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def rec(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',B/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(B)['manifestSHA256']==PIN and not O.exists();raw=T.read_bytes();assert sha(raw)==TEST
s=raw.decode();marker='\nexport { DeviceChannelSession';assert s.count(marker)==1;s=s[:s.index(marker)];getter=' __testWaitCount(channel){const e=this.#channels.get(channel);return e?.roundWaiting||0;}\n';assert s.count(getter)==1;s=s.replace(getter,'');service=s.encode()
stage=Path(tempfile.mkdtemp(prefix='.submission-fair-',dir=O.parent))
try:
 shutil.copytree(B,stage,dirs_exist_ok=True);changed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 registry=json.loads((B/'assets/desktop/shared-services.json').read_bytes());entry=next(x for x in registry['services'] if x['name']=='device-history');old=entry['path'];legal=(B/Path(old).parent/'index.mjs.LEGAL.txt').read_bytes();files={'index.mjs':service,'index.mjs.LEGAL.txt':legal};desc={n:{'sha256':sha(v),'bytes':len(v)} for n,v in sorted(files.items())};folder='assets/desktop/services/device-history/'+sha(json.dumps(desc,separators=(',',':')).encode());entry.update(path=folder+'/index.mjs',files=desc)
 for n,raw in files.items():put(folder+'/'+n,raw)
 put('assets/desktop/shared-services.json',enc(registry));graph=json.loads((B/'assets/desktop/network-release.json').read_bytes());oldnet=graph['directory'];modules={n:(B/oldnet/n).read_bytes() for n in graph['modules']};assert sha(modules['resource-budget.mjs'])=='09d6799b25baf1fd143f089c06422ab38e021412ed0beb323fe44838cc52995f';modules['resource-budget.mjs']=(R/'network/resource-budget.mjs').read_bytes();graph['modules']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in modules.items()};newnet=str(Path(oldnet).parent/key(graph['modules']));graph['directory']=newnet
 for n,raw in modules.items():put(newnet+'/'+n,raw)
 oldcore=graph['coreDirectory'];core={n:(B/oldcore/n).read_bytes() for n in graph['core']};assert sum(v.count(old.encode()) for v in core.values())>0 and sum(v.count(oldnet.encode()) for v in core.values())>0;core={n:v.replace(old.encode(),(folder+'/index.mjs').encode()).replace(oldnet.encode(),newnet.encode()) for n,v in core.items()};graph['core']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in core.items()};newcore=str(Path(oldcore).parent/key(graph['core']));graph['coreDirectory']=newcore
 for n,raw in core.items():put(newcore+'/'+n,raw)
 put('assets/desktop/network-release.json',enc(graph));put('index.html',(B/'index.html').read_text().replace(oldcore,newcore).encode())
 cache=json.loads((B/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:rec(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));put('assets/desktop/offline-worker.js',(R/'scripts/templates/device-cache-worker.js').read_text().replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((B/'release.json').read_bytes());public['files']={n:rec(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((B/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):rec(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(O);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'service':entry['path'],'network':newnet,'core':newcore}))
finally:
 if stage.exists():shutil.rmtree(stage)
