"""Research-only pinned main guard/successor install primitive.

No CLI, production paths or implicit process fencing. The protected caller must
hold the existing host lock and independently enforce a trusted administrative
maintenance freeze covering all supported legacy invocation paths. It supplies
concrete custody, quiescence/timer and successor verification callbacks.
"""
import ctypes,hashlib,json,os,stat,tempfile
from pathlib import Path
OLD='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'
NEW='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783'
INV='bc9f939a9db8849fb7d580e5a71d5c52728b127b74c3bca1ee811b41fdd1f754'
FLOOR={'version':1,'baseline':'e7a5e64272c1d6b78de73c46f5105b9963e2272f40450e39e86a038293d9fb3b','candidate':'3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'}
def sha(b):return hashlib.sha256(b).hexdigest()

def install(*,source,destination,guard,target,journal,floor,primitives,verify_successor,check_lock,check_fence,check_custody,phase=lambda _:None):
 """Idempotent forward-only install; must be invoked under one held lock."""
 if not all(callable(x) for x in (verify_successor,check_lock,check_fence,check_custody,phase)):raise ValueError('Missing protected install controls')
 source,destination,guard,target,journal,floor=map(Path,(source,destination,guard,target,journal,floor))
 def checks():
  check_lock();check_fence();check_custody();primitives.root_path(floor);v=floor.lstat()
  if stat.S_IMODE(v.st_mode)!=0o600 or json.loads(primitives.read_file(floor,4096))!=FLOOR:raise ValueError('Original floor changed')
  for name in ('main-restriction-journal.json','opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json','beta-hosting-journal.json','files-asset-transition.json'):
   if journal.parent/name==journal:continue
   try:(journal.parent/name).lstat()
   except FileNotFoundError:continue
   raise ValueError('Conflicting hosting journal: '+name)
 checks();primitives.root_path(source,True);primitives.root_path(destination.parent,True);primitives.root_path(guard);primitives.root_path(journal.parent,True)
 if stat.S_IMODE(journal.parent.stat().st_mode)!=0o700:raise ValueError('Unsafe private journal directory')
 verify_successor(source,primitives.read_file,check_lock);guard_bytes=primitives.read_file(guard)
 if sha(guard_bytes)!=NEW:raise ValueError('Guard source pin mismatch')
 def target_digest():
  v=target.lstat();primitives.no_acl(target)
  if not stat.S_ISREG(v.st_mode) or v.st_nlink!=1 or (v.st_uid,v.st_gid,stat.S_IMODE(v.st_mode))!=(1000,1000,0o644):raise ValueError('Unexpected controller custody')
  return sha(primitives.read_file(target,root_owned=False))
 actual=target_digest();expected={'version':1,'old':OLD,'new':NEW,'inventory':INV,'target':str(target),'destination':str(destination),'uid':1000,'gid':1000,'mode':0o644}
 try:journal.lstat()
 except FileNotFoundError:pending=False
 else:
  pending=True;primitives.root_path(journal)
  if stat.S_IMODE(journal.stat().st_mode)!=0o600 or json.loads(primitives.read_file(journal,4096))!=expected:raise ValueError('Install journal mismatch')
 if actual not in (OLD,NEW) or (not pending and actual==NEW and not destination.exists()):raise ValueError('Unexpected controller state')
 try:destination.lstat()
 except FileNotFoundError:
  tmp=Path(tempfile.mkdtemp(prefix='.main-successor-stage-',dir=destination.parent))
  # Each verified input is copied into an unselected root-owned generation.
  # Killed staging directories are not selected and require separate cleanup.
  for base,dirs,files in os.walk(source,followlinks=False):
   for name in dirs:
    out=tmp/(Path(base)/name).relative_to(source);out.mkdir(mode=0o755)
   for name in files:
    src=Path(base)/name;out=tmp/src.relative_to(source);data=primitives.read_file(src)
    fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  for base,dirs,files in os.walk(tmp,topdown=False):primitives.syncdir(base)
  checks();verify_successor(tmp,primitives.read_file,check_lock);phase('staged')
  libc=ctypes.CDLL(None,use_errno=True)
  if libc.renameat2(-100,os.fsencode(tmp),-100,os.fsencode(destination),1):raise OSError(ctypes.get_errno(),'successor no-replace publication failed')
  primitives.syncdir(destination.parent);phase('published')
 verify_successor(destination,primitives.read_file,check_lock);checks()
 if target_digest()!=actual:raise ValueError('Controller changed during staging')
 if not pending:
  if actual==NEW:return 'already-installed'
  if actual!=OLD:raise ValueError('Unexpected controller baseline')
  primitives.atomic(journal,(json.dumps(expected,sort_keys=True)+'\n').encode());phase('journaled')
 if actual not in (OLD,NEW):raise ValueError('Controller drift during install')
 checks()
 if actual==OLD:primitives.atomic(target,guard_bytes,0o644,1000,1000);phase('guard-replaced')
 if sha(primitives.read_file(target,root_owned=False))!=NEW:raise ValueError('Guard verification failed')
 checks();verify_successor(destination,primitives.read_file,check_lock);phase('verified')
 journal.unlink();primitives.syncdir(journal.parent);phase('complete')
 return 'installed'
