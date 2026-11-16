#!/usr/bin/env python3
"""Read-only beta Files preflight; no staging, installation or service mutation."""
import fcntl,grp,hashlib,json,os,pwd,socket,stat,subprocess,sys
from pathlib import Path
CANDIDATE='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
NATIVE='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21'
GUARDED_WEBCTL='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'
PINS={'/etc/systemd/system/codi-beta-issuer.service':'e6b8279c32a89f38ee4a3b2ba6c27777413c13b1b98611e78ff9b0d52dca1244','/etc/systemd/system/codi-beta-frontend.service':'4b909882dfd879235e10bf3cbb004bd3e61db1786cfd99e122b7abbd39be5f78','/etc/systemd/system/codi-beta-gateway.service':'f7fe40291ed89df101e511673b201b5606ba526333b1f55743fdec8ed069b47e','/home/dflanag3/webhost-sites/sites.toml':'9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(path,limit=8*1024*1024):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_nlink!=1 or a.st_size>limit:raise ValueError('unsafe regular file')
  chunks=[];remaining=a.st_size
  while remaining:
   b=os.read(fd,min(1048576,remaining))
   if not b:raise ValueError('short file read')
   chunks.append(b);remaining-=len(b)
  z=os.fstat(fd)
  if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('file changed')
  return b''.join(chunks)
 finally:os.close(fd)
def digest_file(path,limit=256*1024*1024):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_nlink!=1 or a.st_size>limit:raise ValueError('unsafe regular file')
  h=hashlib.sha256();size=0
  while True:
   chunk=os.read(fd,1048576)
   if not chunk:break
   size+=len(chunk)
   if size>limit:raise ValueError('oversized file')
   h.update(chunk)
  z=os.fstat(fd)
  if size!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns):raise ValueError('file changed')
  return size,h.hexdigest()
 finally:os.close(fd)
def protected_ancestors(path,uid=0):
 # David and root are trusted administrators. Group/ACL access by anyone else
 # remains a blocker; this is a point-in-time check under the host lock.
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('absolute protected path required')
 admin=pwd.getpwnam('dflanag3');trusted={0,admin.pw_uid}
 def group_trusted(gid):
  group=grp.getgrgid(gid);members={u.pw_uid for u in pwd.getpwall() if u.pw_gid==gid}
  members.update(pwd.getpwnam(name).pw_uid for name in group.gr_mem)
  return members<=trusted
 for p in (path,*path.parents):
  st=p.lstat()
  if not stat.S_ISDIR(st.st_mode) or st.st_uid not in trusted or st.st_mode&0o002 or (st.st_mode&0o020 and not group_trusted(st.st_gid)):raise ValueError('untrusted writable directory: '+str(p))
  output=subprocess.run(['/usr/bin/getfacl','-cp',str(p)],check=True,capture_output=True,text=True,timeout=10).stdout
  for line in output.splitlines():
   part=line.split('#',1)[0].strip().split(':')
   if part and part[0]=='default':part=part[1:]
   if len(part)!=3 or 'w' not in part[2]:continue
   kind,name,_=part
   if kind=='other':raise ValueError('untrusted writable ACL: '+str(p))
   if kind=='user' and name and pwd.getpwnam(name).pw_uid not in trusted:raise ValueError('untrusted writable ACL: '+str(p))
   if kind=='group':
    gid=grp.getgrnam(name).gr_gid if name else st.st_gid
    if not group_trusted(gid):raise ValueError('untrusted writable ACL: '+str(p))

