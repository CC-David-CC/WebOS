#!/usr/bin/env python3
"""Build exact public-code-only 830c actor bundle; never installs it."""
import hashlib,json,os,stat,sys
from pathlib import Path
here=Path(__file__).resolve().parent;base=Path(sys.argv[1]);new=Path(sys.argv[2]);generator=Path(sys.argv[3]);inventory=Path(sys.argv[4]);out=Path(sys.argv[5]);sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(base/'inventory.json').read_bytes()
if sha(raw)!='753812dfc1848d344e36e5bab53ae455c1cdb262d8b538040e0245f6a99637cc':raise ValueError('3ad actor inventory pin changed')
pins=json.loads(raw);found=set();entries={}
for root,dirs,files in os.walk(base,followlinks=False):
 for n in dirs+files:
  p=Path(root)/n;v=p.lstat()
  if not (stat.S_ISDIR(v.st_mode) or stat.S_ISREG(v.st_mode)):raise ValueError('unsafe source entry')
 for n in files:
  p=Path(root)/n;key=p.relative_to(base).as_posix()
  if key=='inventory.json':continue
  data=p.read_bytes()
  if pins.get(key)!=sha(data):raise ValueError('3ad actor source changed: '+key)
  entries[key]=data;found.add(key)
if found!=set(pins):raise ValueError('3ad actor inventory incomplete')
raw=(new/'manifest.json').read_bytes()
if sha(raw)!='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0':raise ValueError('asset manifest pin changed')
# Full target graph must be verified by the pinned generator builder as well.
import importlib.util
spec=importlib.util.spec_from_file_location('asset_builder',here/'build-generator.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
builder.inventory(new,builder.NEW,171)
gen=generator.read_bytes();inv=inventory.read_bytes()
if sha(gen)!='e06fc8aa018ff048138fb2585ddb34ab9c6f1b061fb0022b06b14dca7df55928' or sha(inv)!='49e99fe32497149ee6f89d840f36afc152e4176414dd6978a0f72457b24d37d3':raise ValueError('generated source pin changed')
entries['ops/asset_common.py']=gen;entries['ops/asset_inventory.py']=inv;entries['ops/asset_manifest.json']=raw
for name in ('asset-floor.py','asset-router.py','asset-select.py'):entries['ops/'+name.replace('-','_')]=(here/name).read_bytes()
modules={Path(k).stem:sha(v) for k,v in entries.items() if k.startswith('ops/') and k.endswith('.py')}
template=(here/'asset-launch.py.in').read_text()
if template.count('__PINS__')!=1:raise ValueError('actor template changed')
actor=template.replace('__PINS__',repr(dict(sorted(modules.items())))).encode();compile(actor,'asset-launch.py','exec');entries['ops/asset-launch.py']=actor
out.mkdir(mode=0o700)
for name,data in sorted(entries.items()):p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
record={n:sha(b) for n,b in sorted(entries.items())};(out/'inventory.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
print('actor',sha(actor),'inventory',sha((out/'inventory.json').read_bytes()),'files',len(record))
