#!/usr/bin/env python3
"""Browser-files-only SDK composition over sealed paused 9f; never deploys.

The current network builder/raw app.js are deliberately not inputs. Exact
storage-only edits are applied to the sealed core, retaining its UI/lifecycle.
"""
import argparse,importlib.util,json,re,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
BASE_PIN='9f86587c8590eed2c34bbf3eede2efb109fe0a8401328551a00092f19e3b9fe9'
SERVICE_PIN='b66c4ffe301c94550efa25ce56266550c45294e404602e2511421d106680751d'
HOST_PIN='51941f0e069695bc0dc0d345a86053e3e114e27b9ba0245384ae3aa048285a7c'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
u=module('browser_files_app_composer',ROOT/'scripts/build-native-app-update.py')
def once(text,before,after):
 assert text.count(before)==1,('Expected one audited storage patch',before)
 return text.replace(before,after)
def catalog(root):
 g=json.loads((root/'assets/desktop/network-release.json').read_bytes());host=(root/g['coreDirectory']/'desktop-apps.js').read_text();loader=re.search(r'assets/desktop/apps-v2-[a-f0-9]{64}\.mjs',host)[0];name=re.search(r'apps-v2-[a-f0-9]{64}\.json',(root/loader).read_text())[0]
 return json.loads((root/'assets/desktop'/name).read_bytes())
def verify_boundaries(base,stage):
 a=json.loads((base/'connected-release.json').read_bytes())['files'];b=json.loads((stage/'connected-release.json').read_bytes())['files'];c=module('browser_files_sealed_contract',base/'origin_service/release.py');v=c.verify(stage)
 assert all(a[n]==b[n] for n in c.V19_NATIVE) and len(c.V19_NATIVE)==57
 old=json.loads((base/'assets/desktop/network-release.json').read_bytes());new=json.loads((stage/'assets/desktop/network-release.json').read_bytes())
 assert old['directory']==new['directory'] and old['modules']==new['modules'] and len(new['modules'])==40
 for n in old['modules']:assert a[old['directory']+'/'+n]==b[new['directory']+'/'+n]
 for n in ['networking.js','reference.js','terminal.js']:assert (base/old['coreDirectory']/n).read_bytes()==(stage/new['coreDirectory']/n).read_bytes()
 assert 'const disabled=true;' in (stage/new['coreDirectory']/'networking.js').read_text()
 apps={r['id']:r for r in catalog(base)['apps']};updated={r['id']:r for r in catalog(stage)['apps']};assert set(apps)==set(updated)
 for name in set(apps)-{'files','text'}:assert apps[name]==updated[name]
 registry=json.loads((base/'assets/desktop/shared-services.json').read_bytes());services=json.loads((stage/'assets/desktop/shared-services.json').read_bytes());assert len(registry['services'])==1 and len(services['services'])==2
 assert registry['services'][0] in services['services']
 allowed={'index.html','release.json','assets/desktop/network-release.json','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js','assets/desktop/shared-services.json'}
 def permitted(n):return n in allowed or n.startswith(('assets/desktop/core-v10/','assets/desktop/apps/files/','assets/desktop/apps/text/','assets/desktop/services/browser-files/')) or bool(re.fullmatch(r'assets/desktop/apps-v2-[a-f0-9]{64}\.(mjs|json)',n))
 changed=sorted(n for n in set(a)|set(b) if a.get(n)!=b.get(n));assert all(permitted(n) for n in changed),[n for n in changed if not permitted(n)]
 cache=json.loads((stage/'assets/desktop/cache-manifest.json').read_bytes());assert all(u.record(stage/n)==r for n,r in cache['files'].items()) and cache['id']==u.key(cache['files'])
 for service in services['services']:
  assert service['path'] in cache['files']
  assert all(b[str(Path(service['path']).parent/n)]==r for n,r in service['files'].items())
 return v|{'changedFiles':changed,'nativeFilesUnchanged':57,'networkModulesUnchanged':40,'otherApplicationBundlesUnchanged':5,'chatPaused':True}
