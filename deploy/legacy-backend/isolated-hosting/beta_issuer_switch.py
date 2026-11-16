"""Forward-only issuer unit change under existing protected host lock.

Not a CLI. The protected launcher must validate artifacts, gate/floor, state
custody and real service/config/data health. Never writes account/key data.
"""
import hashlib,json,os,stat,subprocess,tempfile
from pathlib import Path
OLD='1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'
NEW='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21'
UNIT_NAMES=('codi-beta-issuer.service','codi-beta-frontend.service','codi-beta-gateway.service')
PINS={'codi-beta-issuer.service':'e6b8279c32a89f38ee4a3b2ba6c27777413c13b1b98611e78ff9b0d52dca1244','codi-beta-frontend.service':'4b909882dfd879235e10bf3cbb004bd3e61db1786cfd99e122b7abbd39be5f78','codi-beta-gateway.service':'f7fe40291ed89df101e511673b201b5606ba526333b1f55743fdec8ed069b47e'}
def sha(data):return hashlib.sha256(data).hexdigest()
def derive(old):
 if sha(old)!=PINS[UNIT_NAMES[0]]:raise ValueError('Exact beta issuer unit required')
 source=('/srv/codi-connected/releases/microduck-issuer-'+OLD+'/scripts/serve-connected.py').encode();target=('/srv/data/codi-beta-native/'+NEW+'/scripts/serve-connected.py').encode();flag=b' "--user-files"\n'
 if old.count(source)!=1 or old.count(flag)!=1:raise ValueError('Unexpected issuer command')
 return old.replace(source,target).replace(flag,b' "--user-files" "--beta-opfs-file-content"\n')
def run_systemctl(args):
 return subprocess.run(['/usr/bin/systemctl',*args],check=True,capture_output=True,text=True,timeout=30).stdout
