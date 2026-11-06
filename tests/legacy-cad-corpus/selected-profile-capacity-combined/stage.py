"""Stage code-only prerequisites into NEW private signed fixture directories.

Run on R730 after archiving the exact desktop source into --source. No account,
key, gateway state, or previous TMPDIR is read or copied.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--expected-source',required=True);p.add_argument('--expected-app',required=True);p.add_argument('--pins',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--prior-source',type=Path,required=True);p.add_argument('--prior-apps',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
pins=json.loads(a.pins.read_text());assert pins['source']==a.expected_source;assert pins['files']['index.bundle.js']==a.expected_app
for name,want in pins['files'].items():assert sha(a.runtime/'dist/static'/name)==want,name
builder=a.source/'active-system/tools/app-builder/node_modules';assert not builder.exists();shutil.copytree(a.prior_source/'active-system/tools/app-builder/node_modules',builder,symlinks=True)
target=a.source/'apps/system/jsketcher/node_modules/jsketcher-build';assert not target.exists();shutil.copytree(a.runtime/'dist',target,ignore=shutil.ignore_patterns('*.map'))
receipt=a.prior_source/'apps/system/jsketcher/node_modules/jsketcher-build/manifold-build-receipt.json';native=json.loads(receipt.read_text())
for key,name in [('jsSha256','manifold.js'),('wasmSha256','manifold.wasm')]:assert sha(a.runtime/'node_modules/.cache/codi-manifold'/name)==native[key]
shutil.copy2(receipt,target/receipt.name)
manifest=a.source/'apps/system/jsketcher/app.json';data=json.loads(manifest.read_text());assets=[x for x in data['assets'] if '/static/' not in x]
assets.extend('node_modules/jsketcher-build/'+str(f.relative_to(target)) for f in sorted((target/'static').rglob('*')) if f.is_file())
data['assets']=sorted(set(assets));manifest.write_text(json.dumps(data,indent=2)+'\n')
assert not a.output.exists();a.output.mkdir(parents=True)
(a.output/'runtime-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Staged exact reviewed runtime; generated asset inventory; copied code only.')
