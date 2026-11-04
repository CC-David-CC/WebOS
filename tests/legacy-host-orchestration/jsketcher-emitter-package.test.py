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
assert receipt['forkCommit'] == '794c14a36d706a86ac3d834a536f97c34cc99e2f'
assert receipt['occtSelection'] == 'source-research'
assert hashlib.sha256((runtime / 'lib-assets/jsketcher-occ-engine/occt.wasm').read_bytes()).hexdigest() == 'a2b2f7daf6a4eb98b975f8aec136f6cbaf2720295ea32e71edb13ff4c5ceaecb'
worker = receipt['projectValidatorWorker']
assert worker['path'].startswith('static/project-validator.') and worker['path'].endswith('.js')
assert hashlib.sha256((runtime / worker['path']).read_bytes()).hexdigest() == worker['sha256']
code = (runtime / 'static/index.bundle.js').read_text(encoding='utf-8')
assert Path(worker['path']).name in code
assert 'node_modules/component-emitter/index.js' in code
assert 'node_modules/emitter-component/index.js' not in code
assert 'node_modules/stream/index.js' in code and 'node_modules/sax/lib/sax.js' in code
assert hashlib.sha256((runtime / 'MDI-SVG-LICENSE.txt').read_bytes()).hexdigest() == '453b87202c008eac411015ddde3320dd93502e198d4d7e8a579eac8421ab4e81'
assert (runtime / 'SOURCE-PROVENANCE.txt').is_file()
with zipfile.ZipFile(runtime / 'runtime-source-candidates.zip') as sources:
    for name in ['stream/index.js', 'stream/README.md', 'timers/index.js',
                 'react-color/node_modules/@icons/material/CheckIcon.js',
                 'react-color/node_modules/@icons/material/svg/check.svg']:
        assert name in sources.namelist()
with zipfile.ZipFile(runtime / 'dependency-notices.zip') as archive:
    entries = json.loads(archive.read('packages.json'))
    replacement = next(entry for entry in entries if entry['path'] == 'component-emitter')
    old = next(entry for entry in entries if entry['path'] == 'emitter-component')
    assert replacement['version'] == '1.1.3' and replacement['webpackCandidate'] is True
    assert old['version'] == '1.1.1' and old['webpackCandidate'] is False
    assert hashlib.sha256(archive.read('licenses/component-emitter/LICENSE')).hexdigest() == '0f0b408b8b871d983e767528c6dc51e0ad7efaa022890c449fe2b2e1ee24dbb7'
print('PASS exact fork/OCCT input, production emitter resolution, and replacement license inventory')
