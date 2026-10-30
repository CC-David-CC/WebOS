#!/usr/bin/env python3
"""Apply two reviewed source-equivalent edits to the pinned deployed bundle."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'.build/releases/account-block-profile26-r1'
reg=json.loads((base/'assets/desktop/shared-services.json').read_text())
entry=next(x for x in reg['services'] if x['name']=='device-history')
path=Path(entry['path']); src=(base/path).read_text()
assert hashlib.sha256(src.encode()).hexdigest()=='48faea3fce4104fcb201eac6fa8a69f7fd00a2fce51211d49c0624f6d4e8fc3e'
old='relays = peers.filter((p) => !this.#archive.policy().validators.includes(p.actor))'
new='relays = value.path.length === 3 ? [] : peers.filter((p) => !this.#archive.policy().validators.includes(p.actor))'
assert src.count(old)==1;src=src.replace(old,new)
old='''    for (const e of this.#entries.values()) if (!channel || e.channel === channel) {
      e.next = 0;
      e.version = (e.version || 0) + 1;
    }
    this.#arm(0);'''
new='''    let ready = false;
    for (const e of this.#entries.values()) if (!channel || e.channel === channel) {
      e.next = 0;
      e.version = (e.version || 0) + 1;
      if (!this.#busy.has(e)) ready = true;
    }
    if (ready && this.#timer !== null) {
      clearTimeout(this.#timer);
      this.#timer = null;
    }
    this.#arm(0);'''
assert src.count(old)==1;src=src.replace(old,new)
files={'index.mjs':src.encode(),'index.mjs.LEGAL.txt':(base/path.parent/'index.mjs.LEGAL.txt').read_bytes()}
desc={k:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for k,v in sorted(files.items())}
bundle=hashlib.sha256(json.dumps(desc,separators=(',',':')).encode()).hexdigest()
out=ROOT/'.build/shared-services/wake-hop-history-r1';assert not out.exists()
target=out/'assets/desktop/services/device-history'/bundle;target.mkdir(parents=True)
for k,v in files.items():(target/k).write_bytes(v)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(target.relative_to(out)/'index.mjs'),'files':desc}
(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'bundle':bundle,'entry':desc['index.mjs']}))
