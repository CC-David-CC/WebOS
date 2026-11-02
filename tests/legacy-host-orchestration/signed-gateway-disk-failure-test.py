"""Isolated signed gateway: inject storage faults before and after publish."""
import base64,errno,importlib.util,os,threading,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',ROOT/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class DiskFailure(f.HTTP):
 async def exercise(self,mode):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,created,_,_=await self.binary_upload(alice,key,'document',b'original');self.assertEqual(status,200)
  home=self.store.users_path/alice['identity']['sub'][5:].replace('-','')
  fired=threading.Event();original=self.store.put_stream
  def fail_save(*args,**kwargs):
   real_fsync=os.fsync;real_fdopen=os.fdopen;real_close=os.close;real_publish=self.store._publish
   def fdpath(fd):
    try:return os.readlink('/proc/self/fd/'+str(fd))
    except OSError:return ''
   def fsync(fd):
    path=fdpath(fd)
    if (mode=='temp-fsync' and '/.save-' in path) or (mode=='directory-fsync' and path==str(home)):
     fired.set();raise OSError(errno.EIO,'injected fsync failure')
    return real_fsync(fd)
   class FailedWrite:
    def __init__(self,wrapped):self.wrapped=wrapped;self.calls=0
    def __enter__(self):self.wrapped.__enter__();return self
    def __exit__(self,*args):return self.wrapped.__exit__(*args)
    def write(self,data):
     self.calls+=1
     if self.calls==2:fired.set();raise OSError(errno.ENOSPC,'injected disk full')
     return self.wrapped.write(data)
    def flush(self):return self.wrapped.flush()
   def fdopen(fd,*a,**kw):
    result=real_fdopen(fd,*a,**kw)
    return FailedWrite(result) if mode=='write-enospc' and '/.save-' in fdpath(fd) else result
   def publish(*a,**kw):fired.set();raise OSError(errno.EIO,'injected rename failure')
   def close(fd):
    path=fdpath(fd);real_close(fd)
    if mode=='close-after-publish' and path==str(home/'document')+' (deleted)' and not fired.is_set():
     fired.set();raise OSError(errno.EIO,'injected close failure')
   try:
    os.fsync=fsync;os.fdopen=fdopen;os.close=close
    if mode=='rename':self.store._publish=publish
    return original(*args,**kwargs)
   finally:os.fsync=real_fsync;os.fdopen=real_fdopen;os.close=real_close;self.store._publish=real_publish
  self.store.put_stream=fail_save
  payload=b'Z'*131073
  try:status,result,headers,body=await self.binary_upload(alice,key,'document',payload,operation='replace',previous=created['sha256'])
  finally:self.store.put_stream=original
  self.assertTrue(fired.is_set(),'fault did not reach intended syscall')
  self.assertEqual(status,503 if mode in ('directory-fsync','close-after-publish') else 403)
  if mode in ('directory-fsync','close-after-publish'):self.assertIn('may have completed',result['error'])
  status,read,_=await self.rpc(alice,key,'read','document');self.assertEqual(status,200)
  self.assertEqual(base64.b64decode(read['data']),payload if mode in ('directory-fsync','close-after-publish') else b'original')
  self.assertEqual((await self.rpc(bob,bkey,'read','document'))[0],404)
  async with self.client.post(self.gateway_url+'/gateway/upload',data=body,headers=headers) as replay:self.assertEqual(replay.status,401)
  self.assertFalse(any(p.name.startswith('.save-') for p in home.iterdir()))
 async def test_write_enospc(self):await self.exercise('write-enospc')
 async def test_temp_fsync_failure(self):await self.exercise('temp-fsync')
 async def test_rename_failure(self):await self.exercise('rename')
 async def test_directory_fsync_after_rename(self):await self.exercise('directory-fsync')
 async def test_close_failure_after_rename(self):await self.exercise('close-after-publish')
 async def test_json_write_directory_fsync_after_rename(self):
  alice,key=await self.enter('alice');status,created,_=await self.rpc(alice,key,'create','json-note',data=base64.b64encode(b'old').decode());self.assertEqual(status,200)
  home=self.store.users_path/alice['identity']['sub'][5:].replace('-','');original=self.store.put;fired=threading.Event()
  def put(*args,**kwargs):
   real_fsync=os.fsync
   def fsync(fd):
    try:path=os.readlink('/proc/self/fd/'+str(fd))
    except OSError:path=''
    if path==str(home):fired.set();raise OSError(errno.EIO,'injected directory fsync')
    return real_fsync(fd)
   try:os.fsync=fsync;return original(*args,**kwargs)
   finally:os.fsync=real_fsync
  self.store.put=put
  try:status,result,_=await self.rpc(alice,key,'replace','json-note',data=base64.b64encode(b'new').decode(),previousSHA256=created['sha256'])
  finally:self.store.put=original
  self.assertTrue(fired.is_set());self.assertEqual(status,503);self.assertIn('may have completed',result['error'])
  status,result,_=await self.rpc(alice,key,'read','json-note');self.assertEqual(status,200);self.assertEqual(base64.b64decode(result['data']),b'new')
if __name__=='__main__':
 names=['test_write_enospc','test_temp_fsync_failure','test_rename_failure','test_directory_fsync_after_rename','test_close_failure_after_rename','test_json_write_directory_fsync_after_rename']
 r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(DiskFailure(n) for n in names));raise SystemExit(not r.wasSuccessful())
