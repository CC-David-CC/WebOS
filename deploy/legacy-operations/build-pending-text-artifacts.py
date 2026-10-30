#!/usr/bin/env python3
"""Expose already-verified own pending text in pinned live chat and service."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1];B=R/'.build/releases/signed-chess-profile26-r1';O=R/'.build/pending-text-artifacts/r1';assert not O.exists();O.mkdir(parents=True)
def sha(x):return hashlib.sha256(x).hexdigest()
r=json.loads((B/'assets/desktop/shared-services.json').read_text());e=next(x for x in r['services'] if x['name']=='device-history');s=(B/e['path']).read_text();assert sha(s.encode())=='d431babd59d0fb8b9c193e12b7f40cb8b05ddaded77a21eb607e2616988e4aa3'
old='result.push({ id: p.id, wire: row.wire, wireHash: row.wireHash, status: "pending-on-device" });';new='result.push({ id: p.id, wire: row.wire, wireHash: row.wireHash, status: "pending-on-device", kind: p.kind, data: p.data });';assert s.count(old)==1;s=s.replace(old,new);(O/'service.mjs').write_text(s)
g=json.loads((B/'assets/desktop/network-release.json').read_text());host=(B/g['coreDirectory']/'desktop-apps.js').read_text();loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',host)[0];cat=re.search(r'apps-v2-[a-f0-9]{64}\.json',(B/loader).read_text())[0];app=next(x for x in json.loads((B/'assets/desktop'/cat).read_text())['apps'] if x['id']=='chat');u=(B/app['path']).read_text();assert sha(u.encode())=='dd39b1a22c81c706ded159b09d8f837a28075de11f53a442e7f48a87e69b1b1d'
old='          if (snapshot.pending.length) transcript.append(make("div", "", "[" + snapshot.pending.length + " pending on this device; acceptance/delivery not confirmed here]"));';new='''          const accepted = new Set(snapshot.state.messages.map((m) => m.id));
          for (const item of snapshot.pending) {
            if (item.kind === "chat" && !accepted.has(item.id)) {
              const pendingMessage = make("div", "", item.data.text + " — Pending on this device");
              pendingMessage.dataset.pendingMessage = item.id;
              transcript.append(pendingMessage);
            }
          }
'''+old;assert u.count(old)==1;u=u.replace(old,new);(O/'chat.mjs').write_text(u)
print(json.dumps({'serviceSHA256':sha(s.encode()),'chatSHA256':sha(u.encode())}))
