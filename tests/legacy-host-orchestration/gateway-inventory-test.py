#!/usr/bin/env python3
"""Signed inventory must remain bounded and scoped to the authorized account."""
import base64,importlib.util,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('inventory_fixture',ROOT/'active-system/scripts/gateway-http-check.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
from gateway_service.policy import Principal
class Inventory(fixture.HTTP):
 async def inventory(self,session,key,**extra):
  raw=fixture.jose.dumps({'resource':'my-files','operation':'inventory',**extra});status,result,headers=await self.authorize(session,key,raw)
  if status!=200:return status,result
  status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw);return status,result
 async def test_inventory_scope_and_bounds(self):
  alice,ak=await self.enter();bob,bk=await self.enter('bob')
  self.assertEqual((await self.rpc(alice,ak,'mkdir','class'))[0],200);self.assertEqual((await self.rpc(alice,ak,'mkdir','class/notes'))[0],200);self.assertEqual((await self.rpc(alice,ak,'create','class/notes/a.txt',data=base64.b64encode(b'private').decode()))[0],200)
  status,result=await self.inventory(alice,ak);self.assertEqual(status,200);self.assertEqual(result,{'complete':True,'entries':[{'path':'class','directory':True},{'path':'class/notes','directory':True},{'path':'class/notes/a.txt','directory':False}]})
  self.assertEqual(await self.inventory(bob,bk),(200,{'complete':True,'entries':[]}));self.assertEqual((await self.inventory(alice,ak,path='../'))[0],403);self.assertEqual((await self.inventory(alice,ak,subject=bob['identity']['sub']))[0],403)
  identity=alice['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.assertEqual(self.store.inventory(principal,max_directories=1),{'complete':False,'entries':[]});self.assertEqual(self.store.inventory(principal,max_entries=1),{'complete':False,'entries':[]});self.assertEqual(self.store.inventory(principal,max_path_bytes=2),{'complete':False,'entries':[]})
  self.store.set_permission(identity['sub'],'list',False);self.assertEqual((await self.inventory(alice,ak))[0],403);anon,key=await self.enter(None);self.assertEqual((await self.inventory(anon,key))[0],403)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Inventory('test_inventory_scope_and_bounds')]));sys.exit(not result.wasSuccessful())
