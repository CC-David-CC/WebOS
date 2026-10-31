"""Bounded account-scoped batch version reads retain ordinary file permissions."""
import hashlib,os,sys,tempfile,unittest,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.user_store import UserStore
from gateway_service.policy import Principal,Denied
from gateway_service.http import FileGateway

class BatchVersions(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
  self.store=UserStore(state,data);self.a=Principal('user:'+str(uuid.uuid4()),'a','registered',{},9999999999);self.b=Principal('user:'+str(uuid.uuid4()),'b','registered',{},9999999999)
  self.store.ensure_user(self.a);self.store.ensure_user(self.b);self.store.put(self.a,'a.txt',b'abc');self.store.put(self.a,'b.txt',b'defg');self.store.put(self.b,'a.txt',b'other')
 def tearDown(self):self.tmp.cleanup()
 def test_hashes_are_scoped_and_bounded(self):
  a=self.store.version_batch(self.a,['a.txt','b.txt'],maximum_total_bytes=3);self.assertEqual(a,[{'path':'a.txt','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()},{'path':'b.txt','deferred':True}])
  self.assertEqual(self.store.version_batch(self.b,['a.txt'])[0]['sha256'],hashlib.sha256(b'other').hexdigest())
  self.assertEqual(self.store.version_batch(self.b,['b.txt']),[{'path':'b.txt','deferred':True}])
 def test_bad_requests_are_rejected(self):
  for values in ([],['a.txt']*2,['../escape'],[''],[[]],['x']*17):
   with self.subTest(values=values),self.assertRaises(Denied):self.store.version_batch(self.a,values)
  gateway=FileGateway.__new__(FileGateway);gateway.store=self.store
  self.assertEqual(gateway._dispatch(self.a,{'resource':'my-files','operation':'versions','paths':['a.txt']})['entries'][0]['bytes'],3)
  for body in ({'resource':'other','operation':'versions','paths':['a.txt']},{'resource':'my-files','operation':'versions','paths':['a.txt'],'extra':1}):
   with self.assertRaises((ValueError,Denied)):gateway._dispatch(self.a,body)
 def test_restrictive_modes_and_symlinks_are_never_followed(self):
  home=self.store.users_path/uuid.UUID(self.a.sub[5:]).hex;readonly=home/'private.txt';readonly.write_bytes(b'x');readonly.chmod(0o400)
  with self.assertRaises(Denied):self.store.version_batch(self.a,['private.txt'])
  self.assertEqual(readonly.stat().st_mode&0o777,0o400)
  (home/'link.txt').symlink_to(home/'a.txt')
  with self.assertRaises(OSError):self.store.version_batch(self.a,['link.txt'])
 def test_anonymous_and_disabled_read_permissions_are_denied(self):
  anon=Principal('anonymous','x','anonymous',{},9999999999)
  with self.assertRaises(Denied):self.store.version_batch(anon,['a.txt'])
  with self.store.db() as db:db.execute("UPDATE permissions SET allowed=0 WHERE subject=? AND operation='read'",(self.a.sub,));db.commit()
  with self.assertRaises(Denied):self.store.version_batch(self.a,['a.txt'])
if __name__=='__main__':unittest.main()
