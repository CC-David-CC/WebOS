#!/usr/bin/env python3
"""Replace the desktop recovery module in one verified release."""
import hashlib,importlib.util,json,shutil,tempfile,sys
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'.build/releases/control-pacing-profile26-r1';dest=ROOT/'.build/releases/recovery-actions-profile26-r1';pin='7b240ab277bfb16821f2ae8ff9d2ab5d761909c8c886ab8da46b1a589908f154'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(o):return (json.dumps(o,indent=2)+'\n').encode()
def record(p):b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',base/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(base)['manifestSHA256']==pin and not dest.exists();stage=Path(tempfile.mkdtemp(prefix='.recovery-actions-',dir=dest.parent))
try:
 shutil.copytree(base,stage,dirs_exist_ok=True);name='assets/desktop/lifecycle.mjs';assert contract.public_name(name);(stage/name).write_bytes((ROOT/name).read_bytes())
 cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes());cache['files'][name]=record(stage/name);cache['id']=sha(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode());(stage/'assets/desktop/cache-manifest.json').write_bytes(enc(cache));template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();(stage/'assets/desktop/offline-worker.js').write_text(template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
 public=json.loads((base/'release.json').read_bytes())
 for n in (name,'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'):public['files'][n]=record(stage/n)
 (stage/'release.json').write_bytes(enc(public));full=json.loads((base/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(dest);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'release':str(dest)}))
finally:
 if stage.exists():shutil.rmtree(stage)
