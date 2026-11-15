#!/usr/bin/env python3
"""Compose reviewed API2/xterm assets over sealed strict native15, retaining API1.

No routed-group experiment or canonical old native backend enters this artifact.
All old unversioned scripts/catalogs/images remain for existing API1 tabs.
"""
import argparse,hashlib,importlib.util,json,re,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FOUNDATION=ROOT/'.build/releases/connected-signin-r7'
BASE=FOUNDATION
sys.dont_write_bytecode=True
PIN='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def record(path):
 raw=path.read_bytes();return {'bytes':len(raw),'sha256':sha(raw)}
def build(destination):
 spec=importlib.util.spec_from_file_location('xterm_native_contract',FOUNDATION/'origin_service/release.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);assert c.verify(BASE)['manifestSHA256']==PIN
 destination=Path(destination).absolute();assert not destination.exists() and destination.is_relative_to(ROOT/'.build/releases') and not any(p.is_symlink() for p in destination.parents)
 stage=Path(tempfile.mkdtemp(prefix='.xterm-native-',dir=destination.parent))
 try:
  for p in BASE.rglob('*'):
   if p.is_file():target=stage/p.relative_to(BASE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  public=json.loads((BASE/'release.json').read_text());new=set()
  def put(name,data):
   assert c.public_name(name);path=stage/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data if isinstance(data,bytes) else data.encode());new.add(name)
  # API2 registries and loader are content-addressed, independently of API1 URLs.
  catalog=(ROOT/'assets/desktop/apps.json').read_bytes();meta=json.loads(catalog);assert meta['version']=='codi-public-apps/2' and meta['hostAPI']==2
  for app in meta['apps']:
   folder=Path(app['path']).parent
   for name,r in app['files'].items():
    path=ROOT/folder/name;assert record(path)==r and not path.is_symlink();put(str(folder/name),path.read_bytes())
  catalog_name='apps-v2-'+sha(catalog)+'.json';put('assets/desktop/'+catalog_name,catalog)
  instance=(ROOT/'assets/desktop/app-instance.mjs').read_bytes();instance_name='app-instance-v2-'+sha(instance)+'.mjs';put('assets/desktop/'+instance_name,instance)
  loader=(ROOT/'assets/desktop/apps.mjs').read_text();assert loader.count("'apps.json'")==1 and loader.count("'./app-instance.mjs'")==1
  loader=loader.replace("'apps.json'",repr(catalog_name)).replace("'./app-instance.mjs'",repr('./'+instance_name));loader_name='assets/desktop/apps-v2-'+sha(loader.encode())+'.mjs';put(loader_name,loader)
  image=json.loads((ROOT/'assets/terminal/v2/image.json').read_text());raw=(ROOT/image['path']).read_bytes();assert image['version']=='codi-terminal-image/2' and sha(raw)==image['sha256'] and len(raw)==image['bytes'];put(image['path'],raw);put('assets/terminal/v2/image.json',(ROOT/'assets/terminal/v2/image.json').read_bytes())
  # Keep the existing mature P2P implementation; add only view-scoped cleanup.
  network=(FOUNDATION/'networking.js').read_text();anchor='appContext(){return {views,chatBodies';assert network.count(anchor)==1
  network=network.replace(anchor,'appContext(){return {releaseView,releaseRoomView:view=>{roomService?.releaseView(view);pgnImports?.releaseView(view);},views,chatBodies')
  app=(ROOT/'app.js').read_text();old=(BASE/'app.js').read_text();a=app.index('  appendNetworkInfo(popup){');b=app.index('  showStatus(type,anchor)',a);x=old.index('  appendNetworkInfo(popup){');y=old.index('  showStatus(type,anchor)',x);app=app[:a]+old[x:y]+app[b:]
  desktop=(ROOT/'desktop-apps.js').read_text();anchor="import('./assets/desktop/apps.mjs')";assert desktop.count(anchor)==1;desktop=desktop.replace(anchor,"import(new URL("+repr(loader_name)+",document.baseURI))")
  # The shared home README uses the already-proven sign-in copy and lists nano.
  start=desktop.index('  async connect(emulator,');end=desktop.index('\n};',start);before=(FOUNDATION/'desktop-apps.js').read_text();a=before.index('  async connect(emulator,');b=before.index('\n};',a)
  desktop=desktop[:start]+before[a:b].replace('grep, sed, awk and vi.','grep, sed, awk, vi and nano.').replace('vi notes.txt','nano notes.txt')+desktop[end:]
  source={'reference.js':(ROOT/'reference.js').read_text(),'terminal.js':(ROOT/'terminal.js').read_text(),'desktop-apps.js':desktop,'networking.js':network,'app.js':app}
  # Classic scripts retain their shared lexical scope. Rebase literal imports
  # against the desktop document, not their new immutable asset directory.
  for name,text in source.items():source[name]=re.sub(r"import\((['\"])\./([^'\"]+)\1\)",lambda m:'import(new URL('+repr(m[2])+',document.baseURI))',text)
  core_key=sha(json.dumps({n:sha(s.encode()) for n,s in source.items()},sort_keys=True,separators=(',',':')).encode());folder='assets/desktop/core-v2/'+core_key
  for name,text in source.items():put(folder+'/'+name,text)
  style=(ROOT/'style.css').read_text();style=re.sub(r'url\(([\"\x27]?)(assets/[^)\"\x27]+)',lambda m:'url('+m[1]+m[2].removeprefix('assets/'),style);style_name='assets/desktop-style-v2-'+sha(style.encode())+'.css';put(style_name,style)
  index=(FOUNDATION/'index.html').read_text();index=index.replace('href="style.css"','href="'+style_name+'"')
  for name in source:index=index.replace('src="'+name+'"','src="'+folder+'/'+name+'"')
  put('index.html',index)
  # Recreate cache from the exact release map, never a scan of development state.
  cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_text());names=set(cache['files'])|new;names-={'config.json','assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'}
  cache['files']={n:record(stage/n) for n in sorted(names)};cache['id']=sha(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode())
  template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
  put('assets/desktop/cache-manifest.json',json.dumps(cache,indent=2)+'\n');put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))))
  public['files']={n:record(stage/n) for n in sorted(set(public['files'])|new)};(stage/'release.json').write_text(json.dumps(public,indent=2)+'\n')
  full=json.loads((BASE/'connected-release.json').read_text());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_text(json.dumps(full,indent=2)+'\n')
  for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
  verified=c.verify(stage)
  # Every native/backend byte, guest SDK, network protocol and old host asset
  # is retained. Only the entry document/cache and new versioned assets change.
  for name in c.V15_NATIVE:assert record(stage/name)==record(BASE/name)
  for name in ['app.js','style.css','reference.js','terminal.js','desktop-apps.js','networking.js','assets/desktop/apps.json','assets/desktop/apps.mjs','assets/terminal-initramfs.cpio.gz']:assert record(stage/name)==record(BASE/name)
  stage.rename(destination)
  return verified|{'directory':str(destination),'baseManifestSHA256':PIN,'coreDirectory':folder,'loaderPath':loader_name,'image':image,'api1AssetsPreserved':True,'nativeBackendUnchanged':True,'routedGroupExperimentIncluded':False}
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--base',type=Path,default=FOUNDATION);p.add_argument('--base-manifest-sha256',default=PIN);a=p.parse_args();BASE=a.base.resolve();PIN=a.base_manifest_sha256;print(json.dumps(build(a.output),indent=2))
