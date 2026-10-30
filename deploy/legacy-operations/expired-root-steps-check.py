#!/usr/bin/env python3
"""Exercise recovery decisions without reading or changing real authority state."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from origin_service.expired_root_steps import next_step

class Decisions(unittest.TestCase):
 def setUp(self):
  self.old='a'*64;self.new='b'*64
  self.state=dict(base_revision=4,target_revision=5,root_revision=4,fence_revision=4,staged_revision=4,live_revision=4,base_hash=self.old,root_hash=self.old,staged_hash=self.old,live_hash=self.old,root_expired=True,steward_running=False,bindings_verified=True,ledger_verified=True)
 def check(self,expected,**changes):self.assertEqual(next_step(**(self.state|changes)),expected)
 def reject(self,**changes):
  with self.assertRaises(ValueError):next_step(**(self.state|changes))
 def test_expired_seed_and_reserved_fence_renew_once(self):
  self.check('renew-once');self.check('renew-once',fence_revision=5)
 def test_committed_seed_requires_export_before_restart(self):
  self.check('export-committed',root_revision=5,fence_revision=5,root_hash=self.new,root_expired=False)
  self.check('export-committed',root_revision=5,fence_revision=5,staged_revision=5,root_hash=self.new,staged_hash=self.new,root_expired=False)
 def test_fully_exported_seed_starts_or_verifies_running(self):
  ready=dict(root_revision=5,fence_revision=5,staged_revision=5,live_revision=5,root_hash=self.new,staged_hash=self.new,live_hash=self.new,root_expired=False)
  self.check('start-steward',**ready);self.check('verify-running',**(ready|{'steward_running':True}))
 def test_forks_and_inconsistent_exports_are_refused(self):
  self.reject(staged_hash=self.new);self.reject(live_revision=5);self.reject(root_revision=5,fence_revision=5,root_hash=self.new,staged_revision=5,staged_hash=self.old,root_expired=False)
  self.reject(root_revision=5,fence_revision=5,root_hash=self.new,staged_hash='c'*64,live_hash='c'*64,root_expired=False)
 def test_wrong_floor_and_revision_are_refused(self):
  self.reject(fence_revision=6);self.reject(root_revision=3);self.reject(target_revision=6);self.reject(fence_revision=True)
 def test_unverified_or_unavailable_state_is_refused(self):
  self.reject(bindings_verified=False);self.reject(ledger_verified=False);self.reject(root_hash='bad');self.reject(root_expired=False);self.reject(steward_running=True)
 def test_no_start_for_expired_or_partially_exported_seed(self):
  self.reject(root_revision=5,fence_revision=5,root_hash=self.new,root_expired=True)
  self.reject(root_revision=5,fence_revision=5,root_hash=self.new,root_expired=False,steward_running=True)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Decisions));sys.exit(not result.wasSuccessful())
