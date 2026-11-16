"""Beta hosting transaction core. Requires a separately reviewed host adapter.

No CLI is provided: importing this code never changes host state. The adapter
must implement the real managed webctl operations, safe lock protocol and beta
service preflight. Checks before rename cannot exclude uncooperative local writers.
"""
import base64,json,os,stat,tempfile
from pathlib import Path

def _encode(values):return {key:base64.b64encode(value).decode('ascii') for key,value in values.items()}
def _decode(values):return {key:base64.b64decode(value,validate=True) for key,value in values.items()}
def _atomic(path,data):
 path=Path(path);fd,name=tempfile.mkstemp(prefix='.beta-route-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),0o600);out.write(data);out.flush();os.fsync(out.fileno())
  os.replace(name,path);fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if os.path.exists(name):os.unlink(name)
def _clear(path):
 path.unlink();fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)

class Transaction:
 """Adapter contract: held(), check_lock(), read(), beta_ready(), timer_*,
 backup(old), replace_source(key,bytes), apply_caddy(manifest,common), check_health(),
 check_main_health().
 Adapter must make the journal's parent root-protected and precheck all pins.
 """
 KEYS=('common','manifest','caddy')
 def __init__(self,adapter,journal):self.io=adapter;self.journal=Path(journal)
 def _write_journal(self,value):_atomic(self.journal,json.dumps(value,sort_keys=True).encode())
 def _expect(self,expected):
  self.io.check_lock()
  if self.io.read()!=expected:raise ValueError('Unexpected hosting drift; retain journal')
 def apply(self,old,new,*,phase=lambda _:None):
  return self._apply(old,new,gate_only=False,phase=phase)
 def apply_gate(self,old,gate,*,phase=lambda _:None):
  if old==gate:raise ValueError('Distinct gate endpoints required')
  return self._apply(old,gate,gate_only=True,phase=phase)
 def _apply(self,old,new,*,gate_only,phase):
  if set(old)!=set(self.KEYS) or set(new)!=set(self.KEYS):raise ValueError('Exact hosting snapshot required')
  with self.io.held():
   if self.journal.exists() or self.journal.is_symlink():raise ValueError('Pending beta hosting journal')
   self._expect(old);self.io.beta_ready();timer=self.io.timer_snapshot()
   if set(timer)!={'active','enabled'} or any(type(v) is not bool for v in timer.values()):raise ValueError('Unknown timer state')
   backup=self.io.backup(old)
   if not isinstance(backup,str) or not backup:raise ValueError('Durable hosting backup required')
   self._expect(old)
   j={'version':2 if gate_only else 1,'phase':'prepared','old':_encode(old),'new':_encode(new),'timer':timer,'caddy_started':False,'backup':backup}
   if gate_only:j['policy']='gate-only'
   self._write_journal(j);phase('journaled')
   self.io.timer_stop_if_active(timer);self.io.assert_renewal_quiescent();phase('timer-stopped');self._expect(old)
   expected=old.copy()
   for key in ('common','manifest'):
    self._expect(expected);self.io.replace_source(key,new[key]);expected[key]=new[key];phase(key+'-written')
   self._expect(expected);self.io.beta_ready();j['caddy_started']=True;self._write_journal(j);phase('caddy-starting')
   self.io.apply_caddy(new['manifest'],new['common'],recovery=False);expected['caddy']=new['caddy'];phase('caddy-applied')
   self._expect(expected);self.io.check_main_health();self.io.check_health();self.io.beta_ready();self._expect(new)
   j['phase']='committed';self._write_journal(j);phase('committed')
   self.io.timer_restore(timer);phase('timer-restored');_clear(self.journal)
 def recover(self):
  return self._recover(gate_only=False,force_old_gate=False,expected_old=None,expected_gate=None)
 def recover_gate(self,expected_old,expected_gate):
  if set(expected_old)!=set(self.KEYS) or set(expected_gate)!=set(self.KEYS) or expected_old==expected_gate:raise ValueError('Exact distinct gate endpoints required')
  return self._recover(gate_only=True,force_old_gate=False,expected_old=expected_old,expected_gate=expected_gate)
 def recover_old_gate(self,expected_gate,expected_candidate):
  if set(expected_gate)!=set(self.KEYS) or set(expected_candidate)!=set(self.KEYS) or expected_gate==expected_candidate:raise ValueError('Exact distinct gate and candidate endpoints required')
  return self._recover(gate_only=False,force_old_gate=True,expected_old=expected_gate,expected_gate=expected_candidate)
 def _recover(self,*,gate_only,force_old_gate,expected_old,expected_gate):
  with self.io.held():
   j=json.loads(self.journal.read_bytes());old=_decode(j['old']);new=_decode(j['new']);timer=j['timer']
   valid_policy=(type(j.get('version')) is int and j.get('version')==2 and j.get('policy')=='gate-only' and old==expected_old and new==expected_gate) if gate_only else (j.get('version')==1 and 'policy' not in j and (not force_old_gate or (old==expected_old and new==expected_gate)))
   if not valid_policy or j.get('phase') not in ('prepared','committed') or type(j.get('caddy_started')) is not bool or set(old)!=set(self.KEYS) or set(new)!=set(self.KEYS):raise ValueError('Invalid beta journal or recovery policy')
   self.io.check_lock();current=self.io.read()
   if any(current[k] not in (old[k],new[k]) for k in self.KEYS):raise ValueError('Unexpected hosting drift; retain journal')
   self.io.timer_assert_recoverable(timer)
   # A crash may have occurred before timer stop or after timer restoration.
   # Re-establish the maintenance window before any recovery write/reload.
   observed_timer=self.io.timer_snapshot()
   if observed_timer not in (timer,{**timer,'active':False}):raise ValueError('Timer state changed; retain journal')
   self.io.timer_stop_if_active(observed_timer);self.io.assert_renewal_quiescent()
   target=old if force_old_gate else new if gate_only or j['phase']=='committed' else old
   if gate_only or force_old_gate or j['phase']=='committed':self.io.beta_ready()
   expected=current.copy()
   for key in ('common','manifest'):
    self._expect(expected)
    if expected[key]!=target[key]:self.io.replace_source(key,target[key]);expected[key]=target[key]
   self._expect(expected)
   # webctl may have changed generated auxiliary files before updating the
   # active Caddyfile; reapply even when its active bytes already match.
   if j.get('caddy_started') is True or expected['caddy']!=target['caddy']:self.io.apply_caddy(target['manifest'],target['common'],recovery=True);expected['caddy']=target['caddy']
   self._expect(expected);self.io.check_main_health();self._expect(expected)
   if gate_only or force_old_gate or j['phase']=='committed':self.io.check_health();self.io.beta_ready();self._expect(expected)
   self.io.timer_restore(timer);_clear(self.journal)

