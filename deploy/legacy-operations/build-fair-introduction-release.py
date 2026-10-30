#!/usr/bin/env python3
"""Compose a steward-only account-discovery candidate; never installs it."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/no-page-refresh-profile26-r1';DEST=ROOT/'.build/releases/fair-introduction-profile26-r1';PIN='3c0d71d748d41c4b67be954e8e34b3f8a562aa835d85f829bdb6888170308619';FILES=['steward/leases.py','steward/server.py']
def digest(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
spec=importlib.util.spec_from_file_location('release_contract',BASE/'origin_service/release.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);assert c.verify(BASE)['manifestSHA256']==PIN;assert not DEST.exists();stage=Path(tempfile.mkdtemp(prefix='.steward-candidate-',dir=DEST.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True)
 for n in FILES:
  source=ROOT/n;assert source.is_file() and not source.is_symlink();shutil.copyfile(source,stage/n)
 manifest=json.loads((stage/'connected-release.json').read_bytes());before=manifest['files'].copy()
 for n in FILES:assert digest(stage/n)!=before[n];manifest['files'][n]=digest(stage/n)
 (stage/'connected-release.json').write_text(json.dumps(manifest,indent=2)+'\n')
 for p in [stage,*stage.rglob('*')]:p.chmod(0o755 if p.is_dir() else 0o644)
 receipt=c.verify(stage);after=json.loads((stage/'connected-release.json').read_bytes())['files'];assert {n for n in before if before[n]!=after[n]}==set(FILES);assert (stage/'release.json').read_bytes()==(BASE/'release.json').read_bytes()
 stage.rename(DEST);print(json.dumps({'status':'PASS','directory':str(DEST),'baseSHA256':PIN,'candidate':receipt,'changedFiles':FILES,'publicFilesUnchanged':True,'deployed':False},indent=2))
finally:
 if stage.exists():shutil.rmtree(stage)