def tree(root,manifest,pin,uid=0):
 root=Path(root);protected_ancestors(root,uid);raw=read(root/manifest)
 if sha(raw)!=pin:raise ValueError('manifest hash mismatch')
 records=json.loads(raw)['files'];found=set()
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name;st=p.lstat()
   if st.st_uid!=uid or st.st_mode&0o022 or not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):raise ValueError('unsafe artifact entry')
  for name in files:
   p=Path(parent)/name;rel=p.relative_to(root).as_posix();found.add(rel)
   if rel==manifest:continue
   record=records.get(rel);size,digest=digest_file(p)
   if record is None or size!=record['bytes'] or digest!=record['sha256']:raise ValueError('artifact digest mismatch: '+rel)
 if found!=set(records)|{manifest}:raise ValueError('artifact inventory mismatch')
 return {'manifest':pin,'files':len(records)}
def status(name):
 p=subprocess.run(['/usr/bin/systemctl','show',name,'-p','ActiveState','-p','FragmentPath','-p','NeedDaemonReload'],check=True,capture_output=True,text=True,timeout=10)
 x=dict(line.split('=',1) for line in p.stdout.splitlines())
 if x.get('ActiveState')!='active' or x.get('NeedDaemonReload')!='no' or x.get('FragmentPath')!='/etc/systemd/system/'+name:raise ValueError('unexpected beta service state')
 return 'active'
def _inspect_host_locked():
 result={}
 def check(name,fn):
  try:result[name]={'ok':True,'value':fn()}
  except (OSError,ValueError,KeyError,subprocess.SubprocessError) as error:result[name]={'ok':False,'reason':str(error)}
 for p,pin in PINS.items():check('pin:'+p,lambda p=p,pin=pin: 'match' if sha(read(p))==pin else (_ for _ in ()).throw(ValueError('pin mismatch')))
 check('guarded-webctl',lambda:'match' if sha(read('/home/dflanag3/webhost-sites/ops/webctl.py'))==GUARDED_WEBCTL else (_ for _ in ()).throw(ValueError('guarded controller not installed')))
 check('hosting-source-custody',lambda:protected_ancestors('/home/dflanag3/webhost-sites/ops'))
 for name in ('codi-beta-issuer.service','codi-beta-frontend.service','codi-beta-gateway.service'):check('service:'+name,lambda name=name:status(name))
 def space():
  x=os.statvfs('/var/lib/codi-user-files/beta');free=x.f_bavail*x.f_frsize;reserve=5*1024**3;margin=256*1024**2
  if free<reserve:raise ValueError('account filesystem below required 5 GiB reserve: '+str(free))
  observed_stage=120774656
  return {'available':free,'requiredReserve':reserve,'aboveReserve':free-reserve,'observedNativePublicStageBytes':observed_stage,'observedStageFits':free-reserve>=observed_stage,'proposedWorkingMargin':margin,'proposedMarginMet':free-reserve>=margin,'fullWorkingBytes':'not yet measured'}
 check('account-space',space)
 check('candidate-artifact',lambda:tree('/srv/data/codi-beta-opfs/'+CANDIDATE,'manifest.json',CANDIDATE))
 check('native-artifact',lambda:tree('/srv/data/codi-beta-native/'+NATIVE,'connected-release.json',NATIVE))
 result['transition-operator']={'ok':False,'reason':'Protected apply/recover, signed health, retained-route checks and old-entrypoint enforcement are not assembled or installed'}
 return result
def inspect_host():
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('read-only root preflight on box-webhost only')
 path=Path('/home/dflanag3/webhost-sites/.controller.lock');fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 def check():
  a=os.fstat(fd);b=path.lstat()
  if not stat.S_ISREG(a.st_mode) or a.st_uid!=0 or a.st_mode&0o022 or a.st_nlink!=1 or (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('unsafe or replaced hosting lock')
 try:
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);check();result=_inspect_host_locked();check();return result
 finally:os.close(fd)
if __name__=='__main__':
 if sys.argv[1:]!=['plan']:raise SystemExit('Only read-only plan is supported')
 result=inspect_host();print(json.dumps({'action':'plan','checks':result,'ready':all(v['ok'] for v in result.values()),'runtimeChanged':False},sort_keys=True));sys.exit(0 if all(v['ok'] for v in result.values()) else 1)
