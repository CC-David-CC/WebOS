#!/usr/bin/env python3
"""Guarded live renewal tick from a pinned protected bundle."""
import argparse,fcntl,hashlib,importlib.util,json,os,re,stat,sys
from pathlib import Path

FILES={'expired_root_steps.py','expired_root_recovery.py','expired_root_managed.py','live_root_renewal.py','live_root_journal.py','live_root_managed.py','run.py'}
HEX=re.compile(r'[0-9a-f]{64}\Z')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def protected(path,mode=None,limit=16777216):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('Absolute protected path required')
 for part in [path,*path.parents]:
  info=part.lstat()
  if stat.S_ISLNK(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:raise ValueError('Protected root-owned paths required')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or (mode is not None and stat.S_IMODE(info.st_mode)!=mode) or info.st_size>limit:raise ValueError('Protected bounded regular file required')
  with os.fdopen(fd,'rb') as f:fd=-1;raw=f.read(limit+1)
  if len(raw)>limit:raise ValueError('Protected input too large')
  return raw
 finally:
  if fd>=0:os.close(fd)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def controller_lock(path,owner_uid,owner_gid):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('Absolute controller lock required')
 for part in path.parents:
  info=part.lstat()
  if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0,owner_uid) or info.st_mode&0o002 or (info.st_uid==0 and info.st_mode&0o020) or (info.st_uid!=0 and info.st_mode&0o020 and info.st_gid!=owner_gid):raise ValueError('Controller lock ancestors are not trusted')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_nlink!=1 or info.st_mode&0o022:raise ValueError('Protected controller lock required')
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  return fd
 except BaseException:os.close(fd);raise
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['inspect','tick']);p.add_argument('--config',type=Path,required=True);p.add_argument('--config-sha256',required=True);p.add_argument('--release-sha256',required=True);p.add_argument('--bundle-sha256',required=True);p.add_argument('--seconds',type=int,default=86400);p.add_argument('--renewal-window',type=int,default=21600);p.add_argument('--controller-lock',type=Path,required=True);p.add_argument('--controller-owner-uid',type=int,required=True);p.add_argument('--controller-owner-gid',type=int,required=True);a=p.parse_args()
 if os.geteuid()!=0 or any(not HEX.fullmatch(v) for v in [a.config_sha256,a.release_sha256,a.bundle_sha256]) or not 30<=a.seconds<=86400 or not 1<=a.renewal_window<a.seconds or min(a.controller_owner_uid,a.controller_owner_gid)<0:raise ValueError('Root and exact bounded recovery pins are required')
 bundle=Path(__file__).absolute().parent;manifest_raw=protected(bundle/'recovery-operator.json',0o644,65536)
 if digest(manifest_raw)!=a.bundle_sha256:raise ValueError('Recovery bundle manifest pin differs')
 manifest=json.loads(manifest_raw)
 if set(manifest)!={'version','files'} or manifest['version']!='codi-live-root-operator/1' or set(manifest['files'])!=FILES or {p.name for p in bundle.iterdir()}!=FILES|{'recovery-operator.json'}:raise ValueError('Unexpected recovery bundle contents')
 for name in FILES:
  raw=protected(bundle/name,0o644);expected=manifest['files'][name]
  if expected!={'bytes':len(raw),'sha256':digest(raw)}:raise ValueError('Recovery bundle content changed')
 config_raw=protected(a.config,0o600,65536)
 if digest(config_raw)!=a.config_sha256:raise ValueError('Managed config pin changed')
 config=json.loads(config_raw);release=Path(config['release']);raw=protected(release/'connected-release.json',0o644,1048576)
 if digest(raw)!=a.release_sha256 or config['manifestSHA256']!=a.release_sha256:raise ValueError('Native release pin changed')
 release_manifest=json.loads(raw);files=release_manifest['files'];found=set()
 for path in release.rglob('*'):
  if path.is_symlink():raise ValueError('Linked native release input')
  if path.is_dir():continue
  name=str(path.relative_to(release));found.add(name)
  if name=='connected-release.json':continue
  content=protected(path,0o644,268435456)
  if files.get(name)!={'bytes':len(content),'sha256':digest(content)}:raise ValueError('Native release content changed')
 if found!=set(files)|{'connected-release.json'}:raise ValueError('Native release has missing or extra files')
 operator=release/'scripts/manage-services.py'
 sys.path.insert(0,str(release));op=load('expired_recovery_installed_operator',operator)
 from origin_service import maintenance
 load('origin_service.expired_root_steps',bundle/'expired_root_steps.py');load('origin_service.expired_root_recovery',bundle/'expired_root_recovery.py');load('origin_service.expired_root_managed',bundle/'expired_root_managed.py');load('origin_service.live_root_renewal',bundle/'live_root_renewal.py');journal_module=load('origin_service.live_root_journal',bundle/'live_root_journal.py');managed=load('origin_service.live_root_managed',bundle/'live_root_managed.py')
 fd=controller_lock(a.controller_lock,a.controller_owner_uid,a.controller_owner_gid)
 try:
  backend=managed.ManagedLiveRenewal(op,maintenance,a.config,config_sha256=a.config_sha256,release_sha256=a.release_sha256,seconds=a.seconds,renewal_window=a.renewal_window)
  journal_dir=a.config.parent/'live-root-renewal';op.path(journal_dir);journal=journal_module.LiveRenewalJournal(journal_dir/'journal.json')
  if a.action=='inspect':
   with backend.locked():
    pending=journal.path.exists() or journal.path.is_symlink();record=journal.load() if pending else backend.initial();result={'status':'inspect','nextStep':backend.decide(record),'baseRevision':record['checkpoint']['baseRevision'],'publisherFloor':record['publisherRevision'],'pending':pending,'liveChanged':False}
  else:result=journal_module.execute(backend,journal,resume=journal.path.exists() or journal.path.is_symlink())
  print(json.dumps(result,indent=2))
 finally:os.close(fd)
if __name__=='__main__':main()
