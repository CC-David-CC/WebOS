#!/usr/bin/env python3
"""Apply reviewed official rediscovery backoff to the pinned current service."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'.build/releases/official-directory-ui-profile26-r1';reg=json.loads((base/'assets/desktop/shared-services.json').read_text());entry=next(x for x in reg['services'] if x['name']=='device-history');path=Path(entry['path']);src=(base/path).read_text();assert hashlib.sha256(src.encode()).hexdigest()=='1c88d1d8f140c6ccf4f8d0d598aa5c45adcd007793ca1b9efbf0b8609ff013e5'
old='''          e.officialLookupFailures = 0;
          e.officialLookupTimer = setTimeout(() => {
            e.officialLookupTimer = null;
            this.#refreshOfficial(e);
          }, 6e4);'''
new='''          e.officialLookupFailures = 0;
          e.officialLookupMisses = Math.min(5, (e.officialLookupMisses || 0) + 1);
          const delay = e.actor === e.config.channel && e.trafficProfile !== "limited" ? Math.min(6e4, 5e3 * 2 ** (e.officialLookupMisses - 1)) : 6e4;
          e.officialLookupTimer = setTimeout(() => {
            e.officialLookupTimer = null;
            this.#refreshOfficial(e);
          }, delay);'''
assert src.count(old)==1;src=src.replace(old,new)
files={'index.mjs':src.encode(),'index.mjs.LEGAL.txt':(base/path.parent/'index.mjs.LEGAL.txt').read_bytes()};desc={k:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for k,v in sorted(files.items())};bundle=hashlib.sha256(json.dumps(desc,separators=(',',':')).encode()).hexdigest();out=ROOT/'.build/shared-services/official-fast-lookup-r1';assert not out.exists();target=out/'assets/desktop/services/device-history'/bundle;target.mkdir(parents=True)
for k,v in files.items():(target/k).write_bytes(v)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(target.relative_to(out)/'index.mjs'),'files':desc};(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'bundle':bundle,'entry':desc['index.mjs']}))
