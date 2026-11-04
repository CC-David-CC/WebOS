"""Forward-only v2 floor for composition under the managed beta host lock.

No CLI or host paths. The adapter must use the existing managed hosting and
issuer operators; this module does not itself change routes or services.
"""
import json,os,stat,tempfile
from pathlib import Path

class FloorJournal:
 def __init__(self,adapter,directory):
  self.io=adapter;self.dir=Path(directory);self.journal=self.dir/'opfs-transition.json';self.floor=self.dir/'opfs-floor.json'
 def _write(self,path,obj):
  fd,name=tempfile.mkstemp(prefix='.opfs-',dir=self.dir)
  try:
   with os.fdopen(fd,'wb') as out:
    os.fchmod(out.fileno(),0o600);out.write((json.dumps(obj,sort_keys=True)+'\n').encode());out.flush();os.fsync(out.fileno())
   os.replace(name,path);self._syncdir()
  finally:
   if os.path.exists(name):os.unlink(name)
 def _syncdir(self):
  fd=os.open(self.dir,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 def _read(self,path):
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
  try:
   info=os.fstat(fd)
   if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>4096:raise ValueError('Unsafe journal file')
   raw=os.read(fd,4097)
   if len(raw)!=info.st_size:raise ValueError('Journal changed while reading')
  finally:os.close(fd)
  result=json.loads(raw);self._validate(result);return result
 def _validate(self,result):
  if not isinstance(result,dict) or set(result)!={'version','baseline','candidate'} or type(result['version']) is not int or result['version']!=1 or any(not isinstance(result[k],str) or len(result[k])!=64 or any(c not in '0123456789abcdef' for c in result[k]) for k in ('baseline','candidate')):raise ValueError('Invalid floor journal')
 def _clear(self):self.journal.unlink();self._syncdir()
 def _forward(self,record,phase):
  try:
   self.io.forward(record);phase('forward');self.io.candidate_health(record);phase('healthy')
  except BaseException:
   # Best effort: preserve the journal and stop serving when an ordinary
   # failure occurs after exposure. An uncatchable kill requires recovery.
   self.io.gate();self.io.gate_health();raise
 def apply(self,baseline,candidate,*,phase=lambda _:None):
  record={'version':1,'baseline':baseline,'candidate':candidate};self._validate(record)
  with self.io.held():
   self.io.check_lock();self.io.preflight(record)
   if self.journal.exists() or self.journal.is_symlink() or self.floor.exists() or self.floor.is_symlink():raise ValueError('Existing transition or v2 floor')
   self._write(self.journal,record);phase('journaled')
   self.io.gate();self.io.gate_health();phase('gated')
   self.io.check_lock();self._write(self.floor,record);phase('floor')
   self._forward(record,phase)
   self.io.check_lock();self._clear();phase('complete')
 def recover(self,baseline,candidate):
  expected={'version':1,'baseline':baseline,'candidate':candidate};self._validate(expected)
  with self.io.held():
   self.io.check_lock()
   # Gate first, even when journal/floor is missing or malformed.
   self.io.gate();self.io.gate_health();self.io.check_lock()
   record=self._read(self.journal)
   if record!=expected:raise ValueError('Recovery actor is stale; retain gate')
   if self.floor.exists() or self.floor.is_symlink():
    if self._read(self.floor)!=record:raise ValueError('Floor and journal disagree; retain gate')
    self.io.preflight_forward(record);self._forward(record,lambda _:None)
   else:
    self.io.preflight_baseline(record);self.io.restore_baseline(record);self.io.baseline_health(record)
   self.io.check_lock();self._clear()
