"""Exact 830c asset floor atop existing FloorJournal; research only.

Caller must supply the reviewed single hosting lock, pinned managed route
adapter, lifecycle checks, and an entrypoint that fences older recovery code.
This module never rewrites the original OPFS floor or installs an operator.
"""
from pathlib import Path
from opfs_floor import FloorJournal
OLD='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
NEW='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0'
ORIGINAL_BASE='e7a5e64272c1d6b78de73c46f5105b9963e2272f40450e39e86a038293d9fb3b'
class GuardedAdapter:
 def __init__(self,adapter,directory):self.adapter=adapter;self.original=Path(directory)/'opfs-floor.json';self.checker=FloorJournal(adapter,directory)
 def held(self):return self.adapter.held()
 def check_lock(self):
  self.adapter.check_lock()
  if self.checker._read(self.original)!={'version':1,'baseline':ORIGINAL_BASE,'candidate':OLD}:raise ValueError('Original OPFS floor changed')
 def __getattr__(self,name):return getattr(self.adapter,name)
class AssetFloor(FloorJournal):
 def __init__(self,adapter,directory):
  super().__init__(GuardedAdapter(adapter,directory),directory)
  self.journal=self.dir/'files-asset-transition.json';self.floor=self.dir/'files-asset-floor.json'
 def apply_exact(self,*,phase=lambda _:None):return super().apply(OLD,NEW,phase=phase)
 def recover_exact(self):
  expected={'version':1,'baseline':OLD,'candidate':NEW}
  with self.io.held():
   self.io.check_lock()
   if not (self.journal.exists() or self.journal.is_symlink() or self.floor.exists() or self.floor.is_symlink()):raise ValueError('No asset transition or floor')
   self.io.gate();self.io.gate_health();self.io.check_lock()
   pending=self.journal.exists() or self.journal.is_symlink()
   if pending and self._read(self.journal)!=expected:raise ValueError('Stale asset transition; retain gate')
   if self.floor.exists() or self.floor.is_symlink():
    if self._read(self.floor)!=expected:raise ValueError('Asset floor mismatch; retain gate')
    self.io.preflight_forward(expected);self._forward(expected,lambda _:None)
   elif pending:
    self.io.preflight_baseline(expected);self.io.restore_baseline(expected);self.io.baseline_health(expected)
   else:raise ValueError('Missing asset transition')
   self.io.check_lock()
   if pending:self._clear()
