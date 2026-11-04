#!/usr/bin/env python3
"""Build a beta-derived *test candidate*, not an installer or hosting operator."""
import argparse,difflib,hashlib,json,os,pathlib,shutil,stat
ROOT=pathlib.Path(__file__).resolve().parents[2];SOURCE=ROOT/'active-system'
PINS={'app.js':'6965a2a27da3fa1d3318c0ac845924136ad9a2e09cf9ca2d624d2f94f5441df6','desktop-apps.js':'0d1cbcb4e6b23beb0c6b7eecce8b35244438fb4341c2e325203c739c64118b81','apps.json':'c5b79a365135d73c939c0afdc7a97864ea00ba24379d179d8cca06843644cd22','cache-manifest.json':'18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720','offline-worker.js':'e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c'}
SOURCE_PINS={'app.js':'027734f88b87cc99e23acdda97bac15d596386e8280127fc6afe297c6bd2ba94','desktop-apps.js':'e21a9646fcbec695d1f3237bae1c6dd71a1a7aba23a0f2ce572552d5f40b4444','storage/browser/mirror.mjs':'67962be43d99bd0bb22229fc8f30c309d0637f9440e9903c2a070b6d618fa187','storage/browser/account-context.mjs':'dd19562a1a13e2ac79142b9cb7a2cf0a3cba77ff03fa5407c0ced4e5c6a518e9','storage/browser/verified-content.mjs':'4503fade5803896a036430cba092ec5c90c15ba6cd0d1028c7b4fd0503eccc12','storage/browser/opfs/core.mjs':'90b245475d95570135d4eba2b92717ac90350944e9ee7a5e6d595e275ebd5299','storage/browser/opfs/shared.mjs':'7399a7fe440c202f1d645230654aa86c035ac4adf072452ac718cc44efb44d9d','storage/browser/opfs/store.mjs':'65a74ef7439d530d766595834f70334bcfbe01d3fb31a9d906948a88cb334faf','storage/browser/opfs/worker.mjs':'9d97301fb4e9e20173bc0c2f57aa2e23c479b5dac0b2b193b76d0716fef7ca1e','storage/browser/opfs/LICENSE.txt':'2153bd2978793748fbe0eb8f838ae2ae19f03f9d4ee5473dd1628a0c0790e4ab'}
STORAGE=('mirror.mjs','account-context.mjs','verified-content.mjs','opfs/core.mjs','opfs/shared.mjs','opfs/store.mjs','opfs/worker.mjs','opfs/LICENSE.txt')
def digest(x):return hashlib.sha256(x).hexdigest()
def encoded(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def readfile(p):
 p=pathlib.Path(p)
 if p.is_symlink() or not p.is_file():raise ValueError('Non-regular input: '+str(p))
 return p.read_bytes()
def replace_one(s,old,new):
 if s.count(old)!=1:raise ValueError('Expected unique beta/source boundary: '+old[:100])
 return s.replace(old,new,1)
def section(s,a,b):
 if s.count(a)!=1 or s.count(b)!=1:raise ValueError('Ambiguous section: '+a)
 return s[s.index(a):s.index(b)]
def main(base,bundle,out):
 base,bundle,out=map(pathlib.Path,(base,bundle,out))
 if out.exists() or out.is_symlink():raise ValueError('Fresh output directory required')
 inputs={n:readfile(base/n) for n in PINS}
 for n,pin in PINS.items():
  if digest(inputs[n])!=pin:raise ValueError('Beta baseline pin mismatch: '+n)
 for n,pin in SOURCE_PINS.items():
  if digest(readfile(SOURCE/n))!=pin:raise ValueError('Source pin mismatch: '+n)
 source={n:readfile(SOURCE/'storage/browser'/n) for n in STORAGE};graph=digest(encoded({n:{'bytes':len(v),'sha256':digest(v)} for n,v in sorted(source.items())}));graphpath='storage/browser/releases/'+graph+'/'
 original_desktop=inputs['desktop-apps.js'].decode();desired_desktop=(SOURCE/'desktop-apps.js').read_text();a='// One account-bound mirror for all desktop apps.';b='// The v86 home is an in-memory 9p filesystem.'
 replacement=section(desired_desktop,a,b).replace("'./storage/browser/mirror.mjs'",repr('./'+graphpath+'mirror.mjs')).replace("'./storage/browser/account-context.mjs'",repr('./'+graphpath+'account-context.mjs'))
 desktop=replace_one(original_desktop,section(original_desktop,a,b),replacement)
 desktop=replace_one(desktop,"  const view=win.appView;win.appView=null;view?.dispose(reason);","  const view=win.appView;win.appView=null;return view?.dispose(reason)||[];")
 original_app=inputs['app.js'].decode();desired_app=(SOURCE/'app.js').read_text();app=replace_one(original_app,section(original_app,'async function changeAccount(', 'async function maintainIdentity('),section(desired_app,'async function changeAccount(', 'async function maintainIdentity('))
 # The new lifecycle section also depends on the candidate's dirty-state helper.
 helper=section(desired_app,'function windowHasChanges(', '\nclass Desktop') if '\nclass Desktop' in desired_app else None
 if helper is None or '\n' in helper.strip():raise ValueError('Unexpected dirty helper boundary')
 lifecycle=section(desired_app,'function disposeSessionView(', 'let bootRecovery=')
 app=replace_one(app,section(original_app,'async function endSession(', 'let bootRecovery='),helper+'\n'+lifecycle)
 catalog=json.loads(inputs['apps.json']);built=json.loads(readfile(bundle/'apps.json'));entries=built['apps'];
 if len(entries)!=1 or entries[0]['id']!='files' or entries[0]['bundleSHA256']!='12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244' or entries[0]['sha256']!='684bfe19edaf7cce3de3986c87d95cd1e05f6b4b76976218359934137d6d17cb':raise ValueError('Pinned Files-only build required')
 if digest(json.dumps(entries[0]['files'],ensure_ascii=False,separators=(',',':')).encode())!=entries[0]['bundleSHA256']:raise ValueError('Files bundle inventory hash mismatch')
 old=catalog['apps'];matches=[i for i,x in enumerate(old) if x['id']=='files'];
 if len(matches)!=1:raise ValueError('Expected one beta Files entry')
 old[matches[0]]=entries[0];catalog_bytes=(json.dumps(catalog,indent=2)+'\n').encode();files={graphpath+n:v for n,v in source.items()}
 files.update({'shell/app.js':app.encode(),'shell/desktop-apps.js':desktop.encode(),'assets/desktop/apps.json':catalog_bytes,'config/fileStorage.json':encoded({'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2})})
 for rel,record in entries[0]['files'].items():
  r=pathlib.PurePosixPath(rel)
  if r.is_absolute() or not r.parts or any(x in ('..','.') for x in r.parts):raise ValueError('Unsafe bundle path')
  path='assets/desktop/apps/files/'+entries[0]['bundleSHA256']+'/'+rel;value=readfile(bundle/'apps/files'/entries[0]['bundleSHA256']/rel)
  if len(value)!=record['bytes'] or digest(value)!=record['sha256']:raise ValueError('Files bundle mismatch: '+rel)
  files[path]=value
 cache=json.loads(inputs['cache-manifest.json']);cache['files']['assets/desktop/apps.json']={'bytes':len(catalog_bytes),'sha256':digest(catalog_bytes)}
 for n,v in files.items():
  if n.startswith('assets/desktop/apps/files/'):cache['files'][n]={'bytes':len(v),'sha256':digest(v)}
 cache['files']=dict(sorted(cache['files'].items()));cache['id']=digest(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode());files['assets/desktop/cache-manifest.json']=(json.dumps(cache,indent=2)+'\n').encode()
 oldworker=inputs['offline-worker.js'].decode();prefix,marker,tail=oldworker.partition('const RELEASE=');old_release,sep,suffix=tail.partition('\nconst SCOPE=')
 if not marker or not sep or not old_release.endswith(';'):raise ValueError('Unexpected beta worker template')
 files['assets/desktop/offline-worker.js']=(prefix+'const RELEASE='+json.dumps(cache,separators=(',',':'))+';\nconst SCOPE='+suffix).encode()
 files['patches/app.diff']=''.join(difflib.unified_diff(original_app.splitlines(True),app.splitlines(True),fromfile='beta/app.js',tofile='candidate/app.js')).encode()
 files['patches/desktop-apps.diff']=''.join(difflib.unified_diff(original_desktop.splitlines(True),desktop.splitlines(True),fromfile='beta/desktop-apps.js',tofile='candidate/desktop-apps.js')).encode()
 manifest={'version':'codi-beta-opfs-candidate/1','sourceCommit':'6db06c6c3','baseline':PINS,'storageGraph':graph,'files':{n:{'bytes':len(v),'sha256':digest(v)} for n,v in sorted(files.items())},'routeIntent':{'/app.js?simplified=1':'shell/app.js','/desktop-apps.js?simplified=1':'shell/desktop-apps.js','configFragment':'config/fileStorage.json'},'notDeployable':True}
 out.mkdir(parents=True); 
 for n,v in files.items():
  p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
 data=encoded(manifest);(out/'manifest.json').write_bytes(data);print(json.dumps({'manifest':digest(data),'graph':graph,'files':len(files),'cache':cache['id']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--files-bundle',required=True);p.add_argument('--out',required=True);a=p.parse_args();main(a.baseline,a.files_bundle,a.out)
