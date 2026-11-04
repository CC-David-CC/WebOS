#!/usr/bin/env python3
"""Derive narrowly pinned fb27→830c-guard installer; no host installation."""
import hashlib,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parent;out=Path(sys.argv[1]);sha=lambda b:hashlib.sha256(b).hexdigest()
def read(name,pin):
 b=(root/name).read_bytes()
 if sha(b)!=pin:raise ValueError('installation source pin changed: '+name)
 return b.decode()
def one(s,a,b):
 if s.count(a)!=1:raise ValueError('installation source anchor changed')
 return s.replace(a,b)
old='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e';fb='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783';guard='ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9';bc='bc9f939a9db8849fb7d580e5a71d5c52728b127b74c3bca1ee811b41fdd1f754';actor='142509906abcce599465417dcfd0430e80ab647f843b5aa42c9922d7fb152f63'
pre=read('main-successor-preflight.py','9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83');pre=one(pre,bc,actor);pre=one(pre,'len(records)!=28','len(records)!=35');pre=pre.encode()
ins=read('main-install.py','c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96');ins=one(ins,old,fb);ins=one(ins,"NEW='"+fb+"'","NEW='"+guard+"'");ins=one(ins,bc,actor);ins=ins.encode()
launch=read('main-install-launch.py','5c5442d6bb75e00b4520e4b756e6ca4f5bec1f24e19195f834bcadbb0e6f3b3c')
launch=one(launch,'/srv/codi-connected/operators/main-qualified-e7e8-v1','/srv/codi-connected/operators/beta-files-830c-installer-v1');launch=one(launch,'/srv/codi-connected/operators/main-qualified-e7e8-input/successor','/srv/codi-connected/operators/beta-files-830c-input/actor');launch=one(launch,'/srv/codi-connected/operators/beta-recovery-e7-v1','/srv/codi-connected/operators/beta-files-830c-v1')
launch=one(launch,'c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96',sha(ins));launch=one(launch,'9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83',sha(pre));launch=one(launch,"'main-launcher.py')","'main-launcher.py','asset-launch.py')");launch=launch.encode()
# The guard is supplied separately, from the exact independent guard builder.
guard_bytes=Path(sys.argv[2]).read_bytes()
if sha(guard_bytes)!=guard:raise ValueError('asset guard source pin changed')
entries={'main-install-launch.py':launch,'main-install.py':ins,'main-successor-preflight.py':pre,'webctl-main-guard.py':guard_bytes}
out.mkdir(mode=0o700)
for name,data in sorted(entries.items()):(out/name).write_bytes(data)
record={n:sha(v) for n,v in sorted(entries.items())};(out/'manifest.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print('install',sha(launch),'primitive',sha(ins),'preflight',sha(pre),'inventory',sha((out/'manifest.json').read_bytes()))
