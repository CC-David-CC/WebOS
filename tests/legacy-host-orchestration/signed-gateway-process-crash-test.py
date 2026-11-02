"""Signed upload through a separately killed real gateway; temporary data only."""
import asyncio,hashlib,importlib.util,json,os,socket,struct,sys,unittest
from pathlib import Path
from aiohttp import ClientError
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',ROOT/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class Crash(f.HTTP):
 async def exercise(self,point):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,created,_,_=await self.binary_upload(alice,key,'document',b'original');self.assertEqual(status,200)
  previous=created['sha256'];new=b'updated'
  meta={'resource':'my-files','operation':'replace','path':'document','format':'codi-binary-upload/1','size':len(new),'sha256':hashlib.sha256(new).hexdigest(),'previousSHA256':previous}
  raw=f.jose.dumps(meta);status,_,auth=await self.authorize(alice,key,raw);self.assertEqual(status,200)
  encoded=raw.encode();body=struct.pack('>I',len(encoded))+encoded+new
  headers={'Host':self.origin.removeprefix('http://'),'Origin':self.origin,'Content-Type':'application/octet-stream',**auth}
  await self.runner.cleanup()
  policy=self.root/'public-policy.json';policy.write_text(json.dumps(self.issuer.config()['identity']))
  with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
  child=await asyncio.create_subprocess_exec(sys.executable,'-B',str(ROOT/'tests/fixtures/crash-gateway.py'),str(self.store.state_root),str(self.store.data_root),str(policy),str(port),point,stdout=asyncio.subprocess.DEVNULL,stderr=asyncio.subprocess.PIPE)
  self.gateway_url='http://127.0.0.1:'+str(port)
  try:
   for _ in range(100):
    if child.returncode is not None:raise AssertionError('gateway exited before ready')
    try:
     async with self.client.get(self.gateway_url+'/healthz',headers={'Host':self.origin.removeprefix('http://')}) as response:
      if response.status==200:break
    except ClientError:pass
    await asyncio.sleep(.05)
   else:raise AssertionError('gateway did not start')
   with self.assertRaises((ClientError,asyncio.TimeoutError)):
    async with self.client.post(self.gateway_url+'/gateway/upload',data=body,headers=headers,timeout=3) as response:
     await response.read()
   self.assertEqual(await asyncio.wait_for(child.wait(),5),73)
  finally:
   if child.returncode is None:child.kill();await child.wait()
  # Construct the store again, as a fresh service process does; this performs
  # its startup staging cleanup before any account request can trigger cleanup.
  self.store=f.UserStore(self.store.state_root,self.store.data_root)
  self.assertFalse(any(p.name.startswith('.save-') for p in (self.store.users_path/alice['identity']['sub'][5:].replace('-','')).iterdir()))
  await self.start_gateway()
  status,value,_=await self.rpc(alice,key,'read','document');self.assertEqual(status,200)
  import base64
  self.assertEqual(base64.b64decode(value['data']),b'original' if point=='staged' else new)
  self.assertEqual((await self.rpc(bob,bkey,'read','document'))[0],404)
  async with self.client.post(self.gateway_url+'/gateway/upload',data=body,headers=headers) as response:self.assertEqual(response.status,401)
  self.assertFalse(any(p.name.startswith('.save-') for p in (self.store.users_path/alice['identity']['sub'][5:].replace('-','')).iterdir()))
  retry,_,_,_=await self.binary_upload(alice,key,'document',new,operation='replace',previous=previous)
  self.assertEqual(retry,200 if point=='staged' else 409)
 async def test_crash_before_publication(self):await self.exercise('staged')
 async def test_crash_after_durable_publication(self):await self.exercise('committed')
if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Crash('test_crash_before_publication'),Crash('test_crash_after_durable_publication')]));raise SystemExit(not r.wasSuccessful())
