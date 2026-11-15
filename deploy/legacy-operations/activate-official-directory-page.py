#!/usr/bin/env python3
"""Guarded official service replacement; restore old unit if readiness fails."""
import fcntl,hashlib,json,os,pathlib,subprocess,tempfile,time,urllib.request
P=pathlib.Path;unit=P('/etc/systemd/system/codi-official.service');lock=P('/home/dflanag3/webhost-sites/.controller.lock');package=P('/srv/codi-connected/official-services/chat-directory-page-r1');old='/srv/codi-connected/official-services/chat-sparse-cache-r1';oldhash='49af83f34d2de2ae9b6dc5f393f7b4616e5b8251ab56609586d90a653b6d5f15';pin='33e6e30bc4c374f05938ba542ba36c4ff6d39c9d3529461176a36fa93b97b0fd';sha=lambda b:hashlib.sha256(b).hexdigest()
def run(args):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,timeout=90).stdout
def write(path,raw):
 fd,name=tempfile.mkstemp(prefix='.codi-directory-unit-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o644);f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)
assert os.geteuid()==0 and sha((package/'official-service.json').read_bytes())==pin
with lock.open('r+') as held:
 fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);original=unit.read_bytes();assert sha(original)==oldhash and run(['systemctl','is-active','codi-official.service']).strip()=='active'
 backup=P('/var/backups/codi-official-before-directory-page-r1.service');fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(original);f.flush();os.fsync(f.fileno())
 text=original.decode();assert text.count(old)==2;updated=text.replace(old,str(package)).encode()
 try:
  with tempfile.TemporaryDirectory(prefix='.official-directory-',dir=unit.parent) as tmp:
   candidate=P(tmp)/unit.name;candidate.write_bytes(updated);run(['systemd-analyze','verify',candidate])
  write(unit,updated);run(['systemctl','daemon-reload']);run(['systemctl','restart','codi-official.service']);deadline=time.monotonic()+25
  while True:
   try:
    req=urllib.request.Request('http://127.0.0.1:8145/official-directory?after=&limit=32',headers={'Host':'ksu.codes'})
    with urllib.request.urlopen(req,timeout=3) as response:value=json.load(response)
    labels={x['label'] for x in value['items']};assert {'General chess chat','SYSTEM'}<=labels;break
   except Exception:
    if time.monotonic()>=deadline:raise
    time.sleep(.3)
  assert run(['systemctl','is-active','codi-official.service']).strip()=='active'
 except BaseException:
  write(unit,original);run(['systemctl','daemon-reload']);run(['systemctl','restart','codi-official.service']);raise
 result={'status':'PASS','manifestSHA256':pin,'unitSHA256':sha(updated),'backup':str(backup),'labels':sorted(labels),'time':int(time.time())};receipt=P('/srv/codi-connected/official-directory-page-r1-activation-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(result))
