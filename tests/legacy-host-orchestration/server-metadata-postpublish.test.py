"""Signed tests: completed metadata operations with fsync failure."""
import base64,errno,importlib.util,os,threading,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',root/'active-system/scripts/gateway-http-check.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

class PostMutation(f.HTTP):
 async def exercise(self,operation):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bob')
  status,created,_=await self.rpc(alice,key,'create','before',data=base64.b64encode(b'original').decode());self.assertEqual(status,200)
  home=self.store.users_path/alice['identity']['sub'][5:].replace('-','');original=getattr(self.store,operation);fired=threading.Event()
  def wrapped(*args,**kwargs):
   real=os.fsync
   def fail(fd):
    try:path=os.readlink('/proc/self/fd/'+str(fd))
    except OSError:path=''
    if path==str(home):fired.set();raise OSError(errno.EIO,'injected directory fsync')
    return real(fd)
   try:os.fsync=fail;return original(*args,**kwargs)
   finally:os.fsync=real
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

if __name__=='__main__':
 r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(PostMutation(n) for n in ('test_mkdir','test_delete','test_rename')));raise SystemExit(not r.wasSuccessful())
