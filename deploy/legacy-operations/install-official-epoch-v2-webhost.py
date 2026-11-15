#!/usr/bin/env python3
"""Install one verified official-service package under the managed hosting lock."""
import fcntl,hashlib,json,os,pathlib,shutil,stat,subprocess,tempfile,time
P=pathlib.Path;source=P('/tmp/codi-official-epoch-lLWMB4UP');dest=P('/srv/codi-connected/official-service-test');backup=P('/srv/codi-connected/official-service-pre-epoch-v2-r1');lock=P('/home/dflanag3/webhost-sites/.controller.lock');old='aca9cba6d4975ff38972a83a1bfeea5112b5651e1121084cb7321398545e4855';new='d7355c2e48090964459a36d4220f34cb6ee5235b2236ad1ee39607c6e62b8a84';digest=lambda b:hashlib.sha256(b).hexdigest()
def check(root,pin):
 assert root.is_dir() and not root.is_symlink();raw=(root/'official-service.json').read_bytes();assert digest(raw)==pin;manifest=json.loads(raw);assert manifest['version']=='codi-official-service/1';expected=set(manifest['files'])|{'official-service.json'};assert {str(p.relative_to(root)) for p in root.rglob('*') if not p.is_dir()}==expected
 for name,rec in manifest['files'].items():
  p=root/name;assert not P(name).is_absolute() and '..' not in P(name).parts and not p.is_symlink();st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size==rec['bytes'] and digest(p.read_bytes())==rec['sha256']
 return manifest
assert os.geteuid()==0 and not backup.exists() and lock.is_file();check(source,new);check(dest,old)
with lock.open('r+') as lf:
 fcntl.flock(lf,fcntl.LOCK_EX|fcntl.LOCK_NB);check(dest,old);assert subprocess.run(['systemctl','is-active','--quiet','codi-official.service']).returncode==0
 stage=P(tempfile.mkdtemp(prefix='.official-epoch-',dir=dest.parent));moved=False
 try:
  shutil.copytree(source,stage,dirs_exist_ok=True)
  for path in [stage,*stage.rglob('*')]:path.chmod(0o755 if path.is_dir() else 0o644)
  check(stage,new);subprocess.run(['systemctl','stop','codi-official.service'],check=True,timeout=30);os.rename(dest,backup);moved=True;os.rename(stage,dest);subprocess.run(['systemctl','start','codi-official.service'],check=True,timeout=30);time.sleep(1);subprocess.run(['systemctl','is-active','--quiet','codi-official.service'],check=True,timeout=10);check(dest,new)
 except BaseException:
  subprocess.run(['systemctl','stop','codi-official.service'],check=False,timeout=30)
  if moved:
   if dest.exists():shutil.rmtree(dest)
   os.rename(backup,dest);subprocess.run(['systemctl','start','codi-official.service'],check=True,timeout=30)
  raise
 finally:
  if stage.exists():shutil.rmtree(stage)
print(json.dumps({'status':'PASS','manifestSHA256':new,'rollback':str(backup),'service':'codi-official.service'}))
