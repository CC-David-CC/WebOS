#!/usr/bin/env python3
"""Disposable real-systemd process-death model; not production unit/gateway."""
import importlib.util,multiprocessing,os,pathlib,secrets,socket,subprocess,tempfile
root=pathlib.Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('t',root/'research/cad-source-access/beta-transition.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
if os.geteuid()!=0:raise SystemExit('Root required for disposable systemd unit')
name='codi-cad-source-test-'+secrets.token_hex(5)+'.service';unit=pathlib.Path('/run/systemd/system')/name
with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
def blob(label):return ('[Unit]\nDescription='+label+'\nStartLimitIntervalSec=0\n[Service]\nType=exec\nExecStart=/usr/bin/python3 -m http.server '+str(port)+' --bind 127.0.0.1\n').encode()
old,new=blob('CAD source old fixture'),blob('CAD source new fixture');t.OLD=t.sha(old);t.NEW=t.sha(new)
def ctl(*args):subprocess.run(['/usr/bin/systemctl',*args],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=30)
class Adapter:
 def __init__(self,stage=None):self.stage=stage
 def check(self):pass
 def require_no_other_journals(self):pass
 def units(self):return old,new
 def read_unit(self):return unit.read_bytes()
 def verify_candidate(self):pass
 def verify_old(self):assert self.read_unit()==old;ctl('is-active','--quiet',name)
 def verify_new(self):assert self.read_unit()==new;ctl('is-active','--quiet',name)
 def guards(self):return {'fixture':'unchanged'}
 def check_guards(self,g):
  assert g==self.guards()
  if self.stage=='after-journal':os._exit(88)
 def write_unit(self,b):
  t.atomic(unit,b,0o644)
  if self.stage=='after-write':os._exit(88)
 def restart(self):
  ctl('daemon-reload');ctl('restart',name)
  if self.stage=='after-restart':os._exit(88)
def child(journal,stage):t.Transition(Adapter(stage),journal).apply()
try:
 t.atomic(unit,old,0o644);ctl('daemon-reload');ctl('start',name)
 with tempfile.TemporaryDirectory(prefix='codi-cad-systemd-',dir='/run') as folder:
  journal=pathlib.Path(folder)/'journal'
  for stage in ('after-journal','after-write','after-restart'):
   process=multiprocessing.Process(target=child,args=(journal,stage));process.start();process.join(60);assert process.exitcode==88,(stage,process.exitcode)
   t.Transition(Adapter(),journal).recover();assert unit.read_bytes()==old and not journal.exists()
  t.Transition(Adapter(),journal).apply();assert unit.read_bytes()==new and not journal.exists();ctl('is-active','--quiet',name)
 print('PASS unique real-systemd fixture: three process deaths recover old unit; normal apply active; generic HTTP process, not production gateway')
finally:
 subprocess.run(['/usr/bin/systemctl','stop',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if unit.exists():unit.unlink()
 subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
