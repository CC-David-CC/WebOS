#!/usr/bin/env python3
"""Patch the frozen native10 baseline with only reviewed optional-account files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from origin_service.release import verify, record
BASELINE='ced620b043b7054c17e4d943a987f8b3f959c21f63961894091b6088cbbd9058'
PUBLIC=['app.js','style.css','terminal.js','networking.js','assets/terminal-initramfs.cpio.gz']

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    baseline=ROOT/'.build/releases/connected-cookie-20261023-r1'
    assert verify(baseline)['manifestSHA256']==BASELINE
    shutil.copytree(baseline,args.output)
    for name in [*PUBLIC,'origin_service/lifecycle.py']:
        shutil.copyfile(ROOT/name,args.output/name)
    public=json.loads((args.output/'release.json').read_text())
    for name in PUBLIC:public['files'][name]=record(args.output/name)
    (args.output/'release.json').write_text(json.dumps(public,indent=2)+'\n')
    metadata=json.loads((args.output/'connected-release.json').read_text())
    for name in [*PUBLIC,'origin_service/lifecycle.py','release.json']:metadata['files'][name]=record(args.output/name)
    (args.output/'connected-release.json').write_text(json.dumps(metadata,indent=2)+'\n')
    before=json.loads((baseline/'connected-release.json').read_text())
    changed=[name for name in metadata['files'] if metadata['files'][name]!=before['files'].get(name)]
    assert set(changed)=={'app.js','style.css','terminal.js','networking.js','assets/terminal-initramfs.cpio.gz','origin_service/lifecycle.py','release.json'}
    print(json.dumps({**verify(args.output),'baselineManifestSHA256':BASELINE,'changedFiles':changed},indent=2))
