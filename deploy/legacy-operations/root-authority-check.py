#!/usr/bin/env python3
"""Explicit root issuance, durable revision floors and private file boundaries."""
import hashlib,json,os,secrets,sqlite3,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from cryptography.hazmat.primitives.asymmetric import ec
from steward.protocol import jose
from steward.root_authority import RootAuthority,private_read,atomic_private
from steward.provision import verified_seed

class AuthorityTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='codi-authority-');self.folder=Path(self.temp.name);self.path=self.folder/'authority';self.now=1000
  self.service=ec.generate_private_key(ec.SECP256R1());key=jose.public_jwk(self.service);self.realm=secrets.token_urlsafe(32);self.scope=secrets.token_urlsafe(32)
  self.template={'root_key':None,'realm':self.realm,'endpoint':'wss://example.invalid/hidden/rendezvous','identity_policy':{'mode':'local-development'},'origins':['https://example.invalid']}
  self.grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[self.template['endpoint']],'scopes':[self.scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'development-preview'}
 def tearDown(self):self.temp.cleanup()
 def init(self):return RootAuthority.initialize(self.path,self.template,self.grant,600,clock=lambda:self.now)
 def test_initial_provision_and_restart_have_identical_signed_bytes(self):
  a=self.init();first=a.provision();self.assertEqual(first,RootAuthority(self.path,clock=lambda:self.now).provision());p=verified_seed(first['seed'],first['root_key'],self.realm,self.now);self.assertEqual(p['revision'],1);self.assertEqual(p['exp'],1600)
 def test_renew_advances_revision_without_changing_binding(self):
  a=self.init();first=a.provision();self.now+=100;a.renew(600);second=a.provision();self.assertEqual({k:v for k,v in first.items() if k!='seed'},{k:v for k,v in second.items() if k!='seed'});p=verified_seed(second['seed'],second['root_key'],self.realm,self.now);self.assertEqual(p['revision'],2);self.assertEqual(p['exp'],1700)
 def test_expired_policy_can_only_be_renewed_by_operator(self):
  a=self.init();self.now+=700;old=a.provision()
  with self.assertRaises(ValueError):verified_seed(old['seed'],old['root_key'],self.realm,self.now)
  a.renew(600);new=a.provision();self.assertEqual(verified_seed(new['seed'],new['root_key'],self.realm,self.now)['revision'],2)
 def test_reinitialization_and_missing_database_never_reset(self):
  a=self.init()
  with self.assertRaises(FileExistsError):self.init()
  a.db.unlink()
  with self.assertRaises((ValueError,FileNotFoundError)):RootAuthority(self.path)
  self.assertFalse(a.db.exists())
 def test_corrupt_revision_refused(self):
  a=self.init()
  with sqlite3.connect(a.db) as db:db.execute('UPDATE authority SET revision=7')
  with self.assertRaises(ValueError):RootAuthority(self.path,clock=lambda:self.now).provision()
 def test_public_state_or_key_modes_refused(self):
  a=self.init();key=self.path/'root.pem';key.chmod(0o644)
  with self.assertRaises(ValueError):RootAuthority(self.path)
  key.chmod(0o600);a.db.chmod(0o644)
  with self.assertRaises(ValueError):RootAuthority(self.path)
 def test_root_key_change_does_not_rebind_existing_policy(self):
  self.init();other=RootAuthority.initialize(self.folder/'other',self.template,self.grant,600,clock=lambda:self.now)
  (self.path/'root.pem').write_bytes((other.directory/'root.pem').read_bytes())
  with self.assertRaises(ValueError):RootAuthority(self.path,clock=lambda:self.now).provision()
 def test_clock_rollback_and_nonextending_renewal_refused(self):
  a=self.init();self.now-=1
  with self.assertRaises(ValueError):a.renew(600)
  self.now=1001
  with self.assertRaises(ValueError):a.renew(30)
 def test_duration_bounded_by_existing_seed_contract(self):
  a=self.init()
  for value in [True,0,29,86401,'600']:
   with self.assertRaises(ValueError):a.renew(value)
 def test_full_day_bound_is_accepted_without_extending_wire_contract(self):
  a=self.init();a.renew(86400);provision=a.provision();seed=verified_seed(provision['seed'],provision['root_key'],self.realm,self.now);self.assertEqual(seed['exp']-seed['iat'],86400);self.assertEqual(seed['revision'],2)
 def test_private_reader_refuses_symlink_hardlink_and_fifo(self):
  target=self.folder/'input';atomic_private(target,b'fixture');self.assertEqual(private_read(target),b'fixture');target.unlink();target.symlink_to(self.folder/'elsewhere')
  with self.assertRaises(ValueError):private_read(target)
  target.unlink();atomic_private(target,b'fixture');os.link(target,self.folder/'alias')
  with self.assertRaises(ValueError):private_read(target)
  target.unlink();os.mkfifo(target,0o600)
  with self.assertRaises(ValueError):private_read(target)
 def test_atomic_export_contains_no_private_key(self):
  a=self.init();path=self.folder/'provision.json';atomic_private(path,jose.dumps(a.provision()).encode());self.assertEqual(path.stat().st_mode&0o777,0o600);self.assertNotIn(b'PRIVATE KEY',path.read_bytes())
 def test_recovery_advances_external_floor_and_rotates_only_scoped_key(self):
  a=self.init();before=a.provision();private=(self.path/'root.pem').read_bytes();service=ec.generate_private_key(ec.SECP256R1());after=a.recover(600,50,service);p=verified_seed(after['seed'],after['root_key'],self.realm,self.now)
  self.assertEqual(p['revision'],51);self.assertEqual(p['stewards'][0]['key_id'],jose.thumbprint(jose.public_jwk(service)));self.assertEqual(after['root_key'],before['root_key']);self.assertEqual(after['realm'],before['realm']);self.assertEqual(after['identity_policy'],before['identity_policy']);self.assertEqual((self.path/'root.pem').read_bytes(),private)
  self.assertEqual(p['stewards'][0]['scopes'],self.grant['scopes']);self.assertEqual(p['stewards'][0]['limits'],self.grant['limits'])
 def test_recovery_requires_fresh_service_key(self):
  a=self.init();before=a.provision()
  with self.assertRaises(ValueError):a.recover(600,50,self.service)
  self.assertEqual(a.provision(),before)
 def test_recovery_refuses_invalid_floor_without_mutation(self):
  a=self.init();before=a.provision();service=ec.generate_private_key(ec.SECP256R1())
  for floor in [True,0,-1,2**53-1,1.5,'50']:
   with self.subTest(floor=floor),self.assertRaises(ValueError):a.recover(600,floor,service)
  self.assertEqual(a.provision(),before)
 def test_recovery_refuses_clock_rollback(self):
  a=self.init();before=a.provision();self.now-=1
  with self.assertRaises(ValueError):a.recover(600,50,ec.generate_private_key(ec.SECP256R1()))
  self.now=1000;self.assertEqual(a.provision(),before)
 def test_expired_recovery_and_subsequent_normal_renewal(self):
  a=self.init();self.now=2000;a.recover(600,10,ec.generate_private_key(ec.SECP256R1()));self.now+=10;after=a.renew(600);self.assertEqual(verified_seed(after['seed'],after['root_key'],self.realm,self.now)['revision'],12)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(AuthorityTests))
 report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Explicit native root issuance and private SQLite revision persistence; not online service or public deployment','sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['steward/root_authority.py','scripts/root-authority-check.py']}}
 (ROOT/'.build/checks/root-authority-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
