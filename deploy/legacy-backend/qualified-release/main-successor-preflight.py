"""Exact beta recovery successor bundle required before main restriction.

Caller holds the existing hosting lock, checks protected ancestors, and provides
its no-follow bounded read helper. This verifies bytes/custody, not installation,
process quiescence, or execution health.
"""
import hashlib,json,os,stat
from pathlib import Path
INVENTORY='bc9f939a9db8849fb7d580e5a71d5c52728b127b74c3bca1ee811b41fdd1f754'

def verify(bundle,read,check_lock):
 check_lock();bundle=Path(bundle)
 def custody(path,directory):
  v=path.lstat()
  if v.st_uid!=0 or v.st_mode&0o022 or (directory and not stat.S_ISDIR(v.st_mode)) or (not directory and (not stat.S_ISREG(v.st_mode) or v.st_nlink!=1)) or os.listxattr(path,follow_symlinks=False):
   raise ValueError('Unsafe successor bundle entry: '+str(path))
 custody(bundle,True);inventory=bundle/'inventory.json';custody(inventory,False);raw=read(inventory)
 if hashlib.sha256(raw).hexdigest()!=INVENTORY:raise ValueError('Successor inventory pin mismatch')
 records=json.loads(raw)
 if not isinstance(records,dict) or len(records)!=28:raise ValueError('Unexpected successor inventory')
 expected_dirs={'.'}
 for name,digest in records.items():
  path=Path(name)
  if not isinstance(name,str) or path.is_absolute() or any(p in ('','.','..') for p in name.split('/')) or not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Unsafe successor inventory name/hash')
  expected_dirs.update(str(parent) for parent in path.parents)
 found_files={'inventory.json'};found_dirs={'.'}
 for base,dirs,files in os.walk(bundle,followlinks=False):
  for name in dirs:
   path=Path(base)/name;custody(path,True);found_dirs.add(str(path.relative_to(bundle)))
  for name in files:
   path=Path(base)/name;custody(path,False);rel=str(path.relative_to(bundle))
   if rel=='inventory.json':continue
   if rel not in records or hashlib.sha256(read(path)).hexdigest()!=records[rel]:raise ValueError('Successor file pin mismatch: '+rel)
   found_files.add(rel)
 if found_files!=set(records)|{'inventory.json'} or found_dirs!=expected_dirs:raise ValueError('Successor bundle inventory differs')
 check_lock()
