#!/usr/bin/env python3
"""Real signed fixture and simulated service interruption; never touches live data."""
import contextlib,importlib.util,json,secrets,sys,tempfile,time,unittest
from argparse import Namespace
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from origin_service.expired_root_recovery import RecoveryJournal,execute
from origin_service.expired_root_steps import make_checkpoint,inspect_signed_exports
from steward.root_authority import RootAuthority,atomic_private
from steward.publisher import PublisherState
from steward.protocol import jose
spec=importlib.util.spec_from_file_location('fixture_provision_journal',ROOT/'scripts/provision-connected.py');provision=importlib.util.module_from_spec(spec);spec.loader.exec_module(provision)

class Backend:
 def __init__(self,folder):
  self.folder=folder;self.root=folder/'root';self.runtime=folder/'runtime';self.runtime.mkdir(mode=0o700);self.private=self.runtime/'steward-private/provisioned';self.private.mkdir(parents=True,mode=0o700);(self.runtime/'steward-private').chmod(0o700)
  self.service=ec.generate_private_key(ec.SECP256R1());key=jose.public_jwk(self.service);realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);endpoint='wss://fixture.invalid/rendezvous'
  template={'root_key':None,'realm':realm,'endpoint':endpoint,'identity_policy':{'mode':'local-development'},'origins':['https://fixture.invalid']};grant={'key_id':jose.thumbprint(key),'public_key':key,'endpoints':[endpoint],'scopes':[scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'failure_domain':'fixture'}
  self.authority=RootAuthority.initialize(self.root,template,grant,30,clock=lambda:int(time.time())-120);self.old=self.authority.provision();self.live=self.old;self.fence=1;self.running=False;self.signatures=0;self.crash=None
  atomic_private(self.private/'service.pem',self.service.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()));atomic_private(self.private/'provision.json',jose.dumps(self.old).encode());PublisherState.initialize(self.private/'ledger');self.key=(self.root/'root.pem').read_bytes();self.ledger=(self.private/'ledger/publisher.sqlite3').read_bytes()
 def locked(self):return contextlib.nullcontext()
 def initial(self):return {'version':'codi-expired-root-recovery/1','checkpoint':make_checkpoint(self.old),'configSHA256':'a'*64,'releaseSHA256':'b'*64,'publisherRevision':1,'seconds':600}
 def decide(self,record):
  if (self.root/'root.pem').read_bytes()!=self.key or (self.private/'ledger/publisher.sqlite3').read_bytes()!=self.ledger:raise ValueError('Fixture custody changed')
  root=RootAuthority(self.root).provision();staged=jose.loads((self.private/'provision.json').read_bytes())
  return inspect_signed_exports(root,staged,self.live,record['checkpoint'],fence_revision=self.fence,now=int(time.time()),steward_running=self.running,ledger_verified=True)
 def interrupt(self,phase):
  if self.crash==phase:self.crash=None;raise RuntimeError('Injected interruption: '+phase)
 def renew(self,record):
  self.fence=2;self.interrupt('fence');RootAuthority(self.root).renew(600);self.signatures+=1;self.interrupt('signed')
 def export(self,record):
  exported=provision.update(Namespace(runtime_dir=self.runtime,root_dir=self.root,command='export'));self.interrupt('staged');self.live=exported;self.interrupt('live')
 def start(self,record):self.running=True;self.interrupt('started')
 def verify(self,record):
  if self.decide(record)!='verify-running' or self.signatures!=1:raise ValueError('Fixture state not recovered')
 def receipt(self,record):self.receiptWritten=True

class Recovery(unittest.TestCase):
 def test_resume_at_every_authority_transition_without_second_signature(self):
  for where in ['prepared','fence','signed','staged','live','started','verified','receipt']:
   with self.subTest(where=where),tempfile.TemporaryDirectory(prefix='codi-expired-journal-') as folder:
    base=Path(folder);backend=Backend(base);journal=RecoveryJournal(base/'recovery.json');backend.crash=where if where in ['fence','signed','staged','live','started'] else None
    def phase(name):
     if name==where:raise RuntimeError('Injected interruption: '+where)
    with self.assertRaises(RuntimeError):execute(backend,journal,phase=phase)
    self.assertTrue(journal.path.exists());result=execute(backend,journal,resume=True)
    self.assertEqual(result,{'status':'recovered','rootRevision':2});self.assertEqual(backend.signatures,1);self.assertFalse(journal.path.exists());self.assertTrue(backend.receiptWritten)
    self.assertEqual((backend.root/'root.pem').read_bytes(),backend.key);self.assertEqual((backend.private/'ledger/publisher.sqlite3').read_bytes(),backend.ledger)
 def test_journal_rejects_replacement_permissions_and_invalid_data(self):
  with tempfile.TemporaryDirectory(prefix='codi-expired-journal-') as folder:
   base=Path(folder);backend=Backend(base);journal=RecoveryJournal(base/'recovery.json');record=backend.initial();journal.create(record)
   with self.assertRaises(FileExistsError):journal.create(record)
   self.assertEqual(journal.load(),record);journal.path.chmod(0o644)
   with self.assertRaises(ValueError):journal.load()
   journal.path.chmod(0o600);journal.path.write_text('{bad')
   with self.assertRaises((ValueError,json.JSONDecodeError)):journal.load()
   journal.path.write_text('{"version":"codi-expired-root-recovery/1","version":"codi-expired-root-recovery/1"}')
   with self.assertRaises(ValueError):journal.load()
 def test_failed_verification_never_removes_journal(self):
  with tempfile.TemporaryDirectory(prefix='codi-expired-journal-') as folder:
   base=Path(folder);backend=Backend(base);journal=RecoveryJournal(base/'recovery.json')
   backend.verify=lambda record:(_ for _ in ()).throw(ValueError('Changed independent state'))
   with self.assertRaises(ValueError):execute(backend,journal)
   self.assertTrue(journal.path.exists());self.assertEqual(backend.signatures,1)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Recovery));sys.exit(not result.wasSuccessful())
