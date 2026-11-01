"""Server-only folder primitive; no browser or public endpoint is enabled."""
import os,sys,tempfile,time,unittest,uuid
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.policy import Denied,Principal
from gateway_service.user_store import UserStore,Conflict
from gateway_service import folder_manifest as manifest_module

class FolderMove(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);self.state=root/'state';self.data=root/'data';self.state.mkdir(mode=0o700);self.data.mkdir(mode=0o700)
  self.a=Principal('user:'+str(uuid.uuid4()),'a','registered',{},int(time.time())+600);self.b=Principal('user:'+str(uuid.uuid4()),'b','registered',{},int(time.time())+600)
  self.store=UserStore(self.state,self.data);self.store.ensure_user(self.a);self.store.ensure_user(self.b)
  self.store.mkdir(self.a,'source');self.store.mkdir(self.a,'source/empty');self.store.mkdir(self.a,'source/nested');self.store.put(self.a,'source/nested/a.txt',b'hello')
  self.home=self.data/'users'/uuid.UUID(self.a.sub[5:]).hex
 def tearDown(self):self.tmp.cleanup()
 def manifest(self):return self.store.folder_manifest(self.a,'source')['sha256']
 def move(self,op,digest=None,phase=lambda p:None):return self.store.move_folder(self.a,'source','target',manifest_sha256=digest or self.manifest(),operation_id=op,phase=phase)
 def test_manifest_and_move_idempotent(self):
  value=self.store.folder_manifest(self.a,'source');self.assertEqual([e['path'] for e in value['entries']],['empty','nested','nested/a.txt']);self.assertEqual(len(value['sha256']),64)
  op=str(uuid.uuid4());self.assertEqual(self.move(op,value['sha256'])['state'],'done');self.assertEqual(self.store.read(self.a,'target/nested/a.txt')['bytes'],b'hello');self.assertTrue((self.home/'target/empty').is_dir())
  self.assertEqual(self.move(op,value['sha256'])['state'],'done')
  with self.assertRaises(Conflict):self.store.move_folder(self.a,'source','different',manifest_sha256=value['sha256'],operation_id=op)
 def test_interrupted_before_and_after_rename(self):
  for stage in ('prepared','renamed'):
   with self.subTest(stage=stage):
    digest=self.manifest();op=str(uuid.uuid4())
    def crash(p):
     if p==stage:raise RuntimeError('simulated crash')
    with self.assertRaises(RuntimeError):self.move(op,digest,crash)
    self.store=UserStore(self.state,self.data)
    self.assertEqual(self.move(op,digest)['state'],'done');self.assertEqual(self.store.read(self.a,'target/nested/a.txt')['bytes'],b'hello')
    os.rename(self.home/'target',self.home/'source')
 def test_real_process_exit_recovers_receipt(self):
  for stage in ('prepared','renamed'):
   with self.subTest(stage=stage):
    digest=self.manifest();op=str(uuid.uuid4());pid=os.fork()
    if pid==0:
     def crash(phase):
      if phase==stage:os._exit(77)
     try:self.move(op,digest,crash)
     finally:os._exit(78)
    _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),77)
    self.store=UserStore(self.state,self.data)
    self.assertEqual(self.move(op,digest)['state'],'done')
    self.assertEqual(self.store.read(self.a,'target/nested/a.txt')['bytes'],b'hello')
    os.rename(self.home/'target',self.home/'source')
 def test_missing_marker_blocks_identical_recovery(self):
  digest=self.manifest();op=str(uuid.uuid4())
  def crash(phase):
   if phase=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.move(op,digest,crash)
  os.removexattr(self.home/'source','user.codiserver.folder_move')
  os.rename(self.home/'source',self.home/'target')
  with self.assertRaises(Conflict):self.move(op,digest)
  self.assertEqual(self.store.read(self.a,'target/nested/a.txt')['bytes'],b'hello')
 def test_changed_source_and_collision_preserve_both(self):
  digest=self.manifest();self.store.put(self.a,'source/new.txt',b'new')
  with self.assertRaises(Conflict):self.move(str(uuid.uuid4()),digest)
  self.store.mkdir(self.a,'target');op=str(uuid.uuid4())
  with self.assertRaises(Conflict):self.move(op,self.manifest())
  self.assertTrue((self.home/'source/new.txt').exists());self.assertTrue((self.home/'target').is_dir())
 def test_lost_reply_ambiguous_destination_never_adopted(self):
  digest=self.manifest();op=str(uuid.uuid4())
  def crash(p):
   if p=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.move(op,digest,crash)
  self.store.mkdir(self.a,'target');self.store.put(self.a,'target/other.txt',b'keep')
  with self.assertRaises(Conflict):self.move(op,digest)
  self.assertTrue((self.home/'source').is_dir());self.assertEqual(self.store.read(self.a,'target/other.txt')['bytes'],b'keep')
 def test_mutation_after_rename_is_ambiguous(self):
  digest=self.manifest();op=str(uuid.uuid4())
  def alter(p):
   if p=='renamed':
    (self.home/'target/nested/a.txt').write_bytes(b'host changed')
    raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.move(op,digest,alter)
  with self.assertRaises(Conflict):self.move(op,digest)
  self.assertEqual((self.home/'target/nested/a.txt').read_bytes(),b'host changed')
 def test_change_during_prepare_does_not_move(self):
  digest=self.manifest();op=str(uuid.uuid4())
  def mutate(phase):
   if phase=='prepared':(self.home/'source/nested/a.txt').write_bytes(b'new value')
  with self.assertRaises(Conflict):self.move(op,digest,mutate)
  self.assertTrue((self.home/'source').is_dir());self.assertFalse((self.home/'target').exists())
  self.assertEqual((self.home/'source/nested/a.txt').read_bytes(),b'new value')
 def test_no_replace_concurrent_moves(self):
  import concurrent.futures
  self.store.mkdir(self.a,'second');self.store.put(self.a,'second/b.txt',b'other')
  inputs=[('source',self.manifest()),('second',self.store.folder_manifest(self.a,'second')['sha256'])]
  def attempt(item):
   name,digest=item
   try:self.store.move_folder(self.a,name,'target',manifest_sha256=digest,operation_id=str(uuid.uuid4()));return name
   except (Denied,OSError):return None
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,inputs))
  self.assertEqual(sum(x is not None for x in results),1)
  if results[0]:self.assertTrue((self.home/'target/nested/a.txt').is_file());self.assertTrue((self.home/'second/b.txt').is_file())
  else:self.assertTrue((self.home/'target/b.txt').is_file());self.assertTrue((self.home/'source/nested/a.txt').is_file())
 def test_destination_depth_checked_before_rename(self):
  parent='/'.join(['d']*15)
  for i in range(1,16):self.store.mkdir(self.a,'/'.join(['d']*i))
  with self.assertRaises(Denied):self.store.move_folder(self.a,'source',parent+'/target',manifest_sha256=self.manifest(),operation_id=str(uuid.uuid4()))
  self.assertTrue((self.home/'source/nested/a.txt').exists())
 def test_marker_is_invisible_to_file_listing_and_conflicts_are_preserved(self):
  before=self.store.list(self.a,'source');inventory=self.store.inventory(self.a);digest=self.manifest();op=str(uuid.uuid4())
  def crash(phase):
   if phase=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.move(op,digest,crash)
  self.assertEqual(self.store.list(self.a,'source'),before);self.assertEqual(self.store.inventory(self.a),inventory);self.assertEqual(self.manifest(),digest)
  marker=os.getxattr(self.home/'source','user.codiserver.folder_move');self.assertEqual(len(marker),32)
  with self.assertRaises(Conflict):self.move(str(uuid.uuid4()),digest)
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move'),marker)
 def test_backup_copy_cannot_impersonate_prepared_move(self):
  import shutil
  digest=self.manifest();op=str(uuid.uuid4())
  def crash(phase):
   if phase=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.move(op,digest,crash)
  shutil.copytree(self.home/'source',self.home/'target',copy_function=shutil.copy2)
  self.assertNotEqual((self.home/'source').stat().st_ino,(self.home/'target').stat().st_ino)
  shutil.rmtree(self.home/'source')
  with self.assertRaises(Conflict):self.move(op,digest)
  self.assertEqual((self.home/'target/nested/a.txt').read_bytes(),b'hello')
 def test_exit_after_marker_before_receipt_fails_closed(self):
  digest=self.manifest();op=str(uuid.uuid4());pid=os.fork()
  if pid==0:
   def crash(phase):
    if phase=='marked':os._exit(77)
   try:self.move(op,digest,crash)
   finally:os._exit(78)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),77)
  self.store=UserStore(self.state,self.data)
  with self.assertRaises(Conflict):self.move(op,digest)
  self.assertEqual((self.home/'source/nested/a.txt').read_bytes(),b'hello');self.assertFalse((self.home/'target').exists())
 def test_no_replace_if_host_creates_destination_after_preparation(self):
  digest=self.manifest();op=str(uuid.uuid4())
  def collide(phase):
   if phase=='prepared':
    (self.home/'target').mkdir(mode=0o700)
    (self.home/'target'/'keep.txt').write_bytes(b'keep')
  with self.assertRaises(OSError):self.move(op,digest,collide)
  self.assertEqual((self.home/'target'/'keep.txt').read_bytes(),b'keep')
  self.assertEqual((self.home/'source/nested/a.txt').read_bytes(),b'hello')
 def test_committed_receipt_cleans_leftover_marker_on_next_move(self):
  digest=self.manifest();op=str(uuid.uuid4());pid=os.fork()
  if pid==0:
   def crash(phase):
    if phase=='committed':os._exit(77)
   try:self.move(op,digest,crash)
   finally:os._exit(78)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),77)
  self.store=UserStore(self.state,self.data);self.assertEqual(self.move(op,digest)['state'],'done')
  self.assertEqual(len(os.getxattr(self.home/'target','user.codiserver.folder_move')),32)
  target_digest=self.store.folder_manifest(self.a,'target')['sha256']
  self.assertEqual(self.store.move_folder(self.a,'target','next',manifest_sha256=target_digest,operation_id=str(uuid.uuid4()))['state'],'done')
  self.assertEqual(self.store.read(self.a,'next/nested/a.txt')['bytes'],b'hello')
  with self.assertRaises(OSError):os.getxattr(self.home/'next','user.codiserver.folder_move')
 def test_unsupported_xattrs_fail_before_rename(self):
  import errno
  digest=self.manifest()
  with patch('gateway_service.user_store.os.setxattr',side_effect=OSError(errno.ENOTSUP,'not supported')):
   with self.assertRaises(OSError):self.move(str(uuid.uuid4()),digest)
  self.assertEqual((self.home/'source/nested/a.txt').read_bytes(),b'hello');self.assertFalse((self.home/'target').exists())
 def test_security_and_bounds(self):
  digest=self.manifest();op=str(uuid.uuid4())
  for dst in ('source/sub','../outside','source','/absolute'):
   with self.subTest(dst=dst),self.assertRaises(Denied):self.store.move_folder(self.a,'source',dst,manifest_sha256=digest,operation_id=op)
  with self.assertRaises((Denied,FileNotFoundError)):self.store.folder_manifest(self.b,'source')
  self.store.set_permission(self.a.sub,'rename',False)
  with self.assertRaises(Denied):self.move(op,digest)
  self.store.set_permission(self.a.sub,'rename',True)
  os.symlink('/tmp',self.home/'source/link')
  with self.assertRaises(Denied):self.manifest()
  (self.home/'source/link').unlink()
  with patch.object(manifest_module,'MAX_ENTRIES',2),self.assertRaises(Denied):self.manifest()
  with patch.object(manifest_module,'MAX_BYTES',4),self.assertRaises(Denied):self.manifest()

if __name__=='__main__':unittest.main()
