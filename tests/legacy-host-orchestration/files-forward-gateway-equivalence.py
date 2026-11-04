#!/usr/bin/env python3
"""Verify two disposable gateway trees, then compare their complete inventories."""
import hashlib, json, os, pathlib, sys
pins=('c0465afeb10dac4a761b274eb6871a8af750fccc5523a333da2c98dac8b90960','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')
if len(sys.argv)!=3: raise SystemExit('usage: c046-copy dd8-tree')
records=[]
for raw,pin in zip(sys.argv[1:],pins):
 root=pathlib.Path(raw); manifest=(root/'files-service.json').read_bytes()
 if hashlib.sha256(manifest).hexdigest()!=pin: raise ValueError('manifest pin changed')
 entries=json.loads(manifest)['files']; found=set()
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   if (pathlib.Path(base)/name).is_symlink():raise ValueError('symlink')
  for name in files:
   path=pathlib.Path(base)/name; rel=path.relative_to(root).as_posix();found.add(rel)
   if rel=='files-service.json':continue
   data=path.read_bytes(); e=entries.get(rel)
   if not e or len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('inventory drift: '+rel)
 if found!=set(entries)|{'files-service.json'}:raise ValueError('inventory mismatch')
 print(pin,len(entries),'verified');records.append(entries)
for name in sorted(set(records[0])|set(records[1])):
 if records[0].get(name)!=records[1].get(name): print('difference',name,records[0].get(name),records[1].get(name))