class IssuerSwitch:
 """Unit/journal paths must be root-protected by the reviewed launcher.
 check_lock, check_floor_gate, verify_release and health must be real bound
 checks; they are callbacks so the existing hosting authority remains sole owner.
 """
 def __init__(self,*,unit_dir,journal,check_lock,check_floor_gate,verify_release,health,run=run_systemctl):
  if not all(callable(x) for x in (check_lock,check_floor_gate,verify_release,health,run)):raise ValueError('Complete protected checks required')
  self.units=Path(unit_dir);self.journal=Path(journal);self.lock=check_lock;self.gate=check_floor_gate;self.verify=verify_release;self.health=health;self.run=run
 def _read(self,path,mode=None):
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_uid!=os.geteuid() or a.st_nlink!=1 or a.st_size>65536 or (mode is not None and stat.S_IMODE(a.st_mode)!=mode):raise ValueError('Unsafe issuer unit/journal')
   data=os.read(fd,65537);b=os.fstat(fd)
   if len(data)!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise ValueError('Issuer file changed')
   return data
  finally:os.close(fd)
 def _atomic(self,path,data,mode):
  fd,name=tempfile.mkstemp(prefix='.issuer-switch-',dir=path.parent)
  try:
   with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),mode);f.write(data);f.flush();os.fsync(f.fileno())
   os.replace(name,path);d=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
  finally:
   if os.path.exists(name):os.unlink(name)
 def _status(self,name):
  raw=self.run(['show',name,'-p','ActiveState','-p','FragmentPath','-p','DropInPaths','-p','NeedDaemonReload']);return dict(line.split('=',1) for line in raw.splitlines())
 def _units(self,issuer_bytes):
  for name in UNIT_NAMES:
   raw=self._read(self.units/name,0o644)
   if raw!=(issuer_bytes if name==UNIT_NAMES[0] else self.expected[name]):raise ValueError('Beta unit changed: '+name)
 def is_old(self,old):
  self.lock();return self._read(self.units/UNIT_NAMES[0],0o644)==old
 def _snapshot(self):
  out={}
  for name in UNIT_NAMES:
   x=self._status(name)
   if x.get('ActiveState') not in ('active','inactive') or x.get('FragmentPath')!=str(self.units/name) or x.get('DropInPaths') not in ('',None) or x.get('NeedDaemonReload')!='no':raise ValueError('Unqualified beta unit state: '+name)
   out[name]=x['ActiveState']=='active'
  if not out[UNIT_NAMES[0]]:raise ValueError('Beta issuer must already be active')
  return out
 def apply(self,*,retain=True,phase=lambda _:None):
  self.lock();self.gate();self.verify();old=self._read(self.units/UNIT_NAMES[0],0o644);new=derive(old);self.expected={name:self._read(self.units/name,0o644) for name in UNIT_NAMES[1:]}
  if any(sha(self.expected[n])!=PINS[n] for n in self.expected):raise ValueError('Dependent unit pin changed')
  self._units(old);states=self._snapshot()
  if self.journal.exists() or self.journal.is_symlink():raise ValueError('Issuer switch pending')
  record={'version':1,'old':sha(old),'new':sha(new),'active':states};self._atomic(self.journal,(json.dumps(record,sort_keys=True)+'\n').encode(),0o600);phase('journaled')
  self._forward(old,new,states,phase,retain)
 def recover(self,old,*,retain=True,phase=lambda _:None):
  self.lock();self.gate();self.verify();new=derive(old);record=json.loads(self._read(self.journal,0o600));states=record.get('active')
  if record.get('version')!=1 or set(record)!={'version','old','new','active'} or record['old']!=sha(old) or record['new']!=sha(new) or not isinstance(states,dict) or set(states)!=set(UNIT_NAMES) or any(type(v) is not bool for v in states.values()) or not states[UNIT_NAMES[0]]:raise ValueError('Unpinned issuer journal')
  self.expected={n:self._read(self.units/n,0o644) for n in UNIT_NAMES[1:]}
  if any(sha(self.expected[n])!=PINS[n] for n in self.expected):raise ValueError('Dependent unit pin changed')
  current=self._read(self.units/UNIT_NAMES[0],0o644)
  if current not in (old,new):raise ValueError('Issuer unit drift; preserve gate and journal')
  self._forward(old,new,states,phase,retain)
 def verify_current(self,old):
  """Reopen a finalized v2 installation without changing or restarting it."""
  self.lock();self.gate();self.verify();new=derive(old)
  if self._read(self.units/UNIT_NAMES[0],0o644)!=new:raise ValueError('Finalized issuer unit changed')
  self.expected={n:self._read(self.units/n,0o644) for n in UNIT_NAMES[1:]}
  if any(sha(self.expected[n])!=PINS[n] for n in self.expected):raise ValueError('Dependent unit pin changed')
  self._units(new)
  for name in UNIT_NAMES:
   x=self._status(name)
   if x.get('ActiveState')!='active' or x.get('FragmentPath')!=str(self.units/name) or x.get('DropInPaths') not in ('',None) or x.get('NeedDaemonReload')!='no':raise ValueError('Finalized beta unit unavailable: '+name)
  self.health();self.lock();self.gate()
 def finalize(self,old,outer_journal,check_v2_healthy):
  if not callable(check_v2_healthy):raise ValueError('Pinned v2 health required')
  self.lock();self.verify();new=derive(old);record=json.loads(self._read(self.journal,0o600));states=record.get('active')
  if record.get('version')!=1 or set(record)!={'version','old','new','active'} or record['old']!=sha(old) or record['new']!=sha(new) or not isinstance(states,dict) or set(states)!=set(UNIT_NAMES) or any(type(v) is not bool for v in states.values()) or not states[UNIT_NAMES[0]]:raise ValueError('Unpinned issuer journal')
  self.expected={n:self._read(self.units/n,0o644) for n in UNIT_NAMES[1:]}
  if any(sha(self.expected[n])!=PINS[n] for n in self.expected):raise ValueError('Dependent unit pin changed')
  self._units(new)
  for name in UNIT_NAMES:
   x=self._status(name)
   if x.get('ActiveState')!=('active' if states[name] else 'inactive') or x.get('FragmentPath')!=str(self.units/name) or x.get('DropInPaths') not in ('',None) or x.get('NeedDaemonReload')!='no':raise ValueError('Beta unit did not recover: '+name)
  def outer_complete():
   try:Path(outer_journal).lstat()
   except FileNotFoundError:return
   raise ValueError('Outer Files transition is still pending')
  outer_complete();check_v2_healthy();self.health();self.lock();outer_complete();check_v2_healthy();self._clear()
 def _clear(self):
  self.journal.unlink();d=os.open(self.journal.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(d);os.close(d)
 def _forward(self,old,new,states,phase,retain):
  self.lock();self.gate();self.verify();current=self._read(self.units/UNIT_NAMES[0],0o644)
  if current not in (old,new):raise ValueError('Issuer unit drift')
  self._units(current)
  if current!=new:self._atomic(self.units/UNIT_NAMES[0],new,0o644)
  phase('unit-written');self.lock();self.gate();self.run(['daemon-reload']);phase('daemon-reload');self.run(['restart',UNIT_NAMES[0]]);phase('issuer-restarted')
  for name in UNIT_NAMES[1:]:
   self.lock();self.gate();self._units(new);status=self._status(name);state=status.get('ActiveState')
   if status.get('FragmentPath')!=str(self.units/name) or status.get('DropInPaths') not in ('',None) or status.get('NeedDaemonReload')!='no':raise ValueError('Dependent unit identity changed: '+name)
   if states[name] and state in ('inactive','failed'):self.run(['start',name])
   elif states[name] and state!='active':raise ValueError('Unknown dependent state: '+name)
   elif not states[name] and state!='inactive':raise ValueError('Unexpected inactive dependent state: '+name)
  self.lock();self.gate();self.verify();self._units(new)
  for name in UNIT_NAMES:
   x=self._status(name)
   if x.get('ActiveState')!=('active' if states[name] else 'inactive') or x.get('FragmentPath')!=str(self.units/name) or x.get('DropInPaths') not in ('',None) or x.get('NeedDaemonReload')!='no':raise ValueError('Beta unit did not recover: '+name)
  self.health();phase('healthy');self.lock();self.gate()
  if not retain:self._clear()
