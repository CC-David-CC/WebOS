#!/usr/bin/env python3
"""Compose selected generic app bundles over a sealed native16 public graph."""
import argparse,hashlib,importlib.util,json,re,shutil,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'.build/releases/connected-routed-r8'
PIN='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200'
sys.dont_write_bytecode=True
def sha(data):return hashlib.sha256(data).hexdigest()
def record(path):
 data=path.read_bytes();return {'bytes':len(data),'sha256':sha(data)}
def encoded(value):return (json.dumps(value,indent=2)+'\n').encode()
def key(records):return sha(json.dumps(records,sort_keys=True,separators=(',',':')).encode())
def build(assets,destination,base=BASE,pin=PIN,allow_new=()):
 base=Path(base).resolve();assert re.fullmatch("[0-9a-f]{64}",pin)
 spec=importlib.util.spec_from_file_location('app_update_contract',base/'origin_service/release.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);assert c.verify(base)['manifestSHA256']==pin
 destination=Path(destination).absolute();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases')
 partial=json.loads((assets/'apps.json').read_bytes());assert partial['version']=='codi-public-apps/2' and partial['hostAPI']==2 and 1<=len(partial['apps'])<=7
 graph=json.loads((base/'assets/desktop/network-release.json').read_bytes());old_core=graph['coreDirectory'];desktop=(base/old_core/'desktop-apps.js').read_text();old_loader=re.search(r"assets/desktop/apps-v2-[a-f0-9]{64}\.mjs",desktop)[0]
 loader=(base/old_loader).read_text();old_catalog=re.search(r'apps-v2-[a-f0-9]{64}\.json',loader)[0];catalog=json.loads((base/'assets/desktop'/old_catalog).read_bytes());apps={a['id']:a for a in catalog['apps']};assert len(apps)==len(catalog['apps']) and 1<=len(apps)<=32
 stage=Path(tempfile.mkdtemp(prefix='.native-app-update-',dir=destination.parent));new=set();removed=set()
 try:
  shutil.copytree(base,stage,dirs_exist_ok=True)
  def put(name,data):
   assert c.public_name(name),name
   path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);new.add(name)
  for app in partial['apps']:
   assert (app['id'] in apps or app['id'] in allow_new) and app['path'].startswith('assets/desktop/apps/'+app['id']+'/')
   folder=Path(app['path']).parent
   for name,r in app['files'].items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts
    source=assets/str(folder).removeprefix('assets/desktop/')/name;assert not source.is_symlink() and record(source)==r
    put(str(folder/name),source.read_bytes())
   apps[app['id']]=app
  ordered=[a['id'] for a in catalog['apps']];ordered.extend(sorted(set(apps)-set(ordered)));catalog['apps']=[apps[name] for name in ordered];raw=encoded(catalog);catalog_name='apps-v2-'+sha(raw)+'.json';put('assets/desktop/'+catalog_name,raw)
  assert loader.count(old_catalog)==1;raw=loader.replace(old_catalog,catalog_name).encode();new_loader='assets/desktop/apps-v2-'+sha(raw)+'.mjs';put(new_loader,raw)
  assert desktop.count(old_loader)==1
  core={n:(base/old_core/n).read_bytes() for n in graph['core']};core['desktop-apps.js']=desktop.replace(old_loader,new_loader).encode();graph['core']={n:{'bytes':len(b),'sha256':sha(b)} for n,b in core.items()};new_core=str(Path(old_core).parent)+'/'+key(graph['core']);graph['coreDirectory']=new_core
  for name,raw in core.items():put(new_core+'/'+name,raw)
  put('assets/desktop/network-release.json',encoded(graph));put('index.html',(base/'index.html').read_text().replace(old_core,new_core).encode())
  # Keep the active closed app catalog and the declared flat reference entrypoint,
  # not every historical v2 catalog/bundle copied by earlier compositions.
  reachable=set()
  for app in catalog['apps']:
   reachable.update(str(Path(app['path']).parent/name) for name in app['files'])
  legacy=stage/'assets/desktop/apps.json'
  if legacy.exists():
   old_apps=json.loads(legacy.read_bytes());assert old_apps['version']=='codi-public-apps/1'
   reachable.update(app['path'] for app in old_apps['apps'])
  def remove(path):
   n=str(path.relative_to(stage))
   if n not in new and path.is_file():removed.add(n);path.unlink()
  for p in (stage/'assets/desktop/apps').rglob('*'):
   if p.is_file() and str(p.relative_to(stage)) not in reachable:remove(p)
  for p in (stage/'assets/desktop').glob('apps-v2-*'):
   if re.fullmatch(r'apps-v2-[a-f0-9]{64}\.(?:mjs|json)',p.name) and str(p.relative_to(stage)) not in new:remove(p)
  active_loader=(stage/new_loader).read_text()
  for p in (stage/'assets/desktop').glob('app-instance-v2-*.mjs'):
   if p.name not in active_loader and not any(p.name.encode() in raw for raw in core.values()):remove(p)
  if new_core!=old_core:
   for p in (stage/old_core).rglob('*'):
    if p.is_file():remove(p)
  cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted((set(cache['files'])-removed)|new)};cache['id']=key(cache['files'])
  template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();put('assets/desktop/cache-manifest.json',encoded(cache));put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
  public=json.loads((base/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted((set(public['files'])-removed)|new)};(stage/'release.json').write_bytes(encoded(public))
  full=json.loads((base/'connected-release.json').read_bytes());native=set(full['files'])-set(json.loads((base/'release.json').read_bytes())['files'])-{'release.json'}
  for name in native:assert record(stage/name)==record(base/name)
  full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(encoded(full))
  for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
  result=c.verify(stage);stage.rename(destination)
  return result|{'directory':str(destination),'baseManifestSHA256':pin,'updatedApps':[a['id'] for a in partial['apps']],'catalogPath':'assets/desktop/'+catalog_name,'nativeAndGuestSecurityBytesUnchanged':True,'networkProtocolBytesUnchanged':True,'obsoleteGeneratedFilesRemoved':sorted(removed)}
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--app-assets',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--base-release',type=Path,default=BASE);p.add_argument('--base-manifest-sha256',default=PIN);a=p.parse_args();print(json.dumps(build(a.app_assets.resolve(),a.output,a.base_release,a.base_manifest_sha256),indent=2))
