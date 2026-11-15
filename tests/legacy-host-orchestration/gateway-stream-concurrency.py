#!/usr/bin/env python3
"""Two real signed 128 MiB uploads in parallel, with bounded fixture memory."""
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gateway_http_fixture',ROOT/'active-system/scripts/gateway-http-check.py')
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

class Concurrent128(fixture.HTTP):
    async def runTest(self):
        alice,ak=await self.enter('alice');bob,bk=await self.enter('bob')
        size=128*1024*1024;chunk_size=65536
        async def upload(account,key,value):
            block=bytes([value])*chunk_size;hasher=hashlib.sha256()
            for _ in range(size//chunk_size):hasher.update(block)
            digest=hasher.hexdigest()
            meta={'resource':'my-files','operation':'create','path':'large.bin','format':'codi-binary-upload/1','size':size,'sha256':digest}
            raw=fixture.jose.dumps(meta);status,result,auth=await self.authorize(account,key,raw);self.assertEqual(status,200,result)
            header=struct.pack('>I',len(raw.encode()))+raw.encode()
            async def source():
                yield header
                for _ in range(size//chunk_size):yield block
            headers={'Host':self.origin.removeprefix('http://'),'Origin':self.origin,'Content-Type':'application/octet-stream','Content-Length':str(len(header)+size),**auth}
            async with self.client.post(self.gateway_url+'/gateway/upload',data=source(),headers=headers) as response:
                result=await response.json();self.assertEqual(response.status,200,result)
            self.assertEqual(result['sha256'],digest);self.assertEqual(result['bytes'],size)
            return account,digest
        before=time.monotonic();first,second=await asyncio.gather(upload(alice,ak,65),upload(bob,bk,66))
        for account,digest in (first,second):
            sub=account['identity']['sub'];home=self.store.data_root/'users'/sub[5:].replace('-','')
            file=home/'large.bin';self.assertEqual(file.stat().st_size,size)
            with file.open('rb') as f:self.assertEqual(hashlib.file_digest(f,'sha256').hexdigest(),digest)
        peak=int(next(line.split()[1] for line in Path('/proc/self/status').read_text().splitlines() if line.startswith('VmHWM:')))
        self.assertLess(peak,384*1024,'Fixture exceeded live gateway memory cap')
        print(json.dumps({'concurrentUploads':2,'bytesEach':size,'elapsedSeconds':round(time.monotonic()-before,1),'peakKiB':peak}),flush=True)

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Concurrent128()]))
    raise SystemExit(not result.wasSuccessful())
