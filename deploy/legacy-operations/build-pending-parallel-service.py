#!/usr/bin/env python3
"""Replace only the pending fanout class in the active pinned bundle."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];base=R/'.build/releases/peer-pagination-profile26-r1';reg=json.loads((base/'assets/desktop/shared-services.json').read_bytes());entry=next(v for v in reg['services'] if v['name']=='device-history');source=(base/entry['path']).read_text();digest=lambda b:hashlib.sha256(b).hexdigest();assert digest(source.encode())==entry['files']['index.mjs']['sha256']
start=source.index('var ExperimentalPendingGossip = class {');end=source.index('\n};',start)+3
code=(R/'network/experimental-pending-gossip.mjs').read_text();a=code.index('export class ExperimentalPendingGossip{');new=code[a:].replace('export class ExperimentalPendingGossip{','var ExperimentalPendingGossip = class {',1).replace('need(','requireThat(').rstrip()+';';patched=source[:start]+new+source[end:]
files={n:((base/Path(entry['path']).parent/n).read_bytes() if n!='index.mjs' else patched.encode()) for n in entry['files']};desc={n:{'sha256':digest(b),'bytes':len(b)} for n,b in sorted(files.items())};bundle=digest(json.dumps(desc,separators=(',',':')).encode());out=R/'.build/shared-services/peer-parallel-r1';assert not out.exists();dest=out/'assets/desktop/services/device-history'/bundle;dest.mkdir(parents=True)
for n,data in files.items():p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(dest.relative_to(out)/'index.mjs'),'files':desc};(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'service':manifest['path'],'sha256':desc['index.mjs']['sha256']}))
