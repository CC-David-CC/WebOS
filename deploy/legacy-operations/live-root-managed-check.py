#!/usr/bin/env python3
"""Actual signed state and SQLite; simulated systemd and interruptions."""
import hashlib,importlib.util,json,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from origin_service import maintenance
from origin_service.live_root_managed import ManagedLiveRenewal
from origin_service.live_root_journal import LiveRenewalJournal,execute
from steward.root_authority import RootAuthority,atomic_private
from steward.protocol import jose
spec=importlib.util.spec_from_file_location('managed_fixture',Path(__file__).with_name('expired-root-managed-check.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

class LiveFixture(fixture.FixtureOperator):
 def __init__(self,folder):
  super().__init__(folder)
  current=RootAuthority(self.root).renew(600);raw=jose.dumps(current).encode()
  atomic_private(self.private/'provision.json',raw);atomic_private(self.steward/'provision.json',raw)
  fence=json.loads((self.control/'recovery-fence.json').read_bytes());fence['rootFloor']=2;atomic_private(self.control/'recovery-fence.json',jose.dumps(fence).encode())
  seed=jose.inspect(current['seed'],'codi-seed/1',32768)[1];self.publisher.bind(self.publisher_binding,seed);self._publish(seed,int(time.time()))
  self.running=True;self.signatures=0
 def issuer_config(self,c):
  seed=jose.inspect(jose.loads((self.steward/'provision.json').read_bytes())['seed'],'codi-seed/1',32768)[1]
  self.publisher.bind(self.publisher_binding,seed);self._publish(seed,int(time.time()))
  return super().issuer_config(c)

class ManagedLiveTests(unittest.TestCase):
 def test_signed_managed_state_recovers_each_interruption(self):
  for point in ('prepared','fence','signed','staged','live','after-renew-once','verified','receipt'):
   with self.subTest(point=point),tempfile.TemporaryDirectory(prefix='codi-live-managed-') as folder:
    op=LiveFixture(Path(folder));config_hash=hashlib.sha256(op.config_path.read_bytes()).hexdigest()
    backend=ManagedLiveRenewal(op,maintenance,op.config_path,config_sha256=config_hash,release_sha256='b'*64,seconds=1200,renewal_window=600)
    journal=LiveRenewalJournal(op.control/'live-journal.json');op.crash=point
    def phase(name):
     if name==point:raise RuntimeError('Injected '+name)
    with self.assertRaises(RuntimeError):execute(backend,journal,phase=phase)
    result=execute(backend,journal,resume=True)
    self.assertEqual(result,{'status':'renewed','rootRevision':3});self.assertEqual(op.signatures,1);self.assertTrue(op.running)
    self.assertEqual((op.root/'root.pem').read_bytes(),op.key_before);self.assertFalse(journal.path.exists())
 def test_pins_and_window_drift_refused(self):
  with tempfile.TemporaryDirectory(prefix='codi-live-managed-') as folder:
   op=LiveFixture(Path(folder));pin=hashlib.sha256(op.config_path.read_bytes()).hexdigest();journal=LiveRenewalJournal(op.control/'live-journal.json')
   wrong=ManagedLiveRenewal(op,maintenance,op.config_path,config_sha256='a'*64,release_sha256='b'*64,seconds=1200,renewal_window=600)
   with self.assertRaises(ValueError):execute(wrong,journal)
   self.assertFalse(journal.path.exists());self.assertEqual(op.signatures,0)
   backend=ManagedLiveRenewal(op,maintenance,op.config_path,config_sha256=pin,release_sha256='b'*64,seconds=1200,renewal_window=600)
   def stop(name):
    if name=='prepared':raise RuntimeError('stop')
   with self.assertRaises(RuntimeError):execute(backend,journal,phase=stop)
   changed=ManagedLiveRenewal(op,maintenance,op.config_path,config_sha256=pin,release_sha256='b'*64,seconds=1200,renewal_window=599)
   with self.assertRaises(ValueError):execute(changed,journal,resume=True)
   self.assertEqual(op.signatures,0);self.assertTrue(journal.path.exists())

if __name__=='__main__':unittest.main()
