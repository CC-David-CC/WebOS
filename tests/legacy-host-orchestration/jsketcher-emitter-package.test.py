"""Check an explicitly prepared local jSketcher runtime; no live service used."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

if len(sys.argv) != 2:
    raise SystemExit('usage: python tests/jsketcher-emitter-package.test.py /path/to/jsketcher-build')
runtime = Path(sys.argv[1])
receipt = json.loads((runtime / 'BUILD-RECEIPT.json').read_text())
assert receipt['forkCommit'] == '518a4666cfc5c94acb153f0cd315a2ca1625eb2f'
assert receipt['occtSelection'] == 'source-research'
assert hashlib.sha256((runtime / 'lib-assets/jsketcher-occ-engine/occt.wasm').read_bytes()).hexdigest() == 'a2b2f7daf6a4eb98b975f8aec136f6cbaf2720295ea32e71edb13ff4c5ceaecb'
code = (runtime / 'static/index.bundle.js').read_text(encoding='utf-8')
assert 'node_modules/component-emitter/index.js' in code
assert 'node_modules/emitter-component/index.js' not in code
assert 'node_modules/stream/index.js' in code and 'node_modules/sax/lib/sax.js' in code
with zipfile.ZipFile(runtime / 'dependency-notices.zip') as archive:
    entries = json.loads(archive.read('packages.json'))
    replacement = next(entry for entry in entries if entry['path'] == 'component-emitter')
    old = next(entry for entry in entries if entry['path'] == 'emitter-component')
    assert replacement['version'] == '1.1.3' and replacement['webpackCandidate'] is True
    assert old['version'] == '1.1.1' and old['webpackCandidate'] is False
    assert hashlib.sha256(archive.read('licenses/component-emitter/LICENSE')).hexdigest() == '0f0b408b8b871d983e767528c6dc51e0ad7efaa022890c449fe2b2e1ee24dbb7'
print('PASS exact fork/OCCT input, production emitter resolution, and replacement license inventory')
