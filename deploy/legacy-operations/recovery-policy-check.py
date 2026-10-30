#!/usr/bin/env python3
"""Root-owned dummy snapshot path/permission tests; real recovery is separate."""
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from origin_service import maintenance
spec=importlib.util.spec_from_file_location('maintenance_operator',ROOT/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
class Boundaries(unittest.TestCase):
 def setUp(self):
  self.root=Path(tempfile.mkdtemp(prefix='codi-recovery-policy-',dir='/srv'));self.addCleanup(shutil.rmtree,self.root)
  self.snapshot=self.root/'snapshot';self.snapshot.mkdir(mode=0o700);self.control=self.root/'control';self.control.mkdir(mode=0o700);self.config_path=self.control/'managed.json'
  self.config={'instance':'codi-recovery-policy','stateRoot':str(self.root/'live')}
  self.fake=types.SimpleNamespace(path=op.path,read_owned=op.read_owned,ROLES=(),inactive=lambda *args:None)
  files={}
  for name,(owner,mode) in maintenance.FILES.items():
   file=self.snapshot/'state'/name;file.parent.mkdir(parents=True,exist_ok=True,mode=0o700);file.write_bytes(('dummy:'+name).encode());file.chmod(0o600)
   files[name]={'owner':owner,'mode':mode,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
  for folder in self.snapshot.rglob('*'):
   if folder.is_dir():folder.chmod(0o700)
  self.manifest={'version':'codi-managed-backup/1','created':1,'config':{},'binding':{'dummy':True},'files':files};self.write_manifest()
  self.binding=patch.object(maintenance,'binding',return_value={'dummy':True});self.binding.start();self.addCleanup(self.binding.stop)
 def write_manifest(self):
  raw=json.dumps(self.manifest).encode();file=self.snapshot/'backup.json';file.write_bytes(raw);file.chmod(0o600);self.expected=hashlib.sha256(raw).hexdigest()
 def verify(self):return maintenance.verify_backup(self.fake,self.snapshot,self.expected)
 def key(self):return self.snapshot/'state/issuer/state/issuer.pem'
 def test_owned_bounded_dummy_snapshot(self):self.assertEqual(len(self.verify()['files']),13)
 def test_changed_bytes_refused(self):
  self.key().write_bytes(b'changed')
  with self.assertRaises(ValueError):self.verify()
 def test_extra_file_refused(self):
  file=self.snapshot/'extra';file.write_bytes(b'extra');file.chmod(0o600)
  with self.assertRaises(ValueError):self.verify()
 def test_missing_file_refused(self):
  self.key().unlink()
  with self.assertRaises(ValueError):self.verify()
 def test_symlink_refused(self):
  self.key().unlink();self.key().symlink_to('/etc/hosts')
  with self.assertRaises(ValueError):self.verify()
 def test_hardlink_refused(self):
  os.link(self.key(),self.root/'alias')
  with self.assertRaises(ValueError):self.verify()
 def test_fifo_refused_without_blocking(self):
  self.key().unlink();os.mkfifo(self.key(),0o600)
  with self.assertRaises(ValueError):self.verify()
 def test_public_backup_directory_refused(self):
  self.snapshot.chmod(0o755)
  with self.assertRaises(ValueError):self.verify()
 def test_public_data_file_refused(self):
  self.key().chmod(0o644)
  with self.assertRaises(ValueError):self.verify()
 def test_public_child_directory_refused(self):
  self.key().parent.chmod(0o755)
  with self.assertRaises(ValueError):self.verify()
 def test_wrong_manifest_digest_refused(self):
  self.expected='0'*64
  with self.assertRaises(ValueError):self.verify()
 def test_manifest_traversal_name_refused(self):
  self.manifest['files']['../outside']=self.manifest['files'].pop('issuer/state/issuer.pem');self.write_manifest()
  with self.assertRaises(ValueError):self.verify()
 def test_invalid_trusted_recovery_floor_refused_before_state_access(self):
  for value in [True,0,-1,2**53-1,'3',1.5]:
   with self.subTest(value=value),self.assertRaises(ValueError):maintenance.restore(self.fake,self.config,self.config_path,self.snapshot,self.expected,value,3600)
 def test_pending_journal_blocks_online_operations(self):
  (self.control/'maintenance.json').write_text('{}')
  with self.assertRaises(ValueError):maintenance.require_clean(self.fake,self.config_path)
 def journal(self,stage):
  data={'version':'codi-maintenance/1','action':'restore','state':self.config['stateRoot'],'staged':str(stage),'quarantine':str(self.root/'.quarantine-fixture')};file=self.control/'maintenance.json';file.write_text(json.dumps(data));file.chmod(0o600)
 def test_journal_outside_state_parent_refused(self):
  self.journal(Path('/etc/.recovery-fixture'))
  with self.assertRaises(ValueError):maintenance.recover_operation(self.fake,self.config,self.config_path)
 def test_journal_symlink_refused(self):
  linked=self.root/'.recovery-fixture';linked.symlink_to('/etc',target_is_directory=True);self.journal(linked)
  with self.assertRaises(ValueError):maintenance.recover_operation(self.fake,self.config,self.config_path)

if __name__=='__main__':
 if os.geteuid()!=0:
  child=subprocess.run(['sudo','-n',sys.executable,'-B',str(Path(__file__).resolve()),'--root-run'],capture_output=True,text=True,timeout=30)
  if child.stderr:sys.stderr.write(child.stderr)
  if not child.stdout:raise SystemExit(child.returncode or 1)
  report=json.loads(child.stdout);(ROOT/'.build/checks/recovery-policy-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(child.returncode)
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Boundaries))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Actual root-owned dummy snapshot permissions/types/path guards; crypto and recovery lifecycle verified separately','sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['origin_service/maintenance.py','scripts/recovery-policy-check.py']}}
 print(json.dumps(report));raise SystemExit(0 if result.wasSuccessful() else 1)
