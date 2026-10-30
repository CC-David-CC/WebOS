"""External files become private without broadening restrictive permissions."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
ROOT=Path(__file__).resolve().parents[1]/'active-system'
sys.path.insert(0,str(ROOT))
from gateway_service.user_store import UserStore
from gateway_service.policy import Principal,Denied

class ExternalFiles(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();root=Path(self.temp.name)
  self.state=root/'state';self.data=root/'data'
  for p in (self.state,self.data):p.mkdir(mode=0o700)
  self.store=UserStore(self.state,self.data);self.principal=Principal('user:'+str(uuid.uuid4()),'sid','registered',{},9999999999)
  self.home=self.store.users_path/self.store.ensure_user(self.principal)['storageId']
 def tearDown(self):self.temp.cleanup()
 def external(self,name,mode):
  file=self.home/name;file.write_bytes(b'content');file.chmod(mode);return file
 def test_private_mode_is_tightened_without_changing_contents(self):
  file=self.external('flag.gif',0o664)
  self.assertEqual(self.store.read(self.principal,'flag.gif')['bytes'],b'content')
  self.assertEqual(file.stat().st_mode&0o777,0o600)
 def test_quota_scan_also_tightens_external_file(self):
  file=self.external('external.txt',0o644)
  self.store.put(self.principal,'second.txt',b'new')
  self.assertEqual(file.stat().st_mode&0o777,0o600)
 def test_restrictive_mode_is_not_broadened(self):
  file=self.external('readonly.txt',0o400)
  with self.assertRaises(Denied):self.store.read(self.principal,'readonly.txt')
  self.assertEqual(file.stat().st_mode&0o777,0o400)
 def test_hardlinks_are_not_changed(self):
  file=self.external('source.txt',0o664);os.link(file,self.home/'link.txt')
  with self.assertRaises(Denied):self.store.read(self.principal,'source.txt')
  self.assertEqual(file.stat().st_mode&0o777,0o664)
if __name__=='__main__':unittest.main()
