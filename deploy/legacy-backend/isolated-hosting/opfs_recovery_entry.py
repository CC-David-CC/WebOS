"""Candidate legacy-recovery dispatch under the existing hosting lock.

No CLI and no protected host paths. A reviewed launcher must install and call
this for every supported legacy beta recovery route; invoking the underlying
Transaction directly is deliberately outside this adapter's authority.
"""
import os
from beta_transaction import Transaction
from opfs_managed import HeldAdapter

def recover_legacy(*,managed,host_lock,check_lock,floor_path,check_floor_custody,verify_journal,journal):
 if not all(callable(f) for f in (host_lock,check_lock,check_floor_custody,verify_journal)):raise ValueError('Protected launcher checks required')
 with host_lock():
  check_lock();check_floor_custody()
  try:os.lstat(floor_path)
  except FileNotFoundError:pass
  else:raise ValueError('v2 floor present; legacy recovery refused')
  # Caller verifies the pending journal against pinned old/new bytes before
  # the original transaction may inspect or change any managed host state.
  verify_journal();check_lock()
  Transaction(HeldAdapter(managed,check_lock),journal).recover()
