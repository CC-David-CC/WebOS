#!/usr/bin/env python3
"""ROOT LOCAL TEST: unique /run systemd fixtures only, never beta services."""
import fcntl,hashlib,os,subprocess,sys,tempfile,uuid
from pathlib import Path
if os.geteuid()!=0:raise SystemExit('Run this disposable fixture as root')
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'));import beta_issuer_switch as sw
prefix='codi-opfs-fixture-'+str(os.getpid())+'-'+uuid.uuid4().hex[:8];names=tuple(prefix+'-'+x+'.service' for x in ('issuer','frontend','gateway'));unitdir=Path('/run/systemd/system');paths=[unitdir/n for n in names]
def command(*args):
 p=subprocess.run(['/usr/bin/systemctl',*args],capture_output=True,text=True,timeout=40)
 if p.returncode:raise RuntimeError(str(args)+': '+p.stderr+' '+p.stdout)
 return p.stdout
def write_new(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
# All unit names and file paths are newly generated fixture-only names.
issuer='[Unit]\nDescription=Disposable OPFS issuer fixture\nStartLimitIntervalSec=0\n[Service]\nType=simple\nExecStart=/usr/bin/sleep infinity\n'.encode()
def dependent(role):return ('[Unit]\nDescription=Disposable OPFS '+role+' fixture\nStartLimitIntervalSec=0\nRequires='+names[0]+'\nAfter='+names[0]+'\n[Service]\nType=simple\nExecStart=/usr/bin/sleep infinity\n').encode()
original={names[0]:issuer,names[1]:dependent('frontend'),names[2]:dependent('gateway')};new=issuer+b'# disposable candidate revision\n'
sw.UNIT_NAMES=names;sw.PINS={n:hashlib.sha256(raw).hexdigest() for n,raw in original.items()};sw.derive=lambda raw:new if raw==issuer else (_ for _ in ()).throw(ValueError('fixture issuer pin changed'))
created=[]
try:
 for path in paths:write_new(path,original[path.name]);created.append(path)
 command('daemon-reload');command('start',names[0],names[1]);command('stop',names[2])
 with tempfile.TemporaryDirectory(prefix='opfs-real-systemd-') as temp:
  t=Path(temp);t.chmod(0o700);lock=t/'lock';lock.touch();journal=t/'issuer-switch.json'
  # This checks only disposable fixture lock/markers, not production custody.
  def check():assert os.environ.get('OPFS_SYSTEMD_FIXTURE_LOCK')=='held'
  instance=sw.IssuerSwitch(unit_dir=unitdir,journal=journal,check_lock=check,check_floor_gate=check,verify_release=check,health=check)
  for stage in ('journaled','unit-written','daemon-reload','issuer-restarted','healthy'):
   paths[0].write_bytes(issuer);paths[0].chmod(0o644);command('daemon-reload');command('restart',names[0]);command('start',names[1]);command('stop',names[2])
   pid=os.fork()
   if pid==0:
    try:
     with lock.open('r') as f:
      fcntl.flock(f,fcntl.LOCK_EX);os.environ['OPFS_SYSTEMD_FIXTURE_LOCK']='held';instance.apply(retain=False,phase=lambda x:os._exit(17) if x==stage else None)
    except BaseException:
     import traceback;traceback.print_exc();os._exit(18)
   _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17,stage;assert journal.exists()
   with lock.open('r') as f:
    fcntl.flock(f,fcntl.LOCK_EX);os.environ['OPFS_SYSTEMD_FIXTURE_LOCK']='held';instance.recover(issuer,retain=False)
   assert not journal.exists() and paths[0].read_bytes()==new
   state={n:command('show',n,'-p','ActiveState','--value').strip() for n in names}
   assert state=={names[0]:'active',names[1]:'active',names[2]:'inactive'},(stage,state)
 print('PASS actual local systemd Requires/After fixture, five killed phases and only originally-active dependent restored')
finally:
 if created:
  subprocess.run(['/usr/bin/systemctl','stop',*names],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=40)
  subprocess.run(['/usr/bin/systemctl','reset-failed',*names],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=40)
  for path in created:
   try:path.unlink()
   except FileNotFoundError:pass
  subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=40)
