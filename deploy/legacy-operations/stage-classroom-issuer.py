#!/usr/bin/env python3
"""Stage one verified issuer change from the pinned live release; no activation."""
import hashlib,importlib.util,json,os,shutil,socket,sys,tempfile
from pathlib import Path
BASE=Path('/srv/codi-connected/releases/file-admission-r1')
DEST=BASE.parent/'classroom-login-r1'
PIN='037c6d174937f7f5df2f144e25d305b429a2b628b6b5eb62418ab06b6f111804'
OLD='ceea725509827fb1786944cf3df70cfe0e80acd120135a460bea2ff433ba624c'
NAME='origin_service/lifecycle.py'
def digest(b):return hashlib.sha256(b).hexdigest()
def verifier(root):
 spec=importlib.util.spec_from_file_location('release_verifier',root/'origin_service/release.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
 if len(sys.argv)!=3:raise ValueError('Candidate file and SHA-256 required')
 source=Path(sys.argv[1]);expected=sys.argv[2]
 if source.is_symlink() or not source.is_file() or source.stat().st_size>128*1024:raise ValueError('Invalid input')
 raw=source.read_bytes()
 if digest(raw)!=expected:raise ValueError('Input digest changed')
 if BASE.is_symlink() or BASE.stat().st_uid!=0 or BASE.stat().st_mode&0o022:raise ValueError('Unsafe baseline')
 if DEST.exists() or DEST.is_symlink():raise ValueError('Candidate already exists')
 if verifier(BASE).verify(BASE)['manifestSHA256']!=PIN or digest((BASE/NAME).read_bytes())!=OLD:raise ValueError('Baseline changed')
 stage=Path(tempfile.mkdtemp(prefix='.classroom-login-',dir=BASE.parent))
 try:
  shutil.copytree(BASE,stage,dirs_exist_ok=True,symlinks=True)
  target=stage/NAME
  if target.is_symlink() or not target.is_file():raise ValueError('Unsafe target')
  target.write_bytes(raw);target.chmod(0o644)
  manifest_path=stage/'connected-release.json';manifest=json.loads(manifest_path.read_text());manifest['files'][NAME]={'bytes':len(raw),'sha256':digest(raw)};manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');manifest_path.chmod(0o644)
  result=verifier(stage).verify(stage)
  for path in [stage,*stage.rglob('*')]:
   info=path.lstat()
   if info.st_uid!=0 or info.st_mode&0o022:raise ValueError('Candidate must be root-owned and immutable')
  stage.chmod(0o755);os.rename(stage,DEST)
  print(json.dumps({'status':'staged','release':str(DEST),'manifestSHA256':result['manifestSHA256'],'changed':[NAME]}))
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':sys.dont_write_bytecode=True;main()
