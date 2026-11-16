#!/usr/bin/env python3
"""Disposable root-owned fixture; no live hosting, routes or services."""
import fcntl,importlib.util,json,os,pathlib,shutil,signal,tempfile
p=pathlib.Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('installer',p/'ops/files_install_candidate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert os.geteuid()==0
root=pathlib.Path(tempfile.mkdtemp(prefix='codi-install-test-',dir='/run'))
try:
 source=root/'source';shutil.copytree(p,source,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for item in [source,*source.rglob('*')]:
  if not item.is_symlink(): item.chmod(0o755 if item.is_dir() else 0o644)
 parent=root/'bundles';parent.mkdir();state=root/'state';state.mkdir(mode=0o700);lock=root/'lock';lock.touch(mode=0o600)
 fd=os.open(lock,os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 def check():
  if os.fstat(fd).st_ino!=lock.stat().st_ino: raise ValueError('changed lock')
 manifest=source/'ops/files_install_manifest.json';dest=parent/'generation'
 # Actual process death during staging leaves only an unpublished temp tree.
 pid=os.fork()
 if pid==0:
  old_read=m.read_file
  def die_during_copy(path,*args,**kw):
   value=old_read(path,*args,**kw)
   if pathlib.Path(path).name=='beta_launcher.py': os.kill(os.getpid(),signal.SIGKILL)
   return value
  m.read_file=die_during_copy;m.stage(source,manifest,dest,check);os._exit(74)
 _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==-signal.SIGKILL
 assert not dest.exists()
 # Kill after publishing the directory but before reporting completion.
 published=parent/'published'
 pid=os.fork()
 if pid==0:
  old_sync=m.syncdir
  def kill_after_publish(path):
   old_sync(path)
   if pathlib.Path(path)==parent and published.exists(): os.kill(os.getpid(),signal.SIGKILL)
  m.syncdir=kill_after_publish;m.stage(source,manifest,published,check);os._exit(74)
 _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==-signal.SIGKILL
 m.verify_bundle(published,manifest,check)
 m.stage(source,manifest,dest,check)
 m.verify_bundle(dest,manifest,check)
 assert (dest/'ops/beta_files_launch.py').exists()
 try: m.stage(source,manifest,dest,check);raise AssertionError('overwrite accepted')
 except ValueError: pass
 bad=source/'ops/beta_files_launch.py'; good=bad.read_bytes();bad.write_bytes(good+b'changed')
 try: m.stage(source,manifest,parent/'bad',check);raise AssertionError('bad source accepted')
 except ValueError: pass
 assert not (parent/'bad').exists();bad.write_bytes(good)
 link=source/'ops/link';link.symlink_to(bad)
 try: m.root_path(link);raise AssertionError('symlink accepted')
 except ValueError: pass
 target=root/'webctl.py';shutil.copyfile(source/'ops/webctl_live.py',target);target.chmod(0o644)
 journal=state/'install.json';floor=state/'floor.json'
 original=m.atomic
 # Real death immediately after the fsynced journal is recoverable.
 pid=os.fork()
 if pid==0:
  def kill_after_journal(path,*args,**kw):
   original(path,*args,**kw)
   if path==journal: os.kill(os.getpid(),signal.SIGKILL)
  m.atomic=kill_after_journal
  m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check);os._exit(74)
 _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==-signal.SIGKILL
 assert journal.exists() and m.digest(target.read_bytes())==m.OLD
 m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check)
 assert not journal.exists() and m.digest(target.read_bytes())==m.NEW
 target.write_bytes((source/'ops/webctl_live.py').read_bytes())
 def interrupted(path,*args,**kw):
  original(path,*args,**kw)
  if path==journal: raise RuntimeError('interrupted after journal')
 m.atomic=interrupted
 try: m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check);raise AssertionError('fault not injected')
 except RuntimeError: pass
 assert journal.exists() and m.digest(target.read_bytes())==m.OLD
 m.atomic=original
 m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check)
 assert m.digest(target.read_bytes())==m.NEW and not journal.exists()
 # Process death after the replacement but before the journal is removed:
 # the next lock holder can finish without restoring the old controller.
 target.write_bytes((source/'ops/webctl_live.py').read_bytes())
 pid=os.fork()
 if pid==0:
  def kill_after_replace(path,*args,**kw):
   original(path,*args,**kw)
   if path==target: os.kill(os.getpid(),signal.SIGKILL)
  m.atomic=kill_after_replace
  m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check)
  os._exit(74)
 _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==-signal.SIGKILL
 assert journal.exists() and m.digest(target.read_bytes())==m.NEW
 m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check)
 assert not journal.exists() and m.digest(target.read_bytes())==m.NEW
 target.write_bytes((source/'ops/webctl_live.py').read_bytes());floor.touch()
 try: m.guard_install(target=target,guard=source/'ops/webctl_floor_candidate.py',old_source=source/'ops/webctl_live.py',journal=journal,floor=floor,check_lock=check);raise AssertionError('floor ignored')
 except ValueError: pass
 assert m.digest(target.read_bytes())==m.OLD
 print('PASS: exact staged bundle, no overwrite, guard switch, floor refusal')
finally:
 os.close(fd);shutil.rmtree(root)
