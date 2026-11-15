"""Exercise actual operator verification with local disposable artifacts."""
import hashlib,importlib.util,json,os,shutil,stat,sys,tempfile
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1]/'active-system'
spec=importlib.util.spec_from_file_location('candidate_operator',root/'file_service/operator.py');op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
BASE=Path(os.environ['CODI_BASE_WORKER']);NEW=Path(os.environ['CODI_DELTA_WORKER'])
def sha(raw):return hashlib.sha256(raw).hexdigest()
def protected(path,mode=None,directory=False,uid=0):
 p=Path(path)
 if p.is_symlink() or not (p.is_dir() if directory else p.is_file()):raise ValueError('Invalid fixture path')
 return p
def read(path,mode=0o600,maximum=65536):
 p=protected(path);raw=p.read_bytes()
 if len(raw)>maximum:raise ValueError('Too large')
 return raw
with tempfile.TemporaryDirectory(prefix='codi-delta-operator-') as d, patch.object(op,'protected',protected),patch.object(op,'read',read):
 for source in (BASE,NEW):
  folder=Path(d)/source.name;shutil.copytree(source,folder)
  manifest=folder/'files-service.json';pin=sha(manifest.read_bytes());op.verify_worker(folder,pin)
  (folder/'unauthorized.py').write_text('unexpected')
  try:op.verify_worker(folder,pin);raise AssertionError('Extra source accepted')
  except ValueError:pass
  (folder/'unauthorized.py').unlink()
  target=folder/'gateway_service/http.py';data=target.read_bytes();target.write_bytes(data+b'\n')
  try:op.verify_worker(folder,pin);raise AssertionError('Changed source accepted')
  except ValueError:pass
  target.write_bytes(data)
  target.unlink();target.symlink_to(folder/'gateway_service/client.mjs')
  try:op.verify_worker(folder,pin);raise AssertionError('Symlink accepted')
  except ValueError:pass
print('PASS operator accepts exact old/new worker inventories and rejects extra, altered and symlink inputs')
