"""Candidate-only maintenance gate via the existing managed transaction.

This module has no CLI, route generator, privilege boundary, or host paths.
The protected caller must pin snapshots/callbacks and hold the host lock.
"""
import json,os,stat
from beta_transaction import Transaction,_decode
from opfs_managed import HeldAdapter
class GateRescue:
 def __init__(self,managed,check_lock,journal,candidate,gate,check_custody,preflight):
  if not all(callable(x) for x in (check_lock,check_custody,preflight)):raise ValueError('Protected checks required')
  if set(candidate)!={'common','manifest','caddy'} or set(gate)!={'common','manifest','caddy'} or candidate==gate:raise ValueError('Distinct pinned route snapshots required')
  self.managed=managed;self.check=check_lock;self.journal=journal;self.candidate=candidate;self.gate=gate;self.custody=check_custody;self.preflight=preflight
 def _pending(self):
  fd=os.open(self.journal,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
  try:
   before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.geteuid() or stat.S_IMODE(before.st_mode)!=0o600 or before.st_nlink!=1 or before.st_size>8*1024*1024:raise ValueError('Unsafe emergency journal')
   raw=os.read(fd,before.st_size+1);after=os.fstat(fd)
   if len(raw)!=before.st_size or (before.st_ino,before.st_dev,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_ino,after.st_dev,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('Emergency journal changed')
  finally:os.close(fd)
  value=json.loads(raw)
  if value.get('version')!=2 or value.get('policy')!='gate-only' or value.get('phase') not in ('prepared','committed') or _decode(value.get('old',{}))!=self.candidate or _decode(value.get('new',{}))!=self.gate:raise ValueError('Unpinned emergency journal')
 def __call__(self,*,phase=lambda _:None):
  self.check();self.custody();self.preflight();tx=Transaction(HeldAdapter(self.managed,self.check),self.journal)
  if self.journal.exists() or self.journal.is_symlink():self._pending();tx.recover_gate(self.candidate,self.gate)
  self.check();current=self.managed.read()
  if current==self.gate:return
  if current!=self.candidate:raise ValueError('Unknown or untrusted routes; cannot safely gate')
  tx.apply_gate(self.candidate,self.gate,phase=phase)
  self.check()
  if self.managed.read()!=self.gate:raise ValueError('Emergency gate did not persist')
