#!/usr/bin/env python3
"""Review candidate for fixed-path guarded main installer. Never run unreviewed."""
import argparse,hashlib,json,os,socket,stat,subprocess,sys,types
from pathlib import Path
PKG=Path('/srv/codi-connected/operators/main-qualified-e7e8-v1')
BETA=Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops')
SOURCE=Path('/srv/codi-connected/operators/main-qualified-e7e8-input/successor')
DEST=Path('/srv/codi-connected/operators/beta-recovery-e7-v1')
TARGET=Path('/home/dflanag3/webhost-sites/ops/webctl.py')
JOURNAL=Path('/var/lib/webhost-ops/main-restriction-journal.json')
FLOOR=Path('/var/lib/webhost-ops/opfs-floor.json')
PINS={'beta_launcher.py':'9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95','files_install_candidate.py':'4c09350ea824e09a5596f70bdda1303b30242a2f6ccac5238314e1fcc107dd51','beta_files_preflight.py':'4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff','main-install.py':'c6bd426cb8cd87564d14b458c1cda85dbc6655794719fb84615e4d7c9c271e96','main-successor-preflight.py':'9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83'}
def protected(path):
 for p in (path,*path.parents):
  v=p.lstat()
  if p.is_symlink() or v.st_uid!=0 or v.st_mode&0o022:raise ValueError('Unprotected operator path: '+str(p))
def load(base,name,alias):
 path=base/name;protected(path);fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_nlink!=1 or a.st_size>1024*1024:raise ValueError('Unsafe code input')
  raw=b''
  while len(raw)<a.st_size:
   part=os.read(fd,min(65536,a.st_size-len(raw)))
   if not part:raise ValueError('Short code input')
   raw+=part
  b=os.fstat(fd)
  if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise ValueError('Code changed')
 finally:os.close(fd)
 if hashlib.sha256(raw).hexdigest()!=PINS[name]:raise ValueError('Code pin mismatch: '+name)
 m=types.ModuleType(alias);m.__file__=str(path);sys.modules[alias]=m;exec(compile(raw,str(path),'exec'),m.__dict__);return m

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=('plan','install','recover'));args=parser.parse_args()
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or Path(__file__).absolute()!=PKG/'main-install-launch.py':raise ValueError('Protected fixed-path root invocation required')
 protected(PKG);protected(BETA);protected(Path(__file__).absolute())
 host=load(BETA,'beta_launcher.py','beta_launcher');pr=load(BETA,'files_install_candidate.py','files_install_candidate');pre=load(BETA,'beta_files_preflight.py','beta_files_preflight');successor=load(PKG,'main-successor-preflight.py','main_successor_preflight');installer=load(PKG,'main-install.py','main_install')
 lock=host.HostLock()
 def custody():
  lock.check();pre.protected_ancestors(TARGET.parent);pr.root_path(PKG,True);pr.root_path(SOURCE,True);pr.root_path(DEST.parent,True);pr.root_path(JOURNAL.parent,True)
  info=lock.path.lstat();pr.no_acl(lock.path)
  if (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode),info.st_nlink)!=(0,0,0o644,1):raise ValueError('Controller lock metadata drift')
 def fence():
  lock.check()
  # Trusted administrators must separately maintain the no-new-invocations
  # maintenance freeze. A process scan cannot detect arbitrary embedded code.
  for unit,pin in (('codi-ksu-live-root-renew.timer','fe8fdcab3889ec2fb51a063e90487ed9f2efc9fccd185a9825c715c1d40a4718'),('codi-ksu-live-root-renew.service','abb4716e957f856f171e35cb0e97a64386e6a76c7068b0779bf3c993878c8870')):
   path=Path('/etc/systemd/system')/unit;pr.root_path(path)
   if hashlib.sha256(pr.read_file(path)).hexdigest()!=pin:raise ValueError('Renewal unit drift')
   result=subprocess.run(['/usr/bin/systemctl','show',unit,'-p','ActiveState','-p','MainPID','-p','ControlPID','-p','FragmentPath','-p','DropInPaths','-p','NeedDaemonReload'],check=True,capture_output=True,text=True,timeout=15)
   state=dict(line.split('=',1) for line in result.stdout.splitlines())
   if state.get('ActiveState') not in ('inactive','failed') or any(state.get(x) not in (None,'','0') for x in ('MainPID','ControlPID')) or state.get('FragmentPath')!=str(path) or state.get('DropInPaths') or state.get('NeedDaemonReload')!='no':raise ValueError('Renewal timer/service not quiescent')
  needles=('webctl.py','beta_files_launch.py','beta_files_recover.py','main-launcher.py')
  for path in Path('/proc').iterdir():
   if not path.name.isdigit() or int(path.name)==os.getpid():continue
   try:raw=(path/'cmdline').read_bytes()
   except FileNotFoundError:continue
   except PermissionError:raise ValueError('Cannot audit process inventory')
   if any(needle.encode() in part for part in raw.split(b'\0') for needle in needles):raise ValueError('Known controller process remains: '+path.name)
 with lock.held():
  custody();fence()
  if args.action=='plan':
   successor.verify(SOURCE,pr.read_file,lock.check);guard=PKG/'webctl-main-guard.py';pr.root_path(guard)
   if hashlib.sha256(pr.read_file(guard)).hexdigest()!=installer.NEW:raise ValueError('Guard source pin changed')
   pr.root_path(FLOOR)
   if stat.S_IMODE(FLOOR.stat().st_mode)!=0o600 or json.loads(pr.read_file(FLOOR,4096))!=installer.FLOOR:raise ValueError('Original floor changed')
   st=TARGET.lstat();pr.no_acl(TARGET)
   if (st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode),st.st_nlink)!=(1000,1000,0o644,1) or hashlib.sha256(pr.read_file(TARGET,root_owned=False)).hexdigest()!=installer.OLD:raise ValueError('Controller baseline drift')
   if JOURNAL.exists() or JOURNAL.is_symlink():raise ValueError('Install recovery pending')
   for name in ('main-restriction-journal.json','opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json','beta-hosting-journal.json','files-asset-transition.json'):
    try:(JOURNAL.parent/name).lstat()
    except FileNotFoundError:continue
    raise ValueError('Conflicting hosting journal: '+name)
   try:DEST.lstat()
   except FileNotFoundError:pass
   else:successor.verify(DEST,pr.read_file,lock.check)
   print(json.dumps({'action':'plan','status':'PASS','requiresTrustedFreeze':True,'productionQualified':False}));return
  exists=JOURNAL.exists() or JOURNAL.is_symlink()
  if args.action=='install' and exists:raise ValueError('Use recovery for existing install journal')
  # A process can die during staging before publication or journal creation.
  # Under the same maintenance freeze, recovery safely starts a fresh pinned
  # generation; abandoned unselected stages remain for separately reviewed cleanup.
  status=installer.install(source=SOURCE,destination=DEST,guard=PKG/'webctl-main-guard.py',target=TARGET,journal=JOURNAL,floor=FLOOR,primitives=pr,verify_successor=successor.verify,check_lock=lock.check,check_fence=fence,check_custody=custody)
  print(json.dumps({'action':args.action,'status':status,'requiresTrustedFreeze':True}))
if __name__=='__main__':main()
