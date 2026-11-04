"""Exact 3ad→gate→830c route binding; no CLI or live installation.

Caller loads the three generator modules from verified source bytes and holds
one hosting lock. It must supply real custody, service, asset and signed
health checks and must fence every old supported recovery entrypoint first.
"""
import copy,hashlib,json
from pathlib import Path
from beta_transaction import Transaction,ManagedWebctlAdapter
from opfs_managed import HeldAdapter
OLD='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';NEW='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0'
GEN='e06fc8aa018ff048138fb2585ddb34ab9c6f1b061fb0022b06b14dca7df55928'
EXPECT={'0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020':('aba5377563df29c9ad618210cb51fca71ef1e9b5ebccdcb922752a25b8adf7a3','8f46e2762d8b613eb9c6bac7f8f3efc157a97e843f8981ed9a7a5333e01ac1a4'),'e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480':('8b54871643131b4bb4c0e43195f688593e0f9d8068f704e35f535218b8e35862','7fa77b5081eac3c359b5c213f54903e6f40905ec3bcc28571b8a19e06468081b')}
def sha(b):return hashlib.sha256(b).hexdigest()
def snapshots(*,snap,successor,oldgen,v2gen,newgen,manifest,old_manifest,new_manifest,table,selector):
 if selector not in EXPECT or sha(newgen.source)!=GEN or sha(new_manifest)!=NEW:raise ValueError('Unexpected asset inputs')
 parent=snap.build(old=oldgen,new=v2gen,manifest=manifest,candidate_manifest=old_manifest,route_table=table)
 family=successor.families(parent,oldgen,v2gen)[selector]
 data=copy.deepcopy(family['gateData']);data['codi_beta_maintenance']=False;data['codi_beta_opfs']=NEW;newgen.module.validate(data)
 files=json.loads(new_manifest)['files'];routes={'/'+p:r['sha256'] for p,r in files.items() if p.startswith(('assets/','storage/'))}
 if newgen.module.OPFS_NEW_PUBLIC_FILES!=routes:raise ValueError('Asset route list differs from manifest')
 candidate={'common':newgen.source,'manifest':newgen.module.dump(data).encode(),'caddy':newgen.module.caddy(data,'production').encode()}
 if (sha(candidate['manifest']),sha(candidate['caddy']))!=EXPECT[selector]:raise ValueError('Unexpected asset endpoint')
 return {'baseline':family['candidate'],'baselineData':family['candidateData'],'gate':family['gate'],'gateData':family['gateData'],'candidate':candidate,'candidateData':data}

class Router:
 def __init__(self,*,snapshots,baseline_gen,gate_gen,candidate_gen,inventory,ctl,paths,hosting_root,caddy_dir,uid,gid,caddy_gid,caddy_uid,timer,lock,check_lock,beta_ready,gate_ready,main_health,route_health,caddy_active,backup,nested_journal):
  self.x=snapshots;self.generators={'baseline':baseline_gen,'gate':gate_gen,'candidate':candidate_gen};self.Inventory=inventory;self.ctl=ctl;self.paths=paths;self.hosting=hosting_root;self.caddy=caddy_dir;self.uid=uid;self.gid=gid;self.caddy_gid=caddy_gid;self.caddy_uid=caddy_uid;self.timer=timer;self.lock=lock;self.check=check_lock;self.ready=beta_ready;self.gate_ready=gate_ready;self.main=main_health;self.health=route_health;self.active=caddy_active;self.backup=backup;self.nested=Path(nested_journal)
  if set(snapshots)!={'baseline','baselineData','gate','gateData','candidate','candidateData'} or not all(callable(f) for f in (lock,check_lock,beta_ready,gate_ready,main_health,route_health,caddy_active,backup)):raise ValueError('Incomplete exact binding')
 def name(self,raw):
  hits=[n for n in ('baseline','gate','candidate') if self.x[n]==raw]
  if len(hits)!=1:raise ValueError('Unknown asset snapshot')
  return hits[0]
 def adapter(self,old,new):
  a=self.name(old);b=self.name(new)
  if (a,b) not in (('baseline','gate'),('gate','baseline'),('gate','candidate'),('candidate','gate')):raise ValueError('Unreviewed asset transition')
  policy='opfs_to_gate' if b=='gate' else 'opfs_from_gate';ga=self.generators[a];gb=self.generators[b]
  inv=self.Inventory(self.hosting,self.caddy,ga.module,gb.module,self.x[a+'Data'],self.x[b+'Data'],owner_uid=self.uid,owner_gid=self.gid,caddy_gid=self.caddy_gid,caddy_uid=self.caddy_uid,**{policy:True})
  return ManagedWebctlAdapter(self.ctl,ga,gb,self.paths,self.timer,self.lock,self.check,self.gate_ready if b=='gate' else self.ready,lambda:self.health(b),self.main,inv.check,self.active,self.backup)
 def transaction(self,old,new):self.check();return Transaction(HeldAdapter(self.adapter(old,new),self.check),self.nested)
 def read(self):return self.adapter(self.x['gate'],self.x['baseline']).read()
 def prepare(self,asset_floor):
  self.check()
  try:self.nested.lstat()
  except FileNotFoundError:return
  from beta_transaction import _decode
  import json,os,stat
  fd=os.open(self.nested,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or stat.S_IMODE(a.st_mode)!=0o600 or a.st_nlink!=1 or a.st_size>8*1024*1024:raise ValueError('Unsafe nested asset journal')
   raw=b''
   while len(raw)<a.st_size:
    part=os.read(fd,min(65536,a.st_size-len(raw)))
    if not part:raise ValueError('Short asset journal')
    raw+=part
   z=os.fstat(fd)
   if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('Asset journal changed')
  finally:os.close(fd)
  j=json.loads(raw);old=_decode(j['old']);new=_decode(j['new']);a=self.name(old);b=self.name(new)
  if asset_floor and (a,b)==('gate','candidate') and j.get('version')==1 and 'policy' not in j:
   Transaction(HeldAdapter(self.adapter(self.x['candidate'],self.x['gate']),self.check),self.nested).recover_old_gate(self.x['gate'],self.x['candidate']);return
  if asset_floor and (a,b)==('candidate','gate') and j.get('version')==2 and j.get('policy')=='gate-only':self.transaction(old,new).recover_gate(old,new);return
  if not asset_floor and (a,b) in (('baseline','gate'),('gate','baseline')) and j.get('version')==1 and 'policy' not in j:self.transaction(old,new).recover();return
  raise ValueError('Unreviewed nested asset journal')
