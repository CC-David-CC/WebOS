#!/usr/bin/env python3
"""Bounded rendering controls, no live controller or browser claims."""
import copy,importlib.util,json,sys,tempfile,tomllib
from pathlib import Path
here=Path(__file__).resolve().parent;repo=here.parents[1];ops=repo/'beta-isolated-hosting/ops';sys.path.insert(0,str(ops))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
build=load('asset_builder',here/'build-generator.py');original=load('common_old',ops/'common.py')
old=Path(sys.argv[1]);new=Path(sys.argv[2])
with tempfile.TemporaryDirectory(prefix='830c-generator-') as d:
 path=Path(d);build.build(old,new,path/'out');gen=load('asset_common',path/'out/common.py')
 for main in ('0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020','e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480'):
  data=tomllib.loads((ops/'sites_live.toml').read_text());data['codi_beta_maintenance']=False;data['codi_beta_opfs']=build.OLD
  next(site for site in data['sites'] if site['domain']=='ksu.codes')['codi_simplified']=main
  updated=copy.deepcopy(data);updated['codi_beta_opfs']=build.NEW
  for mode in ('prepare','production'):
   assert gen.caddy(data,mode)==original.caddy(data,mode), '3ad output changed'
   a=gen.caddy(data,mode);b=gen.caddy(updated,mode)
   def strip(s):
    at=s.index('beta.ksu.codes {');end=s.index('\n}\n',at)+3;return s[:at]+s[end:]
   assert strip(a)==strip(b),'non-beta output changed'
   assert build.NEW not in a and build.NEW in b
   assert build.OLD in a and build.OLD not in b
   gate=copy.deepcopy(data);gate.pop('codi_beta_opfs');gate['codi_beta_maintenance']=True
   assert gen.caddy(gate,mode)==original.caddy(gate,mode),'maintenance rendering changed'
 assert len(gen.OPFS_NEW_PUBLIC_FILES)==166
 try:gen.validate({**updated,'codi_beta_opfs':'0'*64})
 except ValueError:pass
 else:raise AssertionError('unreviewed endpoint accepted')
 try:build.build(old,new,path/'out')
 except FileExistsError:pass
 else:raise AssertionError('existing output accepted')
 bad=path/'bad';bad.mkdir();(bad/'manifest.json').write_text('{}')
 try:build.build(old,bad,path/'drift')
 except ValueError:pass
 else:raise AssertionError('bad manifest accepted')
 assert not (path/'drift').exists()
print('PASS exact old/gate rendering, 830c-only output, non-beta unchanged and refusal controls')
