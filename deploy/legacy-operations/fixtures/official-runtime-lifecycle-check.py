#!/usr/bin/env python3
"""Disposable local runtime lifecycle and failed startup checks."""
import asyncio,json,signal,socket,sys,tempfile,unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from cryptography.hazmat.primitives.asymmetric import ec
from codiauth import jose
from steward.official_access import initialize as initialize_access
from steward.official_upload_policy import initialize as initialize_policy
from steward.official_registry import OfficialChannelRegistry
from steward.official_runtime import OfficialRuntime
from steward.official_ingest_http import OfficialIngestServer

class Lifecycle(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='codi-runtime-life-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.db=self.root/'official.sqlite';self.ledger=self.root/'access.sqlite';store=OfficialChannelRegistry(self.db);store.close();initialize_policy(self.db);initialize_access(self.ledger);self.db.chmod(0o600);self.ledger.chmod(0o600);key=ec.generate_private_key(ec.SECP256R1());self.policy={'mode':'server','issuer':'http://127.0.0.1:8091','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]}
 def runtime(self,**changes):return OfficialRuntime(database=changes.get('database',self.db),ledger=changes.get('ledger',self.ledger),issuer_policy=self.policy,port=changes.get('port',0))
 async def test_fixed_loopback_port_and_collision(self):
  with socket.socket() as reserved:
   reserved.bind(('127.0.0.1',0));reserved.listen();port=reserved.getsockname()[1];runtime=self.runtime(port=port)
   with self.assertRaises(OSError):await runtime.start()
   self.assertIsNone(runtime.worker);self.assertIsNone(runtime.reader);self.assertIsNone(runtime.port)
  await runtime.start();self.assertEqual(runtime.port,port);await runtime.close()
  await runtime.start();self.assertEqual(runtime.port,port);await runtime.close()
  for bad in (-1,65536,True):
   with self.assertRaises(ValueError):self.runtime(port=bad)
 async def test_receipt_feature_requires_explicit_migration(self):
  from steward.official_receipts import initialize
  with self.assertRaises(ValueError):OfficialRuntime(database=self.db,ledger=self.ledger,issuer_policy=self.policy,receipts=True)
  initialize(self.db)
  runtime=OfficialRuntime(database=self.db,ledger=self.ledger,issuer_policy=self.policy,receipts=True)
  try:
   self.assertIsNotNone(runtime.receipts);await runtime.start()
  finally:await runtime.close()
 async def test_reader_capacity_and_recovery(self):
  from aiohttp import web
  runtime=self.runtime();gate=asyncio.Event();started=0
  class Upstream:
   status=200
   async def __aenter__(self):
    nonlocal started
    started+=1;return self
   async def __aexit__(self,*args):pass
   @property
   def content(self):return self
   async def iter_chunked(self,size):
    await gate.wait();yield b'{}'
  runtime.client=SimpleNamespace(get=lambda *args,**kwargs:Upstream());runtime.reader=SimpleNamespace(server_port=1)
  class Headers(dict):
   def getall(self,key,default):return [self[key]] if key in self else default
  request=SimpleNamespace(headers=Headers(Host='127.0.0.1:8091'),raw_path='/official-directory?after=&limit=1')
  tasks=[asyncio.create_task(runtime._read(request)) for _ in range(8)]
  try:
   async with asyncio.timeout(3):
    while started<8:await asyncio.sleep(.01)
   with self.assertRaises(web.HTTPServiceUnavailable):await runtime._read(request)
   gate.set();responses=await asyncio.gather(*tasks);self.assertTrue(all(response.status==200 for response in responses))
   self.assertEqual((await runtime._read(request)).status,200)
  finally:
   gate.set();await asyncio.gather(*tasks,return_exceptions=True)
 async def test_launcher_restarts_on_same_port_after_sigterm(self):
  with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
  policy=self.root/'issuer.json';policy.write_text(json.dumps(self.policy))
  args=[sys.executable,str(ROOT/'scripts/run-official-runtime.py'),'--database',str(self.db),'--ledger',str(self.ledger),'--issuer-policy',str(policy),'--port',str(port)]
  for _ in range(2):
   child=await asyncio.create_subprocess_exec(*args,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
   try:
    line=await asyncio.wait_for(child.stdout.readline(),10);self.assertEqual(json.loads(line)['port'],port)
    reader,writer=await asyncio.open_connection('127.0.0.1',port);writer.close();await writer.wait_closed()
    child.send_signal(signal.SIGTERM);await asyncio.wait_for(child.wait(),10);self.assertEqual(child.returncode,0)
   finally:
    if child.returncode is None:child.kill();await child.wait()
 async def test_start_stop_and_concurrent_start(self):
  runtime=self.runtime();first,second=await asyncio.gather(runtime.start(),runtime.start(),return_exceptions=True);self.assertEqual(sum(x is runtime for x in (first,second)),1);self.assertEqual(sum(isinstance(x,ValueError) for x in (first,second)),1);ports=[runtime.port,runtime.worker.server_port,runtime.reader.server_port];await runtime.close();await runtime.close()
  for port in ports:
   with socket.socket() as probe:self.assertNotEqual(probe.connect_ex(('127.0.0.1',port)),0)
  await runtime.start();await runtime.close()
 async def test_missing_policy_or_ledger_fails_without_creating_files(self):
  for key in ('database','ledger'):
   missing=self.root/(key+'-missing.sqlite')
   with self.assertRaises(Exception):self.runtime(**{key:missing})
   self.assertFalse(missing.exists())
 async def test_partial_start_failure_closes_worker(self):
  runtime=self.runtime();ports=[]
  def worker(*args,**kwargs):
   instance=OfficialIngestServer(*args,**kwargs);ports.append(instance.server_port);return instance
  with patch('steward.official_runtime.OfficialIngestServer',side_effect=worker),patch('steward.official_runtime.OfficialReadServer',side_effect=RuntimeError('fixture failure')):
   with self.assertRaisesRegex(RuntimeError,'fixture failure'):await runtime.start()
  self.assertIsNone(runtime.worker);self.assertIsNone(runtime.port)
  with socket.socket() as probe:self.assertNotEqual(probe.connect_ex(('127.0.0.1',ports[0])),0)
  await runtime.start();await runtime.close()

if __name__=='__main__':unittest.main(verbosity=2)
