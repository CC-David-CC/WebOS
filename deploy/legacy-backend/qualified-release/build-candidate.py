#!/usr/bin/env python3
"""Research-only 0965 main no-game candidate; never installs or activates."""
import argparse,hashlib,json,os,re,shutil,tempfile
from pathlib import Path
BASE='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020'
APP='6965a2a27da3fa1d3318c0ac845924136ad9a2e09cf9ca2d624d2f94f5441df6'
LOADER='a23f99dc96dfe9cca9212eebfef666f38460b5fbc46671a447f89d4c09189ae2'
CAT='c5b79a365135d73c939c0afdc7a97864ea00ba24379d179d8cca06843644cd22'
CACHE='18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720'
WORKER='e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c'
BLOCK=set('falling-blocks owl-companion physics-playground snake-garden chess-study clockwork-quest clockwork-room crystal-defense drone-circuit expression-puppet garden-defense gravity-pinball kinetic-relay lantern-leap marble-works memory-garden orbital-courier pocket-golf pocket-rally reactive-control-desk rhythm-garden sky-courier sling-targets solitaire stack-balance story-cards tabletop-bot-arena target-garden microduck'.split())
ADMITTED={'files','text','terminal','calculator','help','codemirror'}
UI_ADMITTED=ADMITTED-{'codemirror'}
SPECIAL={'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
def hashfile(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
def encode(v):return json.dumps(v,separators=(',',':'),ensure_ascii=True).encode()
def replace_one(s,a,b):
 if s.count(a)!=1:raise ValueError('Expected exactly one source anchor: '+a[:75])
 return s.replace(a,b)
def validate(base):
 if base.is_symlink() or not base.is_dir():raise ValueError('Invalid baseline')
 for path,pin in [('app.js',APP),('desktop-apps.js',LOADER),('assets/desktop/apps.json',CAT),('assets/desktop/cache-manifest.json',CACHE),('assets/desktop/offline-worker.js',WORKER)]:
  if hashfile(base/path)!=pin:raise ValueError('Baseline mismatch '+path)
 cache=json.loads((base/'assets/desktop/cache-manifest.json').read_bytes())
 if cache['version']!='codi-public-cache/1' or cache['id']!=BASE or hashlib.sha256(json.dumps(cache['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=BASE:raise ValueError('Cache identity mismatch')
 actual={}
 for p in base.rglob('*'):
  if p.is_symlink() or not(p.is_dir() or p.is_file()):raise ValueError('Nonregular baseline')
  if p.is_file():actual[p.relative_to(base).as_posix()]=p
 if set(actual)!=set(cache['files'])|SPECIAL:raise ValueError('Baseline inventory mismatch')
 for name,rec in cache['files'].items():
  p=actual[name]
  if p.stat().st_size!=rec['bytes'] or hashfile(p)!=rec['sha256']:raise ValueError('Baseline content changed '+name)
 return cache
def run(base,out):
 base=Path(base).absolute();out=Path(out).absolute()
 if out.exists() or out.is_symlink() or base==out or base in out.parents or not out.parent.is_dir():raise ValueError('Distinct nonexisting output required')
 cache=validate(base);catalog=json.loads((base/'assets/desktop/apps.json').read_bytes());ids=[a['id'] for a in catalog['apps']]
 if len(ids)!=len(set(ids)) or not (BLOCK|ADMITTED).issubset(ids):raise ValueError('Expected catalog differs')
 removed=set(ids)-ADMITTED
 app=(base/'app.js').read_text();loader=(base/'desktop-apps.js').read_text();worker=(base/'assets/desktop/offline-worker.js').read_text()
 menuStart=app.index('const desktopMenu=[');menuEnd=app.index('// Presentation only:',menuStart)
 menu="""const desktopMenu=[
  {name:'Office',icon:'text',children:[{name:'Text Editor',icon:'text'}]},
  {name:'System Tools',icon:'help',children:[{name:'Terminal',icon:reference.icons.terminal},{name:'Files',icon:reference.icons.files},{name:'Calculator',icon:'calculator'},{name:'Voice input',icon:'microphone',action:()=>voiceControl?.toggle()},{name:'Keyboard lock',icon:'keyboard',action:()=>{setScreenKeyboardEnabled(!onScreenKeyboardEnabled);feedback(onScreenKeyboardEnabled?'On-screen keyboard enabled':'On-screen keyboard locked');}}]},
  {separator:true},{name:'Help',icon:'help'},{name:'End session',icon:'end-session'}
];
"""
 app=app[:menuStart]+menu+app[menuEnd:]
 guard='const mainAdmittedApps=new Set('+json.dumps(sorted(UI_ADMITTED),separators=(',',':'))+');\nconst mainAppAdmitted=id=>mainAdmittedApps.has(id);\n'
 app=replace_one(app,"const reference = window.CODI_REFERENCE;", "const reference = window.CODI_REFERENCE;\n"+guard)
 app=replace_one(app,"    const apps=accountApplications();\n    return apps.length?[{name:'YOUR APP HERE',icon:'prototype-canvas',children:apps.map(entry=>({name:entry.name,icon:entry.icon,action:()=>this.launch(entry.id)}))},...desktopMenu]:desktopMenu;","    return desktopMenu;")
 app=replace_one(app,'  launch(app,title) {',"  launch(app,title) {\n    if(!mainAppAdmitted(app)){feedback('This app is available on beta.ksu.codes.');return null;}")
 app=replace_one(app,'  open(app,context){',"  open(app,context){\n    if(!mainAppAdmitted(app))throw Error('This app is available on beta.ksu.codes.');")
 app=replace_one(app,'if(!v||!allowed.has(v.app)||', 'if(!v||!allowed.has(v.app)||!mainAppAdmitted(v.app)||')
 app=replace_one(app,"return JSON.stringify(['codi-window-layout/1',identityConfig?.identity?.issuer||location.origin,owner]);","return JSON.stringify(['codi-main-core-window-layout/1',identityConfig?.identity?.issuer||location.origin,owner]);")
 app=replace_one(app,"const raw=localStorage.getItem(this.layoutKey(owner));","const raw=localStorage.getItem(this.layoutKey(owner))??localStorage.getItem(JSON.stringify(['codi-window-layout/1',identityConfig?.identity?.issuer||location.origin,owner]));")
 old="if(/\\.game\\.json$/i.test(path)){void openSavedGameDocument(desktop,owner,path);return;}";new="if(/\\.game\\.json$/i.test(path)||/\\.brf$/i.test(path)){feedback('Open this project on beta.ksu.codes.');return;}"
 loader=replace_one(loader,old,new);loader=replace_one(loader,"const app=/\\.brf$/i.test(path)?'microduck':",'const app=');loader=replace_one(loader,":'text';desktop.open(app,Object.freeze({version:1,storage:'mirror',path,owner}));}",":'text';if(!mainAppAdmitted(app)){feedback('Open this project on beta.ksu.codes.');return;}desktop.open(app,Object.freeze({version:1,storage:'mirror',path,owner}));}")
 catalog['apps']=[a for a in catalog['apps'] if a['id'] in ADMITTED]
 # Links are safe only because every modified file is replaced atomically, never opened for writing.
 shutil.copytree(base,out,copy_function=os.link,symlinks=False)
 def put(path,data):
  p=out/path;fd,tmp=tempfile.mkstemp(prefix='.candidate-',dir=p.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(data)
   os.chmod(tmp,0o644);os.replace(tmp,p)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 try:
  put('app.js',app.encode());put('desktop-apps.js',loader.encode());put('assets/desktop/apps.json',encode(catalog))
  for id in removed:shutil.rmtree(out/'assets/desktop/apps'/id)
  files={}
  for name,oldrec in cache['files'].items():
   if name.startswith('assets/desktop/apps/') and name.split('/')[3] in removed:continue
   p=out/name;files[name]={'bytes':p.stat().st_size,'sha256':hashfile(p)}
  new={'version':'codi-public-cache/1','id':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'files':files}
  put('assets/desktop/cache-manifest.json',encode(new))
  lines=worker.splitlines(keepends=True)
  if len(lines)<2 or not lines[1].startswith('const RELEASE='):raise ValueError('Unexpected worker format')
  lines[1]='const RELEASE='+encode(new).decode()+';\n';put('assets/desktop/offline-worker.js',''.join(lines).encode())
  actual={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}
  if actual!=set(files)|SPECIAL:raise ValueError('Candidate inventory mismatch')
  validate(base)
  print(json.dumps({'baseline':BASE,'candidate':new['id'],'appsRemoved':len(removed),'appsRemaining':len(catalog['apps']),'files':len(files),'appSHA256':hashfile(out/'app.js'),'loaderSHA256':hashfile(out/'desktop-apps.js'),'catalogSHA256':hashfile(out/'assets/desktop/apps.json'),'cacheSHA256':hashfile(out/'assets/desktop/cache-manifest.json'),'workerSHA256':hashfile(out/'assets/desktop/offline-worker.js')}))
 except BaseException:shutil.rmtree(out);raise
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('output');a=p.parse_args();run(a.baseline,a.output)
