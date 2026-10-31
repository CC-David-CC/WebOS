#!/usr/bin/env python3
"""Small bounded signed mixed-workload check; not a 100-user benchmark."""
import asyncio,importlib.util,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('batch_fixture',ROOT/'active-system/scripts/gateway-batch-version-check.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from gateway_service.policy import Principal
class Mixed(module.Batch):
 async def runTest(self):
  users=[];paths=[f'file{i:02}.txt' for i in range(16)];payload=b'x'*4096
  for i in range(8):
   session,key=await self.enter('batchuser'+str(i));identity=session['identity'];principal=Principal(identity['sub'],identity['sid'],'registered',identity['key'],int(time.time())+600);self.store.ensure_user(principal)
   for name in paths:self.store.put(principal,name,payload)
   users.append((session,key))
  async def check(index):
   before=time.monotonic();status,result,_=await self.batch(*users[index],paths);self.assertEqual(status,200,result);self.assertEqual(len(result['entries']),16);self.assertTrue(all(item.get('bytes')==len(payload) for item in result['entries']));return time.monotonic()-before
  before=time.monotonic();times=[]
  for i in range(0,8,2):times.extend(await asyncio.gather(check(i),check(i+1)))
  # One binary write and one full batch share the service simultaneously.
  upload=asyncio.create_task(self.binary_upload(*users[0],path='upload.bin',payload=b'y'*(2*1024*1024)));batch=asyncio.create_task(check(1));uploaded,duration=await asyncio.gather(upload,batch);self.assertEqual(uploaded[0],200,uploaded[1]);times.append(duration)
  print(json.dumps({'users':8,'batchRequests':9,'filesPerBatch':16,'overlapUploadBytes':2*1024*1024,'elapsedSeconds':round(time.monotonic()-before,3),'maxBatchSeconds':round(max(times),3),'scope':'local fixture; not a 100-user capacity test'}),flush=True)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Mixed()]));sys.exit(not result.wasSuccessful())
