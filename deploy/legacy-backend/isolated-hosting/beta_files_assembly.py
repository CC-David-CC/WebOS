"""Assemble existing managed beta transactions; requires a protected launcher.

No CLI or default paths. A future launcher must bind verified actual host
adapters, root custody, pinned artifacts, services and signed health checks.
"""
import json,os,stat
from pathlib import Path
from beta_transaction import Transaction,_decode
from opfs_floor import FloorJournal
from opfs_managed import HeldAdapter

def present(path):
 try:Path(path).lstat();return True
 except FileNotFoundError:return False
class IssuerInstall:
 """ManagedBinding.forward calls this under the already-held host lock."""
 def __init__(self,issuer,old_unit):self.issuer=issuer;self.old=old_unit
 def __call__(self,record):
  if present(self.issuer.journal):self.issuer.recover(self.old,retain=True)
  elif self.issuer.is_old(self.old):self.issuer.apply(retain=True)
  else:self.issuer.verify_current(self.old)
class FilesAssembly:
 """Single-host-lock pre-floor normalization and forward-only v2 sequence."""
 def __init__(self,*,floor,issuer,installer,issuer_old,normal_adapter,normal_journal,normal_old,normal_new,v2_health,pre_normalization,pre_normalization_recovery):
  if floor.io._install_issuer is not installer or installer.issuer is not issuer or installer.old!=issuer_old:raise ValueError('Issuer installation must be the bound forward action')
  if not all(callable(x) for x in (v2_health,pre_normalization,pre_normalization_recovery)):raise ValueError('Pinned health and normalization checks required')
  self._held=floor.io.held;self._check=floor.io.check_lock
  self.floor=FloorJournal(HeldAdapter(floor.io,self._check),floor.dir)
  self.issuer=issuer;self.installer=installer;self.issuer_old=issuer_old;self.normal=normal_adapter;self.normal_journal=Path(normal_journal);self.old=normal_old;self.new=normal_new;self.v2_health=v2_health;self.pre_normalization=pre_normalization;self.pre_normalization_recovery=pre_normalization_recovery
 def _normal_tx(self):return Transaction(HeldAdapter(self.normal,self._check),self.normal_journal)
 def _recover_normal(self):
  self._check();fd=os.open(self.normal_journal,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or a.st_size>8*1024*1024:raise ValueError('Unsafe normalization journal')
   raw=b''
   while len(raw)<=8*1024*1024:
    part=os.read(fd,min(65536,8*1024*1024+1-len(raw)))
    if not part:break
    raw+=part
   z=os.fstat(fd)
   if len(raw)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('Normalization journal changed')
  finally:os.close(fd)
  j=json.loads(raw)
  if type(j.get('version')) is not int or j['version']!=1 or 'policy' in j or _decode(j.get('old',{}))!=self.old or _decode(j.get('new',{}))!=self.new:raise ValueError('Unpinned normalization journal')
  self._check();self._normal_tx().recover()
 def _normalize(self):
  self._check()
  if present(self.floor.floor) or present(self.floor.journal) or present(self.issuer.journal):raise ValueError('Normalization requires absent floor and transition journals')
  tx=self._normal_tx()
  if present(self.normal_journal):self._recover_normal()
  current=self.normal.read()
  if current==self.new:return
  if current!=self.old:raise ValueError('Unrecognized normalization baseline')
  tx.apply(self.old,self.new)
 def _finalize(self):
  self._check()
  if present(self.issuer.journal):self.issuer.finalize(self.issuer_old,self.floor.journal,self.v2_health)
  else:self.v2_health()
 def _finalize_or_gate(self):
  try:self._finalize()
  except Exception as error:
   try:self.floor.io.gate();self.floor.io.gate_health()
   except Exception as gate_error:raise RuntimeError('v2 health failed; gate closure unverified') from gate_error
   raise RuntimeError('v2 health failed; maintenance gate verified') from error
 def apply(self,baseline,candidate,*,phase=lambda _:None):
  with self._held():
   self._check();self.pre_normalization();self._check();self._normalize();phase('normalized')
   self.floor.apply(baseline,candidate,phase=phase)
   self._finalize_or_gate();phase('finalized')
 def recover(self,baseline,candidate):
  with self._held():
   self._check()
   if present(self.normal_journal):
    if present(self.floor.floor) or present(self.floor.journal) or present(self.issuer.journal):raise ValueError('Normalization journal conflicts with v2 state')
    self.pre_normalization_recovery();self._check();self._recover_normal()
   if present(self.floor.journal):
    if not present(self.floor.floor) and present(self.issuer.journal):raise ValueError('Issuer switch cannot precede v2 floor')
    self.floor.recover(baseline,candidate)
   if present(self.floor.floor):
    record=self.floor._read(self.floor.floor)
    if record!={'version':1,'baseline':baseline,'candidate':candidate}:raise ValueError('Floor pin mismatch; no gate state claimed')
    if not present(self.floor.journal) and self.floor.io.is_gate():
     # A prior health failure may have closed the gate after the outer
     # journal was finalized. Recreate a durable forward intent from the
     # verified floor before attempting to expose the candidate again.
     self.floor.io.gate_health();self._check();self.floor._write(self.floor.journal,record)
     self.floor.recover(baseline,candidate)
    self._finalize_or_gate()
    return 'v2-verified'
   if present(self.issuer.journal):raise ValueError('Issuer journal exists without v2 floor')
   return 'pre-floor'
