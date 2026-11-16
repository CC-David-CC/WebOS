#!/usr/bin/env python3
"""Exact snapshot and transition-policy tests; no host mutation."""
import copy,importlib.util,subprocess,sys,tempfile,types
from pathlib import Path
here=Path(__file__).resolve().parent;research=here.parents[1];ops=research/'beta-isolated-hosting/ops';sys.path[:0]=[str(ops),str(here.parent)]
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
old=load('common',ops/'common_live.py');v2=load('common_v2',ops/'common.py');snap=load('snap',ops/'beta_files_snapshots.py');successor=load('beta_successor',here.parent/'beta-successor.py');router=load('asset_router',here/'asset-router.py')
with tempfile.TemporaryDirectory(prefix='830c-router-') as d:
 t=Path(d);subprocess.run([sys.executable,'-B',str(here/'build-generator.py'),'--old',sys.argv[1],'--new',sys.argv[2],'--out',str(t/'gen')],check=True,capture_output=True);subprocess.run([sys.executable,'-B',str(here/'build-inventory.py'),str(t/'inv')],check=True,capture_output=True)
 new=load('asset_common',t/'gen/common.py');inventory=load('asset_inventory',t/'inv/render_inventory.py');a=types.SimpleNamespace(source=(ops/'common_live.py').read_bytes(),module=old);b=types.SimpleNamespace(source=(ops/'common.py').read_bytes(),module=v2);c=types.SimpleNamespace(source=(t/'gen/common.py').read_bytes(),module=new)
 args=dict(snap=snap,successor=successor,oldgen=a,v2gen=b,newgen=c,manifest=(ops/'sites_live.toml').read_bytes(),old_manifest=(ops/'beta_files_candidate.json').read_bytes(),new_manifest=(Path(sys.argv[2])/'manifest.json').read_bytes(),table=(ops.parent/'OPFS-ROUTE-TABLE.json').read_bytes())
 for selector in router.EXPECT:
  x=router.snapshots(**args,selector=selector);assert x['baselineData']['codi_beta_opfs']==router.OLD and x['candidateData']['codi_beta_opfs']==router.NEW
  kw=dict(owner_uid=0,owner_gid=0,caddy_uid=0,caddy_gid=0)
  inventory.RenderInventory(t,t,b.module,a.module,x['baselineData'],x['gateData'],opfs_to_gate=True,**kw)
  inventory.RenderInventory(t,t,a.module,c.module,x['gateData'],x['candidateData'],opfs_from_gate=True,**kw)
  invalid=copy.deepcopy(x['candidateData']);invalid['codi_beta_opfs']='0'*64
  try:inventory.RenderInventory(t,t,a.module,c.module,x['gateData'],invalid,opfs_from_gate=True,**kw)
  except ValueError:pass
  else:raise AssertionError('unreviewed target accepted')
 bad={**args,'new_manifest':args['new_manifest']+b' '}
 try:router.snapshots(**bad,selector=next(iter(router.EXPECT)))
 except ValueError:pass
 else:raise AssertionError('tampered target accepted')
print('PASS exact snapshots for both main families, pinned inventory transitions and drift refusal; no host calls')