def build(base,destination,service,node):
 base=base.resolve();destination=destination.absolute();service=service.resolve();assert not destination.exists()
 assert u.sha((base/'connected-release.json').read_bytes())==BASE_PIN and u.sha((service/'shared-service.json').read_bytes())==SERVICE_PIN
 host_source=ROOT/'desktop-apps.js';assert u.sha(host_source.read_bytes())==HOST_PIN
 tested=json.loads((ROOT/'.build/checks/browser-files-bundled-r2-result.json').read_bytes());assert tested['status']=='PASS' and len(tested['checks'])==21
 manifest=json.loads((service/'shared-service.json').read_bytes());assert manifest['name']=='browser-files' and manifest['sourceAlias']=='assets/desktop/browser-files.mjs' and list(manifest['files'])==['index.mjs']
 assert {str(p.relative_to(service)) for p in service.rglob('*') if p.is_file()}=={'shared-service.json',manifest['path']}
 assert u.record(service/manifest['path'])==manifest['files']['index.mjs']
 with tempfile.TemporaryDirectory(prefix='browser-files-apps-') as tmp:
  assets=Path(tmp)/'apps';builder=module('browser_files_public_builder',ROOT/'scripts/build-public-apps.py');builder.build(ROOT.parent/'served_apps_public',assets,['files','text'],node)
  partial=json.loads((assets/'apps.json').read_bytes());expected=[a for a in tested['builtApps']['apps'] if a['id'] in ['files','text']];assert partial['apps']==expected
  intermediate=u.build(assets,destination,base,BASE_PIN)
 try:
  graph=json.loads((destination/'assets/desktop/network-release.json').read_bytes());old_core=graph['coreDirectory'];core={n:(destination/old_core/n).read_text() for n in graph['core']};app=core['app.js']
  app=once(app,"(!w.ownerSub||w.ownerSub===signedInSubject())&&(!isAccountApp", "(!w.ownerSub||w.ownerSub===signedInSubject())&&(!w.browserOwner||w.browserOwner===browserFilesScope())&&(!isAccountApp")
  app=once(app,"(w.storage!=='server'&&win.querySelector", "((!w.storage||w.storage==='guest')&&win.querySelector")
  app=once(app,"!['guest','server'].includes(context.storage)","!['guest','server','browser'].includes(context.storage)")
  marker="    const launchContext=Object.freeze({version:1,storage:context.storage,path:context.path,owner:context.owner});"
  app=once(app,marker,"    if(context.storage==='browser'&&context.owner!==browserFilesScope())throw Error('Switch back to the browser document owner');\n"+marker)
  app=once(app,"(context.storage==='guest'?!w.ownerSub:w.ownerSub===context.owner)","(context.storage==='guest'?!w.ownerSub&&!w.browserOwner:context.storage==='browser'?w.browserOwner===context.owner:w.ownerSub===context.owner)")
  app=once(app,"if(context.storage==='server')w.ownerSub=context.owner;this.render();return w;","if(context.storage==='server')w.ownerSub=context.owner;if(context.storage==='browser')w.browserOwner=context.owner;this.render();return w;")
  core['app.js']=app;host=core['desktop-apps.js']
  host=once(host,'storage:{guestFiles,serverFilesAvailable,serverFileContext,fileVolumeBar,','storage:{guestFiles,serverFilesAvailable,serverFileContext,browserFileContext,browserFilesScope,browserFilesChanged,openBrowserEditor,fileVolumeBar,')
  host=once(host,"  if(!serverFilesAvailable())return document.createDocumentFragment();\n",'')
  host=once(host,"  for(const [storage,label] of [['guest','Temporary files'],['server','My server files']]){","  const volumes=[['guest','Temporary files'],['browser','This browser']];if(serverFilesAvailable())volumes.push(['server','My server files']);\n  for(const [storage,label] of volumes){")
  source=host_source.read_text();start=source.index('// One shared on-device store;');end=source.index('function serverFilesChanged()',start);block=source[start:end]
  block=once(block,"import('./assets/desktop/browser-files.mjs')","import(new URL("+repr(manifest['path'])+",document.baseURI))")
  host=once(host,'function serverFilesChanged()',block+'function serverFilesChanged()');core['desktop-apps.js']=host
  new=set();removed=set()
  contract=module('browser_files_contract',base/'origin_service/release.py')
  def put(name,raw):
   assert contract.public_name(name);p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);new.add(name)
  registry=json.loads((destination/'assets/desktop/shared-services.json').read_bytes());assert all(s['name']!='browser-files' for s in registry['services']);registry['services'].append(manifest);registry['services'].sort(key=lambda s:s['name']);put('assets/desktop/shared-services.json',u.encoded(registry));put(manifest['path'],(service/manifest['path']).read_bytes())
  graph['core']={n:{'bytes':len(t.encode()),'sha256':u.sha(t.encode())} for n,t in core.items()};folder='assets/desktop/core-v10/'+u.key(graph['core']);graph['coreDirectory']=folder
  for n,t in core.items():put(folder+'/'+n,t.encode())
  put('index.html',(destination/'index.html').read_text().replace(old_core,folder).encode());put('assets/desktop/network-release.json',u.encoded(graph))
  for p in (destination/old_core).rglob('*'):
   if p.is_file():removed.add(str(p.relative_to(destination)));p.unlink()
  cache=json.loads((destination/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:u.record(destination/n) for n in sorted((set(cache['files'])-removed)|new)};cache['id']=u.key(cache['files']);put('assets/desktop/cache-manifest.json',u.encoded(cache))
  template=(ROOT/'scripts/templates/device-cache-worker.js').read_text();assert template.count('__PUBLIC_CACHE_MANIFEST__')==1
  sealed_cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes());assert template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(sealed_cache,separators=(',',':'))).encode()==(base/'assets/desktop/offline-worker.js').read_bytes()
  put('assets/desktop/offline-worker.js',template.replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
  public=json.loads((destination/'release.json').read_bytes());public['files']={n:u.record(destination/n) for n in sorted((set(public['files'])-removed)|new)};(destination/'release.json').write_bytes(u.encoded(public))
  full=json.loads((destination/'connected-release.json').read_bytes());full['files']={str(p.relative_to(destination)):u.record(p) for p in sorted(destination.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(destination/'connected-release.json').write_bytes(u.encoded(full))
  for p in [destination,*destination.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
  result=verify_boundaries(base,destination);return result|{'status':'PASS','directory':str(destination),'baseManifestSHA256':BASE_PIN,'serviceManifestSHA256':SERVICE_PIN,'testedWorkflowReceiptSHA256':u.sha((ROOT/'.build/checks/browser-files-bundled-r2-result.json').read_bytes()),'sourceCoreCopiedWholesale':False,'intermediateManifestSHA256':intermediate['manifestSHA256'],'composerSHA256':u.sha(Path(__file__).read_bytes())}
 except BaseException:
  shutil.rmtree(destination);raise
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base-release',type=Path,default=ROOT/'.build/releases/connected-device-history-host-r4');p.add_argument('--output',type=Path,required=True);p.add_argument('--service',type=Path,default=ROOT/'.build/shared-services/browser-files-r1');p.add_argument('--node',default=str(ROOT/'.build/tools/node-v24.22.1-linux-x64/bin/node'));p.add_argument('--receipt',type=Path,required=True);a=p.parse_args();assert not a.receipt.exists();r=build(a.base_release,a.output,a.service,a.node);a.receipt.write_bytes(u.encoded(r));print(json.dumps(r,indent=2))
