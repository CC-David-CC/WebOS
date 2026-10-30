import fcntl,hashlib,json,os,shutil,stat,sys,time
from pathlib import Path
ROOT=Path('/srv/codi-connected/releases');CFG=Path('/etc/codi-connected/ksu/managed.json');LOCK=Path('/home/dflanag3/webhost-sites/.controller.lock')
KEEP={'native26-network-512-r1':'7f6b827263bfb36b530e1e26c46b4bd4f274e6ef8faa8a995a551faf8d0092aa','native26-system-channel-r2':'894b758887f3b426944e668c81e089377549011856a2a1452d78d13167ca6893'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def verify(folder):
 assert folder.parent==ROOT and folder.is_dir() and not folder.is_symlink() and folder.stat().st_uid==0
 m=folder/'connected-release.json';raw=json.loads(m.read_bytes());records=raw['files'];actual={str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()};assert actual==set(records)|{'connected-release.json'}
 for name,rec in records.items():
  path=folder/name;info=path.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_nlink==1 and info.st_size==rec['bytes'] and sha(path)==rec['sha256']
 return sha(m)
def referenced():
 result=set();prefix=str(ROOT)+'/'
 def mark(text):
  for part in text.split(prefix)[1:]:result.add(part.split('/',1)[0].split('\x00',1)[0].split(' ',1)[0].split('\n',1)[0].strip('"\''))
 for proc in Path('/proc').glob('[0-9]*'):
  try:
   mark((proc/'cmdline').read_bytes().decode(errors='ignore'))
   for link in [proc/'cwd',proc/'exe',*(proc/'fd').iterdir()]:
    try:mark(os.readlink(link))
    except OSError:pass
  except OSError:pass
 for base in [Path('/etc/systemd/system'),Path('/etc/codi-connected')]:
  for file in base.rglob('*'):
   try:
    if file.is_file() and not file.is_symlink() and file.stat().st_size<=2*1024*1024:mark(file.read_bytes().decode(errors='ignore'))
   except (OSError,PermissionError):pass
 return result
assert os.geteuid()==0 and ROOT.is_dir() and not ROOT.is_symlink()
with LOCK.open('r+') as f:
 fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 cfgraw=CFG.read_bytes();cfg=json.loads(cfgraw);assert cfg['release']==str(ROOT/'native26-network-512-r1') and cfg['manifestSHA256']==KEEP['native26-network-512-r1']
 assert not any((CFG.parent/n).exists() for n in ('maintenance.json','native-rollout.json','site-cutover.json'))
 for name,pin in KEEP.items():assert verify(ROOT/name)==pin
 active=referenced();removed=[];skipped=[];apply='--apply' in sys.argv
 for folder in sorted(ROOT.iterdir()):
  if not folder.name.startswith('native26-') or folder.name in KEEP or not folder.is_dir() or folder.is_symlink():continue
  if folder.name in active:skipped.append({'name':folder.name,'reason':'referenced'});continue
  try:
   pin=verify(folder);size=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
  except Exception as e:skipped.append({'name':folder.name,'reason':type(e).__name__});continue
  if apply:
   assert folder.name not in referenced();assert CFG.read_bytes()==cfgraw;shutil.rmtree(folder)
  removed.append({'name':folder.name,'manifest':pin,'bytes':size})
 assert CFG.read_bytes()==cfgraw
 result={'status':'PASS','applied':apply,'retained':KEEP,'removed' if apply else 'candidates':removed,'skipped':skipped,'bytes':sum(v['bytes'] for v in removed)}
 if apply:
  out=Path('/srv/codi-connected')/('native26-cleanup-'+str(time.time_ns())+'.json');fd=os.open(out,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as o:json.dump(result,o,indent=2);o.write('\n')
  result['receipt']=str(out)
 print(json.dumps(result))