class SystemdTimer:
 """Timer state adapter; callers must separately preserve failed service state."""
 TIMER='codi-ksu-live-root-renew.timer';SERVICE='codi-ksu-live-root-renew.service'
 def __init__(self,run):self.run=run
 def snapshot(self):
  fields={}
  for line in self.run(['/usr/bin/systemctl','show',self.TIMER,'-p','ActiveState','-p','UnitFileState']).splitlines():
   k,v=line.split('=',1);fields[k]=v
  if fields.get('ActiveState') not in ('active','inactive') or fields.get('UnitFileState') not in ('enabled','disabled'):raise ValueError('Unexpected timer state')
  return {'active':fields['ActiveState']=='active','enabled':fields['UnitFileState']=='enabled'}
 def stop_if_active(self,prior):
  if self.snapshot()!=prior:raise ValueError('Timer changed before stop')
  if prior['active']:self.run(['/usr/bin/systemctl','stop',self.TIMER])
  if self.snapshot()!={**prior,'active':False}:raise ValueError('Timer did not stop')
 def assert_quiescent(self):
  values={}
  for line in self.run(['/usr/bin/systemctl','show',self.SERVICE,'-p','ActiveState','-p','MainPID','-p','ControlPID']).splitlines():
   k,v=line.split('=',1);values[k]=v
  if values.get('ActiveState') not in ('failed','inactive') or values.get('MainPID')!='0' or values.get('ControlPID')!='0':raise ValueError('Renewal service is not quiescent')
 def assert_recoverable(self,prior):
  if self.snapshot() not in (prior,{**prior,'active':False}):raise ValueError('Timer state changed; retain journal')
 def restore(self,prior):
  self.assert_recoverable(prior)
  if prior['active'] and not self.snapshot()['active']:self.run(['/usr/bin/systemctl','start',self.TIMER])
  if self.snapshot()!=prior:raise ValueError('Timer state not restored')

