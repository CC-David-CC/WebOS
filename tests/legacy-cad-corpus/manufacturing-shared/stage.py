#!/usr/bin/env python3
"""Stage public code and an exact CAD dist for private workflow qualification.

No account, key, browser profile, dependency cache or server state is copied.
This is a test fixture, not a release/source-distribution packager.
"""
import argparse, hashlib, json, pathlib, shutil
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--desktop-source',type=pathlib.Path,required=True)
p.add_argument('--cad-dist',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args();source=a.desktop_source.resolve(strict=True);dist=a.cad_dist.resolve(strict=True)
assert (source/'apps/system/jsketcher/index.mjs').is_file()
assert (dist/'index-webos.html').is_file() and (dist/'static/index.bundle.js').is_file()
assert not a.output.exists(),'Use a fresh task-owned fixture output'
a.output.mkdir(parents=True)
app=a.output/'system/jsketcher'
shutil.copytree(source/'apps/system/jsketcher',app,ignore=shutil.ignore_patterns('node_modules'))
target=app/'node_modules/jsketcher-build';target.mkdir(parents=True)
allowed={'.mjs','.js','.css','.html','.json','.xml','.txt','.wasm','.data','.svg','.png','.jpg','.jpeg','.webp','.gif','.ico','.woff','.woff2','.ttf','.eot'}
assets=[];pins={};excluded=[]
for original in sorted(dist.rglob('*')):
 if original.is_symlink():raise ValueError('Symlinked CAD dist input')
 if not original.is_file():continue
 rel=original.relative_to(dist)
 if original.suffix.lower() not in allowed or original.name=='webosTest.bundle.js' or rel.as_posix() in {'index.html','sketcher.html'}:
  excluded.append(rel.as_posix());continue
 destination=target/rel;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,destination)
 digest=hashlib.sha256();size=0
 with destination.open('rb') as copied:
  while chunk:=copied.read(1024*1024):
   size+=len(chunk);digest.update(chunk)
 name='node_modules/jsketcher-build/'+rel.as_posix();assets.append(name)
 pins[name]={'bytes':size,'sha256':digest.hexdigest()}
assert 'node_modules/jsketcher-build/index-webos.html' in assets
manifest=json.loads((app/'app.json').read_text());assert set(manifest)=={'assets'},'Review new manifest fields explicitly'
manifest['assets']=assets;(app/'app.json').write_text(json.dumps(manifest,indent=2)+'\n')
config={'source':str(a.output.resolve()),'output':str(a.output.resolve())+'-apps','apps':['jsketcher'],'entries':{'jsketcher':'system/jsketcher/index.mjs'}}
(a.output/'builder-config.json').write_text(json.dumps(config,indent=2)+'\n')
receipt={'scope':'private code-only fixture staging; no deployment or geometry qualification','desktopSource':str(source),'cadDist':str(dist),'files':pins,'excluded':excluded,'assetBytes':sum(v['bytes'] for v in pins.values())}
(a.output/'stage-pins.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'assets':len(assets),'assetBytes':receipt['assetBytes'],'excluded':excluded}))
