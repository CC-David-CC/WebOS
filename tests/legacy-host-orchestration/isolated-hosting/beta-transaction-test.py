"""Transaction core with disposable files and a fake managed-webctl adapter."""
import contextlib,importlib.util,json,os,tempfile,types,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('tx',root/'ops/beta_transaction.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Adapter:
 def __init__(self,root,old,new):
  self.root=Path(root);self.old=old;self.new=new;self.timer={'active':True,'enabled':True};self.calls=[];self.locked=False
  for k,v in old.items():(self.root/k).write_bytes(v)
 @contextlib.contextmanager
 def held(self):self.locked=True;yield;self.locked=False
 def check_lock(self):assert self.locked
 def read(self):return {k:(self.root/k).read_bytes() for k in ('common','manifest','caddy')}
 def beta_ready(self):self.calls.append('preflight')
 def backup(self,old):self.calls.append('backup');return 'fixture-backup'
 def timer_snapshot(self):return dict(self.timer)
 def timer_stop_if_active(self,prior):self.calls.append('stop-timer');self.timer['active']=False
 def assert_renewal_quiescent(self):self.calls.append('renewal-checked')
 def replace_source(self,key,value):self.calls.append('write-'+key);(self.root/key).write_bytes(value)
 def apply_caddy(self,manifest,common,*,recovery=False):
  self.calls.append('webctl.caddy_apply');desired=self.new if (manifest,common)==(self.new['manifest'],self.new['common']) else self.old
  assert (manifest,common)==(desired['manifest'],desired['common']);(self.root/'caddy').write_bytes(desired['caddy'])
 def check_health(self):self.calls.append('health')
 def check_main_health(self):self.calls.append('main-health')
 def timer_assert_recoverable(self,prior):
  if self.timer not in (prior,{**prior,'active':False}):raise ValueError('Timer drift')
 def timer_restore(self,prior):self.calls.append('restore-timer');self.timer=dict(prior)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='beta-tx-unit-');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.old={k:('old-'+k).encode() for k in ('common','manifest','caddy')};self.new={k:('new-'+k).encode() for k in self.old};self.a=Adapter(self.root,self.old,self.new);self.tx=m.Transaction(self.a,self.root/'journal')
 def test_apply_calls_managed_route_and_restores_timer(self):
  self.tx.apply(self.old,self.new);self.assertEqual(self.a.read(),self.new);self.assertEqual(self.a.timer,{'active':True,'enabled':True});self.assertIn('webctl.caddy_apply',self.a.calls);self.assertFalse(self.tx.journal.exists())
 def test_observed_drift_retains_journal_without_overwrite(self):
  def phase(p):
   if p=='common-written':(self.root/'manifest').write_bytes(b'external')
  with self.assertRaisesRegex(ValueError,'drift'):self.tx.apply(self.old,self.new,phase=phase)
  self.assertEqual((self.root/'manifest').read_bytes(),b'external');self.assertTrue(self.tx.journal.exists())
  with self.assertRaisesRegex(ValueError,'drift'):self.tx.recover()
  self.assertEqual((self.root/'manifest').read_bytes(),b'external')
 def test_precommit_and_committed_recovery(self):
  for stage,target in [('common-written',self.old),('caddy-starting',self.old),('caddy-applied',self.old),('committed',self.new)]:
   for k,v in self.old.items():(self.root/k).write_bytes(v)
   self.a.timer={'active':True,'enabled':True}
   def phase(p):
    if p==stage:raise RuntimeError('injected interruption')
   with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
   self.tx.recover();self.assertEqual(self.a.read(),target);self.assertEqual(self.a.timer,{'active':True,'enabled':True});self.assertFalse(self.tx.journal.exists())
 def test_beta_preflight_failure_does_not_create_journal(self):
  def unavailable():raise ValueError('beta services not ready')
  self.a.beta_ready=unavailable
  with self.assertRaisesRegex(ValueError,'not ready'):self.tx.apply(self.old,self.new)
  self.assertFalse(self.tx.journal.exists());self.assertEqual(self.a.read(),self.old)
 def test_real_managed_webctl_adapter_dispatch(self):
  old={'common':b'old-code','manifest':b'profile="old"\n','caddy':b'old-caddy'};new={'common':b'new-code','manifest':b'profile="new"\n','caddy':b'new-caddy'}
  paths={k:self.root/k for k in old}
  for k,v in old.items():paths[k].write_bytes(v)
  def generator(source):return types.SimpleNamespace(source=source,module=types.SimpleNamespace(validate=lambda data:None,caddy=lambda *args:None,dump=lambda *args:None))
  class Timer:
   def __init__(self):self.state={'active':True,'enabled':True}
   def snapshot(self):return dict(self.state)
   def stop_if_active(self,prior):self.state['active']=False
   def assert_quiescent(self):pass
   def assert_recoverable(self,prior):assert self.state in (prior,{**prior,'active':False})
   def restore(self,prior):self.state=dict(prior)
  class Ctl:
   caddy=dump=validate=None
   def run(self,*args,**kwargs):return None
   def caddy_apply(self,data,mode):assert mode=='production';paths['caddy'].write_bytes(new['caddy'] if data['profile']=='new' else old['caddy'])
  timer=Timer();ctl=Ctl();adapter=m.ManagedWebctlAdapter(ctl,generator(old['common']),generator(new['common']),paths,timer,contextlib.nullcontext,lambda:None,lambda:None,lambda:None,lambda:None,lambda data,**kwargs:None,lambda:None,lambda old:'fixture-backup')
  tx=m.Transaction(adapter,self.root/'managed-journal');tx.apply(old,new);self.assertEqual(adapter.read(),new);self.assertEqual(timer.state,{'active':True,'enabled':True});self.assertIsNone(ctl.caddy)
  original=(ctl.caddy,ctl.dump,ctl.validate,ctl.run)
  for action in ('start','enable','unmask','restart'):
   def tries_to_change(data,mode):ctl.run(['/usr/bin/systemctl',action,'caddy.service'])
   ctl.caddy_apply=tries_to_change
   with self.assertRaisesRegex(ValueError,'not allowed'):adapter.apply_caddy(new['manifest'],new['common'])
   self.assertEqual((ctl.caddy,ctl.dump,ctl.validate,ctl.run),original)
  def reload_only(data,mode):ctl.run(['/usr/bin/systemctl','reload','caddy.service'])
  ctl.caddy_apply=reload_only;adapter.apply_caddy(new['manifest'],new['common'])
 def test_systemd_timer_only_restores_prior_active_state(self):
  state={'active':True,'enabled':True};commands=[]
  def run(argv):
   commands.append(argv)
   if argv[1]=='show' and argv[2].endswith('.timer'):return 'ActiveState='+('active' if state['active'] else 'inactive')+'\nUnitFileState='+('enabled' if state['enabled'] else 'disabled')+'\n'
   if argv[1]=='show':return 'ActiveState=failed\nMainPID=0\nControlPID=0\n'
   if argv[1]=='stop':state['active']=False
   if argv[1]=='start':state['active']=True
   return ''
  timer=m.SystemdTimer(run);prior=timer.snapshot();timer.stop_if_active(prior);timer.assert_quiescent();timer.restore(prior);self.assertEqual(state,prior);self.assertFalse(any('enable' in c or 'disable' in c or 'reset-failed' in c for c in commands))
 def test_timer_refuses_nonzero_renewal_process(self):
  timer=m.SystemdTimer(lambda argv:'ActiveState=failed\nMainPID=123\nControlPID=0\n')
  with self.assertRaisesRegex(ValueError,'not quiescent'):timer.assert_quiescent()
 def test_recovery_stops_active_timer_before_any_mutation(self):
  def phase(p):
   if p=='journaled':raise RuntimeError('interrupt before timer stop')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  self.assertTrue(self.a.timer['active']);self.a.calls.clear();self.tx.recover()
  self.assertEqual(self.a.calls[:2],['stop-timer','renewal-checked']);self.assertEqual(self.a.read(),self.old);self.assertTrue(self.a.timer['active'])
 def test_recovery_retains_journal_if_renewal_running(self):
  def phase(p):
   if p=='common-written':raise RuntimeError('interrupt')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  before=self.a.read()
  def busy():raise ValueError('renewal busy')
  self.a.assert_renewal_quiescent=busy
  with self.assertRaisesRegex(ValueError,'renewal busy'):self.tx.recover()
  self.assertEqual(self.a.read(),before);self.assertTrue(self.tx.journal.exists())
 def test_committed_recovery_requires_beta_readiness(self):
  def phase(p):
   if p=='committed':raise RuntimeError('interrupt')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  def unavailable():raise ValueError('beta unavailable')
  self.a.beta_ready=unavailable
  with self.assertRaisesRegex(ValueError,'beta unavailable'):self.tx.recover()
  self.assertEqual(self.a.read(),self.new);self.assertTrue(self.tx.journal.exists())
 def test_prepared_recovery_does_not_require_beta_readiness(self):
  def phase(p):
   if p=='common-written':raise RuntimeError('interrupt')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  def unavailable():raise ValueError('beta unavailable')
  self.a.beta_ready=unavailable;self.tx.recover();self.assertEqual(self.a.read(),self.old);self.assertFalse(self.tx.journal.exists())
 def test_recovery_refuses_timer_drift_between_checks(self):
  def phase(p):
   if p=='common-written':raise RuntimeError('interrupt')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  before=self.a.read()
  def change_after_first_check(prior):self.a.timer={'active':False,'enabled':False}
  self.a.timer_assert_recoverable=change_after_first_check
  with self.assertRaisesRegex(ValueError,'Timer state changed'):self.tx.recover()
  self.assertEqual(self.a.read(),before);self.assertTrue(self.tx.journal.exists())
 def test_recovery_retains_journal_if_main_health_fails(self):
  def phase(p):
   if p=='common-written':raise RuntimeError('interrupt')
  with self.assertRaises(RuntimeError):self.tx.apply(self.old,self.new,phase=phase)
  def unhealthy():raise ValueError('main unhealthy')
  self.a.check_main_health=unhealthy
  with self.assertRaisesRegex(ValueError,'main unhealthy'):self.tx.recover()
  self.assertEqual(self.a.read(),self.old);self.assertTrue(self.tx.journal.exists())
 def test_activation_main_health_failure_retains_journal(self):
  def unhealthy():raise ValueError('main unhealthy')
  self.a.check_main_health=unhealthy
  with self.assertRaisesRegex(ValueError,'main unhealthy'):self.tx.apply(self.old,self.new)
  self.assertEqual(self.a.read(),self.new);self.assertTrue(self.tx.journal.exists())
if __name__=='__main__':unittest.main(verbosity=2)