class ManagedWebctlAdapter:
 """Adapter for pinned webctl/common modules; caller supplies all trust checks.

`lock` must return a context manager holding the existing reviewed host lock;
`check_lock` verifies the locked inode/path; `ready` and `health` must enforce
independent beta/main service checks. The actual modules, paths and journal must
be verified and bound by a separate protected launcher before constructing this.
 """
 def __init__(self,ctl,old_generator,new_generator,paths,timer,lock,check_lock,ready,health,main_health,render_targets_check,caddy_active_check,backup):
  self.ctl=ctl;self.old_generator=old_generator;self.new_generator=new_generator;self.paths={k:Path(v) for k,v in paths.items()};self.timer=timer;self.lock=lock;self._check_lock=check_lock;self._ready=ready;self._health=health;self._main_health=main_health;self._render_targets_check=render_targets_check;self._caddy_active_check=caddy_active_check;self._backup=backup
  if set(self.paths)!=set(Transaction.KEYS) or not all(callable(x) for x in (lock,check_lock,ready,health,main_health,render_targets_check,caddy_active_check,backup)):raise ValueError('Complete verified host adapter required')
 def held(self):return self.lock()
 def check_lock(self):return self._check_lock()
 def read(self):
  values={}
  for key,path in self.paths.items():
   fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
   try:
    info=os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>1048576:raise ValueError('Unsafe hosting source')
    data=b''
    while len(data)<=1048576:
     chunk=os.read(fd,min(65536,1048577-len(data)))
     if not chunk:break
     data+=chunk
    after=os.fstat(fd)
    if len(data)!=info.st_size or (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('Hosting source changed while reading')
    values[key]=data
   finally:os.close(fd)
  return values
 def beta_ready(self):return self._ready()
 def check_health(self):return self._health()
 def check_main_health(self):return self._main_health()
 def backup(self,old):return self._backup(old)
 def timer_snapshot(self):return self.timer.snapshot()
 def timer_stop_if_active(self,prior):return self.timer.stop_if_active(prior)
 def assert_renewal_quiescent(self):return self.timer.assert_quiescent()
 def timer_assert_recoverable(self,prior):return self.timer.assert_recoverable(prior)
 def timer_restore(self,prior):return self.timer.restore(prior)
 def replace_source(self,key,value):
  if key not in ('common','manifest'):raise ValueError('Only hosting source may be replaced')
  p=self.paths[key];info=p.lstat()
  if p.is_symlink() or not p.is_file():raise ValueError('Unsafe hosting source')
  fd,name=tempfile.mkstemp(prefix='.beta-source-',dir=p.parent)
  try:
   with os.fdopen(fd,'wb') as out:
    os.fchown(out.fileno(),info.st_uid,info.st_gid);os.fchmod(out.fileno(),info.st_mode&0o777);out.write(value);out.flush();os.fsync(out.fileno())
   os.replace(name,p);fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
   try:os.fsync(fd)
   finally:os.close(fd)
  finally:
   if os.path.exists(name):os.unlink(name)
 def apply_caddy(self,manifest,common,*,recovery=False):
  import tomllib
  data=tomllib.loads(manifest.decode('utf-8'))
  if common==self.old_generator.source:generator=self.old_generator
  elif common==self.new_generator.source:generator=self.new_generator
  else:raise ValueError('Unreviewed generator bytes')
  generator.module.validate(data)
  # `caddy_apply` renders auxiliary files for every site. The protected
  # launcher must verify their exact allowed inventory and current hashes.
  self._render_targets_check(data,recovery=recovery);self._caddy_active_check()
  prior=(self.ctl.caddy,self.ctl.dump,self.ctl.validate,self.ctl.run)
  def restricted_run(args,**kwargs):
   cmd=[str(value) for value in args]
   if cmd and Path(cmd[0]).name=='systemctl' and any(value in ('start','enable','unmask','restart') for value in cmd[1:]):raise ValueError('Caddy start/enable/unmask is not allowed')
   return prior[3](args,**kwargs)
  try:
   self.ctl.caddy,self.ctl.dump,self.ctl.validate=generator.module.caddy,generator.module.dump,generator.module.validate
   self.ctl.run=restricted_run
   self.ctl.caddy_apply(data,'production')
   self._render_targets_check(data,recovery=recovery,after=True)
  finally:self.ctl.caddy,self.ctl.dump,self.ctl.validate,self.ctl.run=prior
