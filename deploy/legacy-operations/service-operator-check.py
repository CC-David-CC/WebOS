#!/usr/bin/env python3
"""Operator input/file/unit invariants; real installed units are checked separately."""
import hashlib,importlib.util,json,os,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('managed_service_operator',ROOT/'scripts/manage-services.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class OperatorChecks(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.directory=Path(self.temp.name);self.file=self.directory/'input';self.file.write_bytes(b'input');self.file.chmod(0o600)
  self.config={'release':'/srv/codi/release','stateRoot':'/var/lib/codi/ksu','python':'/opt/codi/venv/bin/python','instance':'codi-ksu','origin':'https://ksu.codes','basePath':'/hidden','ports':{'issuer':8118,'steward':8119,'guest':8132}}
  release=self.directory/'release';release.mkdir();(release/'connected-release.json').write_text(json.dumps({'version':'codi-connected-development/13'}));self.config['release']=str(release)
 def network(self):
  self.config['guestNetwork']={'configFile':'/etc/codi-guest-network/ksu/managed.json','frontendFile':'/etc/codi-guest-network/ksu/frontend.json','frontendSHA256':'1'*64,'policySHA256':'2'*64}
 def test_private_regular_input(self):self.assertEqual(module.read_owned(self.file,os.geteuid(),0o600),b'input')
 def test_wrong_owner(self):
  with self.assertRaises(ValueError):module.read_owned(self.file,os.geteuid()+1,0o600)
 def test_public_mode_refused_for_private(self):
  self.file.chmod(0o644)
  with self.assertRaises(ValueError):module.read_owned(self.file,os.geteuid(),0o600)
 def test_hardlink_refused(self):
  os.link(self.file,self.directory/'linked')
  with self.assertRaises(ValueError):module.read_owned(self.file,os.geteuid(),0o600)
 def test_symlink_refused(self):
  linked=self.directory/'linked';linked.symlink_to(self.file)
  with self.assertRaises(ValueError):module.read_owned(linked,os.geteuid(),0o600)
 def test_symlink_ancestor_refused(self):
  linked=self.directory/'linked';linked.symlink_to(self.directory,target_is_directory=True)
  with self.assertRaises(ValueError):module.read_owned(linked/'input',os.geteuid(),0o600)
 def test_fifo_refused_without_blocking(self):
  fifo=self.directory/'fifo';os.mkfifo(fifo,0o600)
  with self.assertRaises(ValueError):module.read_owned(fifo,os.geteuid(),0o600)
 def test_bounded_input(self):
  with self.assertRaises(ValueError):module.read_owned(self.file,os.geteuid(),0o600,limit=4)
 def test_systemd_metacharacters_refused(self):
  for value in ['%i','$SECRET','a b','a\nb','a;b','`id`','"quote"',"'quote'"]:
   with self.subTest(value=value),self.assertRaises(ValueError):module.quote(value)
 def test_empty_root_prefix_preserved_as_argument(self):
  self.config['basePath']='';text=module.render(self.config,'issuer').decode();self.assertIn('"--base-path" ""',text)
 def test_bootstrap_has_no_discovery_and_no_restart(self):
  text=module.render(self.config,'issuer-bootstrap').decode();self.assertIn('User=codi-issuer\n',text);self.assertIn('Restart=no\n',text);self.assertNotIn('--discovery-policy',text);self.assertNotIn('[Install]',text)
 def test_steward_writes_only_its_private_and_public_output(self):
  text=module.render(self.config,'steward').decode();self.assertIn('ReadWritePaths=/var/lib/codi/ksu/steward /var/lib/codi/ksu/public/steward\n',text);self.assertNotIn('/operator/',text)
 def test_guest_requires_ping_and_has_no_persistent_write_paths(self):
  text=module.render(self.config,'guest').decode();self.assertIn('"--require-ping"',text);self.assertNotIn('ReadWritePaths=',text);self.assertIn('CapabilityBoundingSet=\n',text);self.assertIn('AmbientCapabilities=\n',text)
 def test_issuer_reads_public_policy_and_writes_only_issuer(self):
  text=module.render(self.config,'issuer').decode();self.assertIn('ReadWritePaths=/var/lib/codi/ksu/issuer\n',text);self.assertIn('/public/origin-discovery.json',text);self.assertNotIn('/operator/',text);self.assertNotIn('/steward/service.pem',text)
 def test_managed_issuer_requires_existing_key_and_accounts(self):
  text=module.render(self.config,'issuer').decode();self.assertIn('AssertPathExists=/var/lib/codi/ksu/issuer/state/issuer.pem\n',text);self.assertIn('AssertPathExists=/var/lib/codi/ksu/issuer/state/accounts.sqlite3\n',text)
 def test_unsafe_operator_paths_refused(self):
  for value in ['/tmp','relative','/srv/a/../b','/srv/%i','/srv/a b']:
   with self.subTest(value=value),self.assertRaises(ValueError):module.path(value)
 def test_network_guest_has_three_credentials_and_guard_dependency(self):
  self.network();text=module.render(self.config,'guest').decode()
  self.assertEqual(text.count('\nLoadCredential='),3);self.assertIn('BindsTo=codi-net-ksu-guard.service\n',text);self.assertIn('After=codi-net-ksu-guard.service\n',text)
  for role in ['anonymous','registered']:self.assertIn('LoadCredential='+role+'-wire.secret:/etc/codi-guest-network/ksu/credentials/'+role+'.secret\n',text)
  self.assertIn('"--network-control" "/etc/codi-guest-network/ksu/frontend.json"',text);self.assertIn('"--network-control-sha256" "'+('1'*64)+'"',text)
  self.assertNotIn('ReadWritePaths=',text)
 def test_network_issuer_has_policy_flag_but_no_worker_secrets(self):
  self.network();text=module.render(self.config,'issuer').decode();self.assertIn('"--guest-network-policy-sha256" "'+('2'*64)+'"',text);self.assertNotIn('-wire.secret',text);self.assertNotIn('BindsTo=',text)
 def test_bootstrap_never_enables_network_or_file_authorities(self):
  self.network();self.config['userFiles']={'enabled':'fixture'};text=module.render(self.config,'issuer-bootstrap').decode();self.assertNotIn('--guest-network-policy',text);self.assertNotIn('--user-files',text);self.assertNotIn('LoadCredential=',text)
 def test_network_off_retains_only_cookie_and_no_guard(self):
  text=module.render(self.config,'guest').decode();self.assertEqual(text.count('\nLoadCredential='),1);self.assertNotIn('BindsTo=',text);self.assertNotIn('--network-control',text)
 def test_notice_is_read_only_root_policy_for_profile13_online_issuer(self):
  text=module.render(self.config,'issuer').decode();self.assertIn('"--maintenance-notice" "/var/lib/codi/ksu/public/desktop-maintenance.json"',text)
  self.assertIn('ReadWritePaths=/var/lib/codi/ksu/issuer\n',text);self.assertNotIn('--maintenance-notice',module.render(self.config,'issuer-bootstrap').decode())
  release=Path(self.config['release']);(release/'connected-release.json').write_text(json.dumps({'version':'codi-connected-development/12'}))
  self.assertNotIn('--maintenance-notice',module.render(self.config,'issuer').decode())

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(OperatorChecks))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Native operator file/input/unit invariants; actual installed lifecycle and browsers are separate receipts','sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/manage-services.py','origin_service/release.py','scripts/service-operator-check.py']}}
 output=ROOT/'.build/checks/service-operator-result.json'
 if output.exists():output.rename(output.with_name('service-operator-before-'+str(time.time_ns())+'.json'))
 output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if not result.wasSuccessful():raise SystemExit(1)
