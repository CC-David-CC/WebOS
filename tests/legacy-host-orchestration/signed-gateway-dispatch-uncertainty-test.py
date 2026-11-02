"""Test response failures and timeouts around actual signed mutations."""
import base64,dataclasses,importlib.util,math,time,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',root/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class Dispatch(f.HTTP):
 async def exercise_timeout(self,when):
  alice,key=await self.enter('alice');_,created,_=await self.rpc(alice,key,'create','note',data=base64.b64encode(b'old').decode())
  begin=self.gateway.gate.begin;dispatch=self.gateway._dispatch
  def short(*args,**kwargs):
   use=begin(*args,**kwargs);return dataclasses.replace(use,principal=dataclasses.replace(use.principal,deadline=math.ceil(time.time())+1))
  def delayed(principal,data):
   if when=='before':time.sleep(3)
   result=dispatch(principal,data)
   if when=='after':time.sleep(3)
   return result
  self.gateway.gate.begin=short;self.gateway._dispatch=delayed
  try:status,result,_=await self.rpc(alice,key,'replace','note',data=base64.b64encode(b'new').decode(),previousSHA256=created['sha256'])
  finally:self.gateway.gate.begin=begin;self.gateway._dispatch=dispatch
  self.assertEqual(status,503);self.assertIn('may have completed',result['error'])
  status,read,_=await self.rpc(alice,key,'read','note');self.assertEqual(status,200)
  self.assertEqual(base64.b64decode(read['data']),b'old' if when=='before' else b'new')
 async def test_timeout_before_store_returns_uncertain(self):await self.exercise_timeout('before')
 async def test_timeout_after_mutation_returns_uncertain(self):await self.exercise_timeout('after')
 async def test_binary_timeout_after_mutation_returns_uncertain(self):
  alice,key=await self.enter('alice');_,created,_,_=await self.binary_upload(alice,key,'note',b'old')
  begin=self.gateway.gate.begin;put=self.gateway.store.put_stream
  def short(*args,**kwargs):
   use=begin(*args,**kwargs);return dataclasses.replace(use,principal=dataclasses.replace(use.principal,deadline=math.ceil(time.time())+1))
  def delayed(*args,**kwargs):
   result=put(*args,**kwargs);time.sleep(3);return result
  self.gateway.gate.begin=short;self.gateway.store.put_stream=delayed
  try:status,result,_,_=await self.binary_upload(alice,key,'note',b'new',operation='replace',previous=created['sha256'])
  finally:self.gateway.gate.begin=begin;self.gateway.store.put_stream=put
  self.assertEqual(status,503);self.assertIn('may have completed',result['error'])
  self.assertEqual(base64.b64decode((await self.rpc(alice,key,'read','note'))[1]['data']),b'new')
 async def test_response_encoding_failure_after_mutation(self):
  alice,key=await self.enter('alice');_,created,_=await self.rpc(alice,key,'create','note',data=base64.b64encode(b'old').decode())
  dispatch=self.gateway._dispatch;dumps=f.jose.dumps;fired=[]
  def failing_once(value):
   if isinstance(value,dict) and set(value)=={'bytes','sha256'} and not fired:
    fired.append(True);f.jose.dumps=dumps;raise ValueError('injected response encoding failure')
   return dumps(value)
  def wrapped(principal,data):
   result=dispatch(principal,data);f.jose.dumps=failing_once;return result
  self.gateway._dispatch=wrapped
  try:status,result,_=await self.rpc(alice,key,'replace','note',data=base64.b64encode(b'new').decode(),previousSHA256=created['sha256'])
  finally:self.gateway._dispatch=dispatch;f.jose.dumps=dumps
  self.assertTrue(fired);self.assertEqual(status,503);self.assertIn('may have completed',result['error'])
  self.assertEqual(base64.b64decode((await self.rpc(alice,key,'read','note'))[1]['data']),b'new')
if __name__=='__main__':
 names=['test_timeout_before_store_returns_uncertain','test_timeout_after_mutation_returns_uncertain','test_binary_timeout_after_mutation_returns_uncertain','test_response_encoding_failure_after_mutation']
 r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Dispatch(n) for n in names));raise SystemExit(not r.wasSuccessful())
