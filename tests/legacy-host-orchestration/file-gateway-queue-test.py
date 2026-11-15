#!/usr/bin/env python3
"""Bounded queue, cancellation, timeouts, and real HTTP admission checks."""
import asyncio,base64,importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('gateway_fixture',ROOT/'active-system/scripts/gateway-http-check.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class Queue(f.HTTP):
 async def occupy(self):
  for _ in range(4):await self.gateway._admit()
 def release(self):self.gateway.active-=1;self.gateway.slots.release()
 async def test_bounded_queue_timeout_and_cancellation_release_slots(self):
  self.gateway.max_waiters=2;self.gateway.queue_seconds=.2;await self.occupy();a=asyncio.create_task(self.gateway._admit());b=asyncio.create_task(self.gateway._admit());await asyncio.sleep(.01);self.assertEqual(self.gateway.waiting,2)
  with self.assertRaises(f.web.HTTPTooManyRequests):await self.gateway._admit()
  a.cancel()
  with self.assertRaises(asyncio.CancelledError):await a
  self.assertEqual(self.gateway.waiting,1);self.release();await b;self.assertEqual(self.gateway.active,4)
  with self.assertRaises(f.web.HTTPTooManyRequests):await self.gateway._admit()
  self.assertEqual(self.gateway.waiting,0)
  for _ in range(4):self.release()
  self.assertEqual(self.gateway.active,0);self.assertEqual(self.gateway.slots._value,4)
 async def test_repeated_cancel_during_handoff_does_not_leak_slots(self):
  self.gateway.max_waiters=128;self.gateway.queue_seconds=2
  async def operation():
   admitted=False
   try:
    await self.gateway._admit();admitted=True;await asyncio.sleep(.002)
   finally:
    if admitted:self.release()
  for _ in range(20):
   tasks=[asyncio.create_task(operation()) for _ in range(24)];await asyncio.sleep(0)
   for task in tasks[::3]:task.cancel()
   await asyncio.gather(*tasks,return_exceptions=True)
   self.assertEqual(self.gateway.active,0);self.assertEqual(self.gateway.waiting,0);self.assertEqual(self.gateway.slots._value,4)
 async def test_disconnected_waiter_does_not_consume_or_run_operation(self):
  session,key=await self.enter();raw=f.jose.dumps({'resource':'my-files','operation':'create','path':'waiter.txt','data':base64.b64encode(b'only once').decode()});status,result,headers=await self.authorize(session,key,raw);self.assertEqual(status,200,result)
  await self.occupy();request=asyncio.create_task(self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw))
  for _ in range(200):
   if self.gateway.waiting==1:break
   await asyncio.sleep(.005)
  self.assertEqual(self.gateway.waiting,1);request.cancel()
  with self.assertRaises(asyncio.CancelledError):await request
  await asyncio.sleep(.05);self.release()
  for _ in range(200):
   if self.gateway.waiting==0 and self.gateway.active==3:break
   await asyncio.sleep(.005)
  self.assertEqual(self.gateway.waiting,0);self.assertEqual(self.gateway.active,3)
  # The proof was not consumed and the queued create was not run.
  status,result,_=await self.post('/gateway/use',{},gateway=True,headers=headers,raw=raw);self.assertEqual(status,200,result)
  status,result,_=await self.rpc(session,key,'read','waiter.txt');self.assertEqual(status,200);self.assertEqual(base64.b64decode(result['data']),b'only once')
  for _ in range(200):
   if self.gateway.active==3:break
   await asyncio.sleep(.005)
  self.assertEqual(self.gateway.active,3)
  for _ in range(3):self.release()
  self.assertEqual(self.gateway.slots._value,4)
 async def test_cleanup_failure_still_releases_the_slot(self):
  session,key=await self.enter();finish=self.gateway.quotas.finish
  def fail_after_cleanup(transfer):
   finish(transfer);raise RuntimeError('test cleanup failure')
  self.gateway.quotas.finish=fail_after_cleanup
  try:
   status,result,_=await self.rpc(session,key,'list');self.assertEqual(status,200,result)
   for _ in range(200):
    if self.gateway.active==0:break
    await asyncio.sleep(.005)
   self.assertEqual(self.gateway.active,0);self.assertEqual(self.gateway.waiting,0);self.assertEqual(self.gateway.slots._value,4)
  finally:self.gateway.quotas.finish=finish
 async def test_real_http_requests_wait_then_resume(self):
  self.gateway.max_waiters=2;self.gateway.queue_seconds=2;await self.occupy();key=f.ec.generate_private_key(f.ec.SECP256R1());value={'key':f.jose.public_jwk(key),'request_sha256':f.jose.digest('fixture')}
  first=asyncio.create_task(self.post('/gateway/challenge',value,gateway=True));second=asyncio.create_task(self.post('/gateway/challenge',value,gateway=True))
  for _ in range(200):
   if self.gateway.waiting==2:break
   await asyncio.sleep(.005)
  self.assertEqual(self.gateway.waiting,2);status,result,_=await self.post('/gateway/challenge',value,gateway=True);self.assertEqual(status,429,result)
  self.release();self.assertEqual((await first)[0],200);self.assertEqual((await second)[0],200)
  for _ in range(3):self.release()
  self.assertEqual(self.gateway.active,0);self.assertEqual(self.gateway.waiting,0);self.assertEqual(self.gateway.slots._value,4)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Queue('test_bounded_queue_timeout_and_cancellation_release_slots'),Queue('test_real_http_requests_wait_then_resume'),Queue('test_repeated_cancel_during_handoff_does_not_leak_slots'),Queue('test_disconnected_waiter_does_not_consume_or_run_operation'),Queue('test_cleanup_failure_still_releases_the_slot')]));sys.exit(not result.wasSuccessful())
