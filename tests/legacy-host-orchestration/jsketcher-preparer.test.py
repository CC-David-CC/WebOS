import importlib.util,tempfile,json,os,subprocess,hashlib,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('p',str(Path(__file__).resolve().parents[1]/'apps/system/jsketcher/prepare.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def run(*a,cwd):subprocess.run(a,cwd=cwd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with tempfile.TemporaryDirectory() as td:
 root=Path(td);repo=root/'fork';engine=root/'engine';numeric=root/'numeric';repo.mkdir();engine.mkdir();numeric.mkdir()
 for r in (repo,engine,numeric):
  run('git','init','-q',cwd=r);run('git','config','user.name','test',cwd=r);run('git','config','user.email','test@example.org',cwd=r)
 (repo/'LICENSE').write_text('test license');(repo/'package-lock.json').write_text('{}');run('git','add','.',cwd=repo);run('git','commit','-qm','fixture',cwd=repo)
 (engine/'README.md').write_text('engine source');(engine/'occt').mkdir();(engine/'LICENSE').write_text('root terms');(engine/'occt/LICENSE_LGPL_21.txt').write_text('lgpl');(engine/'occt/OCCT_LGPL_EXCEPTION.txt').write_text('exception');run('git','add','.',cwd=engine);run('git','commit','-qm','fixture',cwd=engine)
 (numeric/'src').mkdir();(numeric/'resources').mkdir();(numeric/'license.txt').write_text('numeric license');(numeric/'resources/LICENSE.quadprog').write_text('quadprog license')
 for name,content in [('numeric.js','a'),('seedrandom.js','b'),('quadprog.js','c'),('svd.js','d')]:(numeric/'src'/name).write_text(content)
 run('git','add','.',cwd=numeric);run('git','commit','-qm','fixture',cwd=numeric)
 m.NUMERIC_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=numeric,text=True).strip();m.NUMERIC_INPUT_SHA256=hashlib.sha256(b'abcd').hexdigest();m.NUMERIC_NOTICE_SHA256={k:hashlib.sha256((numeric/k).read_bytes()).hexdigest() for k in ['license.txt','resources/LICENSE.quadprog']}
 m.FORK_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();m.ENGINE_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine,text=True).strip();m.ENGINE_SHA256={n:hashlib.sha256(v.encode()).hexdigest() for n,v in [('occt.wasm','wasm'),('occt.js','js')]}
 m.ENGINE_TREE=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=engine,text=True).strip();m.ENGINE_SOURCE_NOTICES={n:(target,hashlib.sha256((engine/n).read_bytes()).hexdigest()) for n,(target,_) in m.ENGINE_SOURCE_NOTICES.items()}
 manifold=root/'manifold';manifold.mkdir()
 for name,content in [('manifold.js','fixture js'),('manifold.wasm','fixture wasm'),('manifold-source.zip','fixture source'),('clipper2-source.zip','fixture clipper')]: (manifold/name).write_text(content)
 receipt={'manifoldCommit':m.MANIFOLD_COMMIT,'clipperCommit':m.CLIPPER_COMMIT,'jsSha256':hashlib.sha256(b'fixture js').hexdigest(),'wasmSha256':hashlib.sha256(b'fixture wasm').hexdigest(),'flags':['-sDYNAMIC_EXECUTION=0','-sEMBIND_AOT=1']}
 (manifold/'build-receipt.json').write_text(json.dumps(receipt))
 m.MANIFOLD_INPUTS={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in manifold.iterdir()}
 tools=root/'bin';tools.mkdir();npm=tools/'npm';npm.write_text('''#!/usr/bin/env python3
import sys,pathlib,shutil,os
from pathlib import Path
if sys.argv[1:]==['--version']:print('0.test');sys.exit(0)
if sys.argv[1]=='ci':
 d=Path('node_modules/jsketcher-occ-engine');d.mkdir(parents=True);(d/'occt.wasm').write_text('bad' if os.environ.get('CODI_TEST_BAD_NPM') else 'wasm');(d/'occt.js').write_text('js');(d/'license.md').write_text('exception');(d/'LICENSE_LGPL_21.txt').write_text('lgpl');(d/'opencascade-info.txt').write_text('info');(d/'package.json').write_text('{"name":"jsketcher-occ-engine","version":"1","license":"test"}')
 n=Path('node_modules/numeric');n.mkdir();(n/'numeric-1.2.6.js').write_text('abcd');(n/'package.json').write_text('{\"name\":\"numeric\",\"version\":\"1.2.6\"}');a=Path('node_modules/alpha');a.mkdir();(a/'package.json').write_text('{"name":"alpha","version":"1","license":"MIT"}');(a/'LICENSE-MIT').write_text('license')
elif sys.argv[1]=='run':
 d=Path('dist');(d/'static').mkdir(parents=True);(d/'index-webos.html').write_text('fixture');(d/'static/index.bundle.js').write_text('/***/ "./node_modules/alpha/index.js":');e=d/'lib-assets/jsketcher-occ-engine';e.mkdir(parents=True);shutil.copyfile('node_modules/jsketcher-occ-engine/occt.wasm',e/'occt.wasm');shutil.copyfile('node_modules/jsketcher-occ-engine/occt.js',e/'occt.js')
''');npm.chmod(0o755);node=tools/'node';node.write_text('#!/bin/sh\necho v0.fixture\n');node.chmod(0o755)
 oldpath=os.environ['PATH'];os.environ['PATH']=str(tools)+os.pathsep+oldpath
 m.HERE=root/'output';m.HERE.mkdir();m.DESTINATION=m.HERE/'node_modules'/'jsketcher-build';m.PREFIX='node_modules/jsketcher-build/'
 def build(extra=()):sys.argv=['prepare.py','--repo',str(repo),'--engine-repo',str(engine),'--numeric-repo',str(numeric),'--experimental-local-only','--update-manifest','--manifold-research-input',str(manifold),*extra];m.main()
 (manifold/'manifold.js').write_text('tampered')
 try:build();raise AssertionError('tampered Manifold input accepted')
 except RuntimeError as e:assert 'pinned hash' in str(e)
 (manifold/'manifold.js').write_text('fixture js')
 build();r1=(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();man=(m.HERE/'app.json').read_bytes();build();assert r1==(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();assert man==(m.HERE/'app.json').read_bytes()
 research=root/'occt-research';research.mkdir()
 (research/'occt.js').write_text('source js');(research/'occt.wasm').write_text('source wasm')
 source_receipt={'interpreterCommit':m.ENGINE_COMMIT,'interpreterTree':m.ENGINE_TREE,'jsSHA256':hashlib.sha256(b'source js').hexdigest(),'wasmSHA256':hashlib.sha256(b'source wasm').hexdigest(),'npmWasmSHA256':m.ENGINE_SHA256['occt.wasm'],'bitwiseMatchesNpm':False,'independentRebuildsMatch':False,'licenseCleared':False,'localOnly':True}
 (research/'build-receipt.json').write_text(json.dumps(source_receipt))
 m.OCCT_SOURCE_INPUTS={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in research.iterdir()}
 source_args=['--occt-source-research-input',str(research)]
 build(source_args)
 assert (m.DESTINATION/'lib-assets/jsketcher-occ-engine/occt.wasm').read_text()=='source wasm'
 assert (m.DESTINATION/'OCCT-INTERPRETER-LICENSE.txt').read_text()=='root terms'
 assert json.loads((m.DESTINATION/'BUILD-RECEIPT.json').read_text())['occtSourceResearchReceipt']==source_receipt
 for name in ('occt.js','occt.wasm','build-receipt.json'):
  f=research/name; original=f.read_bytes();f.write_bytes(b'tampered')
  try:build(source_args);raise AssertionError('tampered OCCT accepted: '+name)
  except RuntimeError as e:assert 'pinned hash' in str(e)
  finally:f.write_bytes(original)
  assert (m.DESTINATION/'lib-assets/jsketcher-occ-engine/occt.wasm').read_text()=='source wasm'
 f=research/'occt.js';f.unlink();f.symlink_to(research/'occt.wasm')
 try:build(source_args);raise AssertionError('symlinked OCCT accepted')
 except OSError:pass
 f.unlink();f.write_text('source js')
 # The source candidate must never bypass the upstream npm verification.
 os.environ['CODI_TEST_BAD_NPM']='1'
 try:build(source_args);raise AssertionError('bad npm artifact accepted')
 except RuntimeError as e:assert 'artifact hash differs' in str(e)
 finally:del os.environ['CODI_TEST_BAD_NPM']
 build();assert (m.DESTINATION/'lib-assets/jsketcher-occ-engine/occt.wasm').read_text()=='wasm'
 assert json.loads((m.DESTINATION/'BUILD-RECEIPT.json').read_text())['occtSelection']=='npm'
 r1=(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();man=(m.HERE/'app.json').read_bytes()
 old_replace=m.os.replace
 def fail_once(src,dst):
  if Path(src).name.startswith('.jsketcher-next-'):raise OSError('injected swap failure')
  return old_replace(src,dst)
 m.os.replace=fail_once
 try:
  try:build();raise AssertionError('failure was not propagated')
  except OSError as e:assert str(e)=='injected swap failure'
 finally:m.os.replace=old_replace
 assert r1==(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();assert man==(m.HERE/'app.json').read_bytes();assert not list(m.DESTINATION.parent.glob('.jsketcher-old-*'))
 (m.DESTINATION/'PROVENANCE-LOCAL-ONLY.txt').unlink()
 try:build();raise AssertionError('unmarked directory replaced')
 except RuntimeError as e:assert 'not marked' in str(e)
 assert (m.DESTINATION/'index-webos.html').read_text()=='fixture'
print('PASS source/npm selection, tamper rejection, notices, repeat, rollback and unmarked-directory refusal')
