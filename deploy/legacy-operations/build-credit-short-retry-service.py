#!/usr/bin/env python3
"""Apply the reviewed transient retry edit to the pinned deployed bundle."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'.build/releases/wake-hop-profile26-r1'
reg=json.loads((base/'assets/desktop/shared-services.json').read_text())
entry=next(x for x in reg['services'] if x['name']=='device-history')
path=Path(entry['path']);src=(base/path).read_bytes()
assert hashlib.sha256(src).hexdigest()=='65e159f4d80bd3a939e31c77f881a759926794dd4ec327d1d57e7ac9c3e1f19e'
old=b'error.retryAfterMs || 15e3';new=b'error.retryAfterMs || 1e3';assert src.count(old)==1;src=src.replace(old,new)
files={'index.mjs':src,'index.mjs.LEGAL.txt':(base/path.parent/'index.mjs.LEGAL.txt').read_bytes()}
desc={k:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for k,v in sorted(files.items())}
bundle=hashlib.sha256(json.dumps(desc,separators=(',',':')).encode()).hexdigest()
out=ROOT/'.build/shared-services/credit-short-retry-history-r1';assert not out.exists()
target=out/'assets/desktop/services/device-history'/bundle;target.mkdir(parents=True)
for k,v in files.items():(target/k).write_bytes(v)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(target.relative_to(out)/'index.mjs'),'files':desc}
(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'bundle':bundle,'entry':desc['index.mjs']}))
