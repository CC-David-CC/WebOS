#!/usr/bin/env python3
"""Bounded cache staging/lease tests; no production paths or data."""
import asyncio,hashlib,os,sys,tempfile,threading,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.chunk_sync import SnapshotCache,identity
from gateway_service.policy import Denied
from gateway_service.http import offload

class Store:
 def __init__(self,root):
  self.paths={a:root/a for a in ('a','b')}
  for name,path in self.paths.items():path.write_bytes((name*40).encode())
  self.started=threading.Event();self.resume=threading.Event();self.block=False;self.fail=False
 def file_identity(self,p,path,*,maximum_bytes):return identity(self.paths[p.sub].stat())
 def open_read_snapshot(self,p,path,*,maximum_bytes):
  self.started.set()
  if self.block and not self.resume.wait(5):raise TimeoutError('test stalled')
  if self.fail:raise OSError('injected open failure')
  fd=os.open(self.paths[p.sub],os.O_RDONLY);data=os.pread(fd,40,0);return fd,len(data),hashlib.sha256(data).hexdigest()

def subject(s):return SimpleNamespace(sub=s)
def version(s):return hashlib.sha256((s*40).encode()).hexdigest()
class Reservations(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.store=Store(Path(self.tmp.name));self.cache=SnapshotCache(self.store,maximum_bytes=64,maximum_entries=2);self.addCleanup(self.cache.close)
 def test_filesystem_reserve_rejects_and_cleans_up(self):
  from types import SimpleNamespace
  self.cache.minimum_free_bytes=10
  with patch('gateway_service.chunk_sync.os.statvfs',return_value=SimpleNamespace(f_bavail=49,f_frsize=1)):
   with self.assertRaises(Denied):self.cache.open(subject('a'),'x',version('a'),64)
  self.assertEqual((self.cache.bytes,self.cache.reserved,self.cache.inflight),(0,0,0))
  # Space can disappear after admission; a post-copy guard drops the staging file.
  with patch('gateway_service.chunk_sync.os.statvfs',side_effect=[SimpleNamespace(f_bavail=100,f_frsize=1),SimpleNamespace(f_bavail=9,f_frsize=1)]):
   with self.assertRaises(Denied):self.cache.open(subject('a'),'x',version('a'),64)
  self.assertEqual((self.cache.bytes,self.cache.reserved,self.cache.inflight),(0,0,0))
 def test_filesystem_reserve_counts_simultaneous_staging(self):
  from types import SimpleNamespace
  self.cache.maximum_bytes=80;self.cache.minimum_free_bytes=0;self.store.block=True;results=[]
  def run():results.append(self.cache.open(subject('a'),'x',version('a'),64)[0])
  with patch('gateway_service.chunk_sync.os.statvfs',return_value=SimpleNamespace(f_bavail=70,f_frsize=1)):
   t=threading.Thread(target=run);t.start();self.assertTrue(self.store.started.wait(2));self.assertEqual(self.cache.reserved,40)
   with self.assertRaises(Denied):self.cache.open(subject('b'),'x',version('b'),64)
   self.store.resume.set();t.join(5);self.assertFalse(t.is_alive());self.assertEqual(len(results),1);results[0].close()
 def test_concurrent_miss_and_active_lease_block_eviction(self):
  self.store.block=True;results=[]
  def run():results.append(self.cache.open(subject('a'),'x',version('a'),64))
  t=threading.Thread(target=run);t.start();self.assertTrue(self.store.started.wait(2));self.assertEqual((self.cache.reserved,self.cache.bytes,self.cache.inflight),(40,0,1))
  with self.assertRaises(Denied):self.cache.open(subject('b'),'x',version('b'),64)
  self.assertLessEqual(self.cache.reserved+self.cache.bytes,64)
  self.store.resume.set();t.join(5);self.assertFalse(t.is_alive());lease=results[0][0];self.assertEqual((self.cache.reserved,self.cache.bytes,self.cache.inflight),(0,40,0))
  with self.assertRaises(Denied):self.cache.open(subject('b'),'x',version('b'),64)
  self.assertEqual(os.pread(lease.fd,40,0),b'a'*40);lease.close();lease.close()
  other=self.cache.open(subject('b'),'x',version('b'),64)[0];self.assertEqual(os.pread(other.fd,40,0),b'b'*40);self.assertEqual(self.cache.bytes,40);other.close()
 def test_identical_concurrent_misses_stay_reserved_and_share_result(self):
  self.cache.maximum_bytes=80;self.store.block=True;results=[];errors=[]
  def run():
   try:results.append(self.cache.open(subject('a'),'x',version('a'),64)[0])
   except Exception as e:errors.append(e)
  threads=[threading.Thread(target=run) for _ in range(2)]
  for t in threads:t.start()
  deadline=time.monotonic()+2
  while self.cache.inflight<2 and time.monotonic()<deadline:time.sleep(.001)
  self.assertEqual((self.cache.reserved,self.cache.inflight),(80,2));self.store.resume.set()
  for t in threads:t.join(5);self.assertFalse(t.is_alive())
  self.assertEqual(errors,[]);self.assertEqual(len(results),2);self.assertEqual((self.cache.bytes,self.cache.reserved),(40,0));self.assertEqual(next(iter(self.cache.entries.values()))['users'],2)
  # Repeated closes from different threads must release just one lease.
  closers=[threading.Thread(target=results[0].close) for _ in range(4)]
  for t in closers:t.start()
  for t in closers:t.join()
  self.assertEqual(next(iter(self.cache.entries.values()))['users'],1);results[1].close();self.assertEqual(next(iter(self.cache.entries.values()))['users'],0)
 def test_close_during_staging_prevents_late_install(self):
  self.store.block=True;errors=[]
  def run():
   try:self.cache.open(subject('a'),'x',version('a'),64)
   except Exception as e:errors.append(e)
  t=threading.Thread(target=run);t.start();self.assertTrue(self.store.started.wait(2));self.cache.close();self.store.resume.set();t.join(5)
  self.assertFalse(t.is_alive());self.assertEqual(len(errors),1);self.assertIsInstance(errors[0],Denied);self.assertEqual((self.cache.bytes,self.cache.reserved,self.cache.inflight),(0,0,0));self.assertFalse(self.cache.entries)
 def test_failures_release_reservation_and_descriptors(self):
  self.store.fail=True
  with self.assertRaises(OSError):self.cache.open(subject('a'),'x',version('a'),64)
  self.store.fail=False
  with patch('gateway_service.chunk_sync.tempfile.TemporaryFile',side_effect=OSError('disk full')):
   with self.assertRaises(OSError):self.cache.open(subject('a'),'x',version('a'),64)
  with patch('gateway_service.chunk_sync.os.dup',side_effect=OSError('descriptor limit')):
   with self.assertRaises(OSError):self.cache.open(subject('a'),'x',version('a'),64)
  self.assertEqual((self.cache.reserved,self.cache.bytes,self.cache.inflight),(0,0,0));self.assertEqual(len(self.cache.entries),0)
  lease=self.cache.open(subject('a'),'x',version('a'),64)[0];self.cache.close();self.assertEqual(self.cache.bytes,40);self.assertEqual(os.pread(lease.fd,40,0),b'a'*40);lease.close();self.assertEqual(self.cache.bytes,0)
  with self.assertRaises(Denied):self.cache.open(subject('a'),'x',version('a'),64)
 def test_repeated_failed_staging_does_not_leak_fds(self):
  baseline=len(os.listdir('/proc/self/fd'))
  for _ in range(25):
   with patch('gateway_service.chunk_sync.os.dup',side_effect=OSError('descriptor limit')):
    with self.assertRaises(OSError):self.cache.open(subject('a'),'x',version('a'),64)
   self.assertEqual((self.cache.bytes,self.cache.reserved,self.cache.inflight),(0,0,0))
  self.assertLessEqual(len(os.listdir('/proc/self/fd')),baseline)
 def test_ambiguous_descriptor_close_stays_accounted(self):
  lease=self.cache.open(subject('a'),'x',version('a'),64)[0];real_close=os.close
  def close_then_error(fd):real_close(fd);raise OSError('ambiguous close')
  with patch('gateway_service.chunk_sync.os.close',side_effect=close_then_error):
   with self.assertRaises(OSError):lease.close()
  self.assertEqual(self.cache.bytes,40);self.assertEqual(lease.item['users'],1)
  with self.assertRaises(Denied):self.cache.open(subject('b'),'x',version('b'),64)
  # Our injected close really closed the descriptor; release only for test cleanup.
  self.cache._release(lease.key,lease.item);self.cache.close();self.assertEqual(self.cache.bytes,0)
 def test_entry_bound_even_for_empty_files(self):
  self.store.paths['a'].write_bytes(b'');self.store.paths['b'].write_bytes(b'');h=hashlib.sha256(b'').hexdigest();self.cache.maximum_entries=1
  lease=self.cache.open(subject('a'),'x',h,64)[0]
  with self.assertRaises(Denied):self.cache.open(subject('b'),'x',h,64)
  lease.close();other=self.cache.open(subject('b'),'x',h,64)[0];self.assertEqual(len(self.cache.entries),1);other.close()
class Cancellation(unittest.IsolatedAsyncioTestCase):
 async def test_cancel_waits_for_thread_and_releases_lease(self):
  with tempfile.TemporaryDirectory() as tmp:
   store=Store(Path(tmp));store.block=True;cache=SnapshotCache(store,maximum_bytes=64)
   def dispatch():
    lease,*_=cache.open(subject('a'),'x',version('a'),64)
    try:return 'finished'
    finally:lease.close()
   task=asyncio.create_task(offload(dispatch))
   self.assertTrue(await asyncio.to_thread(store.started.wait,2));task.cancel();await asyncio.sleep(.03);task.cancel();await asyncio.sleep(.03)
   self.assertFalse(task.done());self.assertEqual(cache.reserved,40)
   with self.assertRaises(Denied):await asyncio.to_thread(cache.open,subject('b'),'x',version('b'),64)
   store.resume.set()
   with self.assertRaises(asyncio.CancelledError):await task
   self.assertEqual((cache.reserved,cache.inflight),(0,0));self.assertTrue(all(v['users']==0 for v in cache.entries.values()));cache.close();self.assertEqual(cache.bytes,0)
if __name__=='__main__':unittest.main()
