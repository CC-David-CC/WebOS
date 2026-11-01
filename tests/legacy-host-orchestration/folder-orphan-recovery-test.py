"""Local-only orphan marker inspection and cleanup; no HTTP route is enabled."""
import os,sys,tempfile,time,unittest,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.policy import Denied,Principal
from gateway_service.user_store import UserStore,Conflict

class OrphanRecovery(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);self.state=root/'state';self.data=root/'data';self.state.mkdir(mode=0o700);self.data.mkdir(mode=0o700)
  self.a=Principal('user:'+str(uuid.uuid4()),'a','registered',{},int(time.time())+600);self.b=Principal('user:'+str(uuid.uuid4()),'b','registered',{},int(time.time())+600)
  self.store=UserStore(self.state,self.data);self.store.ensure_user(self.a);self.store.ensure_user(self.b);self.store.mkdir(self.a,'source');self.store.put(self.a,'source/note.txt',b'keep')
  self.home=self.data/'users'/uuid.UUID(self.a.sub[5:]).hex;self.digest=self.store.folder_manifest(self.a,'source')['sha256'];self.op=str(uuid.uuid4())
 def tearDown(self):self.tmp.cleanup()
 def create_marker(self,stage='marked'):
  pid=os.fork()
  if pid==0:
   def crash(phase):
    if phase==stage:os._exit(77)
   try:self.store.move_folder(self.a,'source','target',manifest_sha256=self.digest,operation_id=self.op,phase=crash)
   finally:os._exit(78)
  _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),77);self.store=UserStore(self.state,self.data)
 def inspect(self):return self.store.inspect_orphan_folder_marker(self.a,'source')
 def clear(self,inspection,**kw):return self.store.clear_orphan_folder_marker(self.a,inspection,operator_confirmed=True,**kw)
 def test_inspection_confirmation_and_cleanup(self):
  self.create_marker();i=self.inspect();self.assertTrue(i['present']);self.assertFalse(i['receipt']);self.assertEqual(i['cleanup'],'none');self.assertEqual(i['sha256'],self.digest);self.assertEqual(len(i['marker']),64)
  with self.assertRaises(Denied):self.store.clear_orphan_folder_marker(self.a,i)
  self.assertEqual(self.clear(i),{'state':'done'});self.assertEqual(self.clear(i),{'state':'done'})
  self.assertIsNone(self.inspect()['marker']);self.assertEqual((self.home/'source/note.txt').read_bytes(),b'keep')
  self.assertEqual(self.store.move_folder(self.a,'source','target',manifest_sha256=self.digest,operation_id=str(uuid.uuid4()))['state'],'done')
 def test_stale_manifest_or_marker_is_rejected(self):
  self.create_marker();i=self.inspect();(self.home/'source/note.txt').write_bytes(b'changed')
  with self.assertRaises(Conflict):self.clear(i)
  self.assertEqual((self.home/'source/note.txt').read_bytes(),b'changed');self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move').hex(),i['marker'])
  i=self.inspect();os.setxattr(self.home/'source','user.codiserver.folder_move',b'foreign-marker')
  with self.assertRaises(Conflict):self.clear(i)
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move'),b'foreign-marker')
 def test_replaced_folder_and_foreign_marker_are_preserved(self):
  self.create_marker();i=self.inspect()
  os.rename(self.home/'source',self.home/'old-source');(self.home/'source').mkdir(mode=0o700)
  (self.home/'source/note.txt').write_bytes(b'keep');os.chmod(self.home/'source/note.txt',0o600)
  os.setxattr(self.home/'source','user.codiserver.folder_move',bytes.fromhex(i['marker']))
  with self.assertRaises(Conflict):self.clear(i)
  self.assertEqual((self.home/'old-source/note.txt').read_bytes(),b'keep')
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move').hex(),i['marker'])
 def test_no_marker_and_unconfirmed_cleanup_cannot_create_intent(self):
  clean=self.inspect();self.assertIsNone(clean['marker'])
  with self.assertRaises(Denied):self.clear(clean)
  self.assertIsNone(self.inspect()['marker'])
 def test_receipted_marker_cannot_be_cleared_as_orphan(self):
  self.create_marker('prepared');i=self.inspect();self.assertTrue(i['receipt'])
  with self.assertRaises(Denied):self.clear(i)
  fake=dict(i,receipt=False)
  with self.assertRaises(Conflict):self.clear(fake)
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move').hex(),i['marker'])
  self.assertEqual(self.store.move_folder(self.a,'source','target',manifest_sha256=self.digest,operation_id=self.op)['state'],'done')
 def test_real_crash_during_cleanup_resumes_and_blocks_moves(self):
  for stage in ('cleanup-prepared','cleanup-removed'):
   with self.subTest(stage=stage):
    if stage=='cleanup-prepared':self.create_marker()
    else:
     self.op=str(uuid.uuid4());self.create_marker()
    i=self.inspect();pid=os.fork()
    if pid==0:
     def crash(phase):
      if phase==stage:os._exit(77)
     try:self.clear(i,phase=crash)
     finally:os._exit(78)
    _,status=os.waitpid(pid,0);self.assertEqual(os.waitstatus_to_exitcode(status),77);self.store=UserStore(self.state,self.data)
    with self.assertRaises(Conflict):self.store.move_folder(self.a,'source','target',manifest_sha256=self.digest,operation_id=str(uuid.uuid4()))
    retry=self.inspect();self.assertEqual(retry['marker'],i['marker']);self.assertEqual(retry['cleanup'],'pending');self.assertEqual(retry['present'],stage=='cleanup-prepared')
    self.assertEqual(self.clear(retry),{'state':'done'});self.assertIsNone(self.inspect()['marker']);self.assertEqual((self.home/'source/note.txt').read_bytes(),b'keep')
 def test_pending_cleanup_blocks_overlapping_folder_moves(self):
  self.store.mkdir(self.a,'source/nested');self.store.mkdir(self.a,'source/nested/inside');self.store.mkdir(self.a,'other')
  source_hash=self.store.folder_manifest(self.a,'source')['sha256'];inside_hash=self.store.folder_manifest(self.a,'source/nested/inside')['sha256'];other_hash=self.store.folder_manifest(self.a,'other')['sha256']
  os.setxattr(self.home/'source/nested','user.codiserver.folder_move',os.urandom(32))
  inspected=self.store.inspect_orphan_folder_marker(self.a,'source/nested')
  def crash(phase):
   if phase=='cleanup-prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.clear(inspected,phase=crash)
  for source,destination,digest in [('source','target',source_hash),('source/nested/inside','target',inside_hash),('other','source/nested/new',other_hash),('other','source',other_hash)]:
   with self.subTest(source=source,destination=destination),self.assertRaisesRegex(Conflict,'cleanup overlaps'):
    self.store.move_folder(self.a,source,destination,manifest_sha256=digest,operation_id=str(uuid.uuid4()))
  self.assertTrue((self.home/'source/nested').is_dir());self.assertTrue((self.home/'other').is_dir())
  self.assertEqual(self.clear(inspected),{'state':'done'})
 def test_unreceipted_descendant_marker_blocks_ancestor_move(self):
  self.store.mkdir(self.a,'source/nested');self.store.mkdir(self.a,'source/nested/inside');self.store.mkdir(self.a,'other');digest=self.store.folder_manifest(self.a,'source')['sha256'];inside=self.store.folder_manifest(self.a,'source/nested/inside')['sha256'];other=self.store.folder_manifest(self.a,'other')['sha256']
  os.setxattr(self.home/'source/nested','user.codiserver.folder_move',os.urandom(32))
  for source,destination,sha,reason in [('source','target',digest,'descendant folder'),('source/nested/inside','target',inside,'ancestor folder'),('other','source/nested/new',other,'ancestor folder')]:
   with self.subTest(source=source,destination=destination),self.assertRaisesRegex(Conflict,reason):self.store.move_folder(self.a,source,destination,manifest_sha256=sha,operation_id=str(uuid.uuid4()))
  self.assertTrue((self.home/'source/nested').is_dir());self.assertFalse((self.home/'target').exists())
  self.assertEqual(self.clear(self.store.inspect_orphan_folder_marker(self.a,'source/nested')),{'state':'done'})
  self.assertEqual(self.store.move_folder(self.a,'source','target',manifest_sha256=digest,operation_id=str(uuid.uuid4()))['state'],'done')
 def test_prepared_move_blocks_overlapping_sources_and_destinations(self):
  self.store.mkdir(self.a,'source/nested');self.store.mkdir(self.a,'source/nested/inside');self.store.mkdir(self.a,'other')
  hashes={p:self.store.folder_manifest(self.a,p)['sha256'] for p in ('source','source/nested','source/nested/inside','other')}
  op=str(uuid.uuid4())
  def crash(phase):
   if phase=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.store.move_folder(self.a,'source/nested','target',manifest_sha256=hashes['source/nested'],operation_id=op,phase=crash)
  for source,destination in [('source','elsewhere'),('source/nested/inside','elsewhere'),('other','source/nested/new'),('other','target/child')]:
   with self.subTest(source=source,destination=destination),self.assertRaisesRegex(Conflict,'prepared folder move overlaps'):
    self.store.move_folder(self.a,source,destination,manifest_sha256=hashes[source],operation_id=str(uuid.uuid4()))
  self.assertEqual(self.store.move_folder(self.a,'source/nested','target',manifest_sha256=hashes['source/nested'],operation_id=op)['state'],'done')
 def test_orphan_cleanup_rejects_overlapping_prepared_move(self):
  self.store.mkdir(self.a,'source/nested');digest=self.store.folder_manifest(self.a,'source/nested')['sha256']
  def crash(phase):
   if phase=='prepared':raise RuntimeError('stop')
  with self.assertRaises(RuntimeError):self.store.move_folder(self.a,'source/nested','target',manifest_sha256=digest,operation_id=str(uuid.uuid4()),phase=crash)
  marker=os.urandom(32);os.setxattr(self.home/'source','user.codiserver.folder_move',marker)
  i=self.inspect();self.assertFalse(i['receipt'])
  with self.assertRaisesRegex(Conflict,'prepared folder move overlaps'):self.clear(i)
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move'),marker)
 def test_host_change_during_cleanup_fails_closed(self):
  self.create_marker();i=self.inspect()
  def change(phase):
   if phase=='cleanup-prepared':(self.home/'source/note.txt').write_bytes(b'new')
  with self.assertRaises(Conflict):self.clear(i,phase=change)
  self.assertEqual((self.home/'source/note.txt').read_bytes(),b'new');self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move').hex(),i['marker'])
  with self.assertRaises(Conflict):self.store.move_folder(self.a,'source','target',manifest_sha256=self.store.folder_manifest(self.a,'source')['sha256'],operation_id=str(uuid.uuid4()))
 def test_authorization_and_inspection_shape(self):
  self.create_marker();i=self.inspect()
  with self.assertRaises((Denied,FileNotFoundError)):self.store.inspect_orphan_folder_marker(self.b,'source')
  with self.assertRaises(Denied):self.clear(dict(i,extra=True))
  self.store.set_permission(self.a.sub,'rename',False)
  with self.assertRaises(Denied):self.clear(i)
  self.assertEqual(os.getxattr(self.home/'source','user.codiserver.folder_move').hex(),i['marker'])

if __name__=='__main__':unittest.main()
