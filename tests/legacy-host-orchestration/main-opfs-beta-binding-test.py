#!/usr/bin/env python3
"""Actual generator + selector snapshots; no host locks or service checks."""
import copy,hashlib,importlib.util,sys,types
from pathlib import Path
p=Path(sys.argv[1])/'ops';sys.path.insert(0,str(p));sys.dont_write_bytecode=True
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
for n in ('microduck_hosting','hardware_hosting','cardboard_hosting'):load(n,p/(n+'.py'))
a=load('common',p/'common_live.py');b=load('v2',p/'common.py');c=load('asset_common',p/'asset_common.py');snap=load('beta_files_snapshots',p/'beta_files_snapshots.py');s=load('beta_successor',p/'beta_successor.py');r=load('asset_router',p/'asset_router.py');f=load('asset_floor',p/'asset_floor.py');sel=load('asset_select',p/'asset_select.py')
def bound(n,m):return types.SimpleNamespace(source=(p/(n+'.py')).read_bytes(),module=m)
args=dict(snap=snap,successor=s,oldgen=bound('common_live',a),v2gen=bound('common',b),newgen=bound('asset_common',c),manifest=(p/'sites_live.toml').read_bytes(),old_manifest=(p/'beta_files_candidate.json').read_bytes(),new_manifest=(p/'asset_manifest.json').read_bytes(),table=(p.parent/'OPFS-ROUTE-TABLE.json').read_bytes())
x=r.snapshots(**args,selector=r.F2);old=r.snapshots(**args,selector=r.NEXT)
for n in ('baseline','gate','candidate'):
 data=copy.deepcopy(x[n+'Data']);next(site for site in data['sites'] if site.get('domain')=='ksu.codes')['codi_simplified']=r.NEXT
 assert data==old[n+'Data'],n+' changed unrelated manifest data'
orig={'version':1,'baseline':f.ORIGINAL_BASE,'candidate':f.OLD};floor={'version':1,'baseline':f.OLD,'candidate':f.NEW};snapshots={n:x[n] for n in ('baseline','gate','candidate')}
for n in ('gate','candidate'):
 assert sel.select(snapshots=snapshots,current=x[n],original_floor=orig,asset_floor=floor,asset_journal=None,nested_journal=None,other_pending=False)==n
 for other in ('baseline','gate','candidate'):
  try:sel.select(snapshots=snapshots,current=old[other],original_floor=orig,asset_floor=floor,asset_journal=None,nested_journal=None,other_pending=False)
  except ValueError:pass
  else:raise AssertionError('cross-family snapshot accepted')
mixed=dict(x['candidate']);mixed['manifest']=old['candidate']['manifest']
try:sel.select(snapshots=snapshots,current=mixed,original_floor=orig,asset_floor=floor,asset_journal=None,nested_journal=None,other_pending=False)
except ValueError:pass
else:raise AssertionError('mixed route accepted')
print('PASS f2 exact render hashes, main-selector-only difference, floor gate/candidate selection and cross-family/mixed refusal')
