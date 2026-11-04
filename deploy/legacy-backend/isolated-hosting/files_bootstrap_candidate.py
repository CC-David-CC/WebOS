#!/usr/bin/env python3
"""Root-custodied public input bootstrap candidate; never imports checkout code.

Fixed paths are deliberate. Review before use; no live installation performed.
"""
import ctypes,errno,grp,hashlib,os,pwd,socket,stat,tempfile
from pathlib import Path
SOURCE=Path('/home/dflanag3/files-bootstrap-source')
DEST=Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472')
SELF=Path('/srv/codi-connected/operators/files-bootstrap-v1.py')
PINS='3fbabe6cd71b8d11e4347c0b8bb4a4d3df89263126a327e1ca368ca87d953667'

def secure(p, source=False):
 p=Path(p)
 if not p.is_absolute() or '..' in p.parts: raise ValueError('absolute path required')
 for x in (p,*p.parents):
  s=x.lstat()
  if stat.S_ISLNK(s.st_mode) or s.st_uid not in ((0,1000) if source else (0,)) or s.st_mode&0o002: raise ValueError('unsafe custody: '+str(x))
  if s.st_mode&0o020:
   members={u.pw_uid for u in pwd.getpwall() if u.pw_gid==s.st_gid}
   members.update(pwd.getpwnam(n).pw_uid for n in grp.getgrgid(s.st_gid).gr_mem)
   if not source or not members<={0,1000}: raise ValueError('untrusted writable group: '+str(x))
  for name in ('system.posix_acl_access','system.posix_acl_default'):
   try: os.getxattr(x,name,follow_symlinks=False)
   except OSError as e:
    if e.errno not in (errno.ENODATA,errno.ENOTSUP): raise
   else: raise ValueError('extended ACL: '+str(x))

def read(p, source=False):
 secure(p,source=source);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid not in ((0,1000) if source else (0,)) or s.st_nlink!=1 or s.st_mode&0o002 or (s.st_mode&0o020 and not source) or s.st_size>8*1024*1024: raise ValueError('unsafe source')
  data=bytearray()
  while len(data)<s.st_size:
   b=os.read(fd,min(65536,s.st_size-len(data)))
   if not b: raise ValueError('short source')
   data.extend(b)
  t=os.fstat(fd)
  if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns): raise ValueError('source changed')
  return bytes(data)
 finally:os.close(fd)

def syncdir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try: os.fsync(fd)
 finally: os.close(fd)

def parse(raw):
 if hashlib.sha256(raw).hexdigest()!=PINS: raise ValueError('pin list mismatch')
 files={}
 for line in raw.decode('ascii').splitlines():
  digest,name=line.split('  ');path=Path(name)
  if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest) or path.is_absolute() or '..' in path.parts or len(path.parts)>2 or name in files: raise ValueError('invalid pin entry')
  files[name]=digest
 if not files: raise ValueError('empty pin list')
 return files

def verify(root,files):
 secure(root);found=set()
 for base,dirs,names in os.walk(root,followlinks=False):
  for n in dirs+names:
   p=Path(base)/n;secure(p);rel=p.relative_to(root).as_posix()
   if p.is_dir():
    if rel!='ops': raise ValueError('unexpected directory')
   elif p.is_file():
    if rel not in files or hashlib.sha256(read(p)).hexdigest()!=files[rel]: raise ValueError('bundle mismatch: '+rel)
    found.add(rel)
   else: raise ValueError('invalid entry')
 if found!=set(files): raise ValueError('incomplete bundle')

def main():
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or Path(__file__).absolute()!=SELF: raise ValueError('wrong host or bootstrap path')
 secure(SELF);secure(SOURCE,source=True);secure(DEST.parent)
 files=parse(read(SOURCE/'ops/files_bootstrap_pins.txt',source=True))
 if DEST.exists() or DEST.is_symlink(): verify(DEST,files);print('verified existing input');return
 stage=Path(tempfile.mkdtemp(prefix='.files-input-stage-',dir=DEST.parent))
 # A killed/failed process leaves only an unpublished temporary directory.
 # It is never reused as an input; cleanup requires a separate review.
 for name,pin in files.items():
  raw=read(SOURCE/name,source=True)
  if hashlib.sha256(raw).hexdigest()!=pin: raise ValueError('source digest mismatch: '+name)
  out=stage/name;out.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
  fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o444)
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
 syncdir(stage/'ops');syncdir(stage);verify(stage,files)
 libc=ctypes.CDLL(None,use_errno=True)
 if libc.renameat2(-100,os.fsencode(stage),-100,os.fsencode(DEST),1): raise OSError(ctypes.get_errno(),'renameat2 NOREPLACE')
 syncdir(DEST.parent);verify(DEST,files);print('verified input published; no service or route activated')
if __name__=='__main__':main()
