#!/usr/bin/env python3
"""Bundle a public host service using the existing dependency-aware compiler.

The internal compiler catalog is not added to the desktop's app menu/catalog.
Host services live in their own content-addressed public namespace.
"""
import argparse,hashlib,importlib.util,json,re,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(entry,name,alias,output,public_inputs=()):
 entry=entry.resolve();output=output.resolve()
 assert entry.is_relative_to(ROOT/'assets') and entry.suffix in ['.mjs','.js'] and re.fullmatch('[a-z][a-z0-9-]{0,31}',name)
 assert alias.startswith('assets/') and '..' not in alias.split('/') and '\\' not in alias and alias.endswith('.mjs')
 assert output.is_relative_to(ROOT/'.build/shared-services') and not output.exists()
 for p in public_inputs:
  assert (p.resolve().is_relative_to(ROOT/'network') or p.resolve().is_relative_to(ROOT/'assets/vendor')) and p.suffix in ['.mjs','.js'],'Shared service extra inputs must be exact public network/vendor modules'
 spec=importlib.util.spec_from_file_location('shared_public_compiler',ROOT/'scripts/build-public-apps.py');compiler=importlib.util.module_from_spec(spec);spec.loader.exec_module(compiler)
 with tempfile.TemporaryDirectory(prefix='codi-service-bundle-') as temp:
  temp=Path(temp);compiled=temp/'compiled';compiler.build(entry.parent,compiled,[name],str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'),entries={name:entry.name},public_inputs=public_inputs)
  catalog=json.loads((compiled/'apps.json').read_bytes());assert len(catalog['apps'])==1;app=catalog['apps'][0];assert not app['styles'],'Host service CSS requires an explicit host style contract'
  source=compiled/Path(app['path']).parent.relative_to('assets/desktop');folder=Path('assets/desktop/services')/name/app['bundleSHA256']
  output.mkdir(parents=True);target=output/folder;target.mkdir(parents=True)
  for n,r in app['files'].items():
   p=source/n;assert not p.is_symlink() and r=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
   dest=target/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
  manifest={'version':'codi-shared-service/1','name':name,'sourceAlias':alias,'path':str(folder/'index.mjs'),'files':app['files']}
  (output/'shared-service.json').write_text(json.dumps(manifest,indent=2)+'\n')
  return {'status':'PASS','directory':str(output),'entry':manifest['path'],'files':len(app['files']),'manifestSHA256':hashlib.sha256((output/'shared-service.json').read_bytes()).hexdigest(),'addedMenuApps':0}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--entry',type=Path,required=True);p.add_argument('--name',required=True);p.add_argument('--alias',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--public-input',type=Path,action='append',default=[]);a=p.parse_args();print(json.dumps(build(a.entry,a.name,a.alias,a.output,a.public_input),indent=2))
