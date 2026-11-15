#!/usr/bin/env python3
"""Upgrade the official service after provisioning review-state tables."""
import fcntl,hashlib,json,os,pathlib,subprocess,tempfile,time,urllib.request
P=pathlib.Path;unit=P('/etc/systemd/system/codi-official.service');lock=P('/home/dflanag3/webhost-sites/.controller.lock');package=P('/srv/codi-connected/official-services/chat-reader-cache-r2');venv=P('/srv/codi-connected/venvs/official-chess-r1');state=P('/var/lib/codi-official/state');keys=state/'validator-keys';oldhash='64efa18301e2eaadba3161aadcef4e533b2ed8c41770dce99fbfb6b9b9d273a6';manifest='79defacf1a16e74d77ab65ab461b2ead897676b5e3a0e99d87587eda7c42fd01';sha=lambda raw:hashlib.sha256(raw).hexdigest()
def run(args,timeout=90):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,timeout=timeout).stdout
def write(path,raw):
 fd,name=tempfile.mkstemp(prefix='.official-ban-review-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o644);f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 finally:
  if os.path.exists(name):os.unlink(name)
if os.geteuid()!=0 or not lock.is_file() or lock.is_symlink() or sha((package/'official-service.json').read_bytes())!=manifest:raise ValueError('Official service pin differs')
with lock.open('r+') as held:
 fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);original=unit.read_bytes()
 if sha(original)!=oldhash or run(['systemctl','is-active','codi-official.service']).strip()!='active':raise ValueError('Official service changed')
 channel=json.loads(run(['/usr/sbin/runuser','-u','codi-official','--',venv/'bin/python','-I','-B',package/'scripts/provision-official-chat.py','--database',state/'official.sqlite','--validator-key-dir',keys]))['channel']
 if channel!='J3iEwhBk3DnYoa_lGb4gVw3kYZe0qYYOtAoGvvN1AR4':raise ValueError('Official channel differs')
 backup=P('/var/backups/codi-official-before-reader-cache-r2.service');fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(original);f.flush();os.fsync(f.fileno())
 updated=original.decode();old='/srv/codi-connected/official-services/chat-reader-cache-r1';assert updated.count(old)==2;updated=updated.replace(old,str(package))
 try:
  with tempfile.TemporaryDirectory(prefix='.official-ban-units-',dir=unit.parent) as tmp:
   candidate=P(tmp)/unit.name;candidate.write_text(updated);run(['systemd-analyze','verify',candidate])
  write(unit,updated.encode());run(['systemctl','daemon-reload']);run(['systemctl','restart','codi-official.service']);deadline=time.monotonic()+20
  while True:
   try:
    req=urllib.request.Request('http://127.0.0.1:8145/official-channel?channel=featured-game',headers={'Host':'ksu.codes'})
    with urllib.request.urlopen(req,timeout=2) as response:value=json.load(response)
    if value.get('version')=='codi-featured-game/1':break
   except Exception:
    if time.monotonic()>=deadline:raise
    time.sleep(.25)
  if run(['systemctl','is-active','codi-official.service']).strip()!='active':raise ValueError('Official service did not start')
 except BaseException:
  write(unit,original);run(['systemctl','daemon-reload']);run(['systemctl','restart','codi-official.service']);raise
 report={'status':'PASS','packageSHA256':manifest,'unitBackup':str(backup),'channel':channel,'time':int(time.time())};receipt=P('/srv/codi-connected/official-reader-cache-r2-activation-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps(report))
