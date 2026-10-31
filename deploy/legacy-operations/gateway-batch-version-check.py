#!/usr/bin/env python3
"""Real signed gateway version-batch isolation and validation checks."""
import base64,hashlib,importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('gateway_http_fixture',ROOT/'scripts/gateway-http-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
class Batch(fixture.HTTP):
 async def batch(self,session,key,paths,**extra):
  raw=fixture.jose.dumps({'resource':'my-files','operation':'versions','paths':paths,**extra});status,result,headers=await self.authorize(session,key,raw)
  if status!=200:return status,result,None
  return await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw)
 async def test_signed_batch_is_private_and_validated(self):
  alice,ak=await self.enter();bob,bk=await self.enter('bob')
  status,_,_=await self.rpc(alice,ak,'create','private.txt',data=base64.b64encode(b'private').decode());self.assertEqual(status,200)
  status,result,_=await self.batch(alice,ak,['private.txt']);self.assertEqual(status,200);self.assertEqual(result,{'entries':[{'path':'private.txt','bytes':7,'sha256':hashlib.sha256(b'private').hexdigest()}]})
  status,result,_=await self.batch(bob,bk,['private.txt']);self.assertEqual(status,200);self.assertEqual(result,{'entries':[{'path':'private.txt','deferred':True}]})
  self.assertEqual((await self.batch(alice,ak,['../private.txt']))[0],403);self.assertEqual((await self.batch(alice,ak,['private.txt','private.txt']))[0],403);self.assertEqual((await self.batch(alice,ak,['private.txt'],subject=bob['identity']['sub']))[0],403)
  self.store.set_permission(alice['identity']['sub'],'read',False);self.assertEqual((await self.batch(alice,ak,['private.txt']))[0],403)
  anon,key=await self.enter(None);self.assertEqual((await self.batch(anon,key,['private.txt']))[0],403)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Batch('test_signed_batch_is_private_and_validated')]));sys.exit(not result.wasSuccessful())
