"""Private writable runtime outside an immutable application release.

This is a development launcher boundary, not isolation between issuer/steward
roles. The parent directory is an operator-owned location; requests cannot choose
it. A held file lock prevents two issuers from sharing one private runtime.
"""
import fcntl,os,shutil,stat,tempfile
from pathlib import Path

def _private_directory(path):
 try:path.mkdir(mode=0o700)
 except FileExistsError:pass
 info=path.lstat()
 if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o700:
  raise ValueError('Runtime directories must be owned, real directories with mode 0700')

def _private_tree(path):
 for parent,dirs,files in os.walk(path,followlinks=False):
  for name in dirs+files:
   entry=Path(parent)/name;info=entry.lstat()
   if info.st_uid!=os.geteuid() or info.st_mode&0o077 or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)) or (stat.S_ISREG(info.st_mode) and info.st_nlink!=1):
    raise ValueError('Runtime state must contain only private owned directories and unlinked regular files')

class PrivateRuntime:
 def __init__(self,directory,source_root):
  self.root=Path(directory);self.source=Path(source_root).resolve();self._lock=None;self._umask=None;self.public=None
  self.state=self.root/'state';self.steward_private=self.root/'steward-private'

 def __enter__(self):
  if not self.root.is_absolute() or '..' in self.root.parts:raise ValueError('Runtime directory must be an absolute path without traversal')
  for path in [self.root,*self.root.parents]:
   if path.is_symlink():raise ValueError('Runtime path must not use symlinks')
   if path!=self.root and path.exists():
    info=path.stat()
    if info.st_mode&0o022 and not (info.st_mode&stat.S_ISVTX and info.st_uid in (0,os.geteuid())):
     raise ValueError('Runtime ancestors must not be writable by other users')
  resolved=self.root.resolve()
  if resolved.is_relative_to(self.source) or self.source.is_relative_to(resolved):raise ValueError('Explicit runtime and application source must be disjoint directory trees')
  try:
   _private_directory(self.root)
   lock=self.root/'.runtime.lock'
   self._lock=os.open(lock,os.O_RDWR|os.O_CREAT|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
   info=os.fstat(self._lock)
   if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.geteuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:
    raise ValueError('Runtime lock must be an owned private regular file')
   try:fcntl.flock(self._lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise ValueError('Runtime is already in use by another launcher') from None
   for path in [self.state,self.steward_private]:_private_directory(path);_private_tree(path)
   self._umask=os.umask(0o077)
   # Each process stages a fresh public tree. Old assets or state cannot carry
   # over into a later release's served directory.
   self.public=Path(tempfile.mkdtemp(prefix='public-',dir=self.root))
   return self
  except OSError:
   self.__exit__(None,None,None);raise ValueError('Private runtime directory unavailable') from None
  except BaseException:
   self.__exit__(None,None,None);raise

 def __exit__(self,*args):
  try:
   if self.public is not None:shutil.rmtree(self.public);self.public=None
  finally:
   if self._umask is not None:os.umask(self._umask);self._umask=None
   # Do not unlink: a new inode would let a second process bypass a held lock.
   if self._lock is not None:os.close(self._lock);self._lock=None
