"""Build a BBC-derived code-only Agent tools delta; no installation authority."""
import argparse,copy,hashlib,json,re,shutil
from pathlib import Path,PurePosixPath
PARENT='bbc42921e10d830f25ca314c0989df154f2be9a315d88f512451c0141ba2ff9e'
SOURCE='e5f603b609fe2b9948c4fa03181a706f4a9ee759'
APP='d78d53333222222404fcd030d187b655a24132f750a429b0fa55cbd9b8c1b319'
DESKTOP='e80f04ca34f3e6b011714cb32709e824b0f00a07'
REGISTRY_SOURCE='2ea07fac2ab36d90bfb1440ae07f5da45a41b123'
REGISTRY_SHA='43a7b8cfd70ffbbaf34a5e83d785b1a0c5f61d9ba7c29a4e640f63e4d9520e41'
MUTABLE={'shell/app.js','shell/desktop-apps.js','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
def digest(b):return hashlib.sha256(b).hexdigest()
def encode(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def record(path):
 h=hashlib.sha256();n=0
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return {'sha256':h.hexdigest(),'bytes':n}
def safe(s):
 p=PurePosixPath(s)
 if not isinstance(s,str) or not s or s!='/'.join(p.parts) or p.is_absolute() or any(x in ('.','..') for x in p.parts):raise ValueError('Noncanonical path')
 return s
def inventory(root):
 out={}
 for p in sorted(root.rglob('*')):
  if p.is_symlink() or not(p.is_file() or p.is_dir()):raise ValueError('Nonregular public input')
  if p.is_file():out[p.relative_to(root).as_posix()]=record(p)
 return out
def once(s,old,new,count=1):
 if s.count(old)!=count:raise ValueError('Wrong exact branding anchor: '+old)
 return s.replace(old,new)
def build(parent,apps,pins_path,registry_source,out):
 parent=parent.resolve(strict=True);apps=apps.resolve(strict=True);out=out.absolute()
 if out.exists() or out.is_symlink() or any(out==p or out in p.parents or p in out.parents for p in (parent,apps)):raise ValueError('Fresh unrelated output required')
 raw=(parent/'manifest.json').read_bytes();assert digest(raw)==PARENT
 old=json.loads(raw);got=inventory(parent);got.pop('manifest.json');assert got==old['files'] and len(got)==318
 pins=json.loads(pins_path.read_bytes());assert pins['source']==SOURCE and pins['files']['index.bundle.js']==APP and pins['workersNativeUnchanged'] is True
 oldcat=json.loads((parent/old['catalog']).read_bytes());assert digest((parent/old['catalog']).read_bytes())==old['catalogSHA256']
 ids=[a['id'] for a in oldcat['apps']];assert len(ids)==len(set(ids))==75 and ids.count('jsketcher')==1
 supplied=json.loads((apps/'apps.json').read_bytes());assert [a['id'] for a in supplied['apps']]==['jsketcher']
 cad=supplied['apps'][0];bundle=cad['bundleSHA256'];assert re.fullmatch('[a-f0-9]{64}',bundle) and bundle!=old['cadBundle']
 cadroot=apps/'apps/jsketcher'/bundle;assert inventory(cadroot)==cad['files'] and len(cad['files'])==145
 for name,want in pins['files'].items():assert record(cadroot/'node_modules/jsketcher-build/static'/safe(name))['sha256']==want,name
 entry=(cadroot/'index.mjs').read_text();assert 'CAD Modeler (JSketcher inspired)' in entry and 'CAD Modeler (JSketcher)' not in entry
 assert '<title>CAD Modeler (JSketcher inspired)</title>' in (cadroot/'node_modules/jsketcher-build/index-webos.html').read_text()
 cat=copy.deepcopy(oldcat);cat['apps'][ids.index('jsketcher')]=cad
 for i,row in enumerate(oldcat['apps']):
  if row['id']!='jsketcher':assert encode(row)==encode(cat['apps'][i])
 catbytes=(json.dumps(cat,indent=2)+'\n').encode();catsha=digest(catbytes);catname='assets/desktop/apps-cad-'+catsha+'.json'
 oldloader=old['loader'];loader=(parent/oldloader).read_text();loader=once(loader,"new URL('"+PurePosixPath(old['catalog']).name+"',import.meta.url)","new URL('"+PurePosixPath(catname).name+"',import.meta.url)")
 loaderbytes=loader.encode();loadername='assets/desktop/apps-cad-loader-'+digest(loaderbytes)+'.mjs'
 shell=(parent/'shell/desktop-apps.js').read_text();shell=once(shell,'./'+oldloader,'./'+loadername,19)
 registry=registry_source.read_bytes();assert digest(registry)==REGISTRY_SHA
 registry_name='assets/desktop/command-registry.'+REGISTRY_SHA+'.mjs'
 shell=once(shell,"import('./assets/desktop/command-registry.mjs')","import('./"+registry_name+"')")
 app=once((parent/'shell/app.js').read_text(),'CAD Modeler (JSketcher)','CAD Modeler (JSketcher inspired)')
 added={'shell/app.js':app.encode(),'shell/desktop-apps.js':shell.encode(),catname:catbytes,loadername:loaderbytes,registry_name:registry}
 cache=json.loads((parent/'assets/desktop/cache-manifest.json').read_bytes())
 for name,data in added.items():
  if name.startswith(('assets/','storage/')):cache['files'][name]={'sha256':digest(data),'bytes':len(data)}
 for name,metadata in cad['files'].items():cache['files']['assets/desktop/apps/jsketcher/'+bundle+'/'+safe(name)]=metadata
 cache['files']=dict(sorted(cache['files'].items()));cache['id']=digest(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode())
 added['assets/desktop/cache-manifest.json']=(json.dumps(cache,indent=2)+'\n').encode()
 worker=(parent/'assets/desktop/offline-worker.js').read_text().splitlines(keepends=True);assert worker[1].startswith('const RELEASE=')
 worker[1]='const RELEASE='+json.dumps(cache,separators=(',',':'))+';\n';added['assets/desktop/offline-worker.js']=''.join(worker).encode()
 assert set(added)&set(old['files'])==MUTABLE
 out.mkdir()
 try:
  for name in old['files']:
   target=out/safe(name);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(parent/name,target)
  for name in cad['files']:
   target=out/'assets/desktop/apps/jsketcher'/bundle/safe(name);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(cadroot/name,target)
  for name,data in added.items():target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  final=inventory(out);assert len(final)==466
  for name,metadata in old['files'].items():
   if name not in MUTABLE:assert final[name]==metadata,name
  assert all(final[n]==m for n,m in old['files'].items() if n.startswith('assets/desktop/apps/jsketcher/'))
  manifest=copy.deepcopy(old);manifest.update(parent=PARENT,files=final,catalog=catname,catalogSHA256=catsha,loader=loadername,cadSource=SOURCE,cadAppSHA256=APP,cadBundle=bundle,desktopSource=DESKTOP,builderSHA256=record(Path(__file__))['sha256'],changedBaselinePaths=sorted(MUTABLE),policy='Code-only BBC-derived Agent tools delta; no installation or selection authority')
  manifest.pop('shellPatchSHA256',None)
  manifest.update(commandRegistry=registry_name,commandRegistrySHA256=REGISTRY_SHA,commandRegistrySource=REGISTRY_SOURCE)
  manifest['hostGraph']=digest(encode({'parentHostGraph':old['hostGraph'],'storageGraph':old['storageGraph'],'catalog':catsha,'commandRegistry':{registry_name:final[registry_name]},'shell':{name:final['shell/'+name] for name in ('app.js','desktop-apps.js')}}))
  raw=encode(manifest);(out/'manifest.json').write_bytes(raw)
  return {'artifact':digest(raw),'parent':PARENT,'files':len(final),'bytes':sum(m['bytes'] for m in final.values()),'cadBundle':bundle,'catalog':catname,'catalogSHA256':catsha,'loader':loadername,'cache':cache['id'],'commandRegistry':registry_name,'commandRegistrySHA256':REGISTRY_SHA,'changedBaselinePaths':sorted(MUTABLE),'retainedParentPaths':318,'retainedOldCADFiles':145,'unchangedOtherApps':74,'output':str(out)}
 except BaseException:shutil.rmtree(out);raise
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ('baseline','cad-apps','runtime-pins','registry-source','output'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();print(json.dumps(build(a.baseline,a.cad_apps,a.runtime_pins,a.registry_source,a.output),sort_keys=True))
