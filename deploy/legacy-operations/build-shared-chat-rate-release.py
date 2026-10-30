#!/usr/bin/env python3
"""Seal the fast-poll release with bounded shared official authorization."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/fast-poll-r1';OUT=ROOT/'.build/releases/shared-chat-rate-r1';PIN='21edb52f13f882880e8d878f4d21c7acadf39cb48d9b8565105a5619b5370664'
spec=importlib.util.spec_from_file_location('contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
assert contract.verify(BASE)['manifestSHA256']==PIN and not OUT.exists()
stage=Path(tempfile.mkdtemp(prefix='.shared-chat-rate-',dir=OUT.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True)
 for name in ('codiserver-server-v0.3.0/codiauth/service.py','origin_service/official_authority.py'):shutil.copyfile(ROOT/name,stage/name)
 full=json.loads((BASE/'connected-release.json').read_bytes());full['files']={}
 for p in sorted(stage.rglob('*')):
  if p.is_file() and p.name!='connected-release.json':
   raw=p.read_bytes();full['files'][str(p.relative_to(stage))]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
 (stage/'connected-release.json').write_text(json.dumps(full,indent=2)+'\n')
 for p in (stage,*stage.rglob('*')):p.chmod(0o755 if p.is_dir() else 0o644)
 result=contract.verify(stage);stage.rename(OUT);print(json.dumps({'status':'PASS','manifestSHA256':result['manifestSHA256']}))
finally:
 if stage.exists():shutil.rmtree(stage)
