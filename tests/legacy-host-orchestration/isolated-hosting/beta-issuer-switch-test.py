#!/usr/bin/env python3
"""Disposable unit-state fixture; does not invoke systemctl or private state."""
import fcntl,json,os,sys,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
import beta_issuer_switch as sw,beta_service_operator as svc
plan={'origin':svc.ORIGIN,'ports':svc.PORTS,'network':'disabled','native_release':'/srv/codi-connected/releases/microduck-issuer-'+sw.OLD,'native_manifest':sw.OLD,'worker_release':'/srv/codi-gateway/releases/'+svc.GATEWAY_MANIFEST,'worker_manifest':svc.GATEWAY_MANIFEST,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','guest_source_sha256':svc.GUEST_SOURCE};units=svc.render_units(plan);old=units[sw.UNIT_NAMES[0]].encode();new=sw.derive(old);assert b'/srv/data/codi-beta-native/'+sw.NEW.encode() in new and b'"--beta-opfs-file-content"' in new
with tempfile.TemporaryDirectory(prefix='issuer-switch-test-') as tmp:
 root=Path(tmp)
 for killed in ('journaled','unit-written','daemon-reload','issuer-restarted','healthy'):
  t=root/killed;t.mkdir(mode=0o700);ud=t/'units';ud.mkdir(mode=0o700);journal=t/'journal';state=t/'state';log=t/'log';lock=t/'lock';lock.touch()
  for n,data in units.items():(ud/n).write_text(data);(ud/n).chmod(0o644)
  state.write_text(json.dumps({sw.UNIT_NAMES[0]:'active',sw.UNIT_NAMES[1]:'active',sw.UNIT_NAMES[2]:'inactive'}));log.write_text('')
  def run(args):
   current=json.loads(state.read_text())
   with log.open('a') as f:f.write(' '.join(args)+'\n')
   if args[0]=='show':
    name=args[1];return f"ActiveState={current[name]}\nFragmentPath={ud/name}\nDropInPaths=\nNeedDaemonReload=no\n"
   if args[0]=='restart':
    assert args[1]==sw.UNIT_NAMES[0];current[sw.UNIT_NAMES[0]]='active';current[sw.UNIT_NAMES[1]]='inactive';current[sw.UNIT_NAMES[2]]='inactive';state.write_text(json.dumps(current));return ''
   if args[0]=='start':assert args[1]==sw.UNIT_NAMES[1];current[args[1]]='active';state.write_text(json.dumps(current));return ''
   if args==['daemon-reload']:return ''
   raise AssertionError(args)
  def require():assert os.environ.get('ISSUER_FIXTURE_LOCK')=='held'
  instance=sw.IssuerSwitch(unit_dir=ud,journal=journal,check_lock=require,check_floor_gate=require,verify_release=require,health=require,run=run)
  pid=os.fork()
  if pid==0:
   try:
    with lock.open('r') as f:
     fcntl.flock(f,fcntl.LOCK_EX);os.environ['ISSUER_FIXTURE_LOCK']='held';instance.apply(retain=False,phase=lambda x:os._exit(17) if x==killed else None)
   finally:os._exit(18)
  _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17,killed;assert journal.exists()
  if killed=='journaled':
   evidence=journal.read_bytes();dependent=ud/sw.UNIT_NAMES[1];prior=dependent.read_bytes();dependent.write_bytes(prior+b'# drift\n');before=log.read_text()
   try:
    with lock.open('r') as f:
     fcntl.flock(f,fcntl.LOCK_EX);os.environ['ISSUER_FIXTURE_LOCK']='held';instance.recover(old,retain=False)
    raise AssertionError('changed dependent unit accepted')
   except ValueError as error:assert 'pin changed' in str(error)
   assert journal.read_bytes()==evidence and log.read_text()==before;dependent.write_bytes(prior)
   def badgate():raise ValueError('gate unavailable')
   instance.gate=badgate
   try:
    with lock.open('r') as f:
     fcntl.flock(f,fcntl.LOCK_EX);os.environ['ISSUER_FIXTURE_LOCK']='held';instance.recover(old,retain=False)
    raise AssertionError('ungated recovery accepted')
   except ValueError as error:assert 'gate unavailable' in str(error)
   assert journal.read_bytes()==evidence and log.read_text()==before;instance.gate=require
  with lock.open('r') as f:
   fcntl.flock(f,fcntl.LOCK_EX);os.environ['ISSUER_FIXTURE_LOCK']='held';instance.recover(old,retain=False)
  assert not journal.exists() and (ud/sw.UNIT_NAMES[0]).read_bytes()==new
  assert json.loads(state.read_text())=={sw.UNIT_NAMES[0]:'active',sw.UNIT_NAMES[1]:'active',sw.UNIT_NAMES[2]:'inactive'}
  assert 'start '+sw.UNIT_NAMES[2] not in log.read_text(),killed
 # Outer transition may fail after issuer success. Retain original active
 # states until the outer route commit, then finalize only under v2 health.
 (ud/sw.UNIT_NAMES[0]).write_bytes(old);(ud/sw.UNIT_NAMES[0]).chmod(0o644)
 state.write_text(json.dumps({sw.UNIT_NAMES[0]:'active',sw.UNIT_NAMES[1]:'active',sw.UNIT_NAMES[2]:'inactive'}))
 with lock.open('r') as f:
  fcntl.flock(f,fcntl.LOCK_EX);os.environ['ISSUER_FIXTURE_LOCK']='held';instance.apply(retain=True)
  assert journal.exists();instance.recover(old,retain=True);assert journal.exists()
  outer=t/'opfs-transition.json';outer.write_text('pending')
  try:instance.finalize(old,outer,require);raise AssertionError('pending outer transition accepted')
  except ValueError as error:assert 'Outer Files transition' in str(error)
  assert journal.exists();outer.unlink()
  try:instance.finalize(old,outer,lambda:(_ for _ in ()).throw(ValueError('v2 routes unhealthy')));raise AssertionError('bad routes accepted')
  except ValueError as error:assert 'v2 routes unhealthy' in str(error)
  assert journal.exists();instance.finalize(old,outer,require);assert not journal.exists()
print('PASS fixture: pinned issuer unit, five killed phases, originally-active dependents and retained outer-commit handshake')
