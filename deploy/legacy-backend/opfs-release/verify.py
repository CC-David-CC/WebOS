#!/usr/bin/env python3
"""Check a candidate manifest and every byte, rejecting extras and symlinks."""
import hashlib,json,os,pathlib,stat,sys
root=pathlib.Path(sys.argv[1]);expected=sys.argv[2]
if root.is_symlink() or not root.is_dir():raise ValueError('Invalid candidate root')
manifest_path=root/'manifest.json'
if manifest_path.is_symlink() or not manifest_path.is_file() or manifest_path.stat().st_nlink!=1:raise ValueError('Unsafe manifest')
raw=manifest_path.read_bytes()
if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Manifest hash mismatch')
m=json.loads(raw);assert m['version']=='codi-beta-opfs-candidate/1' and m['notDeployable'] is True
paths=set()
for p in root.rglob('*'):
 if p.is_symlink():raise ValueError('Symlink prohibited')
 if p.is_dir():continue
 if not stat.S_ISREG(p.stat().st_mode) or p.stat().st_nlink!=1:raise ValueError('Unsafe candidate file')
 n=p.relative_to(root).as_posix();paths.add(n)
 if n=='manifest.json':continue
 record=m['files'].get(n)
 if not record:raise ValueError('Unexpected file: '+n)
 b=p.read_bytes()
 if len(b)!=record['bytes'] or hashlib.sha256(b).hexdigest()!=record['sha256']:raise ValueError('Candidate hash mismatch: '+n)
if paths!=set(m['files'])|{'manifest.json'}:raise ValueError('Candidate incomplete')
print('PASS sealed candidate',expected,len(m['files']))
