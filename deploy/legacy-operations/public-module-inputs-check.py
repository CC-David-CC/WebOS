#!/usr/bin/env python3
"""Exercise exact shared-module input declarations in the actual compiler.

No additional source directory is authorized. Default app boundaries and
symlink refusal must still hold, including imports of an approved file.
"""
import argparse,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('module_builder',ROOT/'scripts/build-public-apps.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
def run():
 checks=[];failures=[];runtime=str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node')
 def check(name,ok):assert ok,name;checks.append(name)
 with tempfile.TemporaryDirectory(prefix='codi-public-module-boundary-') as folder:
  root=Path(folder);source=root/'apps';app=source/'calculator';shared=root/'shared';app.mkdir(parents=True);shared.mkdir()
  approved=shared/'approved.mjs';dependency=shared/'dependency.mjs';private=shared/'private.mjs'
  private.write_text('export const privateMarker="UNREFERENCED_PRIVATE_MODULE_MUST_NOT_BE_PUBLISHED";')
  dependency.write_text('export const text="Reviewed shared dependency";')
  approved.write_text('import {text} from "./dependency.mjs";export {text};')
  (app/'index.mjs').write_text('import {text} from "../../shared/approved.mjs";export function mount(host){return {element:host.ui.make("div","window-content",text),dispose(){}};}')
  counter=0
  def build(inputs=()):
   nonlocal counter
   counter+=1;output=root/('out'+str(counter));builder.build(source,output,['calculator'],runtime,public_inputs=inputs);return output
  def refuses(inputs,needle):
   try:build(inputs);return False
   except subprocess.CalledProcessError as e:
    failures.append({'case':counter,'stderr':e.stderr[-2500:]});return needle in e.stderr
  check('default source boundary refuses an undeclared shared module',refuses([], 'outside declared public source/package roots'))
  check('declaring a module does not authorize its undeclared transitive import',refuses([approved], 'outside declared public source/package roots'))
  output=build([approved,dependency]);catalog=json.loads((output/'apps.json').read_bytes());record=catalog['apps'][0];bundle=output/Path(record['path']).parent.relative_to('assets/desktop');code=(bundle/'index.mjs').read_text()
  check('two explicitly reviewed shared files bundle through the ordinary compiler','Reviewed shared dependency' in code)
  check('unreferenced neighboring private source is not copied','UNREFERENCED_PRIVATE_MODULE' not in code and not any('private' in name for name in record['files']))
  approved.write_text('import {privateMarker as text} from "./private.mjs";export {text};')
  check('an approved file cannot import its unapproved neighbor',refuses([approved,dependency], 'outside declared public source/package roots'))
  approved.write_text('import {text} from "./dependency.mjs";export {text};')
  link=shared/'alias.mjs';link.symlink_to(dependency)
  check('explicit declaration still refuses a symlinked file',refuses([approved,dependency,link], 'Symlinked app input'))
  directory=shared/'directory.mjs';directory.mkdir()
  check('explicit declaration refuses directories masquerading as modules',refuses([approved,dependency,directory], 'Regular app input required'))
  check('missing explicit module refuses before emitting a public catalog',refuses([approved,dependency,shared/'missing.mjs'], 'ENOENT'))
  check('directory declarations cannot broaden the source roots',refuses([shared], 'Invalid explicit public module inputs'))
 return {'status':'PASS','scope':__doc__,'checks':checks,'expectedRefusals':failures,'productionChanged':False,'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'scripts/build-public-apps.py',ROOT/'tools/app-builder/build.mjs']}}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();r=run();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'checks':len(r['checks'])}))
