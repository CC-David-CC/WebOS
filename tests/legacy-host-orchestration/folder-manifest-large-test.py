"""Bounded server-only manifest checks; no routes or production state."""
import hashlib,json,os,sys,tempfile,time,tracemalloc,unittest,uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service import folder_manifest as module
from gateway_service.policy import Denied,Principal
from gateway_service.user_store import UserStore,Conflict

class LargeFolderManifest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.root.chmod(0o700)
  self.fd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 def tearDown(self):os.close(self.fd);self.tmp.cleanup()
 def sparse(self,name,size):
  fd=os.open(self.root/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  try:os.ftruncate(fd,size)
  finally:os.close(fd)
 def test_actual_folder_above_128_mib_is_streamed(self):
  size=68*1024*1024;self.sparse('a',size);self.sparse('b',size)
  with patch.object(module,'MAX_TOTAL_BYTES',module.MAX_BYTES),self.assertRaises(Denied):module.folder_manifest(self.fd)
  original=os.read;requests=[]
  def read(fd,n):requests.append(n);return original(fd,n)
  tracemalloc.start()
  try:
   with patch.object(module.os,'read',side_effect=read):entries,digest=module.folder_manifest(self.fd)
   _,peak=tracemalloc.get_traced_memory()
  finally:tracemalloc.stop()
  self.assertTrue(requests);self.assertLessEqual(max(requests),65536);self.assertLess(peak,16*1024*1024)
  h=hashlib.sha256();chunk=bytes(65536)
  for _ in range(size//len(chunk)):h.update(chunk)
  self.assertEqual(entries,[{'path':name,'directory':False,'sha256':h.hexdigest()} for name in ('a','b')])
  canonical=json.dumps(entries,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();self.assertEqual(digest,hashlib.sha256(canonical).hexdigest())
 def test_independent_file_and_total_bounds(self):
  self.sparse('a',6);self.sparse('b',6)
  with patch.object(module,'MAX_BYTES',5),self.assertRaisesRegex(Denied,'file size'):module.folder_manifest(self.fd)
  with patch.object(module,'MAX_BYTES',8),patch.object(module,'MAX_TOTAL_BYTES',11),self.assertRaisesRegex(Denied,'total byte'):module.folder_manifest(self.fd)
  with patch.object(module,'MAX_BYTES',8),patch.object(module,'MAX_TOTAL_BYTES',12):self.assertEqual(len(module.folder_manifest(self.fd)[0]),2)
 def test_actual_oversized_file_rejected_before_read(self):
  self.sparse('oversized',128*1024*1024+1)
  with patch.object(module.os,'read',side_effect=AssertionError('oversized file must not be read')):
   with self.assertRaisesRegex(Denied,'file size'):module.folder_manifest(self.fd)
 def test_mutation_during_hash_fails_closed(self):
  self.sparse('a',131072);original=os.read;changed=False
  def read(fd,n):
   nonlocal changed
   result=original(fd,n)
   if result and not changed:
    changed=True
    with open(self.root/'a','r+b',buffering=0) as target:target.write(b'changed')
   return result
  with patch.object(module.os,'read',side_effect=read),self.assertRaisesRegex(Denied,'changed'):module.folder_manifest(self.fd)
  self.assertTrue(changed)

class LargeFolderMove(unittest.TestCase):
 def test_large_tree_stale_check_and_interrupted_retry(self):
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);state=root/'state';data=root/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
   principal=Principal('user:'+str(uuid.uuid4()),'large','registered',{},int(time.time())+600)
   store=UserStore(state,data);store.ensure_user(principal);store.mkdir(principal,'source')
   home=data/'users'/uuid.UUID(principal.sub[5:]).hex
   for name in ('a','b'):
    fd=os.open(home/'source'/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:os.ftruncate(fd,68*1024*1024)
    finally:os.close(fd)
   old=store.folder_manifest(principal,'source')['sha256']
   with open(home/'source'/'b','r+b',buffering=0) as target:target.seek(-1,os.SEEK_END);target.write(b'X')
   with self.assertRaises(Conflict):store.move_folder(principal,'source','target',manifest_sha256=old,operation_id=str(uuid.uuid4()))
   self.assertTrue((home/'source'/'a').exists());self.assertFalse((home/'target').exists())
   digest=store.folder_manifest(principal,'source')['sha256'];op=str(uuid.uuid4())
   def interrupt(phase):
    if phase=='prepared':raise RuntimeError('simulated interruption')
   with self.assertRaisesRegex(RuntimeError,'interruption'):store.move_folder(principal,'source','target',manifest_sha256=digest,operation_id=op,phase=interrupt)
   store=UserStore(state,data)
   self.assertEqual(store.move_folder(principal,'source','target',manifest_sha256=digest,operation_id=op)['state'],'done')
   self.assertEqual(store.move_folder(principal,'source','target',manifest_sha256=digest,operation_id=op)['state'],'done')
   self.assertEqual((home/'target'/'a').stat().st_size,68*1024*1024)
   with open(home/'target'/'b','rb') as item:item.seek(-1,os.SEEK_END);self.assertEqual(item.read(),b'X')

if __name__=='__main__':unittest.main()
