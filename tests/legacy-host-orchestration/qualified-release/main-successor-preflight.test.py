#!/usr/bin/env python3
"""Disposable root-owned custody tests; does not install a launcher."""
import importlib.util,os,shutil,stat,sys,tempfile
from pathlib import Path
assert os.geteuid()==0, 'run in a disposable root-owned fixture'
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('main_preflight',here/'main-successor-preflight.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=Path(sys.argv[1]);read=lambda p:Path(p).read_bytes();held=[True]
def check():
 if not held[0]:raise ValueError('lock not held')
def refused(path):
 try:m.verify(path,read,check)
 except (ValueError,OSError):return
 raise AssertionError('unsafe bundle accepted')
with tempfile.TemporaryDirectory(prefix='codi-main-successor-preflight-',dir='/run') as t:
 bundle=Path(t)/'bundle';shutil.copytree(source,bundle)
 for path in bundle.rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
 m.verify(bundle,read,check)
 held[0]=False;refused(bundle);held[0]=True
 extra=bundle/'extra';extra.write_text('unexpected');refused(bundle);extra.unlink()
 item=bundle/'ops/beta_successor.py';original=item.read_bytes();item.write_bytes(original+b'\n');refused(bundle);item.write_bytes(original)
 item.chmod(0o666);refused(bundle);item.chmod(0o644)
 original_link=bundle/'ops/copy';os.link(item,original_link);refused(bundle);original_link.unlink()
 item.unlink();item.symlink_to('/etc/passwd');refused(bundle);item.unlink();item.write_bytes(original);item.chmod(0o644)
 try:
  os.setxattr(item,'user.test',b'x');refused(bundle);os.removexattr(item,'user.test')
 except OSError:pass
 m.verify(bundle,read,check)
print('PASS exact successor inventory, missing lock, drift, extra, mode, hardlink, symlink and available xattr refusal')
