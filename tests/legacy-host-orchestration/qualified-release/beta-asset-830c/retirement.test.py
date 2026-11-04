#!/usr/bin/env python3
"""Root-owned disposable retirement fault and custody controls."""
import importlib.util,json,os,shutil,signal,sys,tempfile
from pathlib import Path
from unittest.mock import patch
assert os.geteuid()==0
here=Path(__file__).resolve().parent;main=here.parent;ops=main.parent/'beta-isolated-hosting/ops'
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
pr=load('p',ops/'files_install_candidate.py');ret=load('r',here/'retirement.py');bc=Path(sys.argv[1]);mainactor=Path(sys.argv[2]);ce=ops/'beta_files_launch.py'
with tempfile.TemporaryDirectory(prefix='830c-retire-test-',dir='/run') as d:
 root=Path(d)
 def setup(name):
  t=root/name;t.mkdir(mode=0o700);q=t/'quarantine';j=t/'journal';j.write_text(json.dumps({'fixed':'fixture'}));j.chmod(0o600);entries={}
  for key,source in (('bc9',bc),('ce18-bundle',ce),('ce18-input',ce),('main-once',mainactor)):
   parent=t/key;parent.mkdir();p=parent/'actor';shutil.copyfile(source,p);p.chmod(ret.PINS[key][1]);entries[key]=p
  return t,q,j,entries
 def check():pass
 for stop in ret.PINS:
  t,q,j,entries=setup(stop);pid=os.fork()
  if pid==0:
   ret.retire(entries=entries,quarantine=q,journal=j,expected={'fixed':'fixture'},primitives=pr,check_lock=check,check_fence=check,phase=lambda n:os.kill(os.getpid(),signal.SIGKILL) if n=='retired-'+stop else None);os._exit(3)
  _,status=os.waitpid(pid,0);assert os.WIFSIGNALED(status) and os.WTERMSIG(status)==signal.SIGKILL
  ret.retire(entries=entries,quarantine=q,journal=j,expected={'fixed':'fixture'},primitives=pr,check_lock=check,check_fence=check)
  ret.retire(entries=entries,quarantine=q,journal=j,expected={'fixed':'fixture'},primitives=pr,check_lock=check,check_fence=check)
  assert all(not p.exists() for p in entries.values()) and {p.name for p in q.iterdir()}=={x+'.data' for x in ret.PINS}
  for key,(digest,_) in ret.PINS.items():assert ret.sha((q/(key+'.data')).read_bytes())==digest and (q/(key+'.data')).stat().st_mode&0o777==0o400
 # Simulate cross-device stat before any rename; no source moves.
 t,q,j,entries=setup('cross-device');original=Path.stat;target=entries['main-once'].parent
 def fake(path,*a,**kw):
  value=original(path,*a,**kw)
  if path==target:
   parts=list(value);parts[2]+=1;return os.stat_result(parts)
  return value
 with patch.object(Path,'stat',fake):
  try:ret.validate(entries,q,pr,check,pending=True);raise AssertionError('cross-device allowed')
  except ValueError as e:assert 'Cross-device' in str(e)
 assert all(p.exists() for p in entries.values()) and not q.exists()
 # Any wrong/missing/journal ambiguity is rejected before any rename.
 t,q,j,entries=setup('bad-journal')
 try:ret.retire(entries=entries,quarantine=q,journal=j,expected={'fixed':'other'},primitives=pr,check_lock=check,check_fence=check);raise AssertionError('wrong journal allowed')
 except ValueError:pass
 assert all(p.exists() for p in entries.values()) and not q.exists()
print('PASS each durable retirement kill, idempotent recovery, cross-device and journal refusal; isolated /run')
