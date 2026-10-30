#!/usr/bin/env python3
"""Test-only wrapper: patch bounded member waits into pinned live service candidate."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
source=(R/'assets/desktop/device-channel-session.mjs').read_text()
test=(R/'.build/shared-services/witness-refresh-live-test-r1/apps/replica-core/test/index.mjs').read_text()
assert hashlib.sha256(test.encode()).hexdigest()=='7dc1dd1a34988b1e5f4e305c351b876b3f28b4432aca1c6bad0f11f77124b538'
old='this.#roundWork(e, () => e.member.invoke(method, value, options), { reserve: false })'
new='this.#roundWork(e, () => e.member.invoke(method, value, options), { reserve: false, waitSignal: options.signal || this.#life.signal })'
assert test.count(old)==1;test=test.replace(old,new)
a=test.index('  async #roundWork(e, job, { reserve = true } = {}) {');b=test.index('  async #automaticWork(e, job) {',a)
c=source.index(' async #roundWork(e,job,{reserve=true,waitSignal=null}={}){');d=source.index(' async #automaticWork(e,job)',c)
method=source[c:d].replace('need(', 'requireThat(')
test=test[:a]+method+'\n'+test[b:]
raw=test.encode();out=R/'.build/shared-services/submission-wait-live-test-r2';f=out/'apps/replica-core/test/index.mjs';assert not out.exists();f.parent.mkdir(parents=True);f.write_bytes(raw);(out/'apps.json').write_text(json.dumps({'apps':[{'path':'assets/desktop/apps/replica-core/test/index.mjs','sha256':hashlib.sha256(raw).hexdigest()}]}));print(hashlib.sha256(raw).hexdigest())
