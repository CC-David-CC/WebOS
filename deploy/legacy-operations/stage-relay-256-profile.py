#!/usr/bin/env python3
"""Manifest-pinned bounded TURN profile migration with certificate-job rollback/recovery."""
import argparse,hashlib,json,re,shlex,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,json,os,shutil,stat,subprocess,sys,tempfile,time
from pathlib import Path
v=json.load(sys.stdin);assert os.geteuid()==0
base=Path('/home/dflanag3/webhost-sites');repo=base/'sites/ksu.codes';root=Path('/srv/codi-relay');key='b7008089d7368ac0627dc7850c33407fe3d7183c5051c201fdb80a8343fd8d51'
old=root/'operators/3d2f88f35109d7b052fef3a943776bf10d2cdbd198294bc1778dd1210f6ec162';new=root/'operators'/key
source=Path('/tmp/codi-relay-256-r1');directory=Path('/etc/codi-relay/ksu');outer=root/'ksu-bandwidth-migration.json';python=Path('/srv/codi-connected/venvs/517179c/bin/python')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args,check=True):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=check,timeout=90)
def protected(p):
 for x in [p,*p.parents]:
  s=x.lstat();assert not x.is_symlink() and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
def verify(p,pin,owned):
 raw=(p/'relay-operator.json').read_bytes();assert sha(raw)==pin;manifest=json.loads(raw)
 assert manifest['version']=='codi-relay-operator/2' and set(manifest)=={'version','files'} and set(manifest['files'])=={'relay_service/__init__.py','relay_service/manager.py','relay_service/certificates.py','scripts/manage-relay.py','requirements.lock'}
 assert {str(x.relative_to(p)) for x in p.rglob('*') if not x.is_dir()}==set(manifest['files'])|{'relay-operator.json'}
 for x in [p,*p.rglob('*')]:
  s=x.lstat();assert not x.is_symlink() and (stat.S_ISDIR(s.st_mode) or stat.S_ISREG(s.st_mode))
  if owned:protected(x);assert stat.S_IMODE(s.st_mode)==(0o755 if x.is_dir() else 0o644)
  if x.is_file():
   assert s.st_nlink==1
   if x.name!='relay-operator.json':
    raw=x.read_bytes();assert manifest['files'][str(x.relative_to(p))]=={'bytes':len(raw),'sha256':sha(raw)}
