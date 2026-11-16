#!/usr/bin/env python3
"""Review candidate only. Fixed host paths; no production use before review.

Invoke as root with the protected venv and -I -B. Does not activate services.
"""
import argparse,hashlib,os,pwd,socket,stat,sys,types
from pathlib import Path

INPUT=Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472')
BUNDLE=Path('/srv/codi-connected/operators/files-bundle-ce18b7794adc2472')
HOST=Path('/home/dflanag3/webhost-sites')
STATE=Path('/var/lib/webhost-ops')
HELPER='4c09350ea824e09a5596f70bdda1303b30242a2f6ccac5238314e1fcc107dd51'
HOST_MODULE='9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95'
PREFLIGHT='4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff'

def bootstrap(path,pin):
 # Bootstrap must not import any ambient or unverified Python code.
 for x in (path,*path.parents):
  s=x.lstat()
  if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022: raise ValueError('unsafe bootstrap custody')
  for name in ('system.posix_acl_access','system.posix_acl_default'):
   try: os.getxattr(x,name,follow_symlinks=False)
   except OSError as e:
    if e.errno not in (61,95): raise
   else: raise ValueError('bootstrap ACL')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>8*1024*1024: raise ValueError('unsafe bootstrap file')
  raw=b''
  while len(raw)<s.st_size:
   part=os.read(fd,min(65536,s.st_size-len(raw)))
   if not part: raise ValueError('short bootstrap file')
   raw+=part
  t=os.fstat(fd)
  if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns): raise ValueError('bootstrap changed')
 finally: os.close(fd)
 if hashlib.sha256(raw).hexdigest()!=pin: raise ValueError('bootstrap hash mismatch')
 module=types.ModuleType(path.stem);module.__file__=str(path);sys.modules[path.stem]=module;exec(compile(raw,str(path),'exec'),module.__dict__);return module

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=('plan','install','recover'));args=parser.parse_args()
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost': raise ValueError('root on box-webhost required')
 if Path(__file__).absolute()!=INPUT/'ops/files_install_launch.py': raise ValueError('wrong entrypoint path')
 # Root custody of this script is checked independently of its content pin;
 # installation of this reviewed bootstrap is a separate explicit prerequisite.
 for x in (Path(__file__).absolute(),*Path(__file__).absolute().parents):
  st=x.lstat()
  if stat.S_ISLNK(st.st_mode) or st.st_uid!=0 or st.st_mode&0o022: raise ValueError('unsafe entrypoint custody')
  for acl in ('system.posix_acl_access','system.posix_acl_default'):
   try: os.getxattr(x,acl,follow_symlinks=False)
   except OSError as e:
    if e.errno not in (61,95): raise
   else: raise ValueError('entrypoint ACL')
 helper=bootstrap(INPUT/'ops/files_install_candidate.py',HELPER)
 host=bootstrap(INPUT/'ops/beta_launcher.py',HOST_MODULE)
 pre=bootstrap(INPUT/'ops/beta_files_preflight.py',PREFLIGHT)
 if host.ROOT!=HOST: raise ValueError('hosting path mismatch')
 helper.root_path(INPUT,True);helper.root_path(STATE,True);helper.root_path(BUNDLE.parent,True)
 if stat.S_IMODE(STATE.stat().st_mode)!=0o700: raise ValueError('journal directory must be 0700')
 pre.protected_ancestors(HOST/'ops')
 admin=pwd.getpwnam('dflanag3')
 if (admin.pw_uid,admin.pw_gid)!=(1000,1000): raise ValueError('admin identity changed')
 target=HOST/'ops/webctl.py';lockpath=HOST/'.controller.lock'
 def check_metadata():
  pre.protected_ancestors(HOST/'ops')
  s=target.lstat();helper.no_acl(target)
  if not stat.S_ISREG(s.st_mode) or (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(1000,1000,0o644,1): raise ValueError('controller metadata drift')
  s=lockpath.lstat();helper.no_acl(lockpath)
  if not stat.S_ISREG(s.st_mode) or (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)!=(0,0,0o644,1): raise ValueError('lock metadata drift')
 lock=host.HostLock()
 with lock.held():
  def check(): lock.check();check_metadata()
  check();floor=STATE/'opfs-floor.json';journal=STATE/'files-install-guard.json'
  for name in ('opfs-floor.json','opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json'):
   p=STATE/name
   if p.exists() or p.is_symlink(): raise ValueError('floor or transition exists: '+name)
  manifest=INPUT/'ops/files_install_manifest.json'
  if helper.digest(helper.read_file(manifest))!=helper.MANIFEST: raise ValueError('installer manifest drift')
  target_hash=helper.digest(helper.read_file(target,root_owned=False))
  if target_hash not in (helper.OLD,helper.NEW): raise ValueError('unexpected live controller')
  if BUNDLE.exists() or BUNDLE.is_symlink(): helper.verify_bundle(BUNDLE,manifest,check)
  if args.action=='plan':
   print('pre-floor inputs accepted; bundle present:',BUNDLE.exists(),'guard present:',target_hash==helper.NEW,'journal present:',journal.exists());return
  if not BUNDLE.exists(): helper.stage(INPUT,manifest,BUNDLE,check)
  helper.verify_bundle(BUNDLE,manifest,check)
  if target_hash==helper.NEW and not (journal.exists() or journal.is_symlink()):
   print('verified already installed');return
  if args.action=='recover' and not (journal.exists() or journal.is_symlink()): raise ValueError('no installation journal to recover')
  helper.guard_install(target=target,guard=INPUT/'ops/webctl_floor_candidate.py',old_source=INPUT/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check)
  print('guard and bundle verified; no service or route activated')
if __name__=='__main__': main()
