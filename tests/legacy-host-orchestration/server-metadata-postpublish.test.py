"""Signed tests: completed metadata operations with fsync failure."""
import base64,errno,importlib.util,os,threading,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',root/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class PostMutation(f.HTTP):
 async def exercise(self,operation,fault='fsync'):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,created,_=await self.rpc(alice,key,'create','before',data=base64.b64encode(b'original').decode());self.assertEqual(status,200)
  home=self.store.users_path/alice['identity']['sub'][5:].replace('-','');original=getattr(self.store,operation);fired=threading.Event()
  def wrapped(*args,**kwargs):
   real=os.fsync;real_close=os.close;published=False
   def fail(fd):
    nonlocal published
    try:path=os.readlink('/proc/self/fd/'+str(fd))
    except OSError:path=''
    if path==str(home) and fault=='fsync':fired.set();raise OSError(errno.EIO,'injected directory fsync')
    result=real(fd)
    if path==str(home):published=True
    return result
   def close(fd):
    try:path=os.readlink('/proc/self/fd/'+str(fd))
    except OSError:path=''
    result=real_close(fd)
    if fault=='close' and published and (path==str(home) or path.startswith(str(home)+'/')) and not fired.is_set():
     fired.set();raise OSError(errno.EIO,'injected descriptor close failure')
    return result
   try:os.fsync=fail;os.close=close;return original(*args,**kwargs)
   finally:os.fsync=real;os.close=real_close
  setattr(self.store,operation,wrapped)
  try:
   if operation=='mkdir':status,result,_=await self.rpc(alice,key,'mkdir','created')
   elif operation=='delete':status,result,_=await self.rpc(alice,key,'delete','before',previousSHA256=created['sha256'])
   else:status,result,_=await self.rpc(alice,key,'rename','before',destination='after',previousSHA256=created['sha256'])
  finally:setattr(self.store,operation,original)
  self.assertTrue(fired.is_set());self.assertEqual(status,503);self.assertIn('may have completed',result.get('error',''))
  if operation=='mkdir':self.assertTrue((home/'created').is_dir())
  elif operation=='delete':self.assertFalse((home/'before').exists())
  else:self.assertFalse((home/'before').exists());self.assertEqual((home/'after').read_bytes(),b'original')
  self.assertEqual((await self.rpc(bob,bkey,'read','after' if operation=='rename' else 'before'))[0],404)
 async def test_mkdir(self):await self.exercise('mkdir')
 async def test_delete(self):await self.exercise('delete')
 async def test_rename(self):await self.exercise('rename')
 async def test_mkdir_close(self):await self.exercise('mkdir','close')
 async def test_delete_close(self):await self.exercise('delete','close')
 async def test_rename_close(self):await self.exercise('rename','close')

if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(PostMutation(n) for n in ('test_mkdir','test_delete','test_rename','test_mkdir_close','test_delete_close','test_rename_close')));raise SystemExit(not r.wasSuccessful())
