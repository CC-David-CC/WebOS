#!/usr/bin/env python3
"""Actual release export and refusal of mutated disposable release copies."""
import hashlib,importlib.util,json,os,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)

class ReleaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.fixture=tempfile.TemporaryDirectory(prefix='connected-release-');cls.folder=Path(cls.fixture.name);cls.release=cls.folder/'original';cls.record=exporter.export(cls.release)
 @classmethod
 def tearDownClass(cls):cls.fixture.cleanup()
 def setUp(self):self.copy=self.folder/('case-'+self._testMethodName);shutil.copytree(self.release,self.copy)
 def manifests(self):return json.loads((self.copy/'connected-release.json').read_text()),json.loads((self.copy/'release.json').read_text())
 def rewrite(self,native,public):
  (self.copy/'release.json').write_text(json.dumps(public));native['files']['release.json']=exporter.record(self.copy/'release.json');(self.copy/'connected-release.json').write_text(json.dumps(native))
 def test_actual_export_verifies_and_contains_required_runtime_notices(self):
  self.assertEqual(exporter.verify(self.release),self.record);self.assertTrue((self.release/'licenses/runtime/LICENSE-glibc').is_file());self.assertTrue((self.release/'scripts/serve-connected-discovery.py').is_file())
 def test_real_frozen_profile10_still_verifies(self):
  baseline=ROOT/'.build/releases/connected-account-menu-r2'
  self.assertEqual(exporter.verify(baseline)['manifestSHA256'],'7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625')
 def test_real_frozen_profile11_still_verifies(self):
  self.assertEqual(exporter.verify(ROOT/'.build/releases/connected-files-r2')['manifestSHA256'],'99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0')
 def test_real_frozen_profile13_still_verifies(self):
  self.assertEqual(exporter.verify(ROOT/'.build/releases/connected-policy-recovery-r1')['manifestSHA256'],'ce00294efbc58d835308fd4d4703e6422c199f40c5ee110f56d5c67296138442')
 def test_profile14_preference_implementation_is_private_and_required(self):
  native,public=self.manifests();name='origin_service/ice_preference.py'
  self.assertIn(name,native['files']);self.assertNotIn(name,public['files']);self.assertFalse(exporter.public_name(name))
  (self.copy/name).unlink();del native['files'][name];self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_real_frozen_profile12_still_verifies(self):
  self.assertEqual(exporter.verify(ROOT/'.build/releases/connected-network-r3')['manifestSHA256'],'cd3b0967917a3be6d9113739a997910f21b88ed659565c613c2455333c7241f5')
 def test_profile13_maintenance_operator_is_private_and_required(self):
  native,public=self.manifests();name='scripts/desktop-maintenance.py'
  self.assertIn(name,native['files']);self.assertNotIn(name,public['files']);self.assertFalse(exporter.public_name(name))
  self.assertIn('assets/desktop/offline-worker.js',public['files']);self.assertIn('assets/desktop/apps.json',public['files'])
  (self.copy/name).unlink();del native['files'][name];self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_profile11_contract_survives_new_native_and_server_allowlists(self):
  from unittest.mock import patch
  import origin_service.release as contract
  import serve
  self.assertEqual(set(contract.PUBLIC),serve.PUBLIC);self.assertEqual(set(contract.NETWORK),serve.NETWORK);self.assertEqual(set(contract.RUNTIME),serve.RUNTIME)
  with patch.object(contract,'NATIVE',contract.NATIVE|{'guest_service/worker.py'}),patch.object(serve,'PUBLIC',serve.PUBLIC|{'private-new-file.py'}):
   self.assertEqual(exporter.verify(ROOT/'.build/releases/connected-files-r2')['manifestSHA256'],'99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0')
   self.assertFalse(contract.public_name('private-new-file.py'));self.assertNotIn('guest_service/worker.py',contract.V11_NATIVE)
 def test_current_requires_file_authority_and_management_code(self):
  native,public=self.manifests();self.assertEqual(native['version'],'codi-connected-development/14')
  for name in ['origin_service/gateway_authority.py','origin_service/files_management.py','gateway_service/auth.py']:
   self.assertIn(name,native['files']);self.assertNotIn(name,public['files'])
  name='origin_service/files_management.py';(self.copy/name).unlink();del native['files'][name];self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_profile12_private_network_modules_are_required_but_not_public(self):
  native,public=self.manifests()
  for name in ['origin_service/guest_authority.py','origin_service/network_management.py','guest_service/runtime.py','guest_service/frontend.py','guest_service/client.mjs','guest_service/coordinator.py']:
   self.assertIn(name,native['files']);self.assertNotIn(name,public['files']);self.assertFalse(exporter.public_name(name))
  name='guest_service/frontend.py';(self.copy/name).unlink();del native['files'][name];self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_public_manifest_cannot_expose_network_sdk_or_control_module(self):
  native,public=self.manifests()
  for name in ['guest_service/client.mjs','origin_service/network_management.py']:
   public['files'][name]=native['files'][name]
  self.rewrite(native,public)
  with self.assertRaisesRegex(ValueError,'Nonpublic'):exporter.verify(self.copy)
 def test_changed_file_refused(self):
  (self.copy/'app.js').write_text('tampered')
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_missing_runtime_file_refused(self):
  (self.copy/'.build/v86/v86.wasm').unlink()
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_unlisted_private_file_refused(self):
  (self.copy/'issuer.pem').write_text('fixture')
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_symlink_and_hardlink_refused(self):
  target=self.copy/'style.css';target.unlink();target.symlink_to(self.release/'style.css')
  with self.assertRaises(ValueError):exporter.verify(self.copy)
  target.unlink();os.link(self.release/'style.css',target)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_manifests_cannot_reclassify_private_key_as_public(self):
  native,public=self.manifests();name='assets/issuer.pem';target=self.copy/name;target.write_text('fixture');public['files'][name]=exporter.record(target);native['files'][name]=exporter.record(target);self.rewrite(native,public)
  with self.assertRaisesRegex(ValueError,'Nonpublic'):exporter.verify(self.copy)
 def test_notices_cannot_be_removed_from_both_manifests(self):
  native,public=self.manifests();name='licenses/runtime/LICENSE-glibc';(self.copy/name).unlink();del public['files'][name];del native['files'][name];self.rewrite(native,public)
  with self.assertRaisesRegex(ValueError,'notices missing'):exporter.verify(self.copy)
 def test_missing_native_module_cannot_be_removed_from_manifest(self):
  native,public=self.manifests();name='origin_service/runtime.py';(self.copy/name).unlink();del native['files'][name];self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_existing_destination_is_preserved(self):
  before=(self.copy/'connected-release.json').read_bytes()
  with self.assertRaises(ValueError):exporter.export(self.copy)
  self.assertEqual((self.copy/'connected-release.json').read_bytes(),before)
 def test_public_source_cannot_be_output(self):
  with self.assertRaisesRegex(ValueError,'public source'):exporter.export(ROOT/'assets'/'forbidden-release-output')
 def test_production_authority_label_refused(self):
  native,public=self.manifests();native['authorityClass']='official';self.rewrite(native,public)
  with self.assertRaises(ValueError):exporter.verify(self.copy)
 def test_output_permissions_do_not_depend_on_operators_umask(self):
  restrictive=self.folder/'restrictive';previous=os.umask(0o077)
  try:exporter.export(restrictive)
  finally:os.umask(previous)
  for path in [restrictive,*restrictive.rglob('*')]:self.assertEqual(path.stat().st_mode&0o777,0o755 if path.is_dir() else 0o644,str(path))

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseTests))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Real profile14 export/private preference/maintenance and network allowlists, frozen profile10/11/12/13 compatibility and mutated artifact refusal; not public deployment or authenticity proof','sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['origin_service/release.py','scripts/export-connected.py','scripts/export-desktop.py','scripts/connected-release-check.py']}}
 checks=ROOT/'.build/checks';checks.mkdir(parents=True,exist_ok=True);(checks/'connected-release-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
