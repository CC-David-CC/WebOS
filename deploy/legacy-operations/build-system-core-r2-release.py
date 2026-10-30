#!/usr/bin/env python3
"""Replace only the device-history service in the current official release."""
import hashlib,importlib.util,json,shutil,tempfile,sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/gossip-direction-profile26-r1';OUT=ROOT/'.build/releases/system-core-profile26-r2';SERVICE=ROOT/'.build/shared-services/system-channel-r2';PIN='1630dc96125e41fd25d92535d41f8c73b8d956d06a49930f9a53362cbc25c112'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def key(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists();stage=Path(tempfile.mkdtemp(prefix='.official-rediscovery-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 registry=json.loads((BASE/'assets/desktop/shared-services.json').read_bytes());entry=next(x for x in registry['services'] if x['name']=='device-history');old=entry['path'];new=json.loads((SERVICE/'shared-service.json').read_bytes());assert new['name']=='device-history' and new['sourceAlias']==entry['sourceAlias'];entry.update(new)
 for name,expected in new['files'].items():
  path=str(Path(new['path']).parent/name);assert record(SERVICE/path)==expected;put(path,(SERVICE/path).read_bytes())
 put('assets/desktop/shared-services.json',enc(registry));graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());oldnet=graph['directory'];modules={n:(BASE/oldnet/n).read_bytes() for n in graph['modules']};modules['resource-budget.mjs']=(ROOT/'network/resource-budget.mjs').read_bytes();graph['modules']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in modules.items()};newnet=str(Path(oldnet).parent/key(graph['modules']));graph['directory']=newnet
 for n,raw in modules.items():put(newnet+'/'+n,raw)
 previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']};count=sum(v.count(old.encode()) for v in core.values());assert count>0 and sum(v.count(oldnet.encode()) for v in core.values())>0
 core={n:v.replace(old.encode(),new['path'].encode()).replace(oldnet.encode(),newnet.encode()) for n,v in core.items()}
 network=core['networking.js'].decode();source=(ROOT/'networking.js').read_text()
 for old_part,new_part in [('let deviceChannels,deviceTask,deviceLife,deviceBinding;','let deviceChannels,deviceTask,deviceLife,deviceBinding,systemChannelTimer;'),('  function closeNetwork(){','  function closeNetwork(){\n    clearTimeout(systemChannelTimer);systemChannelTimer=null;')]:
  assert network.count(old_part)==1;network=network.replace(old_part,new_part)
 start=source.index('        if(c.deviceChannels.officialDiscovery===true){let retry=10000;');end=source.index('\n        return true;',start);snippet=source[start:end]
 old_part='networkReady=true;if(c.deviceChannels.channelIndex===true){channelListingTimer=setInterval(()=>refreshOwnedListings(),8000);refreshOwnedListings();}return true;'
 assert network.count(old_part)==1;network=network.replace(old_part,old_part[:-len('return true;')]+'\n'+snippet+'\n        return true;');core['networking.js']=network.encode();graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=folder
 for n,raw in core.items():put(folder+'/'+n,raw)
 put('assets/desktop/network-release.json',enc(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,folder).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'service':new['path'],'core':folder}))
finally:
 if stage.exists():shutil.rmtree(stage)
