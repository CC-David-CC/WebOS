#!/usr/bin/env python3
"""Durable publication tests with isolated private state and actual child processes."""
import asyncio,concurrent.futures,hashlib,json,os,secrets,socket,sqlite3,subprocess,sys,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from steward.publisher import PublisherState
from steward.server import StewardServer
from steward.protocol import jose

ROOT=Path(__file__).resolve().parent.parent
class PublisherChecks(unittest.TestCase):
 def setUp(self):
  self.dir=ROOT/'.build/checks/publisher'/secrets.token_hex(12);self.dir.parent.mkdir(parents=True,exist_ok=True)
  self.store=PublisherState.initialize(self.dir);self.root=ec.generate_private_key(ec.SECP256R1());self.key=ec.generate_private_key(ec.SECP256R1());self.now=int(time.time());self.realm=secrets.token_urlsafe(32);self.scope=secrets.token_urlsafe(32)
  self.endpoint='ws://127.0.0.1:8101/rendezvous'
  grant={'key_id':jose.thumbprint(jose.public_jwk(self.key)),'public_key':jose.public_jwk(self.key),'endpoints':[self.endpoint],'scopes':[self.scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'exp':self.now+1200,'failure_domain':'local-fixture'}
  self.seed={'version':'codi-seed/1','realm':self.realm,'revision':1,'iat':self.now,'exp':self.now+1200,'stewards':[grant]}
 def args(self,seed=None,**extra):
  return dict(seed=jose.sign(seed or self.seed,self.root,'codi-seed/1'),root_key=jose.public_jwk(self.root),realm=self.realm,endpoint=self.endpoint,service_key=self.key,identity_policy={'mode':'local-development'},origins=['http://127.0.0.1:8100'],publisher_state=self.store,**extra)
 def server(self,seed=None,**extra):return StewardServer(**self.args(seed,**extra))
 def payload(self,token):return jose.verify(token,jose.public_jwk(self.key),'codi-steward/1')
 def child(self,operation,*,crash=None):
  # Secret key material stays in an anonymous pipe, never argv/logs/artifacts.
  config={**{k:v for k,v in self.args().items() if k not in ('service_key','publisher_state')},'state':str(self.dir),'operation':operation,'crash':crash,'private':self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()).decode()}
  code="""import json,os,sys
from contextlib import contextmanager
from cryptography.hazmat.primitives import serialization
from steward.publisher import PublisherState
from steward.server import StewardServer
from steward.protocol import jose
c=json.load(sys.stdin);state=PublisherState(c.pop('state'));op=c.pop('operation');crash=c.pop('crash');c['service_key']=serialization.load_pem_private_key(c.pop('private').encode(),password=None);c['publisher_state']=state
s=StewardServer(**c)
if crash=='before-commit':
 original=jose.sign
 def interrupted(*args,**kwargs):
  original(*args,**kwargs);os._exit(71)
 jose.sign=interrupted
if crash=='during-write':
 original_transaction=state.transaction
 @contextmanager
 def interrupted_transaction():
  with original_transaction() as db:
   db.execute('PRAGMA cache_size=1')
   yield db
   os._exit(73)
 state.transaction=interrupted_transaction
wire=s.descriptor(renew=op=='renew')
if crash=='after-commit':os._exit(72)
print(wire,flush=True)
"""
  result=subprocess.run([sys.executable,'-c',code],input=json.dumps(config),text=True,capture_output=True,cwd=ROOT,timeout=15)
  if crash:self.assertEqual(result.returncode,{'before-commit':71,'after-commit':72,'during-write':73}[crash]);self.assertEqual(result.stdout,'');return None
  self.assertEqual(result.returncode,0,'Child publication failed');return result.stdout.strip()
 def test_restart_reuses_identical_published_bytes(self):
  first=self.server().descriptor();self.assertEqual(first,self.server().descriptor());self.assertEqual(first,self.child('cached'))
 def test_child_renewal_survives_parent_cache(self):
  server=self.server();first=server.descriptor();second=self.child('renew');self.assertGreater(self.payload(second)['revision'],self.payload(first)['revision']);self.assertEqual(second,server.descriptor())
 def test_crash_before_commit_does_not_publish_or_poison(self):
  first=self.server().descriptor();self.child('renew',crash='before-commit');self.assertEqual(first,self.child('cached'));self.assertEqual(2,self.payload(self.child('renew'))['revision'])
 def test_crash_during_write_recovers_hot_journal(self):
  first=self.server().descriptor();self.child('renew',crash='during-write');self.assertEqual(first,self.child('cached'));self.assertEqual(2,self.payload(self.child('renew'))['revision'])
 def test_journal_symlink_rejected(self):
  (self.dir/'publisher.sqlite3-journal').symlink_to(self.store.db)
  with self.assertRaises(ValueError):self.server()
 def test_crash_after_commit_before_return_keeps_new_floor(self):
  self.server().descriptor();self.child('renew',crash='after-commit');new=self.child('cached');self.assertEqual(2,self.payload(new)['revision']);self.assertEqual(new,self.server().descriptor())
 def test_parallel_processes_never_reuse_a_revision(self):
  self.server().descriptor()
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:tokens=list(pool.map(lambda _:self.child('renew'),range(8)))
  revisions=[self.payload(t)['revision'] for t in tokens];self.assertEqual(list(range(2,10)),sorted(revisions));self.assertEqual(9,self.payload(self.child('cached'))['revision'])
 def test_missing_state_never_reinitializes(self):
  self.server().descriptor();self.store.db.unlink()
  with self.assertRaises(FileNotFoundError):PublisherState(self.dir)
  self.assertFalse(self.store.db.exists())
 def test_initialization_is_explicit_and_not_repeatable(self):
  with self.assertRaises(FileExistsError):PublisherState.initialize(self.dir)
  with self.assertRaises(FileNotFoundError):PublisherState(self.dir/'missing')
 def test_hardlink_rejected(self):
  os.link(self.store.db,self.dir/'shared.sqlite3')
  with self.assertRaises(ValueError):PublisherState(self.dir)
 def test_new_seed_floor_advances_even_unchanged_policy(self):
  self.server().descriptor();new=self.server({**self.seed,'revision':2}).descriptor();self.assertGreaterEqual(self.payload(new)['revision'],2)
 def test_public_permissions_rejected(self):
  self.store.db.chmod(0o644)
  with self.assertRaises(ValueError):self.server()
 def test_symlink_rejected(self):
  target=self.dir/'real.sqlite3';self.store.db.rename(target);self.store.db.symlink_to(target)
  with self.assertRaises(ValueError):PublisherState(self.dir)
 def test_corruption_and_missing_row_fail_closed(self):
  self.server().descriptor()
  with sqlite3.connect(self.store.db) as db:db.execute('DELETE FROM publisher')
  with self.assertRaises(ValueError):self.server()
 def test_corrupt_token_never_resets_floor(self):
  self.server().descriptor()
  with sqlite3.connect(self.store.db) as db:db.execute("UPDATE publisher SET token='invalid'")
  with self.assertRaises(ValueError):self.server().descriptor()
 def test_seed_rollback_rejected_across_restarts(self):
  self.server().descriptor();self.server({**self.seed,'revision':2}).descriptor()
  with self.assertRaises(ValueError):self.server()
 def test_signed_seed_fork_freezes_persistently(self):
  self.server().descriptor()
  with self.assertRaises(ValueError):self.server({**self.seed,'exp':self.seed['exp']+1})
  with self.assertRaises(ValueError):self.server({**self.seed,'revision':2})
 def test_wrong_provisioning_does_not_poison_original(self):
  first=self.server().descriptor();other={**self.seed,'realm':secrets.token_urlsafe(32)}
  args=self.args(other);args['realm']=other['realm']
  with self.assertRaises(ValueError):StewardServer(**args)
  self.assertEqual(first,self.server().descriptor())
 def test_old_process_cannot_publish_after_new_seed_binding(self):
  old=self.server();old.descriptor();new=self.server({**self.seed,'revision':2});new.descriptor()
  with self.assertRaises(ValueError):old.descriptor(renew=True)
 def test_changed_policy_gets_higher_descriptor(self):
  old=self.server().descriptor();grant={**self.seed['stewards'][0],'limits':{'lease_seconds':60,'sample_size':2,'signal_bytes':16384}}
  new=self.server({**self.seed,'revision':2,'stewards':[grant]}).descriptor();p=self.payload(new)
  self.assertGreater(p['revision'],self.payload(old)['revision']);self.assertEqual(60,p['limits']['lease_seconds'])
 def test_old_valid_seed_can_renew_after_original_descriptor_window(self):
  first=self.server().descriptor();later=self.server(clock=lambda:self.now+400).descriptor();p=self.payload(later)
  self.assertGreater(p['revision'],self.payload(first)['revision']);self.assertEqual(self.now+700,p['exp'])
 def test_delegation_expiry_never_renews(self):
  self.server().descriptor()
  with self.assertRaises(ValueError):self.server(clock=lambda:self.now+1200)
 def test_actual_daemon_applies_signed_provision_file_reload(self):
  from websockets.asyncio.client import connect
  from websockets.exceptions import ConnectionClosed
  from steward.protocol import AUTH,CHALLENGE,RESPONSE
  with socket.socket() as selected:selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
  self.endpoint=f'ws://127.0.0.1:{port}/rendezvous';self.seed['stewards'][0]['endpoints']=[self.endpoint]
  key_path=self.dir/'service.pem';provision_path=self.dir/'provision.json'
  key_raw=self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  provision={k:v for k,v in self.args().items() if k not in ('service_key','publisher_state')}
  for path,raw in [(key_path,key_raw),(provision_path,json.dumps(provision).encode())]:
   fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   with os.fdopen(fd,'wb') as out:out.write(raw)
  public=ROOT/'.build/checks/publisher-public'/self.dir.name;public.mkdir(parents=True);output=public/'discovery.json'
  command=[sys.executable,str(ROOT/'scripts/serve-steward.py'),'serve','--state',str(self.dir),'--key',str(key_path),'--provision',str(provision_path),'--bundle-out',str(output),'--port',str(port)]
  process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=ROOT)
  try:
   deadline=time.monotonic()+10
   while not output.exists():
    self.assertIsNone(process.poll());self.assertLess(time.monotonic(),deadline);time.sleep(.05)
   async def scenario():
    async with connect(self.endpoint,origin='http://127.0.0.1:8100',proxy=None) as ws:
     challenge=jose.verify(await ws.recv(),jose.public_jwk(self.key),CHALLENGE);session_key=ec.generate_private_key(ec.SECP256R1());sid=secrets.token_urlsafe(24);now=int(time.time())
     identity={'sid':sid,'sub':sid,'kind':'anonymous','name':'reload-fixture','key':jose.public_jwk(session_key),'certificate':None}
     await ws.send(jose.sign({'version':AUTH,'realm':self.realm,'endpoint':self.endpoint,'nonce':challenge['nonce'],'iat':now,'exp':now+30,'identity':identity,'scopes':[self.scope]},session_key,AUTH));jose.verify(await ws.recv(),jose.public_jwk(self.key),RESPONSE)
     new_seed={**self.seed,'revision':2,'stewards':[{**self.seed['stewards'][0],'scopes':[secrets.token_urlsafe(32)]}]};updated={**provision,'seed':jose.sign(new_seed,self.root,'codi-seed/1')}
     temporary=self.dir/'updated.json';fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
     with os.fdopen(fd,'wb') as out:out.write(json.dumps(updated).encode());out.flush();os.fsync(out.fileno())
     os.replace(temporary,provision_path)
     try:await asyncio.wait_for(ws.recv(),40)
     except ConnectionClosed as error:self.assertEqual(error.rcvd.code,1012)
     else:self.fail('Old control scope survived provision reload')
     bundle=json.loads(output.read_text());self.assertEqual(jose.verify(bundle['seed'],jose.public_jwk(self.root),'codi-seed/1')['revision'],2);self.assertGreaterEqual(self.payload(bundle['descriptor'])['revision'],2)
   asyncio.run(scenario())
  finally:
   if process.poll() is None:process.terminate();process.wait(timeout=5)
 def test_actual_daemon_sigkill_restart_keeps_published_revision(self):
  with socket.socket() as selected:selected.bind(('127.0.0.1',0));port=selected.getsockname()[1]
  self.endpoint=f'ws://127.0.0.1:{port}/rendezvous';self.seed['stewards'][0]['endpoints']=[self.endpoint]
  key_path=self.dir/'service.pem';provision_path=self.dir/'provision.json'
  key_raw=self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  provision={k:v for k,v in self.args().items() if k not in ('service_key','publisher_state')}
  for path,raw in [(key_path,key_raw),(provision_path,json.dumps(provision).encode())]:
   fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
   with os.fdopen(fd,'wb') as out:out.write(raw)
  public_dir=ROOT/'.build/checks/publisher-public'/self.dir.name;public_dir.mkdir(parents=True);bundle=public_dir/'discovery.json'
  command=[sys.executable,str(ROOT/'scripts/serve-steward.py'),'serve','--state',str(self.dir),'--key',str(key_path),'--provision',str(provision_path),'--bundle-out',str(bundle),'--port',str(port)]
  process=None
  def launch():
   p=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,cwd=ROOT)
   deadline=time.monotonic()+10
   while not bundle.exists():
    if p.poll() is not None:raise AssertionError('Provisioned daemon exited before publishing')
    if time.monotonic()>deadline:p.kill();p.wait();raise AssertionError('Provisioned daemon publication timed out')
    time.sleep(.05)
   return p
  try:
   process=launch();first=json.loads(bundle.read_text())['descriptor'];self.assertEqual(1,self.payload(first)['revision'])
   second=self.server().descriptor(renew=True)
   from importlib.util import spec_from_file_location,module_from_spec
   spec=spec_from_file_location('steward_cli',ROOT/'scripts/serve-steward.py');module=module_from_spec(spec);spec.loader.exec_module(module)
   module.write_bundle(bundle,{'version':'codi-bootstrap-bundle/1','seed':self.args()['seed'],'descriptor':second})
   process.kill();process.wait(timeout=5);process=None;bundle.unlink()
   process=launch();self.assertEqual(second,json.loads(bundle.read_text())['descriptor']);self.assertEqual(2,self.payload(second)['revision'])
  finally:
   if process is not None and process.poll() is None:process.terminate();process.wait(timeout=5)
 def test_file_mode_and_no_secret_state(self):
  self.server().descriptor();self.assertEqual(0o700,self.dir.stat().st_mode&0o777);self.assertEqual(0o600,self.store.db.stat().st_mode&0o777)
  raw=self.store.db.read_bytes();self.assertNotIn(b'PRIVATE KEY',raw);self.assertNotIn(b'certificate',raw)

if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(PublisherChecks);result=unittest.TextTestRunner(verbosity=2).run(suite)
 files=['steward/publisher.py','steward/server.py','steward/provision.py','scripts/publisher-check.py','scripts/serve-steward.py'];receipt={'tests':result.testsRun,'passed':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'scope':'Private SQLite persistence, actual child-process crashes and concurrent publication; no WAN/deployment proof','sourceHashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in files}}
 (ROOT/'.build/checks/publisher-result.json').write_text(json.dumps(receipt,indent=2)+'\n');sys.exit(not result.wasSuccessful())
