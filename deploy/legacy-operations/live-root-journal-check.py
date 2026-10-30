#!/usr/bin/env python3
"""Signed local fixtures for interrupted live-renewal coordination."""
import contextlib,importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from origin_service.live_root_journal import LiveRenewalJournal,execute
from origin_service.live_root_renewal import inspect
from steward.root_authority import RootAuthority
from steward.protocol import jose

spec=importlib.util.spec_from_file_location('live_fixture',Path(__file__).with_name('live-root-renewal-check.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

class Backend:
 def __init__(self,case):
  self.case=case;self.staged=case.old;self.live=case.old;self.fence=1;self.running=True;self.signatures=0;self.failure=None;self.receipts=0
 def locked(self):return contextlib.nullcontext()
 def initial(self):
  return {'version':'codi-live-root-renewal/1','baseline':jose.dumps(self.case.old),'checkpoint':self.case.checkpoint,'configSHA256':'a'*64,'releaseSHA256':'b'*64,'publisherRevision':1,'seconds':600,'renewalWindow':120}
 def decide(self,record):
  root=RootAuthority(self.case.authority.directory,clock=lambda:self.case.clock).provision()
  return inspect(jose.loads(record['baseline']),root,self.staged,self.live,record['checkpoint'],fence_revision=self.fence,now=self.case.clock,steward_running=self.running,ledger_verified=True,renewal_window=record['renewalWindow'])
 def fail(self,name):
  if self.failure==name:self.failure=None;raise RuntimeError('Injected '+name)
 def renew(self,record):
  if self.decide(record)!='renew-once':raise ValueError('State changed')
  self.fence=2;self.fail('fence');self.case.authority.renew(600);self.signatures+=1;self.fail('signed')
 def export(self,record):
  if self.decide(record)!='export-committed':raise ValueError('State changed')
  self.staged=self.case.authority.provision();self.fail('staged');self.live=self.staged;self.fail('live')
 def start(self,record):self.running=True
 def verify(self,record):
  if self.decide(record)!='verify-running':raise ValueError('State not current')
 def receipt(self,record):self.receipts=1

class JournalChecks(unittest.TestCase):
 def test_all_interruption_boundaries_resume_once(self):
  for point in ('prepared','before-renew-once','fence','signed','after-renew-once','before-export-committed','staged','live','after-export-committed','verified','receipt'):
   with self.subTest(point=point):
    case=fixture.LiveRenewal();case.setUp()
    try:
     case.clock+=500;backend=Backend(case);journal=LiveRenewalJournal(Path(case.tmp.name)/'journal.json')
     backend.failure=point
     def phase(name):
      if name==point:raise RuntimeError('Injected '+name)
     with self.assertRaises(RuntimeError):execute(backend,journal,phase=phase)
     self.assertTrue(journal.path.exists())
     self.assertEqual(execute(backend,journal,resume=True),{'status':'renewed','rootRevision':2})
     self.assertEqual(backend.signatures,1);self.assertEqual(backend.receipts,1);self.assertFalse(journal.path.exists())
    finally:case.doCleanups()
 def test_not_due_and_bad_journal_leave_authority_unchanged(self):
  case=fixture.LiveRenewal();case.setUp()
  try:
   backend=Backend(case);journal=LiveRenewalJournal(Path(case.tmp.name)/'journal.json')
   self.assertEqual(execute(backend,journal)['status'],'not-due');self.assertFalse(journal.path.exists())
   record=backend.initial();record['renewalWindow']=record['seconds']
   with self.assertRaises(ValueError):journal.create(record)
   self.assertEqual(backend.signatures,0)
  finally:case.doCleanups()
 def test_expired_pending_journal_requires_intervention(self):
  case=fixture.LiveRenewal();case.setUp()
  try:
   case.clock+=500;backend=Backend(case);journal=LiveRenewalJournal(Path(case.tmp.name)/'journal.json')
   def interrupt(name):
    if name=='prepared':raise RuntimeError('Interrupted before signature')
   with self.assertRaises(RuntimeError):execute(backend,journal,phase=interrupt)
   case.clock+=100
   with self.assertRaises(ValueError):execute(backend,journal,resume=True)
   self.assertTrue(journal.path.exists());self.assertEqual(backend.signatures,0)
  finally:case.doCleanups()

if __name__=='__main__':unittest.main()
