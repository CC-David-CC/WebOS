#!/usr/bin/env python3
"""Switch anonymous rendezvous introductions; existing P2P links are unaffected."""
import argparse,os,stat,tempfile
from pathlib import Path
POLICY=Path('/var/lib/codi-connected/ksu/network-policy/anonymous-introductions')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('state',choices=['enabled','disabled']);args=parser.parse_args()
 if os.geteuid()!=0:raise SystemExit('Root is required')
 parent=POLICY.parent;info=parent.lstat()
 if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or stat.S_IMODE(info.st_mode)&0o022:raise SystemExit('Untrusted policy directory')
 if POLICY.is_symlink():raise SystemExit('Refusing symbolic policy file')
 fd,name=tempfile.mkstemp(prefix='.anonymous-introductions-',dir=parent)
 try:
  with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),0o644);out.write((args.state+'\n').encode());out.flush();os.fsync(out.fileno())
  os.replace(name,POLICY);directory=os.open(parent,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
  try:os.fsync(directory)
  finally:os.close(directory)
 finally:
  if os.path.exists(name):os.unlink(name)
 print('Anonymous introductions '+args.state+'. Existing peer connections may continue.')
if __name__=='__main__':main()
