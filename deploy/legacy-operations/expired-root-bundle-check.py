#!/usr/bin/env python3
"""Bundle content, mutation and extra-file refusal checks."""
import importlib.util,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('expired_export',ROOT/'scripts/export-expired-root-recovery.py');export=importlib.util.module_from_spec(spec);spec.loader.exec_module(export)
class Bundle(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='codi-root-bundle-');self.folder=Path(self.tmp.name)/'bundle';shutil.copytree(ROOT/'.build/recovery-operators/expired-root-r1',self.folder)
 def tearDown(self):self.tmp.cleanup()
 def test_exact_bundle_passes(self):self.assertEqual(export.verify(self.folder)['status'],'PASS')
 def test_modified_source_is_refused(self):
  with (self.folder/'expired_root_managed.py').open('a') as f:f.write('\n# altered\n')
  with self.assertRaises(ValueError):export.verify(self.folder)
 def test_extra_and_missing_files_are_refused(self):
  (self.folder/'extra').write_text('x')
  with self.assertRaises(ValueError):export.verify(self.folder)
  (self.folder/'extra').unlink();(self.folder/'run.py').unlink()
  with self.assertRaises(ValueError):export.verify(self.folder)
 def test_linked_file_is_refused(self):
  path=self.folder/'run.py';path.unlink();path.symlink_to(self.folder/'expired_root_steps.py')
  with self.assertRaises(ValueError):export.verify(self.folder)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Bundle));sys.exit(not result.wasSuccessful())
