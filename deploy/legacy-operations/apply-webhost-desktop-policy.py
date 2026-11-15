#!/usr/bin/env python3
"""Apply the reviewed hosting-generator source under its controller lock on box-webhost."""
import argparse,fcntl,hashlib,importlib,json,sys
from pathlib import Path
ROOT=Path('/home/dflanag3/webhost-sites')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--candidate-sha256',required=True);p.add_argument('--original-sha256',required=True);p.add_argument('--manifest-sha256',required=True);a=p.parse_args()
 sys.path.insert(0,str(ROOT/'ops'));import webctl as ctl;import common
 ctl.root_required()
 with (ROOT/'.controller.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  source=ROOT/'ops/common.py'
  if source.is_symlink() or a.candidate.is_symlink() or digest(source)!=a.original_sha256 or digest(a.candidate)!=a.candidate_sha256 or digest(ROOT/'sites.toml')!=a.manifest_sha256:raise ValueError('Hosting source/candidate/manifest changed; review again before applying')
  raw=source.read_bytes();info=source.stat();mode=ctl.current_mode()
  if mode!='production':raise ValueError('Expected existing production hosting mode')
  # Pin the only allowed generator delta before executing the reviewed candidate.
  prior=common.caddy(ctl.load(),mode);backup=ctl.snapshot(source)
  try:
   ctl.write(source,a.candidate.read_bytes(),info.st_mode&0o777,info.st_uid,info.st_gid,False)
   importlib.invalidate_caches();importlib.reload(common);ctl.caddy=common.caddy
   rendered=ctl.caddy(ctl.load(),mode)
   additions=[line for line in rendered.splitlines(keepends=True) if '@desktop' in line]
   if len(additions)!=2 or ''.join(line for line in rendered.splitlines(keepends=True) if '@desktop' not in line)!=prior:raise ValueError('Unexpected generated policy change')
   ctl.caddy_apply(ctl.load(),mode)
  except BaseException:
   ctl.write(source,raw,info.st_mode&0o777,info.st_uid,info.st_gid,False);importlib.invalidate_caches();importlib.reload(common);ctl.caddy=common.caddy;ctl.caddy_apply(ctl.load(),mode);raise
  print(json.dumps({'status':'PASS','sourceBackup':str(backup),'generatorSHA256':digest(source),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile')),'scope':'Only scoped desktop CSP added; generated and validated via existing controller'}))
if __name__=='__main__':main()
