#!/usr/bin/env python3
"""Exact worker allowlist must reject either missing hash module or notices."""
import hashlib,importlib.util,json,os,shutil,tempfile
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1]/'active-system';spec=importlib.util.spec_from_file_location('candidate_operator',root/'file_service/operator.py');op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
def protected(path,mode=None,directory=False,uid=0):
 p=Path(path)
 if p.is_symlink() or not (p.is_dir() if directory else p.is_file()):raise ValueError('Invalid fixture')
 return p
def read(path,mode=0o600,maximum=65536):
 raw=protected(path).read_bytes()
 if len(raw)>maximum:raise ValueError('Input too large')
 return raw
source=Path(os.environ['CODI_CHUNK_WORKER'])
with tempfile.TemporaryDirectory(prefix='codi-hash-inventory-') as tmp, patch.object(op,'protected',protected),patch.object(op,'read',read):
 folder=Path(tmp)/'worker';shutil.copytree(source,folder);pin=hashlib.sha256((folder/'files-service.json').read_bytes()).hexdigest();op.verify_worker(folder,pin)
 for name in ('core.mjs','shared.mjs','LICENSE.txt'):
  p=folder/'gateway_service/vendor/js-sha256'/name;data=p.read_bytes();p.unlink()
  try:op.verify_worker(folder,pin);raise AssertionError('Missing '+name+' accepted')
  except (ValueError,FileNotFoundError):pass
  p.write_bytes(data)
  # Even an attacker or mistaken packager who recomputes the manifest cannot
  # create an allowed inventory with only one dependency absent.
  manifest=folder/'files-service.json';original=manifest.read_bytes();doc=json.loads(original);del doc['files']['gateway_service/vendor/js-sha256/'+name];altered=(json.dumps(doc,indent=2,sort_keys=True)+'\n').encode();manifest.write_bytes(altered);p.unlink()
  try:op.verify_worker(folder,hashlib.sha256(altered).hexdigest());raise AssertionError('Reduced inventory accepted')
  except (ValueError,FileNotFoundError):pass
  p.write_bytes(data);manifest.write_bytes(original)
 op.verify_worker(folder,pin)
print('PASS exact worker inventory rejects both missing hash modules and missing license')
