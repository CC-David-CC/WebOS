#!/usr/bin/env python3
"""Real signed account inventory/version access and bounded-hashing checks."""
import base64,hashlib,importlib.util,os,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('inventory_fixture',ROOT/'active-system/scripts/gateway-http-check.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
from gateway_service.policy import Principal
class InventoryVersions(f.HTTP):
 async def combined(self,session,key,**extra):
  raw=f.jose.dumps({'resource':'my-files','operation':'inventory-versions',**extra});status,result,headers=await self.authorize(session,key,raw)
  if status!=200:return status,result
  status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw);return status,result
 async def test_scoped_bounded_inventory_and_external_edit(self):
  alice,ak=await self.enter();bob,bk=await self.enter('bob');self.assertEqual((await self.rpc(alice,ak,'mkdir','class'))[0],200);self.assertEqual((await self.rpc(alice,ak,'create','class/a.txt',data=base64.b64encode(b'one!').decode()))[0],200)
  status,items=await self.combined(alice,ak);self.assertEqual(status,200);self.assertEqual(items,{'complete':True,'entries':[{'path':'class','directory':True},{'path':'class/a.txt','directory':False,'bytes':4,'sha256':hashlib.sha256(b'one!').hexdigest()}]});self.assertEqual(await self.combined(bob,bk),(200,{'complete':True,'entries':[]}));self.assertEqual((await self.combined(alice,ak,subject=bob['identity']['sub']))[0],403)
  ident=alice['identity'];principal=Principal(ident['sub'],ident['sid'],'registered',ident['key'],int(time.time())+600);home=self.store.users_path/ident['sub'][5:].replace('-','');(home/'class'/'a.txt').write_bytes(b'two!');status,changed=await self.combined(alice,ak);self.assertEqual(status,200);self.assertEqual(changed['entries'][1]['sha256'],hashlib.sha256(b'two!').hexdigest())
  outside=self.root/'outside';outside.write_bytes(b'secret');(home/'class'/'link.txt').symlink_to(outside);os.link(outside,home/'class'/'hard.txt');status,safe=await self.combined(alice,ak);self.assertEqual(status,200);self.assertEqual([e['path'] for e in safe['entries']],['class','class/a.txt'],'links must not enter inventory');
  deferred=self.store.inventory_versions(principal,maximum_total_bytes=3);self.assertEqual(deferred['entries'][1],{'path':'class/a.txt','directory':False})
  self.store.set_permission(ident['sub'],'read',False);self.assertEqual((await self.combined(alice,ak))[0],403);self.store.set_permission(ident['sub'],'read',True);self.store.set_permission(ident['sub'],'list',False);self.assertEqual((await self.combined(alice,ak))[0],403);anon,key=await self.enter(None);self.assertEqual((await self.combined(anon,key))[0],403)
 async def test_bounded_file_count_and_incomplete_tree(self):
  session,key=await self.enter();i=session['identity'];p=Principal(i['sub'],i['sid'],'registered',i['key'],int(time.time())+600);self.store.ensure_user(p)
  for n in range(66):self.store.put(p,f'f{n:02}.txt',b'x')
  result=self.store.inventory_versions(p);self.assertEqual(len(result['entries']),66);self.assertEqual(sum('sha256' in e for e in result['entries']),64)
  status,result=await self.combined(session,key);self.assertEqual(status,200);self.assertEqual(sum('sha256' in e for e in result['entries']),64)
  self.assertFalse(self.store.inventory(p,max_entries=2)['complete'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([InventoryVersions('test_scoped_bounded_inventory_and_external_edit'),InventoryVersions('test_bounded_file_count_and_incomplete_tree')]));sys.exit(not result.wasSuccessful())
