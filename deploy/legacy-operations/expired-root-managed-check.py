#!/usr/bin/env python3
"""Managed adapter with real signed files/SQLite and simulated systemd; no live writes."""
import contextlib,fcntl,hashlib,importlib.util,json,os,secrets,sqlite3,sys,tempfile,time,unittest
from argparse import Namespace
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from origin_service import maintenance
from origin_service.expired_root_managed import ManagedExpiredRoot
from origin_service.expired_root_recovery import RecoveryJournal,execute
from steward.root_authority import RootAuthority,atomic_private
from steward.publisher import PublisherState
from steward.protocol import jose
spec=importlib.util.spec_from_file_location('fixture_managed_provision',ROOT/'scripts/provision-connected.py');provision=importlib.util.module_from_spec(spec);spec.loader.exec_module(provision)

class FixtureOperator:
 def __init__(self,folder):
  self.folder=folder;self.state=folder/'state';self.state.mkdir(mode=0o700);self.control=folder/'control';self.control.mkdir(mode=0o700);self.config_path=self.control/'managed.json';self.root=self.state/'operator/root';self.runtime=self.state/'operator/staging';self.runtime.mkdir(parents=True,mode=0o700);(self.state/'operator').chmod(0o700);self.private=self.runtime/'steward-private/provisioned';self.private.mkdir(parents=True,mode=0o700);(self.runtime/'steward-private').chmod(0o700)
  self.issuer=self.state/'issuer/state';self.issuer.mkdir(parents=True,mode=0o700);(self.state/'issuer').chmod(0o700);self.steward=self.state/'steward';self.steward.mkdir(mode=0o700);self.public=self.state/'public';self.public.mkdir(mode=0o700)
  self.issuer_key=ec.generate_private_key(ec.SECP256R1());self.service=ec.generate_private_key(ec.SECP256R1());self.realm=secrets.token_urlsafe(32);self.scope=secrets.token_urlsafe(32);self.endpoint='wss://fixture.invalid/rendezvous';key=jose.public_jwk(self.service)
  identity={'mode':'server','authorityClass':'development','authorityKeys':[{'jwk':jose.public_jwk(self.issuer_key)}]};template={'root_key':None,'realm':self.realm,'endpoint':self.endpoint,'identity_policy':identity,'origins':['https://fixture.invalid']};grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[self.endpoint],'scopes':[self.scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'fixture'}
  authority=RootAuthority.initialize(self.root,template,grant,30,clock=lambda:int(time.time())-120);self.original=authority.provision();private_bytes=lambda k:k.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  atomic_private(self.issuer/'issuer.pem',private_bytes(self.issuer_key));atomic_private(self.private/'service.pem',private_bytes(self.service));atomic_private(self.steward/'service.pem',private_bytes(self.service));atomic_private(self.private/'provision.json',jose.dumps(self.original).encode());atomic_private(self.steward/'provision.json',jose.dumps(self.original).encode())
  policy={'identity':identity,'pin':{'rootKey':self.original['root_key'],'realm':self.realm,'endpoints':[self.endpoint]},'scope':self.scope};raw=jose.dumps(policy).encode();atomic_private(self.private/'origin-discovery.json',raw);atomic_private(self.public/'origin-discovery.json',raw);(self.public/'origin-discovery.json').chmod(0o444)
  db=self.issuer/'accounts.sqlite3';db.touch(mode=0o600)
  with sqlite3.connect(db) as sql:sql.executescript('CREATE TABLE account_policy_metadata(version INTEGER); INSERT INTO account_policy_metadata VALUES(1); CREATE TABLE accounts(subject TEXT); CREATE TABLE account_policy(subject TEXT);')
  PublisherState.initialize(self.private/'ledger');self.publisher=PublisherState.initialize(self.steward/'ledger');old=jose.inspect(self.original['seed'],'codi-seed/1',32768)[1];self.publisher_binding={'realm':self.realm,'root_key_id':jose.thumbprint(self.original['root_key']),'service_key_id':grant['key_id'],'endpoint':self.endpoint};self.publisher.bind(self.publisher_binding,old);self._publish(old,old['iat'])
  self.config={'instance':'codi-fixture','stateRoot':str(self.state),'manifestSHA256':'b'*64};atomic_private(self.config_path,json.dumps(self.config).encode());fence={'version':'codi-recovery-fence/1','instance':self.config['instance'],'issuerKeyId':jose.thumbprint(jose.public_jwk(self.issuer_key)),'rootKeyId':jose.thumbprint(self.original['root_key']),'realm':self.realm,'rootFloor':1,'backups':{}};atomic_private(self.control/'recovery-fence.json',jose.dumps(fence).encode())
  self.running=False;self.signatures=0;self.crash=None;self.key_before=(self.root/'root.pem').read_bytes()
 def _publish(self,seed,now):
  grant=seed['stewards'][0];descriptor={'version':'codi-steward/1','realm':self.realm,'key_id':grant['key_id'],'exp':seed['exp'],'endpoint':self.endpoint,'scopes':grant['scopes'],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768}};self.publisher.publish(descriptor,self.service,seed,now=now,minimum_revision=1)
 def path(self,p):return Path(p)
 @contextlib.contextmanager
 def locked(self,path):
  fd=os.open(self.control/'lock',os.O_CREAT|os.O_RDWR,0o600)
  try:fcntl.flock(fd,fcntl.LOCK_EX);yield
  finally:os.close(fd)
 def read_owned(self,p,uid,mode,limit=65536):
  if uid==0:uid=os.geteuid() # Fixture models root ownership without privilege.
  p=Path(p);info=p.lstat()
  if p.is_symlink() or info.st_uid!=uid or info.st_nlink!=1 or info.st_mode&0o777!=mode or info.st_size>limit:raise ValueError('Fixture protected input differs')
  return p.read_bytes()
 def atomic(self,p,raw):atomic_private(Path(p),raw)
 def load(self,path):return json.loads(self.read_owned(path,os.geteuid(),0o600))
 def installed(self,c):return ROOT,{'issuer':{'uid':os.geteuid()},'steward':{'uid':os.geteuid()}}
 def unit(self,c,role):return c['instance']+'-'+role+'.service'
 def inactive(self,c,role):
  if self.running:raise ValueError('Fixture steward running')
 def interrupt(self,point):
  if self.crash==point:self.crash=None;raise RuntimeError('Injected '+point)
 def publish(self,c,action,seconds,path):
  if action=='renew':maintenance.reserve(self,c,path);self.interrupt('fence')
  else:maintenance.guard(self,c,path)
  old_renew=RootAuthority.renew;old_atomic=provision.atomic_private
  def renew(authority,duration):
   value=old_renew(authority,duration);self.signatures+=1;self.interrupt('signed');return value
  def stage(path,raw):
   old_atomic(path,raw)
   if Path(path)==self.private/'provision.json':self.interrupt('staged')
  try:
   RootAuthority.renew=renew;provision.atomic_private=stage
   value=provision.update(Namespace(runtime_dir=self.runtime,root_dir=self.root,command=action,seconds=seconds))
  finally:RootAuthority.renew=old_renew;provision.atomic_private=old_atomic
  atomic_private(self.steward/'provision.json',jose.dumps(value).encode());self.interrupt('live')
 def systemctl(self,*args):
  if args[0]=='show':return ('active' if self.running else 'failed') if '--value' in args else 'ActiveState='+('active' if self.running else 'failed')+'\nMainPID='+('123' if self.running else '0')
  if args[0]=='reset-failed':return ''
  if args[0]=='start':
   self.running=True;seed=jose.inspect(RootAuthority(self.root).provision()['seed'],'codi-seed/1',32768)[1];self.publisher.bind(self.publisher_binding,seed);self._publish(seed,int(time.time()));return ''
  raise ValueError('Unexpected fixture systemctl action')
 def ready(self,c,roles):
  if not self.running:raise ValueError('Fixture service not ready')
 def issuer_config(self,c):
  with sqlite3.connect(self.steward/'ledger/publisher.sqlite3') as db:token=db.execute('SELECT token FROM publisher WHERE id=1').fetchone()[0]
  return {'discovery':{'seed':RootAuthority(self.root).provision()['seed'],'descriptor':token}}

