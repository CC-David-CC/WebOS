"""Bounded signed conflicting operations and independent account isolation."""
import asyncio,base64,importlib.util,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',root/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class Contention(f.HTTP):
 async def exercise(self,second):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,source,_=await self.rpc(alice,key,'create','note',data=base64.b64encode(b'original').decode());self.assertEqual(status,200)
  status,_,_=await self.rpc(bob,bkey,'create','note',data=base64.b64encode(b'bob private').decode());self.assertEqual(status,200)
  async def replace():return await self.rpc(alice,key,'replace','note',data=base64.b64encode(b'updated').decode(),previousSHA256=source['sha256'])
  async def competing():
   if second=='replace':return await self.rpc(alice,key,'replace','note',data=base64.b64encode(b'other').decode(),previousSHA256=source['sha256'])
   if second=='delete':return await self.rpc(alice,key,'delete','note',previousSHA256=source['sha256'])
   return await self.rpc(alice,key,'rename','note',destination='moved',previousSHA256=source['sha256'])
  results=await asyncio.gather(replace(),competing())
  statuses=[r[0] for r in results]
  self.assertEqual(statuses.count(200),1,statuses);self.assertIn(next(s for s in statuses if s!=200),(404,409))
  note=await self.rpc(alice,key,'read','note');moved=await self.rpc(alice,key,'read','moved')
  if results[0][0]==200:self.assertEqual(base64.b64decode(note[1]['data']),b'updated');self.assertEqual(moved[0],404)
  elif second=='replace':self.assertEqual(base64.b64decode(note[1]['data']),b'other')
  elif second=='delete':self.assertEqual(note[0],404)
  else:self.assertEqual(note[0],404);self.assertEqual(base64.b64decode(moved[1]['data']),b'original')
  other=await self.rpc(bob,bkey,'read','note');self.assertEqual(base64.b64decode(other[1]['data']),b'bob private')
  self.assertEqual((await self.rpc(bob,bkey,'read','moved'))[0],404)
 async def test_replace_replace(self):await self.exercise('replace')
 async def test_replace_delete(self):await self.exercise('delete')
 async def test_replace_rename(self):await self.exercise('rename')
 async def test_create_create(self):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,_,_=await self.rpc(bob,bkey,'create','note',data=base64.b64encode(b'bob private').decode());self.assertEqual(status,200)
  async def create(value):return await self.rpc(alice,key,'create','note',data=base64.b64encode(value).decode())
  results=await asyncio.gather(create(b'first'),create(b'second'))
  self.assertEqual(sorted(r[0] for r in results),[200,409])
  status,result,_=await self.rpc(alice,key,'read','note');self.assertEqual(status,200)
  self.assertEqual(base64.b64decode(result['data']),b'first' if results[0][0]==200 else b'second')
  self.assertEqual(base64.b64decode((await self.rpc(bob,bkey,'read','note'))[1]['data']),b'bob private')

if __name__=='__main__':
 names=['test_create_create','test_replace_replace','test_replace_delete','test_replace_rename']
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Contention(n) for n in names));raise SystemExit(not result.wasSuccessful())
