"""Exercise slot expiry without deleting live slots or refunding usage."""
import asyncio,importlib.util,threading,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',root/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
from gateway_service.policy import Principal
from gateway_service.http import finish_transfer

class Recovery(f.HTTP):
 async def test_cancel_during_failed_finish_retries_without_refund(self):
  quotas=f.Quotas(self.store,daily_bytes=10000,shared_daily_bytes=30000,bytes_per_use=1000,concurrent_uses=2,shared_concurrent_uses=4)
  principal=Principal('user:00000001-1111-4111-8111-111111111111','test','registered',{},int(self.store.clock())+120)
  transfer=quotas.begin(principal,100);other=quotas.begin(principal,100)
  started=threading.Event();release=threading.Event();calls=[]
  class Flaky:
   def finish(self,item):
    calls.append(item.id)
    if len(calls)==1:
     started.set();release.wait(2);raise OSError('injected cleanup failure')
    quotas.finish(item)
  task=asyncio.create_task(finish_transfer(Flaky(),transfer))
  self.assertTrue(await asyncio.to_thread(started.wait,2))
  task.cancel();task.cancel();release.set()
  await asyncio.sleep(.01);task.cancel()
  with self.assertRaises(asyncio.CancelledError):await asyncio.wait_for(task,2)
  self.assertEqual(calls,[transfer.id,transfer.id])
  with self.store.db() as db:
   active={r[0] for r in db.execute('SELECT id FROM gateway_active_uses')}
   usage=dict(db.execute('SELECT subject,bytes FROM gateway_usage').fetchall())
  self.assertEqual(active,{other.id});self.assertEqual(usage,{principal.sub:200,'*':200})
 async def test_failed_cleanup_slots_expire_without_refund(self):
  now=[1700000000];self.store.clock=lambda:now[0]
  quotas=f.Quotas(self.store,daily_bytes=10000,shared_daily_bytes=30000,bytes_per_use=1000,concurrent_uses=2,shared_concurrent_uses=4)
  def person(number,deadline):return Principal('user:%08d-1111-4111-8111-111111111111'%number,'test','registered',{},deadline)
  alice=person(1,now[0]+10);bob=person(2,now[0]+20);carol=person(3,now[0]+30)
  transfers=[quotas.begin(alice,100),quotas.begin(alice,100),quotas.begin(bob,100),quotas.begin(bob,100)]
  with self.assertRaises(f.AllowanceExceeded):quotas.begin(carol,100)
  now[0]+=10
  replacement=quotas.begin(carol,100)
  with self.store.db() as db:
   active={r[0] for r in db.execute('SELECT id FROM gateway_active_uses')}
   usage=dict(db.execute('SELECT subject,bytes FROM gateway_usage').fetchall())
  self.assertEqual(active,{transfers[2].id,transfers[3].id,replacement.id})
  self.assertEqual(usage,{alice.sub:200,bob.sub:200,carol.sub:100,'*':500})
  quotas.finish(transfers[0]);quotas.finish(replacement)
  with self.store.db() as db:
   active={r[0] for r in db.execute('SELECT id FROM gateway_active_uses')}
   self.assertEqual(active,{transfers[2].id,transfers[3].id})
   self.assertEqual(dict(db.execute('SELECT subject,bytes FROM gateway_usage').fetchall()),usage)

if __name__=='__main__':
 names=['test_failed_cleanup_slots_expire_without_refund','test_cancel_during_failed_finish_retries_without_refund']
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(Recovery(n) for n in names));raise SystemExit(not result.wasSuccessful())
