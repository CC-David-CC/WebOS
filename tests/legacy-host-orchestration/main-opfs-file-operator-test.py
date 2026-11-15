#!/usr/bin/env python3
"""Actual successor verification on root-protected disposable worker copies."""
import hashlib,importlib.util,os,pathlib,shutil,sys,tempfile
P=pathlib.Path;operator,old,new=map(P,sys.argv[1:]);assert os.geteuid()==0
assert hashlib.sha256((operator/'file-operator.json').read_bytes()).hexdigest()=='51196fee388840cc23871c69c239cece41db9570d79e96582c4b6653d9c3e082'
s=importlib.util.spec_from_file_location('file_operator_test',operator/'file_service/operator.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
pins=['ffaa4bc40925db28bf9c8b218abae36350c99b9193ade2b5d77800971c3c9055','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1']
with tempfile.TemporaryDirectory(prefix='codi-main-worker-test-',dir='/var/lib') as t:
 os.chmod(t,0o755)
 for i,source in enumerate((old,new)):
  dest=P(t)/str(i);shutil.copytree(source,dest)
  for x in [dest,*dest.rglob('*')]:
   if x.is_symlink():raise ValueError('unexpected link')
   os.chmod(x,0o755 if x.is_dir() else 0o644)
  m.verify_worker(dest,pins[i])
  f=dest/'gateway_service/http.py';raw=f.read_bytes();f.write_bytes(raw+b'\n')
  try:m.verify_worker(dest,pins[i])
  except ValueError:pass
  else:raise AssertionError('tampered file accepted')
  f.write_bytes(raw);x=dest/'unexpected';x.write_bytes(b'x');os.chmod(x,0o644)
  try:m.verify_worker(dest,pins[i])
  except ValueError:pass
  else:raise AssertionError('extra file accepted')
  x.unlink()
  try:m.verify_worker(dest,pins[1-i])
  except ValueError:pass
  else:raise AssertionError('wrong manifest pin accepted')
 print('PASS exact ffaa/dd8 worker verification and tamper/extra/wrong-pin refusals')
