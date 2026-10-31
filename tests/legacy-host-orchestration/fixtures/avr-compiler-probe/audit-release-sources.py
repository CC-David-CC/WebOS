#!/usr/bin/env python3
"""Check source-file provenance for the pinned AVR research release.

This is a partial audit: it does not establish the sources of compiler binaries,
precompiled libraries or headers, or determine redistribution requirements.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

REV='23058387b320a133f36c701d55c5cde420caac42'
ARCHIVE_SHA='639a745994b00eb8d806f80c2302056f76403c9dc737df0676da81418c7ddd17'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path);p.add_argument('repository',type=Path);a=p.parse_args()
 if digest(a.archive)!=ARCHIVE_SHA:raise ValueError('Release archive hash does not match the pinned release')
 repo=a.repository.resolve(strict=True)
 def git(*args):return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True).stdout
 if git('rev-parse','HEAD').decode().strip()!=REV:raise ValueError('Unexpected source repository revision')
 with tarfile.open(a.archive,'r:') as tar:
  entries={}
  for m in tar.getmembers():
   n=m.name.removeprefix('./');path=PurePosixPath(n)
   if n in entries or path.is_absolute() or '..' in path.parts:raise ValueError('Unexpected archive path')
   entries[n]=m
  manifest_entry=entries.get('manifest.json')
  if not manifest_entry or not manifest_entry.isfile() or manifest_entry.size>1024*1024:raise ValueError('Invalid release manifest')
  manifest=json.load(tar.extractfile(manifest_entry));groups={'core':manifest['core'],'libraries':[p for library in manifest['libraries'].values() for p in library['files']]};counts={}
  for group,paths in groups.items():
   if not isinstance(paths,list) or len(paths)!=len(set(paths)) or len(paths)>1000:raise ValueError('Invalid manifest entries')
   for name in paths:
    if not isinstance(name,str) or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts:raise ValueError('Invalid source path')
    member=entries.get(name)
    if not member or not member.isfile() or member.size>2*1024*1024:raise ValueError('Missing or invalid release source '+name)
    if group=='core':
     if not name.startswith('arduino-core/'):raise ValueError('Unexpected core path')
     source='src/'+name
    else:
     parts=name.split('/',2)
     if len(parts)!=3 or parts[0]!='libraries':raise ValueError('Unexpected library path')
     prefix='libraries/'+parts[1]+'/';candidate=prefix+'src/'+parts[2]
     try:git('cat-file','-e',REV+':'+candidate);source=candidate
     except subprocess.CalledProcessError:source=prefix+parts[2]
    committed=git('show',REV+':'+source);released=tar.extractfile(member).read()
    if committed!=released:raise ValueError('Release differs from tagged source: '+name)
   counts[group]=len(paths)
  print(json.dumps({'archiveSHA256':ARCHIVE_SHA,'sourceRevision':REV,'matched':counts,'libraries':sorted(manifest['libraries']),'scope':'Arduino core and bundled library source only; toolchain binary provenance not established'},indent=2))
if __name__=='__main__':main()
