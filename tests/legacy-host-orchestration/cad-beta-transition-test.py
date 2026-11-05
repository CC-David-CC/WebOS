#!/usr/bin/env python3
"""Real process exits against disposable files; service actions are models."""
import importlib.util,multiprocessing,os,pathlib,tempfile
root=pathlib.Path(__file__).resolve().parents[1]
def load(n,p):
 s=importlib.util.spec_from_file_location(n,root/p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
t=load('transition','research/cad-source-access/beta-transition.py');h=load('switch','research/cad-source-access/beta-switch.py');old=(root/'research/cad-source-access/beta-unit-f7fe.txt').read_bytes();host=object.__new__(h.Host);host.read_unit=lambda:old;_,new=host.units();assert t.sha(old)==t.OLD and t.sha(new)==t.NEW
class A:
 def __init__(self,d,kill=None):self.d=pathlib.Path(d);self.kill=kill
 def check(self):pass
 def require_no_other_journals(self):pass
 def units(self):return old,new
 def read_unit(self):return (self.d/'unit').read_bytes()
 def verify_candidate(self):pass
 def verify_old(self):assert self.read_unit()==old
 def verify_new(self):assert self.read_unit()==new
 def guards(self):return {'fixed':'unchanged'}
 def check_guards(self,g):assert g==self.guards()
 def write_unit(self,b):
  t.atomic(self.d/'unit',b,0o644)
  if self.kill=='after-write':os._exit(88)
 def restart(self):
  (self.d/'restart').write_text('yes')
  if self.kill=='after-restart':os._exit(88)
def child(d,stage):
 a=A(d,stage);x=t.Transition(a,pathlib.Path(d)/'journal')
 if stage=='after-journal':
  def stop(g):os._exit(88)
  a.check_guards=stop
 x.apply()
for phase in ('after-journal','after-write','after-restart'):
 with tempfile.TemporaryDirectory() as tmp:
  d=pathlib.Path(tmp);(d/'unit').write_bytes(old);proc=multiprocessing.Process(target=child,args=(tmp,phase));proc.start();proc.join(10);assert proc.exitcode==88,(phase,proc.exitcode)
  tr=t.Transition(A(tmp),d/'journal');assert (d/'journal').is_file();tr.recover();assert (d/'unit').read_bytes()==old and not (d/'journal').exists()
with tempfile.TemporaryDirectory() as tmp:
 d=pathlib.Path(tmp);(d/'unit').write_bytes(old);tr=t.Transition(A(tmp),d/'journal');tr.apply();assert (d/'unit').read_bytes()==new and not (d/'journal').exists()
print('PASS exact-unit model: complete journal publication, three killed child phases recover old, normal apply')
# Failed post-restart health leaves a fenced receipt. Recovery depends only on
# the old unit/health; it does not require the new worker or registry.
with tempfile.TemporaryDirectory() as tmp:
 d=pathlib.Path(tmp);(d/'unit').write_bytes(old);a=A(tmp)
 def failure():raise RuntimeError('candidate unhealthy')
 a.verify_new=failure;tr=t.Transition(a,d/'journal')
 try:tr.apply();raise AssertionError('health failure accepted')
 except RuntimeError:pass
 assert (d/'journal').exists() and (d/'unit').read_bytes()==new
 tr=t.Transition(A(tmp),d/'journal');tr.recover();assert (d/'unit').read_bytes()==old
with tempfile.TemporaryDirectory() as tmp:
 d=pathlib.Path(tmp);(d/'unit').write_bytes(old);a=A(tmp,'after-write');p=multiprocessing.Process(target=child,args=(tmp,'after-write'));p.start();p.join(10);assert p.exitcode==88
 (d/'unit').write_bytes(b'foreign unit')
 try:t.Transition(A(tmp),d/'journal').recover();raise AssertionError('foreign unit accepted')
 except ValueError:pass
 assert (d/'journal').exists() and (d/'unit').read_bytes()==b'foreign unit'
print('PASS failed health rollback, missing-candidate recovery model, and foreign-unit refusal')
# Host coordination must check both independently and reject a pending older
# worker journal; the actual lock implementation remains the pinned adapter.
class Lock:
 def __init__(self):self.calls=0
 def check(self):self.calls+=1
class Worker:
 def __init__(self,pending=False):self.calls=0;self.is_pending=pending
 def _check_lock(self):self.calls+=1
 def pending(self):return self.is_pending
host=object.__new__(h.Host);host.lock=Lock();host.worker_lock=Worker();host.check();assert host.lock.calls==host.worker_lock.calls==1
host.worker_lock.is_pending=True
try:host.require_no_other_journals();raise AssertionError('pending worker switch accepted')
except ValueError:pass
print('PASS both lock checks and pending worker-switch refusal')
