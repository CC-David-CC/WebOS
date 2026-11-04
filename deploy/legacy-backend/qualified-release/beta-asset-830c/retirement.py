"""Journal-bound retirement of four exact legacy actor paths; no CLI.

The fixed-path caller supplies the existing lock and trusted maintenance
freeze. The quarantine contains data only, never the old dependency trees.
"""
import ctypes,hashlib,json,os,stat
from pathlib import Path
PINS={'bc9':('314e493ff52b8999bc2fcf57eef220389dda16722bd2b5bec95a945f136a319d',0o644),'ce18-bundle':('aa34f6c9e53f049d012a45da35989d1aab4797ef983d270ab498d01037fbfd82',0o444),'ce18-input':('aa34f6c9e53f049d012a45da35989d1aab4797ef983d270ab498d01037fbfd82',0o444),'main-once':('6469eb631aec6e9d37496dd1547a04dbbda9ea112e280b695c8ea426368f8642',0o644)}
def sha(b):return hashlib.sha256(b).hexdigest()
def validate(entries,quarantine,primitives,check_lock,*,pending):
 check_lock();quarantine=Path(quarantine)
 if set(entries)!=set(PINS) or len({str(Path(v)) for v in entries.values()})!=len(PINS):raise ValueError('Exact four legacy actor paths required')
 primitives.root_path(quarantine.parent,True);device=quarantine.parent.stat().st_dev
 try:q=quarantine.lstat()
 except FileNotFoundError:q=None
 if q is not None:
  primitives.root_path(quarantine,True)
  if stat.S_IMODE(q.st_mode)!=0o700 or q.st_dev!=device:raise ValueError('Unsafe retirement quarantine')
  expected={key+'.data' for key in PINS};found={x.name for x in quarantine.iterdir()}
  if not found<=expected:raise ValueError('Unexpected quarantine entry')
 for key,(pin,mode) in PINS.items():
  src=Path(entries[key]);dest=quarantine/(key+'.data');primitives.root_path(src.parent,True)
  if src.parent.stat().st_dev!=device:raise ValueError('Cross-device retirement forbidden')
  try:a=src.lstat()
  except FileNotFoundError:a=None
  try:b=dest.lstat()
  except FileNotFoundError:b=None
  if (a is None)==(b is None) or (b is not None and not pending):raise ValueError('Unexpected legacy retirement state: '+key)
  path=src if a is not None else dest;primitives.root_path(path);v=path.lstat();allowed=(mode,) if a is not None else (mode,0o400)
  if not stat.S_ISREG(v.st_mode) or v.st_nlink!=1 or stat.S_IMODE(v.st_mode) not in allowed or sha(primitives.read_file(path))!=pin:raise ValueError('Legacy actor pin/custody changed: '+key)
 check_lock()

def retire(*,entries,quarantine,journal,expected,primitives,check_lock,check_fence,phase=lambda _:None):
 check_lock();check_fence();primitives.root_path(journal)
 if stat.S_IMODE(journal.stat().st_mode)!=0o600 or json.loads(primitives.read_file(journal,4096))!=expected:raise ValueError('Retirement journal mismatch')
 validate(entries,quarantine,primitives,check_lock,pending=True);quarantine=Path(quarantine)
 if not quarantine.exists():os.mkdir(quarantine,0o700);primitives.syncdir(quarantine.parent)
 for key in PINS:
  check_lock();check_fence();src=Path(entries[key]);dest=quarantine/(key+'.data')
  if src.exists():
   libc=ctypes.CDLL(None,use_errno=True)
   if libc.renameat2(-100,os.fsencode(src),-100,os.fsencode(dest),1):raise OSError(ctypes.get_errno(),'retirement no-replace failed')
   primitives.syncdir(src.parent);primitives.syncdir(quarantine)
  fd=os.open(dest,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:os.fchmod(fd,0o400);os.fsync(fd)
  finally:os.close(fd)
  phase('retired-'+key)
 validate(entries,quarantine,primitives,check_lock,pending=True);check_fence()
