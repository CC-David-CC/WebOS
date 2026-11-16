#!/usr/bin/env python3
"""Candidate protected beta Files probe provision/inspect. Not yet installed."""
import argparse,hashlib,json,os,socket,stat,sys,types
from pathlib import Path
SELF=Path('/srv/codi-connected/operators/beta-files-probe-entry-v1.py')
INPUT=Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops')
STATE=Path('/var/lib/webhost-ops')
POLICY=Path('/etc/codi-user-files/beta/issuer-policy.json')
PROBE=STATE/'beta-files-probe'
WORKER=Path('/srv/codi-gateway/releases/dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')
ORIGIN='https://beta.ksu.codes';ISSUER=28118;FRONTEND=28132;GATEWAY=28140
POLICY_PIN='71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca'
PINS={'beta_launcher':'9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95','beta_files_preflight':'4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff','beta_signed_probe':'e38cc2007b085666b0279259b7ec4143a7ad67a7d15d87655add57be6851257a'}

def custody(path):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('protected absolute path required')
 for p in (path,*path.parents):
  st=p.lstat()
  if stat.S_ISLNK(st.st_mode) or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('unprotected path')
  for name in ('system.posix_acl_access','system.posix_acl_default'):
   try:os.getxattr(p,name,follow_symlinks=False)
   except OSError as e:
    if e.errno not in (61,95):raise
   else:raise ValueError('extended ACL denied')

def load(name,pin,path,read):
 custody(path);raw=read(path)
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('module pin mismatch')
 module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module;exec(compile(raw,str(path),'exec'),module.__dict__);return module

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=('inspect','provision'));args=parser.parse_args()
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or Path(__file__).absolute()!=SELF:raise ValueError('wrong protected entrypoint')
 custody(SELF);custody(INPUT);custody(STATE)
 if stat.S_IMODE(STATE.stat().st_mode)!=0o700:raise ValueError('private state required')
 # Read the verified module bytes with the same bounded no-follow reader used
 # by the existing launcher; beta_launcher itself is bootstrapped first.
 fd=os.open(INPUT/'beta_launcher.py',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=0 or s.st_nlink!=1 or s.st_mode&0o022 or s.st_size>8*1024*1024:raise ValueError('unsafe bootstrap')
  raw=b''
  while len(raw)<s.st_size:
   part=os.read(fd,min(65536,s.st_size-len(raw)))
   if not part:raise ValueError('short bootstrap')
   raw+=part
  t=os.fstat(fd)
  if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns):raise ValueError('bootstrap changed')
 finally:os.close(fd)
 custody(INPUT/'beta_launcher.py')
 if hashlib.sha256(raw).hexdigest()!=PINS['beta_launcher']:raise ValueError('bootstrap pin mismatch')
 host=types.ModuleType('beta_launcher');host.__file__=str(INPUT/'beta_launcher.py');sys.modules[host.__name__]=host;exec(compile(raw,host.__file__,'exec'),host.__dict__)
 pre=load('beta_files_preflight',PINS['beta_files_preflight'],INPUT/'beta_files_preflight.py',host.read)
 probe=load('beta_signed_probe',PINS['beta_signed_probe'],INPUT/'beta_signed_probe.py',host.read)
 lock=host.HostLock()
 with lock.held():
  lock.check();pre.protected_ancestors(host.ROOT/'ops');custody(STATE);custody(POLICY)
  for name in ('opfs-floor.json','opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json','files-install-guard.json'):
   p=STATE/name
   if p.exists() or p.is_symlink():raise ValueError('beta transition or floor present')
  host.verify_native();host.verify_beta_worker(WORKER,host.GW);host.service_preflight();host.beta_ready();host.main_ready();lock.check()
  for name,pin in host.UNIT.items():
   path=Path('/etc/systemd/system')/name;custody(path)
   if host.sha(host.read(path))!=pin:raise ValueError('beta unit mismatch')
   state=host.unit_state(name);role=name.removeprefix('codi-beta-').removesuffix('.service');user='codi-beta-'+role
   if state.get('ActiveState')!='active' or state.get('MainPID') in (None,'0') or state.get('FragmentPath')!=str(path) or state.get('DropInPaths') or state.get('NeedDaemonReload')!='no' or state.get('User')!=user or state.get('Group')!=user:raise ValueError('beta service state mismatch')
  raw=host.read(POLICY,32768)
  if host.sha(raw)!=POLICY_PIN:raise ValueError('policy pin mismatch')
  policy=json.loads(raw);identity=policy.get('identity',policy)
  if identity.get('issuer')!=ORIGIN or identity.get('mode')!='server':raise ValueError('wrong issuer policy')
  for port in (ISSUER,FRONTEND):
   status,body=host.get(port,'/config.json');config=json.loads(body)
   if status!=200 or config.get('identity')!=identity or 'fileStorage' in config:raise ValueError('beta baseline configuration mismatch')
  josepath=WORKER/'codiserver-server-v0.3.0/codiauth/jose.py';custody(josepath)
  jose=types.ModuleType('probe_pinned_jose');jose.__file__=str(josepath);exec(compile(host.read(josepath),str(josepath),'exec'),jose.__dict__)
  if PROBE.exists() or PROBE.is_symlink():
   custody(PROBE);pre.protected_ancestors(PROBE)
   if not PROBE.is_dir() or stat.S_IMODE(PROBE.stat().st_mode)!=0o700:raise ValueError('private probe directory required')
  elif args.action=='provision':
   os.mkdir(PROBE,0o700);fd=os.open(STATE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd);custody(PROBE)
  else:
   print('probe absent');return
  pending=any((PROBE/n).exists() or (PROBE/n).is_symlink() for n in ('probe-provision.json','signed-probe-acceptance.json'))
  config=PROBE/'probe.json'
  if pending:raise ValueError('private probe journal requires reconciliation')
  if args.action=='inspect':
   if not (config.exists() or config.is_symlink()):print('probe absent');return
   custody(config);probe.load_probe_config(config);lock.check();print('probe configuration present');return
  if config.exists() or config.is_symlink():raise ValueError('probe already provisioned')
  if any(PROBE.iterdir()):raise ValueError('unexpected private probe files')
  lock.check();probe.provision_private(PROBE,origin=ORIGIN,issuer_port=ISSUER,gateway_port=GATEWAY,policy=identity,jose=jose);lock.check()
  custody(config);probe.load_probe_config(config);print('beta probe provisioned and known file verified')
if __name__=='__main__':
 try:main()
 except Exception:
  # Journal/config and credentials stay private; never print traceback or user data.
  print('beta probe operation refused or failed; retain private journal for review',file=sys.stderr);raise SystemExit(1)
