#!/usr/bin/env python3
import importlib.util,itertools,sys
from pathlib import Path
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here.parents[1]/'beta-isolated-hosting/ops'))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
floor=load('asset_floor',here/'asset-floor.py');sel=load('asset_select',here/'asset-select.py');from beta_transaction import _encode
x={n:{k:(n+'-'+k).encode() for k in ('common','manifest','caddy')} for n in ('baseline','gate','candidate')}
def check(**kw):return sel.select(snapshots=x,original_floor=sel.ORIGINAL,other_pending=False,**kw)
def refuse(**kw):
 try:check(**kw)
 except ValueError:return
 raise AssertionError('unsafe state accepted')
assert check(current=x['baseline'],asset_floor=None,asset_journal=None,nested_journal=None)=='baseline'
for floorstate,edges in ((None,(('baseline','gate',1,None),('gate','baseline',1,None))),(sel.EXPECTED,(('gate','candidate',1,None),('candidate','gate',2,'gate-only')))):
 for a,b,version,policy in edges:
  j={'version':version,'phase':'prepared','old':_encode(x[a]),'new':_encode(x[b]),'timer':{'active':True,'enabled':True},'caddy_started':True,'backup':'fixture'}
  if policy:j['policy']=policy
  for bits in itertools.product((0,1),repeat=3):
   current={k:(x[a][k] if v==0 else x[b][k]) for k,v in zip(('common','manifest','caddy'),bits)}
   assert check(current=current,asset_floor=floorstate,asset_journal=sel.EXPECTED,nested_journal=j)=='nested'
  bad={**x[a],'manifest':b'cross-main'};refuse(current=bad,asset_floor=floorstate,asset_journal=sel.EXPECTED,nested_journal=j)
refuse(current=x['baseline'],asset_floor=sel.EXPECTED,asset_journal=None,nested_journal=None)
refuse(current=x['candidate'],asset_floor=None,asset_journal=sel.EXPECTED,nested_journal=None)
refuse(current=x['gate'],asset_floor={**sel.EXPECTED,'version':True},asset_journal=sel.EXPECTED,nested_journal=None)
try:sel.select(snapshots=x,current=x['baseline'],original_floor=sel.ORIGINAL,asset_floor=None,asset_journal=None,nested_journal=None,other_pending=True)
except ValueError:pass
else:raise AssertionError('pending host operation accepted')
print('PASS exact pre/post-floor and mixed journal selection, cross-state and stale refusal; no route mutations')
