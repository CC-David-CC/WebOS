#!/usr/bin/env python3
"""Bounded local signed inventory workload; not a 100-user benchmark."""
import asyncio,importlib.util,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('inventory_checks',ROOT/'gateway-inventory-test.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from gateway_service.policy import Principal
class Mixed(module.Inventory):
 async def runTest(self):
  users=[]
  for i in range(8):
   session,key=await self.enter('inventoryuser'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.store.ensure_user(principal)
   for n in range(6):self.store.mkdir(principal,'folder'+str(n));self.store.put(principal,'folder'+str(n)+'/note.txt',b'data')
   users.append((session,key))
  async def check(i):
   before=time.monotonic();status,result=await self.inventory(*users[i]);self.assertEqual(status,200,result);self.assertTrue(result['complete']);self.assertEqual(len(result['entries']),12);return time.monotonic()-before
  before=time.monotonic();times=[]
  for i in range(0,8,2):times.extend(await asyncio.gather(check(i),check(i+1)))
  upload=asyncio.create_task(self.binary_upload(*users[0],path='upload.bin',payload=b'x'*(2*1024*1024)));scan=asyncio.create_task(check(1));result,duration=await asyncio.gather(upload,scan);self.assertEqual(result[0],200,result[1]);times.append(duration)
  print(json.dumps({'accounts':8,'inventories':9,'directoriesPerAccount':6,'overlapUploadBytes':2097152,'elapsedSeconds':round(time.monotonic()-before,3),'maxInventorySeconds':round(max(times),3),'scope':'local fixture, not a 100-user test'}),flush=True)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Mixed()]));sys.exit(not result.wasSuccessful())
