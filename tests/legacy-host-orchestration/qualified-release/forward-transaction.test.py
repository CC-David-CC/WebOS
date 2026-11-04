"""Disposable fault test; simulated host adapter, no production action."""
import contextlib,fcntl,hashlib,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'research/beta-isolated-hosting/ops'))
from beta_transaction import Transaction
spec=importlib.util.spec_from_file_location('main_forward',Path(__file__).with_name('forward-transaction.py'));main=importlib.util.module_from_spec(spec);spec.loader.exec_module(main)
OLD=main.OLD_SELECTOR;NEW=main.NEW_SELECTOR
class Ctl:
 def __init__(self):self.write=lambda p,b,*a,**k:Path(p).write_bytes(b.encode() if isinstance(b,str) else b)
 def _check_floor_record(self):assert self._floor_guard_active
 def _assert_v2_beta(self,data):assert data['codi_beta_simplified']=='beta'
 def validate(self,data):assert len(data['sites'])==1
 def dump(self,data):return 'codi_beta_simplified = "beta"\n[[sites]]\ndomain = "ksu.codes"\ncodi_simplified = "'+data['sites'][0]['codi_simplified']+'"\n'
 def caddy(self,data,mode):return '# production\nksu='+data['sites'][0]['codi_simplified']+'\nbeta.ksu.codes {\n static beta\n}\n'
 def _beta_block(self,text):return text[text.index('beta.ksu.codes {'):]
def data(selector):return {'codi_beta_simplified':'beta','sites':[{'domain':'ksu.codes','codi_simplified':selector}]}
class Fixture:
 def __init__(self,path):
  self.t=Path(path);self.ctl=Ctl();self.paths={x:self.t/x for x in ('common','manifest','caddy')};self.lock=None;self.fail=False;self.reloads=[]
  self.old={'common':b'fixed generator','manifest':self.ctl.dump(data(OLD)).encode(),'caddy':self.ctl.caddy(data(OLD),'production').encode()};self.new={'common':b'fixed generator','manifest':self.ctl.dump(data(NEW)).encode(),'caddy':self.ctl.caddy(data(NEW),'production').encode()}
  for k,p in self.paths.items():p.write_bytes(self.old[k])
  main.PINS={'common':main.digest(self.old['common']),'old_manifest':main.digest(self.old['manifest']),'new_manifest':main.digest(self.new['manifest']),'old_caddy':main.digest(self.old['caddy']),'new_caddy':main.digest(self.new['caddy'])}
 @contextlib.contextmanager
 def held(self):
  fd=os.open(self.t/'lock',os.O_RDWR|os.O_CREAT,0o600);fcntl.flock(fd,fcntl.LOCK_EX);self.lock=fd
  try:yield
  finally:self.lock=None;os.close(fd)
 def check_lock(self):
  if self.lock is None:raise ValueError('lock missing')
 def read(self):return {k:p.read_bytes() for k,p in self.paths.items()}
 def beta_ready(self):pass
 def timer_snapshot(self):return {'active':False,'enabled':False}
 def timer_stop_if_active(self,v):pass
 def assert_renewal_quiescent(self):pass
 def timer_assert_recoverable(self,v):pass
 def timer_restore(self,v):pass
 def backup(self,v):return str(self.t/'protected-test-backup')
 def replace_source(self,key,value):self.paths[key].write_bytes(value)
 def apply_caddy(self,manifest,common,recovery=False):
  expected=self.ctl.caddy(__import__('tomllib').loads(manifest.decode()),'production');old=self.paths['caddy'].read_bytes();self.ctl.write(self.paths['caddy'],expected)
  if self.fail:self.ctl.write(self.paths['caddy'],old);raise RuntimeError('injected failed reload')
  self.reloads.append(expected)
 def check_main_health(self):pass
 def check_health(self):pass
class Tests(unittest.TestCase):
 def test_killed_boundaries_recover_forward(self):
  for stage in ('journaled','timer-stopped','common-written','manifest-written','caddy-starting','caddy-applied','committed','timer-restored'):
   with self.subTest(stage=stage),tempfile.TemporaryDirectory() as t:
    io=Fixture(t);wrapped=main.ForwardAdapter(io,lambda:None,lambda:None);j=Path(t)/'journal';tx=Transaction(wrapped,j);pid=os.fork()
    if pid==0:
     try:
      with io.held():tx.apply_gate(io.old,io.new,phase=lambda x:os._exit(17) if x==stage else None)
     except BaseException:os._exit(18)
     os._exit(19)
    _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),17);self.assertTrue(j.exists())
    with io.held():main.recover(tx,wrapped,io.old,io.new,OLD,NEW)
    self.assertEqual(io.read(),io.new);self.assertFalse(j.exists())
 def test_failed_reload_cannot_restore_old_and_recovery_is_forward(self):
  with tempfile.TemporaryDirectory() as t:
   io=Fixture(t);io.fail=True;wrapped=main.ForwardAdapter(io,lambda:None,lambda:None);j=Path(t)/'journal';tx=Transaction(wrapped,j)
   with io.held():
    with self.assertRaisesRegex(RuntimeError,'Refused Caddy rollback'):main.apply(tx,wrapped,io.old,io.new,OLD,NEW)
   self.assertTrue(j.exists());self.assertEqual(io.paths['caddy'].read_bytes(),io.new['caddy']);io.fail=False
   with io.held():main.recover(tx,wrapped,io.old,io.new,OLD,NEW)
   self.assertEqual(io.read(),io.new);self.assertFalse(j.exists());self.assertNotIn(io.old['caddy'].decode(),io.reloads)
 def test_drift_and_unrelated_changes_refused(self):
  with tempfile.TemporaryDirectory() as t:
   io=Fixture(t);wrapped=main.ForwardAdapter(io,lambda:None,lambda:None);tx=Transaction(wrapped,Path(t)/'journal')
   with self.assertRaises(ValueError):main.apply(tx,wrapped,io.old,io.new,OLD,NEW)
   bad=dict(io.new);bad['manifest']=bad['manifest'].replace(b'"beta"',b'"other"')
   with io.held():
    with self.assertRaises(ValueError):main.apply(tx,wrapped,io.old,bad,OLD,NEW)
   self.assertEqual(io.read(),io.old)
if __name__=='__main__':unittest.main(verbosity=2)
