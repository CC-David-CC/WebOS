#!/usr/bin/env python3
"""Read-only invariants for the e7-derived main no-ZIP test candidate."""
import hashlib,json,pathlib,sys
if len(sys.argv)!=3:raise SystemExit('usage: e7-baseline nozip-candidate')
base,out=map(pathlib.Path,sys.argv[1:]);cache=json.loads((out/'assets/desktop/cache-manifest.json').read_bytes());expected='0366e10aa555117191757db8ad0dd91ccf0ee7a33ee252be17079696cf0ed3b8'
assert cache['id']==hashlib.sha256(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==expected
actual={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()};assert actual==set(cache['files'])|{'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
for name,record in cache['files'].items():
 b=(out/name).read_bytes();assert len(b)==record['bytes'] and hashlib.sha256(b).hexdigest()==record['sha256'],name
entries=json.loads((out/'assets/desktop/apps.json').read_bytes())['apps'];assert {x['id'] for x in entries}=={'files','text','calculator','terminal','help','codemirror'}
f=next(x for x in entries if x['id']=='files');assert hashlib.sha256(json.dumps(f['files'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==f['bundleSHA256'];new=(out/f['path']).read_text();old=(base/'assets/desktop/apps/files/bd33bb70885171501dec4cc5ac7cc2c0551304e88345235432e2a6e30bd5bd88/index.mjs').read_text();guard='    if (event.id === ArchiveFiles.id) {'
assert old.count(', ArchiveFiles, ExtractZip')==2 and old.count(guard)==1
expected_source=old.replace(', ArchiveFiles, ExtractZip','').replace(guard,'    if (event.id === ArchiveFiles.id || event.id === ExtractZip.id) return;\n'+guard,1);assert new==expected_source
assert (out/'assets/desktop/apps/files/bd33bb70885171501dec4cc5ac7cc2c0551304e88345235432e2a6e30bd5bd88/index.mjs').read_bytes()==old.encode()
for path in ('app.js','desktop-apps.js','assets/desktop/apps.mjs','assets/desktop/app-instance.mjs'):
 assert (base/path).read_bytes()==(out/path).read_bytes(),path
assert json.loads((out/'assets/desktop/offline-worker.js').read_text().splitlines()[1].removeprefix('const RELEASE=').removesuffix(';'))==cache
print('PASS exact e7-derived Files action omission, retained old URL, catalog/cache integrity')
