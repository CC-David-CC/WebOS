#!/usr/bin/env python3
"""Actual process termination and durable-file tests; fixture adapter only."""
import fcntl,importlib.util,os,subprocess,sys,tempfile
from contextlib import contextmanager
from pathlib import Path
here=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('floor',here/'floor_journal.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FixtureAdapter:
 def __init__(self,root):self.root=Path(root);self.held_fd=None
 @contextmanager
 def held(self):
  with open(self.root/'lock','w') as f:
   fcntl.flock(f,fcntl.LOCK_EX);self.held_fd=f
   try:yield
   finally:self.held_fd=None
 def check_lock(self):
  if self.held_fd is None:raise ValueError('no lock')
 def state(self):return (self.root/'route').read_text()
 def set(self,s):
  p=self.root/'route';p.write_text(s)
  with p.open('r') as f:os.fsync(f.fileno())
 def preflight(self,r):
  if self.state()!='old':raise ValueError('drift')
 def gate(self):self.set('gate')
 def gate_health(self):assert self.state()=='gate'
 def forward(self,r):
  assert self.state()=='gate'
  if (self.root/'bad-candidate').exists():raise ValueError('candidate unavailable')
  self.set('new')
 def candidate_health(self,r):
  if (self.root/'bad-health').exists():raise ValueError('unhealthy candidate')
  assert self.state()=='new'
 def preflight_forward(self,r):
  if (self.root/'bad-candidate').exists():raise ValueError('candidate unavailable')
 def preflight_baseline(self,r):pass
 def restore_baseline(self,r):assert self.state()=='gate';self.set('old')
 def baseline_health(self,r):assert self.state()=='old'
if len(sys.argv)>1:
 root=Path(sys.argv[1]);target=sys.argv[2];adapter=FixtureAdapter(root);op=m.FloorJournal(adapter,root)
 if target=='recover':op.recover('a'*64,'b'*64)
 elif target=='stale':op.recover('a'*64,'c'*64)
 else:op.apply('a'*64,'b'*64,phase=lambda s:os._exit(17) if s==target else None)
 sys.exit(0)
with tempfile.TemporaryDirectory(prefix='opfs-journal-test-') as tmp:
 for phase in ('journaled','gated','floor','forward','healthy'):
  root=Path(tmp)/phase;root.mkdir(mode=0o700);(root/'route').write_text('old')
  p=subprocess.run([sys.executable,'-B',__file__,str(root),phase],timeout=10);assert p.returncode==17
  p=subprocess.run([sys.executable,'-B',__file__,str(root),'stale'],capture_output=True,timeout=10);assert p.returncode!=0 and (root/'route').read_text()=='gate' and (root/'opfs-transition.json').exists()
  if phase in ('floor','forward','healthy'):
   (root/'bad-candidate').touch();p=subprocess.run([sys.executable,'-B',__file__,str(root),'recover'],capture_output=True,timeout=10);assert p.returncode!=0 and (root/'route').read_text()=='gate' and (root/'opfs-transition.json').exists();(root/'bad-candidate').unlink()
  p=subprocess.run([sys.executable,'-B',__file__,str(root),'recover'],capture_output=True,timeout=10);assert p.returncode==0,p.stderr
  assert (root/'route').read_text()==('old' if phase in ('journaled','gated') else 'new')
  assert (root/'opfs-floor.json').exists()==(phase in ('floor','forward','healthy'))
  assert not (root/'opfs-transition.json').exists()
with tempfile.TemporaryDirectory(prefix='opfs-journal-fault-') as tmp:
 root=Path(tmp);(root/'route').write_text('old');adapter=FixtureAdapter(root);op=m.FloorJournal(adapter,root);original=m.os.replace
 def fail_floor(source,dest):
  if Path(dest).name=='opfs-floor.json':raise OSError('injected rename failure')
  return original(source,dest)
 m.os.replace=fail_floor
 try:
  try:op.apply('a'*64,'b'*64);raise AssertionError('failure not injected')
  except OSError:pass
 finally:m.os.replace=original
 assert adapter.state()=='gate' and not op.floor.exists() and op.journal.exists();op.recover('a'*64,'b'*64);assert adapter.state()=='old'
with tempfile.TemporaryDirectory(prefix='opfs-journal-fsync-') as tmp:
 root=Path(tmp);(root/'route').write_text('old');adapter=FixtureAdapter(root);op=m.FloorJournal(adapter,root);original=op._syncdir
 def fail_after_floor():
  if op.floor.exists():raise OSError('injected directory fsync failure')
  original()
 op._syncdir=fail_after_floor
 try:op.apply('a'*64,'b'*64);raise AssertionError('failure not injected')
 except OSError:pass
 op._syncdir=original;assert adapter.state()=='gate' and op.floor.exists() and op.journal.exists();op.recover('a'*64,'b'*64);assert adapter.state()=='new'
with tempfile.TemporaryDirectory(prefix='opfs-journal-health-') as tmp:
 root=Path(tmp);(root/'route').write_text('old');(root/'bad-health').touch();adapter=FixtureAdapter(root);op=m.FloorJournal(adapter,root)
 try:op.apply('a'*64,'b'*64);raise AssertionError('failure not injected')
 except ValueError:pass
 assert adapter.state()=='gate' and op.floor.exists() and op.journal.exists()
print('PASS rename/fsync fault recovery and failed candidate health re-gates')
print('PASS five process-kill phases; stale actor rejection, pre-floor restore and post-floor gate/forward on real journal files')
