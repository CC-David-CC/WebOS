#!/usr/bin/env python3
"""Demonstrate actual legacy main reads before flock and survives replacement."""
import fcntl,importlib.util,os,pathlib,sys,tempfile,types
p=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(p/'ops'))
sys.modules['scaffold']=types.SimpleNamespace(scaffold=lambda *a:None)
spec=importlib.util.spec_from_file_location('old_webctl',p/'ops/webctl_live.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='preloaded-webctl-') as t:
 root=pathlib.Path(t);(root/'.controller.lock').touch();active=root/'webctl.py';active.write_bytes((p/'ops/webctl_live.py').read_bytes())
 ready_r,ready_w=os.pipe();wake_r,wake_w=os.pipe();pid=os.fork()
 if pid==0:
  os.close(ready_r);os.close(wake_w);m.ROOT=root;m.root_required=lambda:None
  def load():
   os.write(ready_w,b'R');assert os.read(wake_r,1)==b'W';return {'sites':[]}
  m.load=load;m.render=lambda data:(root/'old-render-ran').write_text('old code ran')
  sys.argv=['webctl','render'];m.main();os._exit(0)
 os.close(ready_w);os.close(wake_r);assert os.read(ready_r,1)==b'R'
 fd=os.open(root/'.controller.lock',os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 replacement=root/'replacement';replacement.write_bytes((p/'ops/webctl_floor_candidate.py').read_bytes());os.replace(replacement,active)
 (root/'opfs-floor.json').write_text('floor');os.close(fd)
 os.write(wake_w,b'W');os.close(wake_w);_,status=os.waitpid(pid,0)
 assert os.waitstatus_to_exitcode(status)==0 and (root/'old-render-ran').read_text()=='old code ran'
 print('PASS negative control: preloaded legacy dispatch executes after replacement and floor')
