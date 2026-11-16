#!/usr/bin/env python3
"""Root-owned disposable process-kill tests. No production paths used."""
import fcntl,importlib.util,json,os,shutil,signal,sys,tempfile
from pathlib import Path
assert os.geteuid()==0
here=Path(__file__).resolve().parent;ops=here.parent/'beta-isolated-hosting/ops'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pr=load('fixture_install_primitives',ops/'files_install_candidate.py');pre=load('fixture_successor',here/'main-successor-preflight.py');ins=load('fixture_main_install',here/'main-install.py')
source=Path(sys.argv[1])
with tempfile.TemporaryDirectory(prefix='codi-main-install-test-',dir='/run') as name:
 root=Path(name);sourcecopy=root/'source';shutil.copytree(source,sourcecopy)
 for p in sourcecopy.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
 sourcecopy.chmod(0o755);guard=root/'guard.py';shutil.copyfile(here/'webctl-main-guard.py',guard);guard.chmod(0o644)
 lock=root/'lock';lock.touch();fd=os.open(lock,os.O_RDWR);held=[False];fenced=[True]
 def check_lock():
  if not held[0]:raise ValueError('fixture lock not held')
 def check_fence():
  if not fenced[0]:raise ValueError('fixture maintenance fence absent')
 def custody():pass # target ancestry confined to root-owned /run tree
 def acquire():fcntl.flock(fd,fcntl.LOCK_EX);held[0]=True
 def release():held[0]=False;fcntl.flock(fd,fcntl.LOCK_UN)
 def setup(label):
  case=root/label;case.mkdir(mode=0o700);pub=case/'operators';pub.mkdir(mode=0o755);private=case/'private';private.mkdir(mode=0o700);floor=private/'opfs-floor.json';floor.write_text(json.dumps(ins.FLOOR));floor.chmod(0o600);target=case/'webctl.py';shutil.copyfile(ops/'webctl_floor_candidate.py',target);target.chmod(0o644);os.chown(target,1000,1000)
  return dict(source=sourcecopy,destination=pub/'beta-recovery-e7-v1',guard=guard,target=target,journal=private/'main-restriction-journal.json',floor=floor,primitives=pr,verify_successor=pre.verify,check_lock=check_lock,check_fence=check_fence,check_custody=custody)
 for stop in ('staged','published','journaled','guard-replaced','verified'):
  kw=setup(stop);pid=os.fork()
  if pid==0:
   acquire()
   try:ins.install(**kw,phase=lambda name:os.kill(os.getpid(),signal.SIGKILL) if name==stop else None)
   finally:release()
   os._exit(2)
  _,status=os.waitpid(pid,0);assert os.WIFSIGNALED(status) and os.WTERMSIG(status)==signal.SIGKILL,stop
  assert json.loads(kw['floor'].read_text())==ins.FLOOR
  acquire()
  try:
   result=ins.install(**kw);assert result in ('installed','already-installed');assert ins.sha(kw['target'].read_bytes())==ins.NEW;assert not kw['journal'].exists();assert ins.install(**kw)=='already-installed'
  finally:release()
 kw=setup('refusal');acquire()
 try:
  fenced[0]=False
  try:ins.install(**kw);raise AssertionError('unfenced install accepted')
  except ValueError:pass
  fenced[0]=True;(kw['journal'].parent/'opfs-transition.json').touch()
  try:ins.install(**kw);raise AssertionError('conflicting journal accepted')
  except ValueError:pass
  assert ins.sha(kw['target'].read_bytes())==ins.OLD and not kw['destination'].exists()
 finally:release()
 # Main-transaction journal shares the name but must never be interpreted as
 # this installer's schema or cause even an unselected bundle publication.
 foreign=setup('foreign');foreign['journal'].write_text('{"version":2,"policy":"gate-only"}');foreign['journal'].chmod(0o600)
 acquire()
 try:
  try:ins.install(**foreign);raise AssertionError('foreign journal accepted')
  except ValueError:pass
  assert not foreign['destination'].exists() and ins.sha(foreign['target'].read_bytes())==ins.OLD
 finally:release()
 os.close(fd)
print('PASS five real SIGKILL boundaries, floor/guard/successor, idempotence and fenced/conflicting refusal; custody/timer callback simulated')
