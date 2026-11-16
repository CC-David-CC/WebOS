"""Isolated transaction research; NOT an installed hosting controller.

The supplied adapter must enforce external writer quiescence. The read/check/
replace sequence is not atomic CAS against an uncooperative writer. No systemd,
real hosting config, public routes, or account data may be passed to this model.
"""
import base64,contextlib,fcntl,json,os,tempfile
from pathlib import Path

def atomic(path,data):
 path=Path(path);fd,name=tempfile.mkstemp(prefix='.beta-tx-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(data);out.flush();os.fsync(out.fileno())
  os.replace(name,path);fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if os.path.exists(name):os.unlink(name)

def encode(values):return {k:base64.b64encode(v).decode('ascii') for k,v in values.items()}
def decode(values):return {k:base64.b64decode(v,validate=True) for k,v in values.items()}
def remove_journal(path):
 path.unlink();fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)

class Window:
 def __init__(self,root):
  self.root=Path(root);self.paths={k:self.root/k for k in ('common','manifest','caddy')};self.journal=self.root/'journal';self.lock=self.root/'controller.lock';self.timer=self.root/'timer'
 def read(self):return {k:p.read_bytes() for k,p in self.paths.items()}
 def timer_state(self):return json.loads(self.timer.read_bytes())
 def write_journal(self,j):atomic(self.journal,json.dumps(j,sort_keys=True).encode())
 @contextlib.contextmanager
 def held(self):
  fd=os.open(self.lock,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  try:
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);a=os.fstat(fd);b=self.lock.stat(follow_symlinks=False)
   if (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('lock path changed')
   yield fd
  finally:os.close(fd)
 def check_lock(self,fd):
  a=os.fstat(fd);b=self.lock.stat(follow_symlinks=False)
  if (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('lock path changed')
 def update(self,expected,target,fd,phase):
  for key in ('common','manifest','caddy'):
   self.check_lock(fd)
   if self.read()!=expected:raise ValueError('unexpected hosting drift')
   # The phase hook exposes the real check-to-replace race for a negative test.
   phase('before-'+key)
   atomic(self.paths[key],target[key]);expected={**expected,key:target[key]};phase('after-'+key)
  return expected
 def run(self,expected,target,*,phase=lambda _:None):
  with self.held() as fd:
   if self.journal.exists():raise ValueError('pending journal')
   self.check_lock(fd)
   if self.read()!=expected:raise ValueError('unexpected baseline')
   prior=self.timer_state();assert set(prior)=={'active','enabled'} and all(type(x) is bool for x in prior.values())
   j={'version':1,'state':'prepared','old':encode(expected),'new':encode(target),'timer':prior};self.write_journal(j);phase('journaled')
   if prior['active']:atomic(self.timer,json.dumps({**prior,'active':False}).encode())
   phase('timer-stopped');self.update(expected,target,fd,phase)
   self.check_lock(fd)
   if self.read()!=target:raise ValueError('unexpected hosting drift')
   j['state']='committed';self.write_journal(j);phase('committed')
   atomic(self.timer,json.dumps(prior).encode());phase('timer-restored');remove_journal(self.journal)
 def recover(self):
  with self.held() as fd:
   j=json.loads(self.journal.read_bytes());old=decode(j['old']);new=decode(j['new']);prior=j['timer'];current=self.read();timer=self.timer_state()
   if j.get('version')!=1 or j.get('state') not in ('prepared','committed') or any(current[k] not in (old[k],new[k]) for k in old) or timer not in (prior,{**prior,'active':False}):raise ValueError('unexpected recovery drift')
   target=new if j['state']=='committed' else old;self.update(current,target,fd,lambda _:None);atomic(self.timer,json.dumps(prior).encode());remove_journal(self.journal)
