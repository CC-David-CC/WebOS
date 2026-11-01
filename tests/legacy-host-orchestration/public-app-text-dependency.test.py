#!/usr/bin/env python3
"""A Text-only selection must include the host-loaded CodeMirror bundle."""
import json
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix='codi-text-selection-') as tmp:
 output=Path(tmp)/'apps'
 subprocess.run(['python3',str(root/'active-system/scripts/build-public-apps.py'),
                 '--apps','text','--output',str(output)],cwd=root,check=True)
 catalog=json.loads((output/'apps.json').read_text())
 assert {entry['id'] for entry in catalog['apps']}=={'text','codemirror'}
 for entry in catalog['apps']:
  assert (output/entry['path'].removeprefix('assets/desktop/')).is_file()
print('PASS Text-only build includes the shared CodeMirror tool')
