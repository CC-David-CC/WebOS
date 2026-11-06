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
# Added authenticated asset checks strengthen the unchanged native/runtime oracle.
needle="  ['a81af0b78dd585124f3f.wasm','a81af0b78dd585124f3f2d05d09b4a387b276bd1f655f0234002a6ab4646a637']"
extra="  ['a81af0b78dd585124f3f.wasm','a81af0b78dd585124f3f2d05d09b4a387b276bd1f655f0234002a6ab4646a637'],\n  ['oci-verified-worker.js','6189a58b58667c4bca68c67e1593f8656d04ad0875162b301659392a82fd96e4'],\n  ['occ-portable.js','a84b31900e58e61a1d7e3f8d04978408455764ad149923359e7fba19d3d07884'],\n  ['manifold-verified-worker.js','35876bd7cd773b5eb243fde935599afb670314c192ba77ec11036dcb12aa79e4'],\n  ['07d763a05f35cd257501.wasm','07d763a05f35cd257501d339d9087df63c65bcaeb51a4f4f80832e333892e12e'],\n  ['7bb5f8ee10fcafdab787.wasm','7bb5f8ee10fcafdab78799b1e5dd2cdc7c282ea0bf8e7939c43f3ad34b823e3d']"
wanted=wanted.replace(needle,extra)
assert (here/'helpers.mjs').read_text()==wanted
assert (here/'composition/check-v2-3mf.py').read_bytes()==(base/'selected-profile/composition/check-v2-3mf.py').read_bytes()
print('PASS unchanged depth/bracket/typed/enclosure assertions and independent3MF oracle; pin/import/source-label adaptations only')
