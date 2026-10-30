#!/usr/bin/env python3
"""Validate staged root hosting and mount plans on the host without activation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import time

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import copy,fcntl,hashlib,json,os,pathlib,pwd,sqlite3,stat,subprocess,sys,tempfile,types
P=pathlib.Path;v=json.load(sys.stdin);base=P('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';cfg=P('/etc/codi-connected/ksu/managed.json')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def read(path,protected=False):
 p=P(path)
 for q in [p,*p.parents]:
  s=q.lstat();assert not q.is_symlink()
  if protected:assert s.st_uid==0 and not s.st_mode&0o022
 with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
  s=os.fstat(f.fileno());assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=134217728
  b=f.read(s.st_size+1);assert len(b)==s.st_size;return b
def run(args,timeout=60):return subprocess.check_output(list(map(str,args)),text=True,timeout=timeout).strip()
def git(*args):return run(['runuser','-u','dflanag3','--','git','-C',repo,*args])
def role_pids(c):return {r:int(run(['systemctl','show',c['instance']+'-'+r+'.service','-p','MainPID','--value'])) for r in ['issuer','steward','guest']}
assert os.geteuid()==0 and __import__('socket').gethostname()=='box-webhost'
with (base/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert git('rev-parse','HEAD')==v['commit'] and not git('status','--porcelain')
 before=read(cfg,True);assert sha(before)=='39d88cd8fd56d223d88efaa8291cbf0693f0105660f937e9c022765b136d2c51';c=json.loads(before);assert c['basePath']=='/hidden'
 assert not any((cfg.parent/n).exists() for n in ['native-rollout.json','maintenance.json','guest-signin-migration.json','site-cutover.json'])
 pins={'common.py':'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4','sites.toml':'c946c1e71461a49692332f4287633f64ab6e4bebb97283a4263d53bf98f10715','Caddyfile':'694518124e11bd918471cfc4b10ad3164d557bba0d003cc1de01fe7ce214dbad'}
 files={'common.py':base/'ops/common.py','sites.toml':base/'sites.toml','Caddyfile':P('/etc/caddy/Caddyfile')}
 originals={n:read(p) for n,p in files.items()};assert {n:sha(b) for n,b in originals.items()}==pins
 candidate=repo/'tools/codiserver/root-mount-r3/hosting-candidate';metadata=json.loads(read(candidate/'hosting-candidate.json'))
 for n,r in metadata['files'].items():
  assert P(n).name==n;b=read(candidate/n);assert r=={'bytes':len(b),'sha256':sha(b)}
 assert metadata['files']['common.py']['sha256']=='c3181a47ed0b9489bf2b6093ce2f54e62bab089560eb57eec86c6f0ec0c290e7'
 assert metadata['files']['sites.toml']['sha256']=='f583f6f43f5b03d1e48afd71567f0c508373a7073c1bfc5add1dd75a591bee12'
 assert metadata['files']['Caddyfile.production']['sha256']=='4cf23397bd3d1885e8f2c386072633c9ffec36459811753bce68866b50252bb5'
 sys.path.insert(0,str(base/'ops'));import common
 for n in ['hardware_hosting.py','cardboard_hosting.py']:assert read(base/'ops'/n)==read(candidate/n)
 reviewed=types.ModuleType('root_cutover_reviewed');reviewed.__file__=str(base/'ops/common.py');exec(compile(read(candidate/'common.py'),reviewed.__file__,'exec'),reviewed.__dict__)
 old=common.tomllib.loads(originals['sites.toml'].decode());proposed=reviewed.tomllib.loads(read(candidate/'sites.toml').decode());reviewed.validate(proposed)
 expected=copy.deepcopy(old);next(s for s in expected['sites'] if s['domain']=='ksu.codes')['codi_mount']='';assert proposed==expected
 assert reviewed.caddy(old,'production').encode()==originals['Caddyfile']
 assert all(common.unit(s)==reviewed.unit(s) for s in old['sites'])
 validated=[];caddy_gid=pwd.getpwnam('caddy').pw_gid
 for mode in ['prepare','production']:
  raw=reviewed.caddy(proposed,mode).encode();assert raw==read(candidate/('Caddyfile.'+mode))
  fd,name=tempfile.mkstemp(prefix='.root-cutover-validation-',dir='/etc/caddy')
  try:
   with os.fdopen(fd,'wb') as f:os.fchmod(f.fileno(),0o640);os.fchown(f.fileno(),0,caddy_gid);f.write(raw);f.flush();os.fsync(f.fileno())
   result=subprocess.run(['runuser','-u','caddy','--','/usr/bin/caddy','validate','--config',name,'--adapter','caddyfile'],capture_output=True,timeout=60)
   if result.returncode:raise ValueError('Actual Caddy '+mode+' validation failed: '+result.stderr.decode(errors='replace')[-3000:])
   validated.append({'mode':mode,'sha256':sha(raw),'validatedAs':'caddy','logSHA256':sha(result.stdout+result.stderr)})
  finally:P(name).unlink()
 native=P('/srv/codi-connected/releases/native16-c23b1b73df68ffb2');assert sha(read(native/'connected-release.json',True))==v['nativeSHA256']
 manifest=json.loads(read(native/'connected-release.json',True))
 for n,r in manifest['files'].items():
  assert not P(n).is_absolute() and '..' not in P(n).parts;b=read(native/n,True);assert r=={'bytes':len(b),'sha256':sha(b)}
 operator=P('/srv/codi-connected/mount-operators')/v['operatorSHA256'];raw=read(operator/'mount-operator.json',True);assert sha(raw)==v['operatorSHA256'];m=json.loads(raw)
 for n,r in m['files'].items():
  assert not P(n).is_absolute() and '..' not in P(n).parts;b=read(operator/n,True);assert r=={'bytes':len(b),'sha256':sha(b)}
 def authority_row():
  p=P(c['stateRoot'])/'operator/root/authority.sqlite3'
  with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:revision,token=db.execute('SELECT revision,token FROM authority WHERE id=1').fetchone()
  return revision,sha(token.encode())
 prior_pids=role_pids(c);assert all(prior_pids.values());prior_authority=authority_row();fence=read(cfg.parent/'recovery-fence.json',True)
 args=[c['python'],'-I','-B',str(operator/'scripts/migrate-desktop-mount.py'),'plan','--config',str(cfg),'--native-release',str(native),'--native-manifest-sha256',v['nativeSHA256'],'--base-path','','--seconds','86400']
 result=json.loads(run(args,150));assert result['status']=='mount-prepared-readonly' and result['beforeBasePath']=='/hidden' and result['basePath']=='' and not result['servicesChanged'] and not result['dataRestored']
 assert read(cfg)==before and role_pids(c)==prior_pids and authority_row()==prior_authority and read(cfg.parent/'recovery-fence.json')==fence
 assert {n:read(p) for n,p in files.items()}==originals and not (cfg.parent/'maintenance.json').exists()
 print(json.dumps({'status':'PASS','sourceCommit':v['commit'],'caddyValidation':validated,'mountPlan':result,'nativePIDsUnchanged':prior_pids,'authorityRevisionUnchanged':prior_authority[0],'configHostingAndFenceUnchanged':True,'privateHardwareImportKeptOnServer':True,'servicesRestarted':False,'activated':False}))
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    assert re.fullmatch('[0-9a-f]{40}', args.commit)
    payload = {'commit': args.commit, 'nativeSHA256': 'c23b1b73df68ffb25da810a7db73074d09297f0ccc06c459e8bc9c0430ca30c1',
               'operatorSHA256': '6e4ebb33e945ea8712dd72c56f5a9928a955af5b340ceaff6ef0221112ebe0dc'}
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', 'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(REMOTE)],
                           input=json.dumps(payload), capture_output=True, text=True, timeout=240)
    if child.returncode:
        raise ValueError(child.stderr[-5000:] or child.stdout[-5000:])
    result = json.loads(child.stdout)
    result['sourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    path = ROOT/'.build/checks/root-cutover-validation-result.json'
    if path.exists():
        path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
    path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
