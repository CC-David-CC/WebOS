#!/usr/bin/env python3
"""Map the exact operator-written beta issuer unit to a unique fixture unit.

Test-only adapter: it changes no production unit and accepts only the two
reviewed unit hashes. The final fixture ExecStart argument controls which
sealed public issuer executable the trampoline execs.
"""
import hashlib,os,re,shlex,stat,sys,tempfile
from pathlib import Path
OLD='e6b8279c32a89f38ee4a3b2ba6c27777413c13b1b98611e78ff9b0d52dca1244';NEW='d3ed82ddf87ff643288baac0a7476b35ed701a016b3d297ccb4a10cfaec224e4'
def selection(raw):
 digest=hashlib.sha256(raw).hexdigest()
 if digest not in (OLD,NEW):raise ValueError('unrecognized operator issuer unit')
 lines=[line for line in raw.decode().splitlines() if line.startswith('ExecStart=')]
 if len(lines)!=1:raise ValueError('unexpected issuer ExecStart')
 args=shlex.split(lines[0][len('ExecStart='):]);scripts=[v for v in args if v.endswith('/scripts/serve-connected.py')]
 if len(scripts)!=1:raise ValueError('unexpected issuer executable')
 selected='old' if digest==OLD else 'new'
 if selected=='old':
  if '1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51' not in scripts[0] or '--beta-opfs-file-content' in args:raise ValueError('invalid old unit')
 else:
  if '853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21' not in scripts[0] or args.count('--beta-opfs-file-content')!=1:raise ValueError('invalid new unit')
 return selected
def update(source,target):
 target=Path(target)
 if target.parent!=Path('/run/systemd/system') or not re.fullmatch(r'codi-files-test-[0-9]+-[0-9a-f]{8}-issuer\.service',target.name):raise ValueError('only a uniquely named fixture unit may be updated')
 source_fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  before=os.fstat(source_fd)
  if not stat.S_ISREG(before.st_mode) or before.st_uid!=0 or before.st_nlink!=1 or stat.S_IMODE(before.st_mode)!=0o644 or before.st_size>16384:raise ValueError('unsafe operator unit')
  source_bytes=os.read(source_fd,16385);after=os.fstat(source_fd)
  if len(source_bytes)!=before.st_size or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('operator unit changed')
 finally:os.close(source_fd)
 choice=selection(source_bytes);fd=os.open(target,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_nlink!=1 or stat.S_IMODE(info.st_mode)!=0o644 or info.st_size>16384:raise ValueError('unsafe fixture unit')
  raw=os.read(fd,16385)
 finally:os.close(fd)
 text=raw.decode();lines=text.splitlines(keepends=True);indices=[i for i,line in enumerate(lines) if line.startswith('ExecStart=')]
 if len(indices)!=1:raise ValueError('unexpected fixture ExecStart')
 index=indices[0];line=lines[index]
 if not line.endswith((' old\n',' new\n')) or '/service.py issuer ' not in line:raise ValueError('unrecognized fixture service command')
 lines[index]=line.rsplit(' ',1)[0]+' '+choice+'\n';data=''.join(lines).encode()
 fd,name=tempfile.mkstemp(prefix='.codi-fixture-unit-',dir=target.parent)
 try:
  with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),0o644);out.write(data);out.flush();os.fsync(out.fileno())
  os.replace(name,target);directory=os.open(target.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(directory);os.close(directory)
 finally:
  if os.path.exists(name):os.unlink(name)
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: mapper source-unit fixture-unit')
 update(sys.argv[1],sys.argv[2])
