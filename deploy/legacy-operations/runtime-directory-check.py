#!/usr/bin/env python3
"""Private external runtime boundary, including actual cross-process exclusion."""
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service.runtime import PrivateRuntime

class RuntimeTests(unittest.TestCase):
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory(prefix='codi-runtime-policy-');self.folder=Path(self.temporary.name);self.source=self.folder/'release';self.source.mkdir();self.runtime=self.folder/'runtime'
 def tearDown(self):self.temporary.cleanup()
 def open(self,path=None):return PrivateRuntime(self.runtime if path is None else path,self.source)
 def test_private_paths_are_separate_and_cache_is_disposable(self):
  with self.open() as paths:
   public=paths.public
   for path in [paths.root,paths.state,paths.steward_private,public]:self.assertEqual(path.stat().st_mode&0o777,0o700)
   self.assertFalse(paths.state.is_relative_to(public));(paths.state/'marker').write_text('persistent');(public/'index.html').write_text('temporary')
  self.assertFalse(public.exists());self.assertTrue((self.runtime/'state/marker').exists())
  with self.open() as paths:self.assertNotEqual(paths.public,public);self.assertEqual((paths.state/'marker').read_text(),'persistent')
 def test_relative_and_dotdot_paths_refused(self):
  for path in [Path('relative'),self.folder/'unused/../runtime']:
   with self.assertRaises(ValueError):
    with self.open(path):pass
 def test_source_overlap_both_directions_refused(self):
  for path in [self.source,self.source/'state',self.folder]:
   with self.assertRaises(ValueError):
    with self.open(path):pass
 def test_existing_public_directory_mode_is_not_silently_changed(self):
  self.runtime.mkdir(mode=0o755)
  with self.assertRaises(ValueError):
   with self.open():pass
  self.assertEqual(self.runtime.stat().st_mode&0o777,0o755)
 def test_symlink_in_root_path_refused(self):
  (self.folder/'alias').symlink_to(self.folder,target_is_directory=True)
  with self.assertRaises(ValueError):
   with self.open(self.folder/'alias/runtime'):pass
 def test_child_symlink_and_regular_file_in_place_of_directory_refused(self):
  self.runtime.mkdir(mode=0o700);(self.runtime/'state').symlink_to(self.source,target_is_directory=True)
  with self.assertRaises(ValueError):
   with self.open():pass
  (self.runtime/'state').unlink();(self.runtime/'state').write_text('file')
  with self.assertRaises(ValueError):
   with self.open():pass
 def test_symlink_hardlink_and_public_state_file_refused(self):
  with self.open():pass
  target=self.runtime/'state/unsafe';target.symlink_to(self.source)
  with self.assertRaises(ValueError):
   with self.open():pass
  target.unlink();original=self.folder/'private';original.write_text('private');original.chmod(0o600);os.link(original,target)
  with self.assertRaises(ValueError):
   with self.open():pass
  target.unlink();target.write_text('exposed');target.chmod(0o644)
  with self.assertRaises(ValueError):
   with self.open():pass
 def test_fifo_lock_refused_without_blocking(self):
  self.runtime.mkdir(mode=0o700);os.mkfifo(self.runtime/'.runtime.lock',0o600)
  with self.assertRaises(ValueError):
   with self.open():pass
 def test_cross_process_lock_and_restart(self):
  command=[sys.executable,'-B','-c',"import sys;sys.path.insert(0,sys.argv[1]);from origin_service.runtime import PrivateRuntime;\nwith PrivateRuntime(sys.argv[2],sys.argv[3]):pass",str(ROOT),str(self.runtime),str(self.source)]
  with self.open():
   child=subprocess.run(command,capture_output=True,timeout=5);self.assertNotEqual(child.returncode,0);self.assertIn(b'already in use',child.stderr)
  child=subprocess.run(command,capture_output=True,timeout=5);self.assertEqual(child.returncode,0,child.stderr.decode())
 def test_lock_symlink_refused(self):
  self.runtime.mkdir(mode=0o700);(self.runtime/'.runtime.lock').symlink_to(self.folder/'outside')
  with self.assertRaises(ValueError):
   with self.open():pass
  self.assertFalse((self.folder/'outside').exists())
 def test_failure_releases_lock_and_restores_umask(self):
  old=os.umask(0o022)
  try:
   with self.assertRaisesRegex(RuntimeError,'fixture failure'):
    with self.open():raise RuntimeError('fixture failure')
   actual=os.umask(0o022);self.assertEqual(actual,0o022)
   with self.open():pass
  finally:os.umask(old)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(RuntimeTests))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Private runtime path policy and actual process locks; not a public deployment','sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['origin_service/runtime.py','scripts/runtime-directory-check.py']}}
 checks=ROOT/'.build/checks';checks.mkdir(parents=True,exist_ok=True);(checks/'runtime-directory-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
