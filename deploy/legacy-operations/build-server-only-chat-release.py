#!/usr/bin/env python3
"""Disable automatic peer channel introductions in the server-only desktop."""
import hashlib,importlib.util,json,shutil,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R/'.build/releases/online-retry-profile27-r2';O=R/'.build/releases/server-only-chat-profile27-r1';PIN='572123536e4ba13d1cb657d28a732a52fa0f3c5bc99044246c99e705aff1e653'
def sha(x):return hashlib.sha256(x).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def key(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def record(p):b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',B/'origin_service/release.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);assert c.verify(B)['manifestSHA256']==PIN and not O.exists();stage=Path(tempfile.mkdtemp(prefix='.server-only-chat-',dir=O.parent))
try:
 shutil.copytree(B,stage,dirs_exist_ok=True);changed=set();removed=set()
 def put(n,raw):
  assert c.public_name(n);p=stage/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(n)
 graph=json.loads((B/'assets/desktop/network-release.json').read_bytes());old=graph['coreDirectory'];core={n:(B/old/n).read_bytes() for n in graph['core']};text=core['networking.js'].decode()
 changes=[("  let accountBook=null,accountBookFrozen=false,accountDiscoveryTask=null,channelDiscoveryTask=null,channelIndex=null,channelIndexTask=null,channelListingTimer=null,channelListingBusy=false,channelListingCursor=null;", "  let accountBook=null,accountBookFrozen=false,accountDiscoveryTask=null,channelDiscoveryTask=null,channelIndex=null,channelIndexTask=null,channelListingTimer=null,channelListingBusy=false,channelListingCursor=null;\n  const peerChannelsEnabled=c=>(c?.deviceChannels?.channelTransport??'server')!=='server';"),
 ("if(!config?.discovery||!networkReady||config?.deviceChannels?.channelIndex!==true)","if(!config?.discovery||!networkReady||config?.deviceChannels?.channelIndex!==true||!peerChannelsEnabled(config))"),
 ("if(!config?.discovery||config?.deviceChannels?.channelDiscovery!==true)return;","if(!config?.discovery||config?.deviceChannels?.channelDiscovery!==true||!peerChannelsEnabled(config))return;"),
 ("if(c.deviceChannels.channelIndex===true){channelListingTimer=", "if(c.deviceChannels.channelIndex===true&&peerChannelsEnabled(c)){channelListingTimer="),
 ("channelDiscovery:true,channelIndex:true,officialDiscovery:true","channelDiscovery:false,channelIndex:false,officialDiscovery:true")]
 for before,after in changes:
  assert text.count(before)==1,before;text=text.replace(before,after)
 core['networking.js']=text.encode();graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder=str(Path(old).parent/key(graph['core']));graph['coreDirectory']=folder
 for n,raw in core.items():put(folder+'/'+n,raw)
 for p in (stage/old).rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)))
 shutil.rmtree(stage/old);put('assets/desktop/network-release.json',enc(graph));index=(B/'index.html').read_text();assert index.count(old)>0;put('index.html',index.replace(old,folder).encode())
 cache=json.loads((B/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(R/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((B/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((B/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(p for p in stage.rglob('*') if p.is_file() and p.name!='connected-release.json')};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=c.verify(stage);stage.rename(O);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'core':folder,'removedObsoleteFiles':len(removed)}))
finally:
 if stage.exists():shutil.rmtree(stage)
