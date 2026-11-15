#!/usr/bin/env python3
"""Code transition metadata boundaries; actual installed transitions are separate."""
import copy,hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service import deployment
spec=importlib.util.spec_from_file_location('deployment_operator',ROOT/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)

class Boundaries(unittest.TestCase):
 def setUp(self):
  self.root=Path(tempfile.mkdtemp(prefix='codi-deployment-policy-',dir='/srv'));self.addCleanup(shutil.rmtree,self.root)
  self.control=self.root/'control';self.control.mkdir(mode=0o700);self.config_path=self.control/'managed.json'
  self.config={'version':'codi-managed-instance/2','maintenance':1,'instance':'codi-deployment-policy','stateRoot':str(self.root/'state'),'unitDir':'/etc/systemd/system','origin':'https://example.invalid','basePath':'/hidden','release':str(self.root/'before'),'python':str(self.root/'venv/bin/python'),'manifestSHA256':'a'*64,'ports':{'issuer':8118,'steward':8119,'guest':8132}}
  self.after={**self.config,'release':str(self.root/'after'),'manifestSHA256':'b'*64}
  for name in ['before','after']:
   folder=self.root/name;folder.mkdir();(folder/'connected-release.json').write_text(json.dumps({'version':'codi-connected-development/7'}))
 def test_ice_profile_boundary_requires_relay_only_in_both_directions(self):
  for old,new in [(13,14),(14,13)]:
   (self.root/'before/connected-release.json').write_text(json.dumps({'version':'codi-connected-development/'+str(old)}))
   (self.root/'after/connected-release.json').write_text(json.dumps({'version':'codi-connected-development/'+str(new)}))
   before={**self.config,'turn':{'iceTransportPolicy':'all'}};after={**self.after,'turn':before['turn']}
   with self.assertRaisesRegex(ValueError,'relay-only'):self.pair(current=before,before=before,after=after)
   before['turn']={'iceTransportPolicy':'relay'};after['turn']=before['turn'];self.pair(current=before,before=before,after=after)
 def pair(self,current=None,before=None,after=None):return deployment.validate_pair(op,current or self.config,before or self.config,after or self.after)
 def write_history(self,**updates):
  value={'version':'codi-code-history/1','instance':self.config['instance'],'entries':[]};value.update(updates);op.atomic(self.control/'code-history.json',json.dumps(value).encode())
 def journal(self,**updates):
  value={'version':'codi-code-transition/1','kind':'upgrade','activeRoles':['issuer'],'before':self.config,'after':self.after};value.update(updates);op.atomic(self.control/'maintenance.json',json.dumps(value).encode())
 def test_only_code_environment_digest_may_change(self):self.pair()
 def test_recovery_accepts_either_config_after_partial_write(self):self.pair(current=self.after)
 def test_unknown_current_config_refused(self):
  with self.assertRaises(ValueError):self.pair(current={**self.config,'release':'/srv/unknown'})
 def test_identity_state_ports_mount_and_unit_directory_cannot_change(self):
  for name,value in [('stateRoot','/var/lib/other'),('instance','other'),('origin','https://foreign.invalid'),('basePath',''),('ports',{}),('unitDir','/tmp')]:
   with self.subTest(field=name),self.assertRaises(ValueError):self.pair(after={**self.after,name:value})
 def test_unknown_metadata_field_refused(self):
  with self.assertRaises(ValueError):self.pair(after={**self.after,'extra':True})
 def test_checkpoint_required(self):
  before={**self.config,'version':'codi-managed-instance/1'};after={**self.after,'version':'codi-managed-instance/1'}
  with self.assertRaises(ValueError):self.pair(current=before,before=before,after=after)
 def test_nonstandard_unit_directory_refused_even_when_unchanged(self):
  before={**self.config,'unitDir':'/srv/units'};after={**self.after,'unitDir':'/srv/units'}
  with self.assertRaises(ValueError):self.pair(current=before,before=before,after=after)
 def test_state_cannot_contain_candidate(self):
  with self.assertRaises(ValueError):deployment.target(op,self.config,Path(self.config['stateRoot'])/'code',Path(self.config['python']))
 def test_candidate_cannot_contain_environment(self):
  with self.assertRaises(ValueError):deployment.target(op,self.config,self.root,self.root/'venv/bin/python')
 def test_home_and_temporary_candidates_refused(self):
  for source in ['/home/nonexistent-codi-code','/root/nonexistent-codi-code','/tmp/nonexistent-codi-code','/var/tmp/nonexistent-codi-code','/run/nonexistent-codi-code']:
   with self.subTest(source=source),self.assertRaises(ValueError):deployment.target(op,self.config,Path(source),Path(self.config['python']))
 def test_new_history_is_empty_and_instance_bound(self):self.assertEqual(deployment.history(op,self.config,self.config_path),{'version':'codi-code-history/1','instance':self.config['instance'],'entries':[]})
 def test_invalid_history_metadata_refused(self):
  for updates in [{'version':'unknown'},{'instance':'other'},{'entries':{}},{'entries':[{}]*17},{'extra':True}]:
   self.write_history(**updates)
   with self.subTest(updates=updates),self.assertRaises(ValueError):deployment.history(op,self.config,self.config_path)
 def test_public_history_permissions_refused(self):
  self.write_history();(self.control/'code-history.json').chmod(0o644)
  with self.assertRaises(ValueError):deployment.history(op,self.config,self.config_path)
 def test_history_bounded_and_repeated_commit_deduplicated(self):
  for index in range(20):
   journal={'id':str(index),'kind':'upgrade','before':self.config,'after':self.after,'activeRoles':['issuer']};deployment.record(op,self.config,self.config_path,journal,'applied')
  deployment.record(op,self.config,self.config_path,journal,'applied')
  entries=deployment.history(op,self.config,self.config_path)['entries'];self.assertEqual(len(entries),16);self.assertEqual([entry['id'] for entry in entries],[str(index) for index in range(4,20)])
 def test_recovery_rejects_non_code_journal(self):
  for updates in [{'version':'codi-maintenance/1'},{'kind':'restore'}]:
   self.journal(**updates)
   with self.subTest(updates=updates),self.assertRaises(ValueError):deployment.recover(op,self.config,self.config_path)
 def test_recovery_rejects_duplicate_unknown_and_bootstrap_roles(self):
  for roles in [['issuer','issuer'],['unknown'],['issuer-bootstrap'],'issuer']:
   self.journal(activeRoles=roles)
   with self.subTest(roles=roles),self.assertRaises(ValueError):deployment.recover(op,self.config,self.config_path)

if __name__=='__main__':
 if os.geteuid()!=0:
  child=subprocess.run(['sudo','-n',sys.executable,'-B',str(Path(__file__).resolve()),'--root-run'],capture_output=True,text=True,timeout=30)
  if child.stderr:sys.stderr.write(child.stderr)
  if not child.stdout:raise SystemExit(child.returncode or 1)
  report=json.loads(child.stdout);(ROOT/'.build/checks/deployment-policy-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(child.returncode)
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Boundaries))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Root-owned code metadata/history/path boundaries; real installed transitions are separate receipts','sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['origin_service/deployment.py','scripts/manage-services.py','scripts/deployment-policy-check.py']}}
 print(json.dumps(report));raise SystemExit(0 if result.wasSuccessful() else 1)
