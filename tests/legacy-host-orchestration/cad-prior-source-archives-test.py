#!/usr/bin/env python3
"""Check exact archived inputs and pinned source/license members."""
import hashlib,importlib.util,pathlib,sys,zipfile
P=pathlib.Path;root=P(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('cad_preparer',root/'apps/system/jsketcher/prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
numeric,engine=map(P,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest()
assert m.sha256_file(numeric)=='00ec7f37fcb940cd55db1aa142ee27d8b2ca784edd1f02704693a37a0f63df0c'
assert m.sha256_file(engine)=='5c7e9dfca8f9c5f01e1da0e672039ec0e19a78e78fb3ec41bbb330ae71febe39'
with zipfile.ZipFile(numeric) as z:
 assert sha(b''.join(m.checked_archive_member(z,n) for n in ('src/numeric.js','src/seedrandom.js','src/quadprog.js','src/svd.js')))==m.NUMERIC_INPUT_SHA256
 for n,pin in m.NUMERIC_NOTICE_SHA256.items():assert sha(m.checked_archive_member(z,n))==pin
with zipfile.ZipFile(engine) as z:
 for n,(_,pin) in m.ENGINE_SOURCE_NOTICES.items():assert sha(m.checked_archive_member(z,n))==pin
print('PASS exact prior numeric/interpreter archive hashes and pinned source/license members; commit attribution derives from prior receipt')
