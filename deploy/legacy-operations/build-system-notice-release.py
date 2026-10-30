#!/usr/bin/env python3
"""Seal only the SYSTEM notice UI and its session-owned verified observer."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/system-chat-r1';OUT=ROOT/'.build/releases/system-notice-r1';PIN='630864f7aa2fa8a891b90ba959704d6672df10338f0267a81ac79f4bd48c50e5'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(x):return (json.dumps(x,indent=2)+'\n').encode()
def key(x):return sha(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists();stage=Path(tempfile.mkdtemp(prefix='.system-notice-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set();removed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']}
 source=(ROOT/'networking.js').read_text();network=core['networking.js'].decode()
 prefix=source[source.index('// SYSTEM messages'):source.index('// All applications share this session pool')];assert network.count(" 'use strict';\n")==1;network=network.replace(" 'use strict';\n"," 'use strict';\n"+prefix)
 old='let deviceChannels,deviceTask,deviceLife,deviceBinding,systemChannelTimer;';assert network.count(old)==1;network=network.replace(old,'let deviceChannels,deviceTask,deviceLife,deviceBinding,systemChannelTimer,systemView;')
 old='    clearTimeout(systemChannelTimer);systemChannelTimer=null;';assert network.count(old)==1;network=network.replace(old,old+"\n    systemView?.close();systemView=null;if(typeof clearSystemAnnouncement==='function')clearSystemAnnouncement();")
 start=source.index('        if(c.deviceChannels.officialDiscovery===true){\n');end=source.index('\n        return true;',start);snippet=source[start:end]
 old="        if(c.deviceChannels.officialDiscovery===true){let retry=10000;const joinSystem=async()=>{if(!current())return;let view;try{view=deviceChannels.attach({signal:lifetime.signal,onChange:()=>{}});const joined=await view.joinSystemChannel();if(joined||!current())return;}catch(error){if(!current())return;}finally{view?.close();}const delay=retry;retry=Math.min(300000,retry*2);systemChannelTimer=setTimeout(joinSystem,delay);};systemChannelTimer=setTimeout(joinSystem,0);}"
 assert network.count(old)==1;network=network.replace(old,snippet);core['networking.js']=network.encode()
 app=core['app.js'].decode();src=(ROOT/'app.js').read_text();start=src.index('function clearSystemAnnouncement()');end=src.index('function icon(',start);snippet=src[start:end]
 assert app.count('function icon(key, direct = false) {')==1;app=app.replace('function icon(key, direct = false) {',snippet+'function icon(key, direct = false) {');core['app.js']=app.encode()
 graph['core']={n:{'bytes':len(raw),'sha256':sha(raw)} for n,raw in core.items()};folder=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=folder
 for n,raw in core.items():put(folder+'/'+n,raw)
 for p in (stage/previous).rglob('*'):
  if p.is_file():removed.add(str(p.relative_to(stage)))
 shutil.rmtree(stage/previous);put('assets/desktop/network-release.json',enc(graph));put('index.html',(BASE/'index.html').read_text().replace(previous,folder).encode())
 style=(ROOT/'style.css').read_text();css=style[style.index('#system-announcement{'):];assert css.count('#system-announcement{')==1;put('style.css',(BASE/'style.css').read_bytes()+b'\n'+css.encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|changed)};(stage/'release.json').write_bytes(enc(public))
 full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(p for p in stage.rglob('*') if p.is_file() and p.name!='connected-release.json')};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'core':folder}))
finally:
 if stage.exists():shutil.rmtree(stage)
