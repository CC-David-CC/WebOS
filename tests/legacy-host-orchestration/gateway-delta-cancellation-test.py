"""A cancelled delta snapshot must close the fd after disk work finishes."""
import asyncio
import errno
import os
from pathlib import Path
import sys
import threading
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.http import offload, ReadResponse

async def main():
    before=len(os.listdir('/proc/self/fd'))
    for iteration in range(26):
        started=threading.Event();release=threading.Event();opened=[]
        def snapshot():
            fd=os.open('/dev/null',os.O_RDONLY);opened.append(fd);started.set();release.wait(5)
            return ReadResponse(fd,0,'0'*64) if iteration==25 else (fd,0,'0'*64)
        task=asyncio.create_task(offload(snapshot,cancel_result=lambda result:os.close(result[0])))
        assert await asyncio.to_thread(started.wait,5)
        task.cancel();await asyncio.sleep(0)
        task.cancel();await asyncio.sleep(0)
        assert not task.done(), 'Repeated cancellation released the slot before disk work ended'
        os.fstat(opened[0])
        release.set()
        try:await task;raise AssertionError('Cancellation swallowed')
        except asyncio.CancelledError:pass
        try:os.fstat(opened[0]);raise AssertionError('Snapshot descriptor leaked')
        except OSError as exc:assert exc.errno==errno.EBADF
    assert len(os.listdir('/proc/self/fd'))==before
    print('PASS repeated cancellation retains worker and closes snapshot descriptors')
asyncio.run(main())
