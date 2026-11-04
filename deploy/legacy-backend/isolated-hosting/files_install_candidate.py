#!/usr/bin/env python3
"""Review-only installer primitives. No production entrypoint or host invocation.

Caller must hold and recheck the existing protected hosting flock throughout.
This module is not yet qualified to install on a live host.
"""
import hashlib, json, os, stat, tempfile
from pathlib import Path

MANIFEST='ce18b7794adc247218cd99a85b44c0df27e224690a9709cdf9bd6a9d4da7f322'
OLD='e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c'
NEW='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'

def digest(data): return hashlib.sha256(data).hexdigest()
def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
 try: os.fsync(fd)
 finally: os.close(fd)

def no_acl(p):
 # Conservative: reject extended access or inherited ACLs rather than trying to
 # determine whether an ACL's named user happens to be trusted.
 for name in ('system.posix_acl_access','system.posix_acl_default'):
  try: os.getxattr(p,name,follow_symlinks=False)
  except OSError as e:
   if e.errno not in (61,95): raise
  else: raise ValueError('extended ACL forbidden: '+str(p))

def root_path(p, directory=False):
 p=Path(p)
 if not p.is_absolute() or '..' in p.parts: raise ValueError('absolute path required')
 for x in (p,*p.parents):
  s=x.lstat()
  if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022: raise ValueError('unsafe root custody: '+str(x))
  no_acl(x)
 if directory and not p.is_dir(): raise ValueError('directory required')

def read_file(p,limit=8*1024*1024,root_owned=True):
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_size>limit or (root_owned and (s.st_uid!=0 or s.st_mode&0o022)): raise ValueError('unsafe input: '+str(p))
  data=b''
  while len(data)<s.st_size:
   b=os.read(fd,min(65536,s.st_size-len(data)))
   if not b: raise ValueError('short read')
   data+=b
  t=os.fstat(fd)
  if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns): raise ValueError('input changed')
  no_acl(p)
  return data
 finally: os.close(fd)

def atomic(path,data,mode=0o600,uid=0,gid=0):
 path=Path(path);fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  os.fchown(fd,uid,gid);os.fchmod(fd,mode)
  with os.fdopen(fd,'wb') as f: f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(name,path);syncdir(path.parent)
 finally:
  if os.path.exists(name): os.unlink(name)

def stage(source,manifest_file,destination,check_lock):
 """Publish exact verified bundle once; caller supplies trusted lock checker."""
 source=Path(source);destination=Path(destination);root_path(source,True);root_path(manifest_file);root_path(destination.parent,True);check_lock()
 raw=read_file(manifest_file)
 if digest(raw)!=MANIFEST: raise ValueError('manifest pin mismatch')
 entries=json.loads(raw)
 if not isinstance(entries,dict) or not entries: raise ValueError('bad manifest')
 if destination.exists() or destination.is_symlink(): raise ValueError('generation already exists')
 stage_dir=Path(tempfile.mkdtemp(prefix='.files-stage-',dir=destination.parent))
 try:
  for name,pin in entries.items():
   relative=Path(name)
   if relative.is_absolute() or '..' in relative.parts or len(relative.parts)>2: raise ValueError('invalid path')
   inp=source/relative;root_path(inp);data=read_file(inp)
   if digest(data)!=pin: raise ValueError('source pin mismatch: '+name)
   out=stage_dir/relative;out.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
   fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
   with os.fdopen(fd,'wb') as f: f.write(data);f.flush();os.fsync(f.fileno())
  syncdir(stage_dir/'ops');syncdir(stage_dir);check_lock()
  # renameat2 NOREPLACE is required: ordinary rename can overwrite an empty
  # directory. This primitive intentionally refuses without platform support.
  import ctypes
  libc=ctypes.CDLL(None,use_errno=True);result=libc.renameat2(-100,os.fsencode(stage_dir),-100,os.fsencode(destination),1)
  if result: raise OSError(ctypes.get_errno(),'renameat2 NOREPLACE failed')
  syncdir(destination.parent)
 except BaseException:
  # A crash can leave this unselected stage behind; never publish it as valid.
  # Cleanup is deliberately a separate reviewed action.
  raise

def guard_install(*,target,guard,old_source,journal,floor,check_lock):
 """Forward-only recovery: an exact prepared journal completes guard install.

 The hosting parent and target owner/custody must additionally be checked by the
 caller using the existing beta_files_preflight.protected_ancestors verifier.
 Never call this primitive without those checks and the same host flock.
 """
 target=Path(target);guard=Path(guard);old_source=Path(old_source);journal=Path(journal);floor=Path(floor)
 check_lock();root_path(guard);root_path(old_source);root_path(journal.parent,True)
 if floor.exists() or floor.is_symlink(): raise ValueError('floor already exists')
 new=read_file(guard);old=read_file(old_source)
 if digest(new)!=NEW or digest(old)!=OLD: raise ValueError('source pin mismatch')
 before=target.lstat()
 if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_mode&0o022: raise ValueError('unsafe target')
 actual=digest(read_file(target,root_owned=False))
 expected={'version':1,'old':OLD,'new':NEW,'uid':before.st_uid,'gid':before.st_gid,'mode':stat.S_IMODE(before.st_mode)}
 if journal.exists() or journal.is_symlink():
  root_path(journal);stored=json.loads(read_file(journal));
  if stored!=expected: raise ValueError('journal or target metadata drift')
 else:
  if actual!=OLD: raise ValueError('unexpected initial guard')
  atomic(journal,json.dumps(expected,sort_keys=True).encode());check_lock()
 if actual not in (OLD,NEW): raise ValueError('guard drift')
 if actual==OLD:
  if floor.exists() or floor.is_symlink(): raise ValueError('floor appeared')
  check_lock();atomic(target,new,expected['mode'],expected['uid'],expected['gid'])
 if digest(read_file(target,root_owned=False))!=NEW: raise ValueError('guard verify failed')
 check_lock();journal.unlink();syncdir(journal.parent)
