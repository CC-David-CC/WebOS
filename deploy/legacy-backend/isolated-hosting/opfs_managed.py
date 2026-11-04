"""Bind the OPFS floor to existing managed beta transactions, with one host lock.
No CLI, host paths, privileged installation or real service switching here.
"""
from contextlib import contextmanager
class HeldAdapter:
 """Run a nested beta_transaction.Transaction under the caller's host lock."""
 def __init__(self,managed,check_lock):self._managed=managed;self._check=check_lock
 @contextmanager
 def held(self):
  self._check()
  try:yield
  finally:self._check()
 def __getattr__(self,name):return getattr(self._managed,name)
class ManagedBinding:
 """Existing Transaction instances only; exact reviewed routes and callbacks.

prepare_routes(floor) must reconcile an interrupted inner transaction while
preserving the floor. After the floor, no pending transaction may have the old
baseline as either endpoint. Callbacks are protected-launcher responsibilities.
"""
 def __init__(self,lock,check_lock,snapshots,make_transaction,read_routes,prepare_routes,floor_present,verify,gate_health,candidate_health,baseline_health,install_issuer,emergency_gate):
  required=(lock,check_lock,make_transaction,read_routes,prepare_routes,floor_present,verify,gate_health,candidate_health,baseline_health,install_issuer,emergency_gate)
  if not all(callable(x) for x in required) or set(snapshots)!={'baseline','gate','candidate'}:raise ValueError('Incomplete managed binding')
  self._lock=lock;self._check=check_lock;self.snapshots=snapshots;self._make=make_transaction;self._read=read_routes;self._prepare=prepare_routes;self._floor_present=floor_present;self._verify=verify;self._gate_health=gate_health;self._candidate_health=candidate_health;self._baseline_health=baseline_health;self._install_issuer=install_issuer;self._emergency_gate=emergency_gate;self._floor=False
  if any(set(v)!={'common','manifest','caddy'} for v in snapshots.values()) or len({tuple(sorted(v.items())) for v in snapshots.values()})!=3:raise ValueError('Distinct exact route snapshots required')
 def held(self):return self._lock()
 def check_lock(self):return self._check()
 def is_gate(self):
  self._check();return self._read()==self.snapshots['gate']
 def _transition(self,source,target):
  self._check();current=self._read()
  if current==self.snapshots[target]:return
  if current!=self.snapshots[source]:raise ValueError('Managed routes are not the pinned expected source')
  tx=self._make(self.snapshots[source],self.snapshots[target])
  if not isinstance(getattr(tx,'io',None),HeldAdapter) or tx.io._check is not self._check:raise ValueError('Nested managed transaction must share the held host lock')
  if target=='gate' and self._floor:tx.apply_gate(self.snapshots[source],self.snapshots[target])
  else:tx.apply(self.snapshots[source],self.snapshots[target])
  self._check()
  if self._read()!=self.snapshots[target]:raise ValueError('Managed route transition did not persist')
 def preflight(self,record):
  self._check()
  if self._floor_present():raise ValueError('A v2 floor already exists; use forward recovery')
  self._verify(record,'initial');self._prepare(False)
  if self._read()!=self.snapshots['baseline']:raise ValueError('Unexpected baseline routes')
 def gate(self):
  self._check();self._floor=self._floor or self._floor_present()
  try:self._prepare(self._floor)
  except Exception:
   if self._floor:
    self._emergency_gate();self._gate_health()
   raise
  current=self._read()
  if current==self.snapshots['baseline']:
   if self._floor:raise ValueError('Old routes cannot be a recovery baseline after v2 floor')
   self._transition('baseline','gate')
  elif current==self.snapshots['candidate']:self._transition('candidate','gate')
  elif current!=self.snapshots['gate']:raise ValueError('Unknown managed route state')
 def gate_health(self):self._gate_health()
 def preflight_forward(self,record):self._floor=True;self._verify(record,'forward')
 def preflight_baseline(self,record):self._verify(record,'baseline')
 def forward(self,record):
  self._floor=True;self._check();self._verify(record,'forward');self._install_issuer(record);self._transition('gate','candidate')
 def candidate_health(self,record):self._candidate_health(record)
 def restore_baseline(self,record):self._transition('gate','baseline')
 def baseline_health(self,record):self._baseline_health(record)
