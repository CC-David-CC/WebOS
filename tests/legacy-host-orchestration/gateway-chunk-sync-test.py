#!/usr/bin/env python3
"""Signed isolated gateway chunk-read and existing atomic-delta upload tests."""
import asyncio,base64,hashlib,importlib.util,io,random,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_fixture',ROOT/'active-system/scripts/gateway-http-check.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
from gateway_service import chunk_sync

class Chunks(f.HTTP):
 async def manifest(self,session,key,path,sha):return await self.rpc(session,key,'chunk-manifest-v1',path,previousSHA256=sha)
 async def part(self,session,key,path,sha,c):return await self.rpc(session,key,'chunk-read-v1',path,previousSHA256=sha,offset=c[0],length=c[1],chunkSHA256=c[2])
 async def delta(self,session,key,path,previous,target,patch,interrupt=False):
  metadata={'resource':'my-files','operation':'replace-delta','path':path,'format':'codi-file-delta/1','size':len(target),'sha256':hashlib.sha256(target).hexdigest(),'previousSHA256':previous,'patchSize':len(patch),'patchSHA256':hashlib.sha256(patch).hexdigest()}
  raw=f.jose.dumps(metadata);status,_,headers=await self.authorize(session,key,raw);self.assertEqual(status,200);encoded=raw.encode();body=struct.pack('>I',len(encoded))+encoded+patch
  if interrupt:
   port=int(self.gateway_url.rsplit(':',1)[1]);reader,writer=await asyncio.open_connection('127.0.0.1',port)
   request=('POST /gateway/upload HTTP/1.1\r\nHost: '+self.origin[7:]+'\r\nOrigin: '+self.origin+'\r\nContent-Type: application/octet-stream\r\nContent-Length: '+str(len(body))+'\r\nAuthorization: '+headers['Authorization']+'\r\n\r\n').encode()
   writer.write(request+body[:4+len(encoded)+1]);await writer.drain();writer.close();await writer.wait_closed();await asyncio.sleep(.1);return None
  headers.update({'Host':self.origin[7:],'Origin':self.origin,'Content-Type':'application/octet-stream'})
  async with self.client.post(self.gateway_url+'/gateway/upload',data=body,headers=headers) as r:return r.status,await r.json()
 async def test_signed_chunks_changed_upload_download_and_conflicts(self):
  alice,key=await self.enter('alice');bob,bkey=await self.enter('bobby');data=random.Random(19).randbytes(1024*1024)
  status,created,_,_=await self.binary_upload(alice,key,'a.bin',data);self.assertEqual(status,200);old=created['sha256']
  status,m,_=await self.manifest(alice,key,'a.bin',old);self.assertEqual(status,200,m);self.assertEqual(m['sha256'],old)
  self.assertIn((await self.manifest(bob,bkey,'a.bin',old))[0],(403,404));self.assertNotEqual((await self.part(bob,bkey,'a.bin',old,m['chunks'][0]))[0],200)
  cache={};received=0
  for c in m['chunks']:
   status,item,_=await self.part(alice,key,'a.bin',old,c);self.assertEqual(status,200);block=base64.b64decode(item['data']);self.assertEqual(hashlib.sha256(block).hexdigest(),c[2]);cache[c[2]]=block;received+=len(block)
  changed=data[:333333]+b'Z'+data[333333:]
  with tempfile.TemporaryFile() as t:
   t.write(changed);t.flush();new=chunk_sync.manifest(t.fileno(),len(changed),hashlib.sha256(changed).hexdigest())
  oldmap={h:(off,n) for off,n,h in m['chunks']};patch=bytearray()
  for off,n,h in new['chunks']:
   if h in oldmap:
    oldoff,_=oldmap[h];patch.extend(b'C'+struct.pack('>II',oldoff,n))
   else:patch.extend(b'I'+struct.pack('>I',n)+changed[off:off+n])
  self.assertLess(len(patch),len(changed)//2)
  await self.delta(alice,key,'a.bin',old,changed,patch,interrupt=True);self.assertEqual((await self.manifest(alice,key,'a.bin',old))[0],200)
  status,result=await self.delta(alice,key,'a.bin',old,changed,patch);self.assertEqual(status,200,result)
  self.assertEqual((await self.manifest(alice,key,'a.bin',old))[0],409)
  status,m2,_=await self.manifest(alice,key,'a.bin',result['sha256']);self.assertEqual(status,200);output=bytearray();downloaded=0
  for c in m2['chunks']:
   block=cache.get(c[2])
   if block is None:
    status,item,_=await self.part(alice,key,'a.bin',result['sha256'],c);self.assertEqual(status,200);block=base64.b64decode(item['data']);downloaded+=len(block)
   self.assertEqual(hashlib.sha256(block).hexdigest(),c[2]);output.extend(block)
  self.assertEqual(bytes(output),changed);self.assertLess(downloaded,len(changed)//2)
  bad=m2['chunks'][0].copy();bad[2]='f'*64;self.assertNotEqual((await self.part(alice,key,'a.bin',result['sha256'],bad))[0],200)
  self.assertNotEqual((await self.delta(alice,key,'a.bin',old,changed,patch))[0],200)
  corrupt=b'C'+struct.pack('>II',len(changed)+1,5)
  self.assertNotEqual((await self.delta(alice,key,'a.bin',result['sha256'],b'hello',corrupt))[0],200)
  self.assertEqual((await self.manifest(alice,key,'a.bin',result['sha256']))[0],200)
  left,right=b'concurrent left',b'concurrent right'
  def literal(x):return b'I'+struct.pack('>I',len(x))+x
  pair=await asyncio.gather(self.delta(alice,key,'a.bin',result['sha256'],left,literal(left)),self.delta(alice,key,'a.bin',result['sha256'],right,literal(right)))
  self.assertEqual(sorted(x[0] for x in pair),[200,409],pair)
  print('changed upload bytes:',len(patch),'changed download bytes:',downloaded,'original bytes:',len(data))
 async def test_cached_snapshot_external_edit_and_permission(self):
  from unittest.mock import patch
  session,key=await self.enter('cacheuser');data=random.Random(9).randbytes(512*1024)
  status,created,_,_=await self.binary_upload(session,key,'cache.bin',data);self.assertEqual(status,200);sha=created['sha256']
  with patch.object(self.store,'open_read_snapshot',wraps=self.store.open_read_snapshot) as opened:
   status,m,_=await self.manifest(session,key,'cache.bin',sha);self.assertEqual(status,200)
   for c in m['chunks'][:3]:self.assertEqual((await self.part(session,key,'cache.bin',sha,c))[0],200)
   self.assertEqual(opened.call_count,1,'cache hit must not hash entire file again')
   sub=session['identity']['sub'];path=self.store.users_path/sub[5:].replace('-','')/'cache.bin';before=path.stat()
   # Simulate a host write between cache lookup and the post-read check.
   original=self.store.file_identity;calls=0
   def racing(*args,**kwargs):
    nonlocal calls
    calls+=1
    if calls==2:
     with path.open('r+b') as out:out.write(bytes([data[0]^1]))
    return original(*args,**kwargs)
   with patch.object(self.store,'file_identity',side_effect=racing):
    self.assertNotEqual((await self.part(session,key,'cache.bin',sha,m['chunks'][0]))[0],200)
   # Restore bytes via a fresh direct host write, then get a new valid manifest.
   with path.open('r+b') as out:out.write(data[:1])
   status,m,_=await self.manifest(session,key,'cache.bin',sha);self.assertEqual(status,200);before=path.stat()
   with path.open('r+b') as out:out.seek(0);out.write(bytes([data[0]^1]))
   import os;os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
   self.assertNotEqual((await self.part(session,key,'cache.bin',sha,m['chunks'][0]))[0],200,'same-size external mutation must invalidate snapshot')
   self.store.set_permission(sub,'read',False)
   self.assertNotEqual((await self.part(session,key,'cache.bin',sha,m['chunks'][0]))[0],200,'cache must recheck permission')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Chunks('test_signed_chunks_changed_upload_download_and_conflicts'),Chunks('test_cached_snapshot_external_edit_and_permission')]));sys.exit(not result.wasSuccessful())
