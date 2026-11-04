"""Disposable maintenance model tests; never modifies host state."""
import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
p=Path(__file__).parent/'fixtures/maintenance_transaction.py';spec=importlib.util.spec_from_file_location('model',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='beta-window-model-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.old={x:('old-'+x).encode() for x in ('common','manifest','caddy')};self.new={x:('new-'+x).encode() for x in self.old};self.prior={'active':True,'enabled':True}
  for k,v in self.old.items():(self.root/k).write_bytes(v)
  (self.root/'timer').write_text(json.dumps(self.prior));self.tx=m.Window(self.root)
 def test_success_restores_timer_and_commits(self):
  self.tx.run(self.old,self.new);self.assertEqual(self.tx.read(),self.new);self.assertEqual(self.tx.timer_state(),self.prior);self.assertFalse(self.tx.journal.exists())
 def test_observed_drift_is_not_overwritten(self):
  def hook(p):
   if p=='after-common':(self.root/'manifest').write_bytes(b'external')
  with self.assertRaisesRegex(ValueError,'drift'):self.tx.run(self.old,self.new,phase=hook)
  self.assertEqual((self.root/'manifest').read_bytes(),b'external');self.assertTrue(self.tx.journal.exists())
  with self.assertRaisesRegex(ValueError,'drift'):self.tx.recover()
  self.assertEqual((self.root/'manifest').read_bytes(),b'external')
 def test_replaced_lock_is_detected(self):
  def hook(p):
   if p=='timer-stopped':self.tx.lock.unlink();self.tx.lock.touch()
  with self.assertRaisesRegex(ValueError,'lock path changed'):self.tx.run(self.old,self.new,phase=hook)
  self.assertEqual(self.tx.read(),self.old);self.assertTrue(self.tx.journal.exists())
 def test_interruption_recovers_old_or_committed_new_and_timer(self):
  for marker,target in [('timer-stopped',self.old),('after-manifest',self.old),('committed',self.new)]:
   for k,v in self.old.items():(self.root/k).write_bytes(v)
   (self.root/'timer').write_text(json.dumps(self.prior))
   code='import os,sys;sys.path.insert(0,sys.argv[1]);from maintenance_transaction import Window\nr=Window(sys.argv[2]);old={x:("old-"+x).encode() for x in ("common","manifest","caddy")};new={x:("new-"+x).encode() for x in old}\ndef phase(x):\n if x==sys.argv[3]:os._exit(73)\nr.run(old,new,phase=phase)'
   result=subprocess.run([sys.executable,'-B','-c',code,str(p.parent),str(self.root),marker],timeout=5);self.assertEqual(result.returncode,73);self.tx.recover();self.assertEqual(self.tx.read(),target);self.assertEqual(self.tx.timer_state(),self.prior);self.assertFalse(self.tx.journal.exists())
 def test_negative_control_uncooperative_check_to_replace_race(self):
  def hook(p):
   if p=='before-common':(self.root/'common').write_bytes(b'uncooperative')
  self.tx.run(self.old,self.new,phase=hook)
  self.assertEqual((self.root/'common').read_bytes(),self.new['common'])
  # This passing test demonstrates why the model is not safe with an uncooperative writer.
 def test_timer_state_drift_prevents_recovery(self):
  def hook(p):
   if p=='timer-stopped':raise RuntimeError('test interruption')
  with self.assertRaises(RuntimeError):self.tx.run(self.old,self.new,phase=hook)
  (self.root/'timer').write_text(json.dumps({'active':False,'enabled':False}))
  with self.assertRaisesRegex(ValueError,'recovery drift'):self.tx.recover()
  self.assertEqual(self.tx.timer_state(),{'active':False,'enabled':False});self.assertEqual(self.tx.read(),self.old)
if __name__=='__main__':unittest.main(verbosity=2)
