"""Seed only disposable namespace paths from the reviewed e7 beta snapshot."""
import importlib.util,os,sys,types
from pathlib import Path
p=Path(os.environ['CODI_FILES_FIXTURE_BUNDLE']);sys.path.insert(0,str(p/'ops'))
def load(name,file):
 s=importlib.util.spec_from_file_location(name,p/'ops'/file);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
old=load('common','common_live.py');new=load('candidate_common','common.py')
snap=load('beta_files_snapshots','beta_files_snapshots.py');successor=load('beta_successor','beta_successor.py')
root=Path('/home/dflanag3/webhost-sites');old.ROOT=new.ROOT=root;old.MANIFEST=new.MANIFEST=root/'sites.toml'
a=types.SimpleNamespace(source=(p/'ops/common_live.py').read_bytes(),module=old);b=types.SimpleNamespace(source=(p/'ops/common.py').read_bytes(),module=new)
x=snap.build(old=a,new=b,manifest=(p/'ops/sites_live.toml').read_bytes(),candidate_manifest=(p/'ops/beta_files_candidate.json').read_bytes(),route_table=(p/'OPFS-ROUTE-TABLE.json').read_bytes())
families=successor.families(x,a,b)
s=families[successor.NEW]['candidate']
# Reproduce the main selector transaction's complete generated Caddy outputs,
# not just its three primary files. Refuse an unexpected pre-seed fixture.
old_data=families[successor.OLD]['candidateData'];new_data=families[successor.NEW]['candidateData']
aux=[]
for mode in ('prepare','production'):
 before=new.caddy(old_data,mode).encode();after=new.caddy(new_data,mode).encode()
 for path in (root/'deploy/caddy'/('Caddyfile.'+mode),Path('/etc/caddy')/('Caddyfile.'+mode)):
  if path.read_bytes()!=before:raise ValueError('Unexpected fixture auxiliary output '+str(path))
  aux.append((path,after))
for path,data in aux:path.write_bytes(data)
for path,key in ((root/'ops/common.py','common'),(root/'sites.toml','manifest'),(Path('/etc/caddy/Caddyfile'),'caddy')):path.write_bytes(s[key])
