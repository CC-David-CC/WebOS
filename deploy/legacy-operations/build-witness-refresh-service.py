#!/usr/bin/env python3
"""Patch only single-submission witness handling in the pinned live service."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'.build/releases/official-fast-profile26-r1'
reg=json.loads((base/'assets/desktop/shared-services.json').read_text())
entry=next(x for x in reg['services'] if x['name']=='device-history')
path=Path(entry['path']);src=(base/path).read_text()
assert hashlib.sha256(src.encode()).hexdigest()=='4be9ca9cd5df877822657149645195a90ed782971783457b187fa9273429cea8'
for variable,indent in [('op2','        '),('op','    ')]:
 old=indent+'await this.#round.submit(value.record, { signal });'
 new=indent+f'const record = await this.#archive.operationReceipt({variable}.id, {{ signal }}) ? value.record : {{ ...value.record, absence: await this.#archive.witness({variable}.id, {{ signal }}) }};\n'+indent+'await this.#round.submit(record, { signal });'
 assert src.count(old)==1,(variable,src.count(old));src=src.replace(old,new)
files={'index.mjs':src.encode(),'index.mjs.LEGAL.txt':(base/path.parent/'index.mjs.LEGAL.txt').read_bytes()}
desc={k:{'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for k,v in sorted(files.items())}
bundle=hashlib.sha256(json.dumps(desc,separators=(',',':')).encode()).hexdigest()
out=ROOT/'.build/shared-services/witness-refresh-r1';assert not out.exists()
target=out/'assets/desktop/services/device-history'/bundle;target.mkdir(parents=True)
for k,v in files.items():(target/k).write_bytes(v)
manifest={'version':'codi-shared-service/1','name':'device-history','sourceAlias':entry['sourceAlias'],'path':str(target.relative_to(out)/'index.mjs'),'files':desc}
(out/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Test-only exports expose the exact patched service internals to the fixture.
exports=['DeviceChannelSession','DeviceChannelArchive','DeviceChannelDirectory','PersistentDeviceStorage','DeviceChannelKeys','DeviceReplica','DeviceReplicaRound','DeviceMemberChannel','DeviceMemberIntroductions','verifyDeviceMemberContact','DeviceReplicaExchange','createDeviceChannelPolicy','readDeviceChannelPolicy','prepareDeviceChannelBlock','deviceChannelAccess']
raw=(src+'\nexport { '+', '.join(exports)+' };\n').encode();test=ROOT/'.build/shared-services/witness-refresh-live-test-r1';assert not test.exists();testpath=test/'apps/replica-core/test/index.mjs';testpath.parent.mkdir(parents=True);testpath.write_bytes(raw);(test/'apps.json').write_text(json.dumps({'apps':[{'path':'assets/desktop/'+str(testpath.relative_to(test)),'sha256':hashlib.sha256(raw).hexdigest()}]}))
print(json.dumps({'bundle':bundle,'entry':desc['index.mjs'],'testSHA256':hashlib.sha256(raw).hexdigest()}))
