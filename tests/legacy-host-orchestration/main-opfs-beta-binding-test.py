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
host=load('beta_launcher',p/'beta_launcher.py');host.protected=lambda p:None;host.unit_state=lambda n:{'ActiveState':'active','MainPID':'123','NeedDaemonReload':'no'};host.get=lambda *a:(200,b'{"identity":{"issuer":"https://ksu.codes"}}')
oldpair=('6d72467c7dfabcdc65bc1216a31cf67bc6156b1d08f7a6c5d69778a595b2e6b8','8111fa0c926fbdb1878910aa7ba59b3d33426a7939569f60152dce0c565140d5');newpair=('c9bfb2d5011b9b9d9a28fab5bde3328f0cb1e0afb4a3bd1c52cc5610c844b679','f3c97a07dc155e8239e533824de29e18503c515f4fb0a398cdae5e116200e79e')
for expected in (oldpair,newpair):
 for actual in (oldpair,newpair,(oldpair[0],newpair[1]),(newpair[0],oldpair[1])):
  host.read=lambda path: (actual[0] if 'codi-connected' in str(path) else actual[1]).encode();host.sha=lambda raw:raw.decode()
  try:host.main_ready(*expected)
  except ValueError:
   if actual==expected:raise
  else:
   if actual!=expected:raise AssertionError('mixed or wrong config pair accepted')
actor=(p/'asset-launch.py').read_text();assert 'for name in (routermod.NEXT,routermod.F2)' in actor and "if family==routermod.F2:host.main_ready=lambda:original_main_ready(" in actor
print('PASS f2 exact renders, floor selection, cross-family/mixed refusal and main managed config pair checks (service/health mocked)')
