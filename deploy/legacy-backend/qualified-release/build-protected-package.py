#!/usr/bin/env python3
"""Build exact public-code-only review package; does not install on a host."""
import hashlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent;enabled=Path(sys.argv[1]);out=Path(sys.argv[2])
pins={'main-launcher.py':'6469eb631aec6e9d37496dd1547a04dbbda9ea112e280b695c8ea426368f8642','main-install-launch.py':'5c5442d6bb75e00b4520e4b756e6ca4f5bec1f24e19195f834bcadbb0e6f3b3c','main-install.py':'c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96','main-successor-preflight.py':'9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83','webctl-main-guard.py':'fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783','forward-transaction.py':'538d7e7438f61ab39f0449ab1e44f9af3df4db824cb0bca026fb8eb352cf8508','render-inventory.py':'e4f139b6956b0315b2728d82c1036aaaccf2e2d9313bd49f6fe8229a887fd3a8'}
inputs={}
for name,want in pins.items():
 raw=((enabled/name) if name=='main-launcher.py' else (here/name)).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=want:raise ValueError('Source pin mismatch: '+name)
 inputs[name]=raw
out.mkdir(mode=0o700)
for name,raw in inputs.items():(out/name).write_bytes(raw)
manifest=json.dumps(pins,sort_keys=True,indent=2)+'\n';(out/'manifest.json').write_text(manifest)
print('package-manifest',hashlib.sha256(manifest.encode()).hexdigest(),'files',len(inputs))
