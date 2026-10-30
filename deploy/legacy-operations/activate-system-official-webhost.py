#!/usr/bin/env python3
"""Switch the official service to the verified SYSTEM-capable package."""
import fcntl,hashlib,json,os,subprocess,tempfile,time,urllib.request
from pathlib import Path
unit=Path('/etc/systemd/system/codi-official.service');candidate=Path('/srv/codi-connected/official-services/system-channel-r2');lock=Path('/home/dflanag3/webhost-sites/.controller.lock');backup=Path('/var/backups/codi-official-before-system.service');old='/srv/codi-connected/official-service-test';new=str(candidate)
pin='04fd3157bf1fbd094a4324a9654868a76179879cb0d0a6cc4a12988946e18d4b';oldunit='1d530f62f207c6d87a0c22cc56a50de9ce11d012c65acacabdb9e77c0f88f3cf'
def run(args):return subprocess.run(args,check=True,capture_output=True,text=True,timeout=90).stdout
assert os.geteuid()==0 and hashlib.sha256((candidate/'official-service.json').read_bytes()).hexdigest()==pin
with lock.open('r+') as f:
 fcntl.flock(f,fcntl.LOCK_EX);original=unit.read_bytes();assert hashlib.sha256(original).hexdigest()==oldunit and original.count(old.encode())==2 and not backup.exists();assert run(['systemctl','is-active','codi-official.service']).strip()=='active'
 fd=os.open(backup,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'wb') as out:out.write(original);out.flush();os.fsync(out.fileno())
 def install(content):
  with tempfile.TemporaryDirectory(prefix='.official-system-',dir=unit.parent) as folder:
   temp=Path(folder)/unit.name;temp.write_bytes(content);temp.chmod(0o644);run(['systemd-analyze','verify',str(temp)]);os.replace(temp,unit)
  run(['systemctl','daemon-reload']);run(['systemctl','restart','codi-official.service'])
 try:
  install(original.replace(old.encode(),new.encode()));deadline=time.monotonic()+20
  while True:
   try:
    req=urllib.request.Request('http://127.0.0.1:8145/internal/official-health',headers={'Host':'ksu.codes'})
    with urllib.request.urlopen(req,timeout=2) as response:health=json.load(response)
    assert health['version']=='codi-official-health/1';break
   except Exception:
    if time.monotonic()>=deadline:raise
    time.sleep(.25)
  assert run(['systemctl','is-active','codi-official.service']).strip()=='active'
 except BaseException:
  install(original);raise
 result={'status':'PASS','package':str(candidate),'manifestSHA256':pin,'unitSHA256':hashlib.sha256(unit.read_bytes()).hexdigest(),'backup':str(backup),'pid':run(['systemctl','show','codi-official.service','-p','MainPID','--value']).strip()}
 receipt=Path('/srv/codi-connected/system-official-activation-result.json');assert not receipt.exists();fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as out:json.dump(result,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
print(json.dumps(result))
