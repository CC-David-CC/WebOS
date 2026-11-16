"""Beta gateway switch adapter, source only; no CLI or automatic installation.

Requires an independently reviewed root-protected launcher, exact source pins,
exclusive cooperation from beta writers and a signed data-health callback.
No method points at the main site's service, database or user files.
"""
import base64,contextlib,ctypes,fcntl,hashlib,http.client,json,os,pwd,shutil,stat,subprocess,tempfile,threading,time
from pathlib import Path
UNIT=Path('/etc/systemd/system/codi-beta-gateway.service')
ROOT=Path('/var/lib/codi-gateway/beta-operator')
JOURNAL=ROOT/'worker-switch.json'
LOCK=Path('/run/lock/codi-beta-worker-switch.lock')
RELEASES=Path('/srv/codi-gateway/releases')
_fork_guard=threading.RLock()
_lock_fds=set()
def _prepare_fork():_fork_guard.acquire()
def _after_parent():_fork_guard.release()
def _after_child():
 try:
  for fd in _lock_fds:
   try:os.close(fd)
   except OSError:pass
  _lock_fds.clear()
 finally:_fork_guard.release()
os.register_at_fork(before=_prepare_fork,after_in_parent=_after_parent,after_in_child=_after_child)
class Adapter:
 def __init__(self,switch,signed_health):
  if not callable(signed_health):raise ValueError('signed data-health callback required')
  self.switch=switch;self.signed_health=signed_health;self.fd=None;self.owner_pid=None
 def _root_dir(self,path,mode=None):
  for parent in path.parents:
   item=parent.lstat()
   if not stat.S_ISDIR(item.st_mode) or item.st_uid!=0 or item.st_mode&0o022:raise ValueError('unprotected directory ancestor')
  st=path.lstat()
  if not stat.S_ISDIR(st.st_mode) or st.st_uid!=0 or st.st_mode&0o022 or (mode is not None and stat.S_IMODE(st.st_mode)!=mode):raise ValueError('unprotected directory')
 def _read(self,path,limit):
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
  try:
   before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode) or before.st_uid!=0 or before.st_nlink!=1 or before.st_mode&0o022 or before.st_size>limit:raise ValueError('unsafe protected file')
   raw=b''
   while len(raw)<=limit:
    chunk=os.read(fd,min(65536,limit+1-len(raw)))
    if not chunk:break
    raw+=chunk
   after=os.fstat(fd)
   if len(raw)!=before.st_size or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('protected file changed')
   return raw
  finally:os.close(fd)
 def _atomic(self,path,data,mode):
  self._root_dir(path.parent)
  fd,name=tempfile.mkstemp(prefix='.beta-switch-',dir=path.parent)
  try:
   with os.fdopen(fd,'wb') as out:os.fchmod(out.fileno(),mode);out.write(data);out.flush();os.fsync(out.fileno())
   os.replace(name,path);d=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
   try:os.fsync(d)
   finally:os.close(d)
  finally:
   if os.path.exists(name):os.unlink(name)
 @contextlib.contextmanager
 def locked(self):
  lockdir=LOCK.parent;st=lockdir.lstat()
  if not stat.S_ISDIR(st.st_mode) or st.st_uid!=0 or stat.S_IMODE(st.st_mode)!=0o1777:raise ValueError('unsafe lock directory')
  self._root_dir(ROOT,0o700)
  with _fork_guard:
   fd=os.open(LOCK,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
   try:
    info=os.fstat(fd);entry=LOCK.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_nlink!=1 or stat.S_IMODE(info.st_mode)!=0o600 or (info.st_dev,info.st_ino)!=(entry.st_dev,entry.st_ino):raise ValueError('unsafe beta lock')
    fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);_lock_fds.add(fd)
   except BaseException:os.close(fd);raise
  owner=os.getpid();self.fd=fd;self.owner_pid=owner
  try:yield
  finally:
   self.fd=None;self.owner_pid=None
   if os.getpid()==owner:
    with _fork_guard:_lock_fds.discard(fd);os.close(fd)
 def _check_lock(self):
  if self.fd is None or self.owner_pid!=os.getpid():raise ValueError('beta lock not held by this process')
  a=os.fstat(self.fd);b=LOCK.lstat()
  if (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino) or a.st_nlink!=1:raise ValueError('beta lock replaced')
 def pending(self):self._check_lock();return JOURNAL.exists() or JOURNAL.is_symlink()
 def read_unit(self):self._check_lock();return self._read(UNIT,65536)
 def write_unit(self,raw):self._check_lock();self._read(UNIT,65536);self._atomic(UNIT,raw,0o644)
 def publish(self,source,copy_verified):
  """Seal a candidate in the beta worker release directory without replacement."""
  self._check_lock();self._root_dir(RELEASES)
  stats=os.statvfs(RELEASES)
  if stats.f_bavail*stats.f_frsize<5*1024**3+2*1024**2:raise ValueError('insufficient staging headroom')
  target=RELEASES/self.switch.CANDIDATE
  if target.exists() or target.is_symlink():
   self.switch.verify_release(target,require_root=True);return
  temporary=Path(tempfile.mkdtemp(prefix='.beta-worker-',dir=RELEASES));published=False
  try:
   copy_verified(source,temporary)
   os.chmod(temporary,0o755);self.switch.verify_release(temporary,require_root=True)
   self._check_lock()
   libc=ctypes.CDLL(None,use_errno=True);rename=libc.renameat2
   rename.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint];rename.restype=ctypes.c_int
   if rename(-100,os.fsencode(temporary),-100,os.fsencode(target),1)!=0:
    error=ctypes.get_errno();raise OSError(error,os.strerror(error))
   published=True
   fd=os.open(RELEASES,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
   try:os.fsync(fd)
   finally:os.close(fd)
  finally:
   if not published:shutil.rmtree(temporary)
 def verify_release(self):
  self._check_lock();self._root_dir(RELEASES);self.switch.verify_release(RELEASES/self.switch.CANDIDATE,require_root=True)
 def _journal(self,old,new,committed):
  return json.dumps({'version':1,'old':base64.b64encode(old).decode(),'new':base64.b64encode(new).decode(),'committed':committed},sort_keys=True).encode()
 def prepare(self,old,new):
  self._check_lock()
  if self.pending():raise ValueError('pending switch')
  self._atomic(JOURNAL,self._journal(old,new,False),0o600)
 def read_journal(self):
  self._check_lock();st=JOURNAL.lstat()
  if stat.S_IMODE(st.st_mode)!=0o600:raise ValueError('journal mode changed')
  value=json.loads(self._read(JOURNAL,262144))
  if set(value)!={'version','old','new','committed'} or value['version']!=1 or type(value['committed']) is not bool:raise ValueError('invalid journal')
  return base64.b64decode(value['old'],validate=True),base64.b64decode(value['new'],validate=True),value['committed']
 def commit(self):
  old,new,committed=self.read_journal()
  if committed:raise ValueError('already committed')
  self._atomic(JOURNAL,self._journal(old,new,True),0o600)
 def clear(self):
  self._check_lock();self._read(JOURNAL,262144);JOURNAL.unlink();fd=os.open(ROOT,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:os.fsync(fd)
  finally:os.close(fd)
 def _run(self,*args):return subprocess.run(args,check=True,capture_output=True,text=True,timeout=30).stdout
 def _expected_args(self,release):
  python='/srv/codi-connected/venvs/517179c/bin/python';script='/srv/codi-gateway/releases/'+release+'/scripts/serve-user-files.py'
  return [python,'-I','-B',script,'serve','--state-root','/var/lib/codi-gateway/beta','--data-root','/var/lib/codi-user-files/beta','--issuer-policy','/run/credentials/codi-beta-gateway.service/issuer-policy.json','--issuer-policy-sha256','71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','--base-path','','--port','28140']
 def _command_prefix(self,release):
  args=self._expected_args(release);return '{ path='+args[0]+' ; argv[]='+' '.join(args)+' ; ignore_errors=no ; '
 def _process_state(self,pid,release):
  proc=Path('/proc')/str(pid)
  def bounded(name,limit):
   with (proc/name).open('rb') as f:data=f.read(limit+1)
   if len(data)>limit:raise ValueError('unbounded process metadata')
   return data
  def start():
   raw=bounded('stat',4096);tail=raw.rpartition(b')')[2].split()
   if len(tail)<20:raise ValueError('invalid process stat')
   return tail[19]
  before=start();cmd=bounded('cmdline',16384)
  if cmd!=b'\x00'.join(os.fsencode(x) for x in self._expected_args(release))+b'\x00':raise ValueError('running beta command changed')
  status=bounded('status',32768).decode('ascii');fields={}
  for line in status.splitlines():
   key,sep,value=line.partition(':')
   if sep and key in ('Uid','Gid'):
    if key in fields:raise ValueError('duplicate process credentials')
    fields[key]=value.split()
  user=pwd.getpwnam('codi-beta-gateway')
  if fields.get('Uid')!=[str(user.pw_uid)]*4 or fields.get('Gid')!=[str(user.pw_gid)]*4:raise ValueError('running beta credentials changed')
  actual=os.stat(proc/'exe');expected=os.stat(self._expected_args(release)[0])
  if (actual.st_dev,actual.st_ino)!=(expected.st_dev,expected.st_ino):raise ValueError('running beta executable changed')
  current=self._run('/usr/bin/systemctl','show','codi-beta-gateway.service','-p','MainPID','--value').strip()
  if current!=str(pid) or before!=start():raise ValueError('beta process changed during inspection')
 def _service_state(self,*,strict=True):
  self._check_lock();unit=self.read_unit();digest=hashlib.sha256(unit).hexdigest()
  if digest==self.switch.UNIT_HASH:release=self.switch.BASE
  elif digest=='d94a346a364538a33ed5f76403b6c4067b28c813dda469cc0a4b0a9655141fea':release=self.switch.CANDIDATE
  else:raise ValueError('unexpected beta gateway unit')
  raw=self._run('/usr/bin/systemctl','show','codi-beta-gateway.service','-p','FragmentPath','-p','DropInPaths','-p','NeedDaemonReload','-p','UnitFileState','-p','User','-p','Group','-p','ActiveState','-p','MainPID','-p','ExecStart','--no-pager')
  fields={}
  for line in raw.splitlines():
   key,sep,value=line.partition('=')
   if not sep or key in fields:raise ValueError('invalid beta service state')
   fields[key]=value
  expected={'FragmentPath':str(UNIT),'DropInPaths':'','UnitFileState':'enabled','User':'codi-beta-gateway','Group':'codi-beta-gateway'}
  if any(fields.get(key)!=value for key,value in expected.items()) or fields.get('NeedDaemonReload') not in ('yes','no') or fields.get('ActiveState') not in ('active','inactive','failed') or not fields.get('MainPID','').isdigit():raise ValueError('beta gateway effective unit drift')
  if strict:
   if fields['NeedDaemonReload']!='no' or fields['ActiveState']!='active' or int(fields['MainPID'])<=0 or not fields.get('ExecStart','').startswith(self._command_prefix(release)):raise ValueError('beta gateway loaded command drift')
   self._process_state(int(fields['MainPID']),release)
  elif not any(fields.get('ExecStart','').startswith(self._command_prefix(version)) for version in (self.switch.BASE,self.switch.CANDIDATE)):
   raise ValueError('beta gateway loaded command drift')
 def _global_reload_check(self):
  raw=self._run('/usr/bin/systemctl','list-units','--all','--plain','--no-legend','--no-pager')
  names=[line.split()[0] for line in raw.splitlines() if line.split()]
  if not names or len(names)>10000 or len(set(names))!=len(names):raise ValueError('cannot inspect loaded units')
  raw=self._run('/usr/bin/systemctl','show','-p','Id','-p','NeedDaemonReload','--no-pager','--',*names)
  states=[]
  for block in raw.strip().split('\n\n'):
   fields={}
   for line in block.splitlines():
    key,sep,value=line.partition('=')
    if not sep or key in fields:raise ValueError('invalid global unit state')
    fields[key]=value
   if set(fields)!={'Id','NeedDaemonReload'}:raise ValueError('incomplete global unit state')
   states.append(fields)
  if len(states)!=len(names) or {x['Id'] for x in states}!=set(names):raise ValueError('global unit inventory changed')
  if any(x['NeedDaemonReload']!='no' and not (x['Id']=='codi-beta-gateway.service' and x['NeedDaemonReload']=='yes') for x in states):raise ValueError('unrelated unit requires daemon reload')
 def restart(self):
  self._service_state(strict=False);self._global_reload_check();self._run('/usr/bin/systemctl','daemon-reload');self._service_state(strict=False);self._run('/usr/bin/systemctl','restart','codi-beta-gateway.service')
 def check_ready(self):self.health()
 def read_only_health(self):
  self._service_state()
  deadline=time.monotonic()+15
  while True:
   c=http.client.HTTPConnection('127.0.0.1',28140,timeout=1)
   try:
    c.request('GET','/healthz',headers={'Host':'beta.ksu.codes'});r=c.getresponse();body=r.read(4097)
    if r.status!=200 or len(body)>4096 or json.loads(body)!={'status':'ok','scope':'personal-files'}:raise ValueError('beta gateway health failed')
    break
   except (ConnectionRefusedError,TimeoutError):
    if time.monotonic()>=deadline:raise ValueError('beta gateway listener did not become ready')
    time.sleep(0.1)
   finally:c.close()
  self._service_state()
 def health(self):
  self.read_only_health();self.signed_health(hashlib.sha256(self.read_unit()).hexdigest()!=self.switch.UNIT_HASH)
