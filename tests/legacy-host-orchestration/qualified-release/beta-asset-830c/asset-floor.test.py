#!/usr/bin/env python3
"""Fork fault controls for asset journal only; fixture adapter is simulated."""
import contextlib,fcntl,hashlib,importlib.util,json,os,signal,sys,tempfile
from pathlib import Path
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here.parents[1]/'beta-isolated-hosting/ops'))
spec=importlib.util.spec_from_file_location('asset_floor',here/'asset-floor.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Adapter:
 def __init__(self,t):self.t=t;self.fd=None
 @contextlib.contextmanager
 def held(self):
  self.fd=os.open(self.t/'lock',os.O_RDWR|os.O_CREAT,0o600);fcntl.flock(self.fd,fcntl.LOCK_EX)
  try:yield
  finally:os.close(self.fd);self.fd=None
 def check_lock(self):
  if self.fd is None:raise ValueError('lock required')
 def route(self,v):
  self.check_lock();p=self.t/'route';p.write_text(v)
  with p.open('rb') as f:os.fsync(f.fileno())
 def preflight(self,r):self.check_lock()
 def gate(self):self.route('gate')
 def gate_health(self):assert (self.t/'route').read_text()=='gate'
 def preflight_forward(self,r):
  self.check_lock()
  if (self.t/'missing').exists():raise ValueError('candidate unavailable')
 def preflight_baseline(self,r):self.check_lock()
 def forward(self,r):self.route('new')
 def candidate_health(self,r):assert (self.t/'route').read_text()=='new'
 def restore_baseline(self,r):self.route('old')
 def baseline_health(self,r):assert (self.t/'route').read_text()=='old'
with tempfile.TemporaryDirectory(prefix='asset-floor-') as d:
 root=Path(d)
 for stage in ('journaled','gated','floor','forward','healthy'):
  t=root/stage;t.mkdir(mode=0o700);(t/'route').write_text('old');floor=t/'opfs-floor.json';floor.write_text(json.dumps({'version':1,'baseline':m.ORIGINAL_BASE,'candidate':m.OLD}));floor.chmod(0o600);before=hashlib.sha256(floor.read_bytes()).hexdigest()
  pid=os.fork()
  if pid==0:
   m.AssetFloor(Adapter(t),t).apply_exact(phase=lambda x:os.kill(os.getpid(),signal.SIGKILL) if x==stage else None);os._exit(3)
  _,status=os.waitpid(pid,0);assert os.WIFSIGNALED(status) and os.WTERMSIG(status)==signal.SIGKILL
  post=stage in ('floor','forward','healthy');m.AssetFloor(Adapter(t),t).recover_exact()
  assert (t/'route').read_text()==('new' if post else 'old'),stage
  assert hashlib.sha256(floor.read_bytes()).hexdigest()==before and not (t/'files-asset-transition.json').exists()
  if post:
   (t/'missing').touch()
   try:m.AssetFloor(Adapter(t),t).recover_exact()
   except ValueError as e:assert 'candidate unavailable' in str(e)
   else:raise AssertionError('missing target accepted')
   assert (t/'route').read_text()=='gate'
   (t/'missing').unlink();m.AssetFloor(Adapter(t),t).recover_exact();assert (t/'route').read_text()=='new'
 t=root/'bad';t.mkdir(mode=0o700);(t/'route').write_text('old');p=t/'opfs-floor.json';p.write_text(json.dumps({'version':1,'baseline':'0'*64,'candidate':m.OLD}));p.chmod(0o600)
 try:m.AssetFloor(Adapter(t),t).apply_exact()
 except ValueError:pass
 else:raise AssertionError('invalid original floor accepted')
 assert (t/'route').read_text()=='old'
print('PASS five SIGKILL points, original-floor preservation, pre/post-floor and finalized unavailable-target recovery; simulated route adapter')
