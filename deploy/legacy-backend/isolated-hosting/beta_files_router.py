"""Concrete bridge to the existing managed host controller; not a CLI.

A root-protected launcher must load pinned code and supply real service checks,
artifact/custody verification, a signed file-health check and exact snapshots.
"""
import json,os,stat
from pathlib import Path
from beta_transaction import Transaction,ManagedWebctlAdapter,_decode
from opfs_managed import HeldAdapter
from render_inventory import RenderInventory
class FilesRouter:
 def __init__(self,*,snapshots,old_generator,new_generator,ctl,paths,hosting_root,caddy_dir,uid,gid,caddy_gid,caddy_uid,timer,lock,check_lock,beta_ready,gate_ready,main_health,route_health,caddy_active,backup,nested_journal):
  self.x=snapshots;self.oldgen=old_generator;self.newgen=new_generator;self.ctl=ctl;self.paths=paths;self.hosting=hosting_root;self.caddy=caddy_dir;self.uid=uid;self.gid=gid;self.caddy_gid=caddy_gid;self.caddy_uid=caddy_uid;self.timer=timer;self.lock=lock;self.check=check_lock;self.ready=beta_ready;self.gate_ready=gate_ready;self.main=main_health;self.health=route_health;self.active=caddy_active;self.backup=backup;self.nested=Path(nested_journal)
  checks=(lock,check_lock,beta_ready,gate_ready,main_health,route_health,caddy_active,backup)
  if not all(callable(v) for v in checks):raise ValueError('Complete real host checks required')
  self.pairs={('initial','normalized'):'normalize_maintenance',('normalized','gate'):'maintenance_only',('gate','normalized'):'maintenance_only',('gate','candidate'):'opfs_from_gate',('candidate','gate'):'opfs_to_gate'}
 def _name(self,raw):
  hits=[name for name in ('initial','normalized','gate','candidate') if self.x[name]==raw]
  if len(hits)!=1:raise ValueError('Unknown pinned hosting snapshot')
  return hits[0]
 def adapter(self,old,new):
  a=self._name(old);b=self._name(new);policy=self.pairs.get((a,b))
  if policy is None:raise ValueError('Unreviewed hosting transition')
  ao=self.newgen if a=='candidate' else self.oldgen;bo=self.newgen if b=='candidate' else self.oldgen
  inv=RenderInventory(self.hosting,self.caddy,ao.module,bo.module,self.x[a+'Data'],self.x[b+'Data'],owner_uid=self.uid,owner_gid=self.gid,caddy_gid=self.caddy_gid,caddy_uid=self.caddy_uid,**{policy:True})
  ready=self.gate_ready if b=='gate' else self.ready
  return ManagedWebctlAdapter(self.ctl,ao,bo,self.paths,self.timer,self.lock,self.check,ready,lambda:self.health(b),self.main,inv.check,self.active,self.backup)
 def transaction(self,old,new):
  self.check();return Transaction(HeldAdapter(self.adapter(old,new),self.check),self.nested)
 def read(self):
  # All adapters use the same pinned host paths and read implementation.
  return self.adapter(self.x['initial'],self.x['normalized']).read()
 def _journal(self):
  fd=os.open(self.nested,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or a.st_size>8*1024*1024:raise ValueError('Unsafe managed journal')
   data=b''
   while len(data)<=8*1024*1024:
    part=os.read(fd,min(65536,8*1024*1024+1-len(data)))
    if not part:break
    data+=part
   z=os.fstat(fd)
   if len(data)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('Managed journal changed')
  finally:os.close(fd)
  j=json.loads(data);return j,_decode(j.get('old',{})),_decode(j.get('new',{}))
 def prepare(self,floor):
  self.check()
  try:self.nested.lstat()
  except FileNotFoundError:return
  j,old,new=self._journal();a=self._name(old);b=self._name(new)
  if floor:
   if (a,b)==('gate','candidate') and j.get('version')==1 and 'policy' not in j:
    # Recovery is targeting the old gate; use the reverse inventory/health.
    adapter=self.adapter(self.x['candidate'],self.x['gate'])
    Transaction(HeldAdapter(adapter,self.check),self.nested).recover_old_gate(self.x['gate'],self.x['candidate']);return
   if (a,b)==('candidate','gate') and j.get('version')==2 and j.get('policy')=='gate-only':
    self.transaction(old,new).recover_gate(old,new);return
   raise ValueError('Unsafe managed journal after v2 floor')
  if (a,b) not in (('normalized','gate'),('gate','normalized')) or j.get('version')!=1 or 'policy' in j:raise ValueError('Unreviewed pre-floor managed journal')
  self.transaction(old,new).recover()
