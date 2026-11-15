#!/usr/bin/env python3
"""Apply or roll back the official ingress through the webhost controller."""
import fcntl,hashlib,importlib.util,json,os,socket,sys
from pathlib import Path
HOST=Path('/home/dflanag3/webhost-sites');COMMON=HOST/'ops/common.py';MANIFEST=HOST/'sites.toml';CADDY=Path('/etc/caddy/Caddyfile')
BEFORE_COMMON='6c3dd881d1938512b3934a46984a9192f683becd3795bbb854099f7a3a89bc24';BEFORE_MANIFEST='636a4ea3bc0492d1611848e6d4847864baf25a3e231e5bfdcd9c3a8e50d121c4';CANDIDATE='556d76519cb0bb1c906ce9ee81081058905ce286ad17b1a4c85a066f7ffaeef4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def modules():
 sys.path.insert(0,str(HOST/'ops'))
 for n in ('common','webctl'):sys.modules.pop(n,None)
 import common,webctl
 return common,webctl
def main(candidate):
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
 if sha(candidate)!=CANDIDATE:raise ValueError('Candidate generator hash mismatch')
 with (HOST/'.controller.lock').open('rb') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if sha(COMMON)!=BEFORE_COMMON or sha(MANIFEST)!=BEFORE_MANIFEST:raise ValueError('Hosting state has changed; rebuild candidate')
  common,webctl=modules();data=common.load();old_common=COMMON.read_bytes();old_manifest=MANIFEST.read_bytes();old_caddy=CADDY.read_bytes()
  if common.caddy(data,'production').encode()!=old_caddy:raise ValueError('Generated and installed Caddy differ')
  backups=[str(webctl.snapshot(p)) for p in (COMMON,MANIFEST,CADDY)];owner=webctl.owner()
  try:
   webctl.write(COMMON,candidate.read_bytes(),0o644,owner.pw_uid,owner.pw_gid);common,webctl=modules()
   next(s for s in data['sites'] if s['domain']=='ksu.codes')['codi_official']=True
   webctl.caddy_apply(data,'production');webctl.save_manifest(data)
   if common.caddy(common.load(),'production').encode()!=CADDY.read_bytes():raise ValueError('Applied Caddy does not match generator')
  except BaseException:
   webctl.write(COMMON,old_common,0o644,owner.pw_uid,owner.pw_gid);common,webctl=modules();webctl.write(MANIFEST,old_manifest,0o644,owner.pw_uid,owner.pw_gid);webctl.caddy_apply(common.load(),'production')
   if CADDY.read_bytes()!=old_caddy:raise RuntimeError('Hosting rollback mismatch')
   raise
  print(json.dumps({'status':'applied','backups':backups,'commonSHA256':sha(COMMON),'manifestSHA256':sha(MANIFEST),'caddySHA256':sha(CADDY)}))
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Pass reviewed candidate common.py')
 main(Path(sys.argv[1]))
