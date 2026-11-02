"""Bounds and integrity of the account delta reconstruction primitive."""
import hashlib
import io
import os
from pathlib import Path
import struct
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'active-system'))
from gateway_service.delta import BLOCK, MAX_FILE, MAX_OPS, apply_patch, signatures
from gateway_service.policy import Denied

with tempfile.TemporaryFile() as base:
    data=bytes(range(256))*(BLOCK//256)*3+b'tail'
    base.write(data);base.flush()
    sig=signatures(base.fileno(),len(data),hashlib.sha256(data).hexdigest())
    assert len(sig['chunks'])==3 and sig['size']==len(data)
    def rejected(patch,size=1,sha='0'*64,declared=None):
        try:
            with tempfile.TemporaryFile() as output:
                apply_patch(base.fileno(),len(data),io.BytesIO(patch),len(patch) if declared is None else declared,output,size,sha)
        except Denied:return
        raise AssertionError('Invalid delta was accepted')
    rejected(b'C'+struct.pack('>II',len(data),1))
    rejected(b'C'+struct.pack('>II',0,0))
    rejected(b'I'+struct.pack('>I',2)+b'x',size=2)
    rejected(b'X')
    rejected((b'I'+struct.pack('>I',1)+b'x')*(MAX_OPS+1),size=MAX_OPS+1)
    rejected(b'I'+struct.pack('>I',1)+b'x',size=1,sha='f'*64)
    rejected(b'I'+struct.pack('>I',1)+b'x',size=1,declared=MAX_FILE+1)
    try:signatures(base.fileno(),MAX_FILE+1,'0'*64);raise AssertionError('oversized signature accepted')
    except Denied:pass
    expected=data[:BLOCK]+b'NEW'+data[BLOCK:2*BLOCK]
    patch=b'C'+struct.pack('>II',0,BLOCK)+b'I'+struct.pack('>I',3)+b'NEW'+b'C'+struct.pack('>II',BLOCK,BLOCK)
    with tempfile.TemporaryFile() as output:
        apply_patch(base.fileno(),len(data),io.BytesIO(patch),len(patch),output,len(expected),hashlib.sha256(expected).hexdigest())
        assert output.read()==expected
print('PASS delta bounds, malformed input, operation limits and exact reconstruction')
