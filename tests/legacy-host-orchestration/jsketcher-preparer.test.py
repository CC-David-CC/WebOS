import importlib.util,tempfile,json,os,subprocess,hashlib,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('p',str(Path(__file__).resolve().parents[1]/'apps/system/jsketcher/prepare.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def run(*a,cwd):subprocess.run(a,cwd=cwd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
with tempfile.TemporaryDirectory() as td:
 root=Path(td);repo=root/'fork';engine=root/'engine';numeric=root/'numeric';repo.mkdir();engine.mkdir();numeric.mkdir()
 for r in (repo,engine,numeric):
  run('git','init','-q',cwd=r);run('git','config','user.name','test',cwd=r);run('git','config','user.email','test@example.org',cwd=r)
 (repo/'LICENSE').write_text('test license');(repo/'package-lock.json').write_text('{}');run('git','add','.',cwd=repo);run('git','commit','-qm','fixture',cwd=repo)
 (engine/'README.md').write_text('engine source');run('git','add','.',cwd=engine);run('git','commit','-qm','fixture',cwd=engine)
 (numeric/'src').mkdir();(numeric/'resources').mkdir();(numeric/'license.txt').write_text('numeric license');(numeric/'resources/LICENSE.quadprog').write_text('quadprog license')
 for name,content in [('numeric.js','a'),('seedrandom.js','b'),('quadprog.js','c'),('svd.js','d')]:(numeric/'src'/name).write_text(content)
 run('git','add','.',cwd=numeric);run('git','commit','-qm','fixture',cwd=numeric)
 m.NUMERIC_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=numeric,text=True).strip();m.NUMERIC_INPUT_SHA256=hashlib.sha256(b'abcd').hexdigest();m.NUMERIC_NOTICE_SHA256={k:hashlib.sha256((numeric/k).read_bytes()).hexdigest() for k in ['license.txt','resources/LICENSE.quadprog']}
 m.FORK_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip();m.ENGINE_COMMIT=subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine,text=True).strip();m.ENGINE_SHA256={n:hashlib.sha256(v.encode()).hexdigest() for n,v in [('occt.wasm','wasm'),('occt.js','js')]}
 tools=root/'bin';tools.mkdir();npm=tools/'npm';npm.write_text('''#!/usr/bin/env python3
import sys,pathlib,shutil
from pathlib import Path
if sys.argv[1:]==['--version']:print('0.test');sys.exit(0)
if sys.argv[1]=='ci':
 d=Path('node_modules/jsketcher-occ-engine');d.mkdir(parents=True);(d/'occt.wasm').write_text('wasm');(d/'occt.js').write_text('js');(d/'license.md').write_text('exception');(d/'LICENSE_LGPL_21.txt').write_text('lgpl');(d/'opencascade-info.txt').write_text('info');(d/'package.json').write_text('{"name":"jsketcher-occ-engine","version":"1","license":"test"}')
 n=Path('node_modules/numeric');n.mkdir();(n/'numeric-1.2.6.js').write_text('abcd');(n/'package.json').write_text('{\"name\":\"numeric\",\"version\":\"1.2.6\"}');a=Path('node_modules/alpha');a.mkdir();(a/'package.json').write_text('{"name":"alpha","version":"1","license":"MIT"}');(a/'LICENSE-MIT').write_text('license')
elif sys.argv[1]=='run':
 d=Path('dist');(d/'static').mkdir(parents=True);(d/'index-webos.html').write_text('fixture');(d/'static/index.bundle.js').write_text('/***/ "./node_modules/alpha/index.js":');e=d/'lib-assets/jsketcher-occ-engine';e.mkdir(parents=True);shutil.copyfile('node_modules/jsketcher-occ-engine/occt.wasm',e/'occt.wasm');shutil.copyfile('node_modules/jsketcher-occ-engine/occt.js',e/'occt.js')
''');npm.chmod(0o755);node=tools/'node';node.write_text('#!/bin/sh\necho v0.fixture\n');node.chmod(0o755)
 oldpath=os.environ['PATH'];os.environ['PATH']=str(tools)+os.pathsep+oldpath
 m.HERE=root/'output';m.HERE.mkdir();m.DESTINATION=m.HERE/'node_modules'/'jsketcher-build';m.PREFIX='node_modules/jsketcher-build/'
 def build():sys.argv=['prepare.py','--repo',str(repo),'--engine-repo',str(engine),'--numeric-repo',str(numeric),'--experimental-local-only','--update-manifest'];m.main()
 build();r1=(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();man=(m.HERE/'app.json').read_bytes();build();assert r1==(m.DESTINATION/'BUILD-RECEIPT.json').read_bytes();assert man==(m.HERE/'app.json').read_bytes()
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
print('PASS repeated mock packaging identical, atomic swap rollback, and unmarked-directory refusal')
