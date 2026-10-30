#!/usr/bin/env python3
"""Guarded profile26 code transition with root-renewal pins reconciled under the hosting lock."""
import fcntl,hashlib,json,os,pathlib,stat,subprocess,tempfile,time
P=pathlib.Path;cfg=P('/etc/codi-connected/ksu/managed.json');unit=P('/etc/systemd/system/codi-ksu-live-root-renew.service');lock=P('/home/dflanag3/webhost-sites/.controller.lock');oldcfg='cb47b2724af5f8b55d3fccfed7e0870d7fa2bbb9b858afe8276a27388765e7ef';oldmanifest='894b758887f3b426944e668c81e089377549011856a2a1452d78d13167ca6893';newmanifest='7f6b827263bfb36b530e1e26c46b4bd4f274e6ef8faa8a995a551faf8d0092aa';candidate=P('/srv/codi-connected/releases/native26-network-512-r1');python=P('/srv/codi-connected/venvs/517179c/bin/python');digest=lambda b:hashlib.sha256(b).hexdigest()
def run(args,timeout=180):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,timeout=timeout).stdout
assert os.geteuid()==0 and lock.is_file() and not lock.is_symlink() and digest((candidate/'connected-release.json').read_bytes())==newmanifest
with lock.open('r+') as lf:
 fcntl.flock(lf,fcntl.LOCK_EX|fcntl.LOCK_NB)
 before=cfg.read_bytes();current=json.loads(before);assert digest(before)==oldcfg and current['manifestSHA256']==oldmanifest and current['release']=='/srv/codi-connected/releases/native26-system-channel-r2' and current['python']==str(python)
 assert not (cfg.parent/'maintenance.json').exists();assert run(['systemctl','is-active','codi-ksu-live-root-renew.timer']).strip()=='active'
 active=subprocess.run(['systemctl','is-active','--quiet','codi-ksu-live-root-renew.service']);assert active.returncode!=0
 original=unit.read_bytes();assert original.count(oldcfg.encode())==1 and original.count(oldmanifest.encode())==1
 backup=P('/var/backups/codi-renew-before-network-512.service');assert not backup.exists();fd=os.open(backup,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'wb') as f:f.write(original);f.flush();os.fsync(f.fileno())
 result=None;error=None
 try:
  proc=subprocess.run([str(python),'-I','-B',str(candidate/'scripts/manage-services.py'),'upgrade','--config',str(cfg),'--release',str(candidate),'--python',str(python)],capture_output=True,text=True,timeout=240)
  if proc.returncode:raise RuntimeError('Managed upgrade failed: '+proc.stderr[-3000:]+' '+proc.stdout[-3000:])
  result=json.loads(proc.stdout);assert result['status']=='upgraded' and set(result['activeRoles'])=={'issuer','steward','guest'}
 except Exception as e:error=repr(e)
 finally:
  raw=cfg.read_bytes();after=json.loads(raw);assert after['manifestSHA256'] in (oldmanifest,newmanifest) and (after['release'],after['manifestSHA256']) in ((current['release'],oldmanifest),(str(candidate),newmanifest));assert {k:v for k,v in after.items() if k not in ('release','manifestSHA256')}=={k:v for k,v in current.items() if k not in ('release','manifestSHA256')}
  replacement=original.replace(oldcfg.encode(),digest(raw).encode()).replace(oldmanifest.encode(),after['manifestSHA256'].encode())
  with tempfile.TemporaryDirectory(prefix='.codi-peer-renew-',dir=unit.parent) as directory:
   path=P(directory)/unit.name
   with path.open('wb') as f:f.write(replacement);f.flush();os.fsync(f.fileno())
   path.chmod(0o644);run(['systemd-analyze','verify',path]);os.replace(path,unit);run(['systemctl','daemon-reload'])
 if error:raise RuntimeError(error)
 assert after['manifestSHA256']==newmanifest and not (cfg.parent/'maintenance.json').exists()
 report={'status':'PASS','action':'upgrade','result':result,'release':after['release'],'manifestSHA256':newmanifest,'configSHA256':digest(raw),'renewalBackup':str(backup),'at':int(time.time())}
 receipt=P('/srv/codi-connected/network-512-activation-result.json');assert not receipt.exists();fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(report))
