#!/usr/bin/env python3
"""Controlled quiescence of an actual preloaded legacy CLI; no live host."""
import fcntl,importlib.util,os,pathlib,signal,sys,tempfile,types
p=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'ops'))
sys.modules['scaffold']=types.SimpleNamespace(scaffold=lambda *a:None)
spec=importlib.util.spec_from_file_location('legacy_cli',p/'ops/webctl_live.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
with tempfile.TemporaryDirectory(prefix='legacy-quiesce-') as t:
 root=pathlib.Path(t);lock=root/'.controller.lock';lock.touch();active=root/'webctl.py';active.write_bytes((p/'ops/webctl_live.py').read_bytes())
 ready_r,ready_w=os.pipe();hold_r,hold_w=os.pipe();pid=os.fork()
 if pid==0:
  os.close(ready_r);os.close(hold_w);legacy.ROOT=root;legacy.root_required=lambda:None
  def load():
   os.write(ready_w,b'R');os.read(hold_r,1);return {'sites':[]}
  legacy.load=load;legacy.render=lambda data:(root/'old-render-ran').write_text('old')
  sys.argv=['webctl','render'];legacy.main();os._exit(0)
 os.close(ready_w);os.close(hold_r)
 try:
  assert os.read(ready_r,1)==b'R'
  # A cooperating administrative maintenance window prevents new invocations.
  # The process is a known supervised child, not an arbitrary PID selected by
  # name. Hold the actual flock until that preloaded process has exited.
  fd=os.open(lock,os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  try:
   os.kill(pid,signal.SIGTERM);_,status=os.waitpid(pid,0);pid=None
   assert os.waitstatus_to_exitcode(status)==-signal.SIGTERM
   replacement=root/'replacement';replacement.write_bytes((p/'ops/webctl_floor_candidate.py').read_bytes());os.replace(replacement,active)
   (root/'opfs-floor.json').write_text('floor')
  finally:os.close(fd)
  assert not (root/'old-render-ran').exists()
  print('PASS: known preloaded CLI drained under fixture flock before replacement and floor')
 finally:
  os.close(ready_r);os.close(hold_w)
  if pid is not None:
   os.kill(pid,signal.SIGKILL);os.waitpid(pid,0)
