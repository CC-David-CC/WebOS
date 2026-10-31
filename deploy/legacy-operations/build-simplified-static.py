#!/usr/bin/env python3
"""Build a public-only Simplified tree and hash-verified lazy cache worker."""
import argparse
from pathlib import Path
import hashlib, importlib.util, json, shutil
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'.build/simplified-release')
p.add_argument('--apps-bundle',type=Path,default=ROOT/'.build/simplified-apps')
args=p.parse_args();OUT=args.output.absolute()
if OUT.exists() or OUT.is_symlink() or not OUT.parent.is_dir():raise ValueError('Choose a new release directory under an existing parent')
spec=importlib.util.spec_from_file_location('staging',ROOT/'scripts/serve-connected.py')
staging=importlib.util.module_from_spec(spec);spec.loader.exec_module(staging);staging.stage(OUT,bundled=args.apps_bundle)
# Keep only app bundles referenced by the catalog; never publish private state.
catalog=json.loads((OUT/'assets/desktop/apps.json').read_text())
for appdir in (OUT/'assets/desktop/apps').iterdir():
 if not appdir.is_dir():raise ValueError('Unexpected application output')
 app=next((x for x in catalog['apps'] if x['id']==appdir.name),None)
 if app is None:raise ValueError('Unregistered application bundle')
 for version in appdir.iterdir():
  if version.name!=app['bundleSHA256']:shutil.rmtree(version)
# The issuer supplies config, never a static development config.
(OUT/'config.json').unlink()
files={}
for p in sorted(OUT.rglob('*')):
 if p.is_symlink():raise ValueError('Unexpected symlink in release')
 if p.is_file() and p.relative_to(OUT).as_posix() not in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):
  rel=p.relative_to(OUT).as_posix();digest=hashlib.sha256();size=0
  with p.open('rb') as stream:
   while chunk:=stream.read(1024*1024):digest.update(chunk);size+=len(chunk)
  files[rel]={'bytes':size,'sha256':digest.hexdigest()}
canonical=json.dumps(files,sort_keys=True,separators=(',',':')).encode();manifest={'version':'codi-public-cache/1','id':hashlib.sha256(canonical).hexdigest(),'files':files}
(OUT/'assets/desktop/cache-manifest.json').write_text(json.dumps(manifest,separators=(',',':')))
template=(ROOT/'scripts/templates/device-cache-worker.js').read_text().replace("'networking.js',", "'bootstrap.js',")
template=template.replace("if(event.data?.type!=='cache-loaded'||!event.ports[0])return;", "if(event.data?.type==='codi-cache-version'&&event.ports[0]){event.ports[0].postMessage({protocol:'codi-simplified-cache/1',release:RELEASE.id});return;}\n  if(event.data?.type!=='cache-loaded'||!event.ports[0])return;")
(OUT/'assets/desktop/offline-worker.js').write_text(template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(manifest,separators=(',',':'))))
print(json.dumps({'release':str(OUT),'cacheId':manifest['id'],'files':len(files)}))
