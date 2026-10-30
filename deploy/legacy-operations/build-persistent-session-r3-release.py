#!/usr/bin/env python3
"""Seal the tested issuer session recovery change on the active release."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.build/releases/idle-receipt-r1';OUT=ROOT/'.build/releases/persistent-session-r3'
PIN='1695ec65541333a4826a4725a03b2b8a247b426e7da23cb3a8201bfad122481d'
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists()
stage=Path(tempfile.mkdtemp(prefix='.persistent-session-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True)
 shutil.copyfile(ROOT/'origin_service/lifecycle.py',stage/'origin_service/lifecycle.py')
 full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={}
 for p in sorted(stage.rglob('*')):
  if p.is_file() and p.name!='connected-release.json':
   raw=p.read_bytes();full['files'][str(p.relative_to(stage))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 (stage/'connected-release.json').write_text(json.dumps(full,indent=2)+'\n')
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256']}))
finally:
 if stage.exists():shutil.rmtree(stage)
