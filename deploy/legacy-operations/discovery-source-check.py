#!/usr/bin/env python3
"""Issuer reads signed public metadata without any steward/root private inputs."""
import hashlib,json,os,secrets,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from cryptography.hazmat.primitives.asymmetric import ec
from origin_service.discovery import DiscoverySource,public_bytes
from steward.protocol import jose
from steward.server import StewardServer

class SourceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='codi-source-');self.folder=Path(self.temp.name);self.policy=self.folder/'policy.json';self.bundle=self.folder/'bundle.json';self.now=1000
  self.root=ec.generate_private_key(ec.SECP256R1());self.service=ec.generate_private_key(ec.SECP256R1());self.realm=secrets.token_urlsafe(32);self.scope=secrets.token_urlsafe(32);self.endpoint='wss://preview.invalid/hidden/rendezvous';self.identity={'mode':'server','issuer':'https://preview.invalid','apiBase':'/hidden/api/v1','authorityClass':'development'}
  key=jose.public_jwk(self.service);self.grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[self.endpoint],'scopes':[self.scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'exp':1600,'failure_domain':'fixture'}
  self.seed={'version':'codi-seed/1','realm':self.realm,'revision':1,'iat':self.now,'exp':1600,'stewards':[self.grant]}
  self.policy_doc={'version':'codi-discovery-source/1','pin':{'realm':self.realm,'rootKey':jose.public_jwk(self.root),'endpoints':[self.endpoint],'allowLoopback':False},'scope':self.scope,'sourcePath':'/hidden/discovery.json','identity':self.identity}
  self.policy.write_text(jose.dumps(self.policy_doc));self.publish(self.seed)
  self.source=DiscoverySource(self.policy,self.bundle,self.identity,'/hidden',clock=lambda:self.now)
 def tearDown(self):self.temp.cleanup()
 def publish(self,seed):
  token=jose.sign(seed,self.root,'codi-seed/1');server=StewardServer(seed=token,root_key=jose.public_jwk(self.root),realm=self.realm,endpoint=self.endpoint,service_key=self.service,identity_policy=self.identity,origins=['https://preview.invalid'],clock=lambda:self.now)
  doc=server.bundle();self.bundle.write_text(jose.dumps(doc));return doc
 def test_valid_public_only_config(self):
  config=self.source.config();self.assertEqual(config['scope'],self.scope);self.assertEqual(config['pin'],self.policy_doc['pin']);self.assertNotIn('identity',config);self.assertNotIn('PRIVATE KEY',jose.dumps(config))
 def test_wrong_issuer_or_mount_refused(self):
  with self.assertRaises(ValueError):DiscoverySource(self.policy,self.bundle,{**self.identity,'issuer':'https://wrong.invalid'},'/hidden')
  with self.assertRaises(ValueError):DiscoverySource(self.policy,self.bundle,self.identity,'')
 def test_unavailable_bundle_does_not_create_authority(self):
  self.bundle.unlink();self.assertIsNone(self.source.config())
 def test_expired_bundle_refused_without_reissuance(self):
  self.now=1601
  with self.assertRaises(ValueError):self.source.read()
 def test_signed_renewal_advances_and_old_seed_cannot_return(self):
  old=self.source.read();new=self.publish({**self.seed,'revision':2});self.assertEqual(self.source.read(),new);self.bundle.write_text(jose.dumps(old))
  with self.assertRaises(ValueError):self.source.read()
  self.assertEqual(self.source.config()['seed'],new['seed'])
 def test_equal_revision_fork_refused(self):
  self.source.read();self.publish({**self.seed,'exp':1601})
  with self.assertRaises(ValueError):self.source.read()
 def test_wrong_root_signature_refused(self):
  doc=self.source.read();doc['seed']=jose.sign(self.seed,ec.generate_private_key(ec.SECP256R1()),'codi-seed/1');self.bundle.write_text(jose.dumps(doc))
  with self.assertRaises(ValueError):self.source.read()
 def test_scoped_key_cannot_extend_limits_endpoint_or_expiry(self):
  original=self.source.read();claims=jose.inspect(original['descriptor'],'codi-steward/1')[1]
  for changed in [{**claims,'limits':{**claims['limits'],'sample_size':16}},{**claims,'endpoint':'wss://wrong.invalid/hidden/rendezvous'},{**claims,'scopes':[secrets.token_urlsafe(32)]},{**claims,'exp':1700}]:
   self.bundle.write_text(jose.dumps({**original,'descriptor':jose.sign(changed,self.service,'codi-steward/1')}))
   with self.assertRaises(ValueError):self.source.read()
 def test_invalid_public_bytes_cannot_replace_cached_signed_metadata(self):
  old=self.source.config();self.bundle.write_text('{malformed');self.assertEqual(self.source.config(),old)
 def test_link_fifo_and_size_boundaries(self):
  self.bundle.unlink();self.bundle.symlink_to(self.policy)
  with self.assertRaises(ValueError):public_bytes(self.bundle,49152)
  self.bundle.unlink();os.link(self.policy,self.bundle)
  with self.assertRaises(ValueError):public_bytes(self.bundle,49152)
  self.bundle.unlink();os.mkfifo(self.bundle,0o600)
  with self.assertRaises(ValueError):public_bytes(self.bundle,49152)
  self.bundle.unlink();self.bundle.write_bytes(b'x'*49153)
  with self.assertRaises(ValueError):public_bytes(self.bundle,49152)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceTests));report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Actual signatures and public metadata path/bounds; Unix UID isolation is a separate runtime check','sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['origin_service/discovery.py','scripts/discovery-source-check.py']}}
 (ROOT/'.build/checks/discovery-source-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
