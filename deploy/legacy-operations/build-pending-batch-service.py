#!/usr/bin/env python3
"""Patch pending inbox, protocol, fanout and guards into the exact live service."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];base=R/'.build/releases/peer-parallel-profile26-r1';reg=json.loads((base/'assets/desktop/shared-services.json').read_bytes());entry=next(v for v in reg['services'] if v['name']=='device-history');source=(base/entry['path']).read_text();digest=lambda b:hashlib.sha256(b).hexdigest();assert digest(source.encode())==entry['files']['index.mjs']['sha256']
def replace_class(name,path,aliases):
 global source
 marker='var '+name+' = class {';start=source.index(marker);end=source.index('\n};',start)+3;code=(R/path).read_text();begin=code.index('export class '+name+'{');new=code[begin:].replace('export class '+name+'{',marker,1).rstrip()+';'
 for a,b in aliases.items():new=re.sub(a,b,new)
 source=source[:start]+new+source[end:]
replace_class('PendingPeerInbox','assets/desktop/pending-peer-inbox.mjs',{r'\bneed\(':'requireThat(',r'\bid\(':'operationId(',r'\bexact\(':'exact10(',r'\bDB\b':'DB3'})
replace_class('ExperimentalPendingPeer','network/experimental-pending-peer.mjs',{r'\bneed\(':'requireThat(',r'\bid\(':'operationId(',r'\bexact\(':'exact11('})
replace_class('ExperimentalPendingGossip','network/experimental-pending-gossip.mjs',{r'\bneed\(':'requireThat('})
def change(a,b,count=1):
 global source
 assert source.count(a)==count,(a[:120],source.count(a));source=source.replace(a,b)
change('''let pendingAuthor = null;
    if (method === "pending-share") {
      requireThat(this.#profile === "member" && value && typeof value.wire === "string", "Invalid pending share");
      pendingAuthor = (await readDeviceChannelProposal(value.wire, this.#channel(channel, genesisHash).policy)).actor;
    }''','''let pendingAuthors = null;
    if (method === "pending-share") {
      requireThat(this.#profile === "member" && value, "Invalid pending share");
      const wires = typeof value.wire === "string" ? [value.wire] : value.wires;
      requireThat(Array.isArray(wires) && wires.length >= 1 && wires.length <= 16 && wires.every(w => typeof w === "string") && enc.encode(JSON.stringify(wires)).length <= 65536, "Invalid pending share batch");
      const actors = []; for (const wire of wires) actors.push((await readDeviceChannelProposal(wire, this.#channel(channel, genesisHash).policy)).actor);
      pendingAuthors = [...new Set(actors)].sort();
    }''')
change('const guard = pendingAuthor ? async () => {','const guard = pendingAuthors ? async () => {')
change('await this.#authorize(fresh.channel, pendingAuthor, "submit", owned);','for (const author of pendingAuthors) await this.#authorize(fresh.channel, author, "submit", owned);')
change('''if (pendingAuthor && !Object.hasOwn(input.ref, "wire")) {
        const entry = this.#values.get(this.#valueKey(channel, genesisHash, input.ref.root));
        requireThat(entry && (!entry.pendingAuthor || entry.pendingAuthor === pendingAuthor), "Pending value author mismatch");
        entry.pendingAuthor = pendingAuthor;
      }''','''if (pendingAuthors && !Object.hasOwn(input.ref, "wire")) {
        const entry = this.#values.get(this.#valueKey(channel, genesisHash, input.ref.root));
        requireThat(entry && (!entry.pendingAuthors || JSON.stringify(entry.pendingAuthors) === JSON.stringify(pendingAuthors)), "Pending value authors mismatch");
        entry.pendingAuthors = pendingAuthors;
      }''')
change('if (entry.pendingAuthor) await this.#authorize(channel, entry.pendingAuthor, "submit", signal);','for (const author of entry.pendingAuthors || []) await this.#authorize(channel, author, "submit", signal);',2)
files={n:((base/Path(entry['path']).parent/n).read_bytes() if n!='index.mjs' else source.encode()) for n in entry['files']};desc={n:{'sha256':digest(b),'bytes':len(b)} for n,b in sorted(files.items())};bundle=digest(json.dumps(desc,separators=(',',':')).encode());out=R/'.build/shared-services/peer-batch-exact-r1';assert not out.exists();dest=out/'assets/desktop/services/device-history'/bundle;dest.mkdir(parents=True)
for n,data in files.items():p=dest/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(dest.relative_to(out)/'index.mjs'),'files':desc};(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'service':manifest['path'],'sha256':desc['index.mjs']['sha256']}))
