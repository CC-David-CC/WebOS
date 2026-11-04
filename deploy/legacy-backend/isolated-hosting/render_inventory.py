"""Verify all webctl.caddy_apply render targets before a beta transition.

The caller must derive modules/data from pinned reviewed bytes and hold the
hosting coordination lock. This bounds observed drift; it cannot prevent an
uncooperative writer in the documented check-to-rename window.
"""
import os,re,stat
from pathlib import Path

def read_regular(path):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('Absolute render target required')
 parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:
  for name in path.parts[1:-1]:
   child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);os.close(parent);parent=child
  fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
  try:
   info=os.fstat(fd)
   if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>4*1024*1024:raise ValueError('Unsafe render target')
   chunks=[];size=0
   while size<=4*1024*1024:
    part=os.read(fd,min(65536,4*1024*1024+1-size))
    if not part:break
    chunks.append(part);size+=len(part)
   after=os.fstat(fd)
   if size!=info.st_size or (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('Render target changed while reading')
   return b''.join(chunks),(info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode))
  finally:os.close(fd)
 finally:os.close(parent)

class RenderInventory:
 def __init__(self,root,caddy_dir,oldgen,newgen,olddata,newdata,*,owner_uid,owner_gid,caddy_gid,caddy_uid=0,baseline_only=False,maintenance_only=False,normalize_maintenance=False,opfs_only=False,opfs_from_gate=False,opfs_to_gate=False):
  root=Path(root);caddy_dir=Path(caddy_dir)
  if sum(bool(x) for x in (baseline_only,maintenance_only,normalize_maintenance,opfs_only,opfs_from_gate,opfs_to_gate))>1:raise ValueError('Conflicting inventory policies')
  if opfs_to_gate:
   omitted={'codi_beta_opfs','codi_beta_maintenance'}
   if (olddata.get('codi_beta_opfs')!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or olddata.get('codi_beta_maintenance') is not False or newdata.get('codi_beta_maintenance') is not True or 'codi_beta_opfs' in newdata or {k:v for k,v in olddata.items() if k not in omitted}!={k:v for k,v in newdata.items() if k not in omitted}):raise ValueError('Only the reviewed beta OPFS to gate transition is allowed')
  elif opfs_from_gate:
   omitted={'codi_beta_opfs','codi_beta_maintenance'}
   if ('codi_beta_opfs' in olddata or olddata.get('codi_beta_maintenance') is not True or newdata.get('codi_beta_maintenance') is not False or newdata.get('codi_beta_opfs')!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or {k:v for k,v in olddata.items() if k not in omitted}!={k:v for k,v in newdata.items() if k not in omitted}):raise ValueError('Only the reviewed gated beta OPFS activation is allowed')
  elif opfs_only:
   if ('codi_beta_opfs' in olddata or newdata.get('codi_beta_opfs')!='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc' or {k:v for k,v in newdata.items() if k!='codi_beta_opfs'}!=olddata or olddata.get('codi_beta_maintenance') is not False or olddata.get('codi_beta_simplified')!=newdata.get('codi_beta_simplified')):raise ValueError('Only the exact beta OPFS candidate may be added')
  elif normalize_maintenance:
   if ('codi_beta_simplified' not in olddata or olddata.get('codi_beta_simplified')!=newdata.get('codi_beta_simplified') or 'codi_beta_maintenance' in olddata or newdata.get('codi_beta_maintenance') is not False or {k:v for k,v in newdata.items() if k!='codi_beta_maintenance'}!=olddata):raise ValueError('Only absent-to-false beta maintenance normalization is allowed')
  elif maintenance_only:
   if ('codi_beta_simplified' not in olddata or olddata.get('codi_beta_simplified')!=newdata.get('codi_beta_simplified') or type(olddata.get('codi_beta_maintenance')) is not bool or type(newdata.get('codi_beta_maintenance')) is not bool or olddata['codi_beta_maintenance']==newdata['codi_beta_maintenance'] or {k:v for k,v in olddata.items() if k!='codi_beta_maintenance'}!={k:v for k,v in newdata.items() if k!='codi_beta_maintenance'}):raise ValueError('Only an explicit boolean beta maintenance transition is allowed')
  elif baseline_only:
   if olddata!=newdata or 'codi_beta_simplified' not in olddata:raise ValueError('Active beta baseline required')
  elif 'codi_beta_simplified' in olddata or {k:v for k,v in newdata.items() if k!='codi_beta_simplified'}!=olddata:raise ValueError('Beta must be the only manifest change')
  oldgen.validate(olddata);newgen.validate(newdata);self.olddata=olddata;self.newdata=newdata;self.targets={}
  def without_beta(value):
   matches=list(re.finditer(r'(?m)^(?:https?://)?beta\.ksu\.codes(?::[0-9]+)? \{',value))
   if len(matches)!=1:raise ValueError('Exactly one beta generated site required')
   start=matches[0].start();end=value.find('\n}\n',start)
   if end<0:raise ValueError('Beta generated site is incomplete')
   return value[:start]+value[end+3:]
  def add(path,old,new,metadata):
   if (opfs_only or opfs_from_gate or opfs_to_gate) and ((path.name.startswith('Caddyfile.') and without_beta(old)!=without_beta(new)) or (not path.name.startswith('Caddyfile.') and old!=new)):raise ValueError('OPFS transition changed non-beta output')
   if path in self.targets:raise ValueError('Duplicate render target')
   if normalize_maintenance and old!=new:raise ValueError('Normalization changed generated output')
   self.targets[path]=(old.encode(),new.encode(),metadata)
  for mode in ('prepare','production'):
   old=oldgen.caddy(olddata,mode);new=newgen.caddy(newdata,mode)
   add(root/'deploy/caddy'/('Caddyfile.'+mode),old,new,(owner_uid,owner_gid,0o644))
   add(caddy_dir/('Caddyfile.'+mode),old,new,(caddy_uid,caddy_gid,0o640))
  for oldsite,newsite in zip(olddata['sites'],newdata['sites'],strict=True):
   if oldsite!=newsite:raise ValueError('Existing site changed')
   add(root/'deploy/systemd'/oldsite['service'],oldgen.unit(oldsite),newgen.unit(newsite),(owner_uid,owner_gid,0o644))
 def check(self,data,*,recovery=False,after=False):
  if data not in (self.olddata,self.newdata):raise ValueError('Unreviewed render data')
  # Before apply require baseline (or old/new during recovery). After apply
  # require every target to match the chosen generator's exact output.
  for path,(old,new,metadata) in self.targets.items():
   value,observed=read_regular(path)
   allowed=((new,) if data==self.newdata else (old,)) if after else ((old,new) if recovery else (old,))
   if observed!=metadata or value not in allowed:raise ValueError('Unexpected generated render target: '+str(path))
