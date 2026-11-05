#!/usr/bin/env python3
"""Prepare an isolated local rectangle host fixture. This is not a signed service."""
import argparse
from pathlib import Path
import shutil
p=argparse.ArgumentParser()
p.add_argument('--output',type=Path,required=True)
p.add_argument('--cad-dist',type=Path,required=True)
a=p.parse_args()
root=Path(__file__).resolve().parents[1]
dist=a.cad_dist.resolve(strict=True)
if not (dist/'index-webos.html').is_file() or not (dist/'static/webosTest.bundle.js').is_file():
    p.error('CAD dist and its test helper must already be built')
a.output.mkdir(parents=True,exist_ok=False)
out=a.output.resolve()
harness=(root/'tests/fixtures/jsketcher-rectangle-host-harness.html').read_text()
opening='<script type="module">'
if harness.count(opening)!=1 or harness.count('</script>')!=1:
    raise ValueError('Unexpected host harness script inventory')
before,tail=harness.split(opening,1)
script,after=tail.split('</script>',1)
# Serve the fixture module externally so self-only script CSP also covers it.
(out/'fixture-host.mjs').write_text(script)
(out/'index.html').write_text(before+'<script type="module" src="./fixture-host.mjs"></script>'+after)
for name in ['index.mjs','style.css','inspect-state.mjs','file-read.mjs','sketch-commands.mjs','rectangle-commands.mjs','feature-commands.mjs','material-commands.mjs','document-commands.mjs','source-dialog.mjs']:
    text=(root/'apps/system/jsketcher'/name).read_text()
    if name=='index.mjs':
        if not text.startswith("import './style.css';\n"): raise ValueError('Unexpected CSS import')
        text=text.split('\n',1)[1] # Browser fixture links stylesheet from HTML.
    (out/name).write_text(text)
shutil.copy2(root/'active-system/assets/desktop/command-registry.mjs',out/'command-registry.mjs')
shutil.copy2(root/'active-system/assets/desktop/document-operations.mjs',out/'document-operations.mjs')
(out/'node_modules').mkdir()
(out/'node_modules/jsketcher-build').symlink_to(dist,target_is_directory=True)
print(out)
