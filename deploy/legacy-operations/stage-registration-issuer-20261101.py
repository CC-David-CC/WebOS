import hashlib,importlib.util,json,os,shutil,socket,tempfile
from pathlib import Path
BASE=Path('/srv/codi-connected/releases/classroom-login-r1');DEST=BASE.parent/'registration-admission-r1';IN=Path('/tmp/codi-reg-input-1101')
PIN='9d4bbe6dfe4f82e2dbb472e4ce8c1a7d0061f4466b4e5533d0b71a8ad8d22533'
FILES={'origin_service/lifecycle.py':('542813fa29ac042a4c4545c1fe152aa9bb85762218ed803382e2d931f766cf64','94ab8e0abf03e4f2e5e28960590ec7d5c426d2488e0b9258ccb0d41dd59e483e'),'origin_service/http_server.py':('6e3ad04a5a78fd3328d787d64e89b76fccafcb4d62071953da73cad91cd244f3','74b1c590f8831e5d01662b2fc8c0ee442c9a950fb05fba7b2d40923a5bb5ed27')}
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(root):
 spec=importlib.util.spec_from_file_location('release_verifier',root/'origin_service/release.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.verify(root)
assert os.geteuid()==0 and socket.gethostname()=='box-webhost'
assert not BASE.is_symlink() and BASE.stat().st_uid==0 and not BASE.stat().st_mode&0o022
assert not DEST.exists() and not DEST.is_symlink() and verify(BASE)['manifestSHA256']==PIN
for name,(old,new) in FILES.items():
 p=IN/Path(name).name
 assert not p.is_symlink() and p.is_file() and sha(p.read_bytes())==new and sha((BASE/name).read_bytes())==old
stage=Path(tempfile.mkdtemp(prefix='.registration-admission-',dir=BASE.parent))
try:
 shutil.copytree(BASE,stage,dirs_exist_ok=True,symlinks=True)
 manifest_path=stage/'connected-release.json';manifest=json.loads(manifest_path.read_text())
 for name,(_,new) in FILES.items():
  raw=(IN/Path(name).name).read_bytes();target=stage/name;assert not target.is_symlink() and target.is_file();target.write_bytes(raw);target.chmod(0o644);manifest['files'][name]={'bytes':len(raw),'sha256':new}
 manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');manifest_path.chmod(0o644);result=verify(stage)
 for p in [stage,*stage.rglob('*')]:
  x=p.lstat();assert x.st_uid==0 and not x.st_mode&0o022
 stage.chmod(0o755);os.rename(stage,DEST);print(json.dumps({'release':str(DEST),'manifestSHA256':result['manifestSHA256'],'changed':list(FILES)}))
finally:
 if stage.exists():shutil.rmtree(stage)