def install():
 protected(new.parent)
 if not new.exists():
  temp=Path(tempfile.mkdtemp(prefix='.relay-operator-',dir=new.parent))
  try:
   for x in source.rglob('*'):
    dest=temp/x.relative_to(source)
    if x.is_dir():dest.mkdir(mode=0o755)
    else:
     with dest.open('wb') as f:os.fchmod(f.fileno(),0o644);f.write(x.read_bytes());f.flush();os.fsync(f.fileno())
   temp.chmod(0o755);verify(temp,key,True);temp.rename(new)
   fd=os.open(new.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
  finally:
   if temp.exists():shutil.rmtree(temp)
 verify(new,key,True)
with (base/'.controller.lock').open('rb') as hosting_lock:
 fcntl.flock(hosting_lock,fcntl.LOCK_EX)
 verify(source,key,False);verify(old,old.name,True)
 native=Path('/etc/codi-connected/ksu/managed.json');native_pin=sha(native.read_bytes())
 pins={str(p):sha(p.read_bytes()) for p in [base/'ops/common.py',base/'sites.toml',Path('/etc/caddy/Caddyfile')]}
 def stable_pids():return {n:run(['systemctl','show',n,'-p','MainPID','--value']).stdout.strip() for n in ['caddy.service','web-ksu-codes.service','codi-ksu-hidden-issuer.service','codi-ksu-hidden-steward.service','codi-ksu-hidden-guest.service','codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']}
 before_pids=stable_pids();assert all(int(p)>0 for p in before_pids.values())
 if v['action']!='recover':assert not outer.exists() and sha((directory/'managed.json').read_bytes())==v['configSHA256']
 if v['action'] in ['plan','install']:
  assert not (directory/'maintenance.json').exists()
  if v['action']=='install':install()
  result={'status':'PASS','action':v['action'],'operatorManifestSHA256':key,'runtimeChanged':False,'profileChanged':False}
 else:
  install();sys.path.insert(0,str(new));from relay_service.manager import Manager,atomic,encoded,read;from relay_service import certificates
  manager=Manager(directory);service='codi-relay-ksu-hidden-certificate-refresh.service';timer='codi-relay-ksu-hidden-certificate-refresh.timer';units=[service,timer]
  if v['action']=='recover':
   journal=json.loads(read(outer));assert set(journal)=={'version','phase','before','after','timerWasActive','unitsBefore','operatorBefore','operatorAfter'} and journal['version']=='codi-relay-profile-migration/1' and journal['phase'] in ['prepared','committed']
   assert journal['operatorAfter']==str(new) and journal['operatorBefore'] in [str(old),str(new)] and type(journal['timerWasActive']) is bool
   assert journal['before'] in ['legacy','text-32k/1','text-128/1','text-256/1'] and journal['after'] in ['legacy','text-32k/1','text-128/1','text-256/1'] and set(journal['unitsBefore'])==set(units)
   profile=journal['after'] if journal['phase']=='committed' else journal['before'];operator=(old if profile=='text-128/1' else new) if journal['phase']=='committed' else Path(journal['operatorBefore'])
  else:
   with manager.locked():
    manager.clean();c=manager.load();manager.installed(c);profile='text-128/1' if v['action']=='rollback' else 'text-256/1';prior=c.get('bandwidthProfile','legacy');prior_operator=old if prior=='text-128/1' else new
    expected=certificates.refresh_units(manager,prior_operator,python)['units']
    assert all(read(Path('/etc/systemd/system')/n,0o644)==body.encode() for n,body in expected.items())
    journal={'version':'codi-relay-profile-migration/1','phase':'prepared','before':prior,'after':profile,'timerWasActive':run(['systemctl','is-active',timer],False).stdout.strip()=='active','unitsBefore':expected,'operatorBefore':str(prior_operator),'operatorAfter':str(new)}
    atomic(outer,encoded(journal));operator=old if profile=='text-128/1' else new
  def apply_profile(target,operator_path):
   run(['systemctl','stop',timer,service])
   with manager.locked():
    if manager.journal.exists():manager.recover()
    changed=manager.bandwidth_profile(target);value=manager.load();manager.installed(value)
    rendered=certificates.refresh_units(manager,operator_path,python)['units']
    for name,body in rendered.items():atomic(Path('/etc/systemd/system')/name,body.encode(),0o644)
    run(['systemd-analyze','verify',*[Path('/etc/systemd/system')/n for n in rendered]]);run(['systemctl','daemon-reload'])
   run(['systemctl','start',service])
   if journal['timerWasActive']:run(['systemctl','start',timer])
   with manager.locked():
    value=manager.load();manager.installed(value);assert value.get('bandwidthProfile','legacy')==target
    ready=manager.ready(value);props={}
    for name in manager.names(value)[:2]:
     p=dict(row.split('=',1) for row in run(['systemctl','show',name,'-p','MainPID','-p','CapabilityBoundingSet','-p','NoNewPrivileges','-p','UnitFileState']).stdout.splitlines());pid=int(p['MainPID'])
     assert pid>0 and p['CapabilityBoundingSet']=='' and p['NoNewPrivileges']=='yes' and p['UnitFileState']=='static';info=dict(row.split(':',1) for row in (Path('/proc')/str(pid)/'status').read_text().splitlines());uids=set(map(int,info['Uid'].split()));assert len(uids)==1 and 0 not in uids and int(info['CapEff'],16)==0
     props[name]={'pid':pid,'uid':next(iter(uids)),'namespace':os.readlink('/proc/'+str(pid)+'/ns/net')}
    assert len({p['namespace'] for p in props.values()})==1 and len({p['uid'] for p in props.values()})==2 and next(iter(props.values()))['namespace']!=os.readlink('/proc/self/ns/net')
    pid=next(iter(props.values()))['pid'];assert [i['ifname'] for i in json.loads(run(['nsenter','-t',pid,'-n','ip','-j','address','show']).stdout)]==['lo']
    assert not manager.journal.exists()
   return changed,ready,props
  try:
   changed,ready,processes=apply_profile(profile,operator)
   assert stable_pids()==before_pids and all(sha(Path(p).read_bytes())==h for p,h in pins.items()) and sha(native.read_bytes())==native_pin
   if v['action']!='recover':journal['phase']='committed';atomic(outer,encoded(journal))
   outer.unlink();fd=os.open(root,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
   result={'status':'PASS','action':v['action'],'operator':str(operator),'operatorManifestSHA256':operator.name,'profile':profile,'change':changed,'readiness':ready,'processes':processes,'nativeAndFileAndWebsitePIDsUnchanged':before_pids,'certificateJobActuallyExecuted':True,'timerActive':run(['systemctl','is-active',timer],False).stdout.strip()=='active','publicRouterFirewallPortsChanged':False,'aggregateBandwidthCeilingRaised':True}
  except BaseException:
   if journal['phase']=='prepared':
    apply_profile(journal['before'],Path(journal['operatorBefore']));outer.unlink()
   raise
 assert stable_pids()==before_pids
 if v['action']!='plan':
  receipt=root/('text-profile-'+v['action']+'-'+str(time.time_ns())+'-result.json')
  with os.fdopen(os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  result['rootReceipt']=str(receipt)
 result['relayConfigSHA256']=sha((directory/'managed.json').read_bytes());print(json.dumps(result))
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--action',choices=['plan','install','apply','rollback','recover'],default='plan');p.add_argument('--relay-config-sha256',required=True);a=p.parse_args()
 assert re.fullmatch('[0-9a-f]{64}',a.relay_config_sha256)
 v={'action':a.action,'configSHA256':a.relay_config_sha256}
 r=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/srv/codi-connected/venvs/517179c/bin/python','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(v),text=True,capture_output=True,timeout=300)
 if r.returncode:raise RuntimeError(r.stderr[-4000:] or r.stdout[-4000:])
 result=json.loads(r.stdout);result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('relay-256-profile-'+a.action+'-result.json')
 if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