class ManagedRecovery(unittest.TestCase):
 def test_recovery_with_actual_signed_state_and_real_managed_adapter(self):
  for point in ['prepared','fence','signed','staged','live','after-renew-once','after-start-steward','receipt']:
   with self.subTest(point=point),tempfile.TemporaryDirectory(prefix='codi-managed-expired-') as folder:
    op=FixtureOperator(Path(folder));config_hash=hashlib.sha256(op.config_path.read_bytes()).hexdigest();backend=ManagedExpiredRoot(op,maintenance,op.config_path,config_sha256=config_hash,release_sha256='b'*64,seconds=600);journal=RecoveryJournal(op.control/'expired-root-journal.json')
    if point in ['fence','signed','staged','live']:op.crash=point
    def phase(name):
     if name==point:raise RuntimeError('Injected '+point)
    with self.assertRaises(RuntimeError):execute(backend,journal,phase=phase)
    self.assertTrue(journal.path.exists());result=execute(backend,journal,resume=True);self.assertEqual(result['rootRevision'],2);self.assertEqual(op.signatures,1);self.assertTrue(op.running);self.assertEqual((op.root/'root.pem').read_bytes(),op.key_before);self.assertFalse(journal.path.exists())
 def test_configuration_pin_drift_refuses_before_mutation(self):
  with tempfile.TemporaryDirectory(prefix='codi-managed-expired-') as folder:
   op=FixtureOperator(Path(folder));backend=ManagedExpiredRoot(op,maintenance,op.config_path,config_sha256='a'*64,release_sha256='b'*64,seconds=600);journal=RecoveryJournal(op.control/'expired-root-journal.json')
   with self.assertRaises(ValueError):execute(backend,journal)
   self.assertEqual(op.signatures,0);self.assertFalse(journal.path.exists())
 def test_resume_refuses_changed_authority_lifetime(self):
  with tempfile.TemporaryDirectory(prefix='codi-managed-expired-') as folder:
   op=FixtureOperator(Path(folder));pin=hashlib.sha256(op.config_path.read_bytes()).hexdigest();backend=ManagedExpiredRoot(op,maintenance,op.config_path,config_sha256=pin,release_sha256='b'*64,seconds=600);journal=RecoveryJournal(op.control/'expired-root-journal.json')
   def stop(name):
    if name=='prepared':raise RuntimeError('Fixture stopped after journal')
   with self.assertRaises(RuntimeError):execute(backend,journal,phase=stop)
   changed=ManagedExpiredRoot(op,maintenance,op.config_path,config_sha256=pin,release_sha256='b'*64,seconds=1200)
   with self.assertRaises(ValueError):execute(changed,journal,resume=True)
   self.assertEqual(op.signatures,0);self.assertTrue(journal.path.exists());self.assertEqual(execute(backend,journal,resume=True)['rootRevision'],2)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ManagedRecovery));sys.exit(not result.wasSuccessful())
