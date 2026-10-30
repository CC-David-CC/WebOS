#!/usr/bin/env python3
"""Package the account gate and username policy onto the running release."""
import hashlib,importlib.util,json,re,shutil,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/simple-password-profile26-r1';OUT=ROOT/'.build/releases/required-login-profile26-r1';PIN='ed9a25feec34e8f27ee417d32cbfd0c793cdcba5c6ee4c828a26b61a0db53632'
def sha(b):return hashlib.sha256(b).hexdigest()
def enc(v):return (json.dumps(v,indent=2)+'\n').encode()
def key(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def record(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':sha(b)}
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists();stage=Path(tempfile.mkdtemp(prefix='.required-login-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True);changed=set()
 def put(name,raw):
  assert contract.public_name(name);p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);changed.add(name)
 (stage/'origin_service/lifecycle.py').write_bytes((ROOT/'origin_service/lifecycle.py').read_bytes())
 graph=json.loads((BASE/'assets/desktop/network-release.json').read_bytes());previous=graph['coreDirectory'];core={n:(BASE/previous/n).read_bytes() for n in graph['core']};old=core['app.js'].decode();source=(ROOT/'app.js').read_text()
 def replace_once(a,b):
  global old
  assert old.count(a)==1,(a[:80],old.count(a));old=old.replace(a,b)
 replace_once("  for(const field of fields){\n", "  for(const field of fields){\n    if(field.closest?.('.login-gate'))continue;\n")
 replace_once("try{await changeAccount('anonymous');}catch(error){feedback(error.message);}","try{await endSession();}catch(error){feedback(error.message);}")
 start='  showAccountForm(mode,anchor){';end='  async showDeviceStorage(anchor){';replace_once(old[old.index(start):old.index(end)],source[source.index(start):source.index(end)])
 replace_once("      await changeAccount('anonymous');\n      feedback('Server restarted. Linux and local drafts stayed in this tab. Sign in again to use your private server files.');", "      await endSession();")
 replace_once("  const session=await identityModule.beginSession(identityConfig,'anonymous');", "  const session=await requiredLogin();")
 replace_once('  await desktopNetwork.initialize(session,identityConfig);\n',"  await desktopNetwork.initialize(session,identityConfig);\n  document.documentElement.classList.remove('login-required');\n")
 gate=source[source.index('function requiredLogin(){'):source.index('async function changeAccount(')];replace_once('async function changeAccount(',gate+'async function changeAccount(')
 replace_once("feedback('Cleared the local session. Creating a new ephemeral user…');", "feedback('Signing out…');")
 core['app.js']=old.encode();graph['core']={n:{'bytes':len(v),'sha256':sha(v)} for n,v in core.items()};newcore=str(Path(previous).parent/key(graph['core']));graph['coreDirectory']=newcore
 for n,raw in core.items():put(newcore+'/'+n,raw)
 put('assets/desktop/network-release.json',enc(graph));html=(BASE/'index.html').read_text();assert html.count('<html lang="en">')==1;html=html.replace('<html lang="en">','<html lang="en" class="login-required">').replace(previous,newcore)
 match=re.search(r'assets/desktop-style-v2-[0-9a-f]{64}\.css',html);assert match;oldcss=match.group();sourcecss=(ROOT/'style.css').read_text();marker='/* The desktop and guest remain inaccessible until an account is verified. */';assert sourcecss.count(marker)==1;css=(BASE/oldcss).read_bytes()+b'\n'+sourcecss[sourcecss.index(marker):].encode();newcss='assets/desktop-style-v2-'+sha(css)+'.css';put(newcss,css);put('index.html',html.replace(oldcss,newcss).encode())
 cache=json.loads((BASE/'assets/desktop/cache-manifest.json').read_bytes());cache['files']={n:record(stage/n) for n in sorted(set(cache['files'])|changed)};cache['id']=key(cache['files']);put('assets/desktop/cache-manifest.json',enc(cache));put('assets/desktop/offline-worker.js',(ROOT/'scripts/templates/device-cache-worker.js').read_text().replace('__PUBLIC_CACHE_MANIFEST__',json.dumps(cache,separators=(',',':'))).encode())
 public=json.loads((BASE/'release.json').read_bytes());public['files']={n:record(stage/n) for n in sorted(set(public['files'])|changed)};(stage/'release.json').write_bytes(enc(public));full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={str(p.relative_to(stage)):record(p) for p in sorted(stage.rglob('*')) if p.is_file() and p.name!='connected-release.json'};(stage/'connected-release.json').write_bytes(enc(full))
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256'],'core':newcore,'stylesheet':newcss}))
finally:
 if stage.exists():shutil.rmtree(stage)
