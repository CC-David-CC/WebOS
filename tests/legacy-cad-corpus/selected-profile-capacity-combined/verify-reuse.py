"""Acceptance-driver reuse guard; only fixture pins/import/source labels change."""
from pathlib import Path
import hashlib
here=Path(__file__).resolve().parent
base=here.parent
old=(base/'selected-profile-depth/signed.test.mjs').read_text()
wanted=old.replace("from '../selected-profile/helpers.mjs'","from './helpers.mjs'").replace("from './lifecycle.mjs'","from '../selected-profile-depth/lifecycle.mjs'").replace("assert.equal(new URL(process.env.CODI_TEST_URL).port,'20407');assert.equal(process.env.CODI_SOURCE,'15b9607a7880eeb7cf98f9de40a3563d19a3c5a6');", "assert.equal(new URL(process.env.CODI_TEST_URL).port,process.env.CODI_TEST_PORT);assert.equal(process.env.CODI_SOURCE,process.env.CODI_EXPECTED_SOURCE);assert.match(process.env.CODI_DESKTOP_SOURCE||'',/^[a-f0-9]{40}$/);").replace("desktopSource:'19396b4bee0fb99dfc330ce2b465cfb1175c2913'","desktopSource:process.env.CODI_DESKTOP_SOURCE")
assert (here/'signed.test.mjs').read_text()==wanted
for name in ['bracket.test.mjs','typed-bracket.test.mjs','enclosure.test.mjs']:
 old=(base/'selected-profile/composition'/name).read_text()
 wanted=old.replace('// Selected-profile r4 integration regression: only import/pin/source labels adapted.','// Selected-profile capacity combined regression: only pin/source labels adapted.').replace("desktopSource:'478970d72'","desktopSource:process.env.CODI_DESKTOP_SOURCE")
 assert (here/'composition'/name).read_text()==wanted,name
old=(base/'selected-profile/helpers.mjs').read_text()
wanted=old.replace("['selected-profile-worker.js','0f3240cdde9b5faced831ace71ee5ffcfb6fe159dacba5b7265e5a09b0ca9853']", "['selected-profile-worker.js',process.env.CODI_EXPECTED_SELECTED_WORKER_SHA]").replace("for(const name of['APP','SKETCH','PROJECT','SEMANTIC'])", "assert.match(process.env.CODI_EXPECTED_SELECTED_WORKER_SHA||'',/^[a-f0-9]{64}$/);\n for(const name of['APP','SKETCH','PROJECT','SEMANTIC'])")
assert (here/'helpers.mjs').read_text()==wanted
assert (here/'composition/check-v2-3mf.py').read_bytes()==(base/'selected-profile/composition/check-v2-3mf.py').read_bytes()
print('PASS unchanged depth/bracket/typed/enclosure assertions and independent3MF oracle; pin/import/source-label adaptations only')
