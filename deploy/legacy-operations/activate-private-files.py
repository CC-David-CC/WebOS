#!/usr/bin/env python3
"""Git-first one-time private file worker activation; no public route/UI change."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import errno,hashlib,http.client,json,os,pathlib,pwd,secrets,socket,stat,subprocess,sys,tempfile,time
Path=pathlib.Path;inputs=json.load(sys.stdin)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=90).stdout.strip()
def protected(path,directory=False,owner=0,mode=None):
 p=Path(path)
 for ancestor in [p,*p.parents]:
  info=ancestor.lstat();assert not stat.S_ISLNK(info.st_mode)
  if ancestor!=p:assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
 info=p.stat();assert info.st_uid==owner and not info.st_mode&0o022
 if directory:assert p.is_dir()
 else:assert p.is_file() and info.st_nlink==1
 if mode is not None:assert stat.S_IMODE(info.st_mode)==mode
 return p
def mkdir(p,mode=0o755):
 p=Path(p)
 if not p.exists():protected(p.parent,True);p.mkdir(mode=mode)
 protected(p,True,mode=mode)
def source(folder,name,pin,expected):
 with os.fdopen(os.open(folder/name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as stream:
  info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=65536
  raw=stream.read(65537)
 assert digest(raw)==pin
 value=json.loads(raw);assert set(value)=={'version','files'} and set(value['files'])==expected
 assert value['version']=={'files-service.json':'codi-private-file-service/1','file-operator.json':'codi-file-operator/1'}[name]
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==expected|{name}
 values={name:raw}
 for path,record in value['files'].items():
  p=folder/path
  for ancestor in [p,*p.parents]:assert not ancestor.is_symlink()
  with os.fdopen(os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as stream:
   info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=262144
   data=stream.read(262145);assert record=={'bytes':len(data),'sha256':digest(data)};values[path]=data
 return values
def install(target,values):
 if target.exists() or target.is_symlink():
  protected(target,True,mode=0o755)
  assert {str(p.relative_to(target)) for p in target.rglob('*') if not p.is_dir()}==set(values)
  for name,raw in values.items():assert protected(target/name,mode=0o644).read_bytes()==raw
  return
 mkdir(target.parent)
 stage=Path(tempfile.mkdtemp(prefix='.files-install-',dir=target.parent))
 try:
  for name,raw in values.items():
   p=stage/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);p.chmod(0o644)
   with p.open('rb') as stream:os.fsync(stream.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  os.rename(stage,target)
  fd=os.open(target.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():__import__('shutil').rmtree(stage)
assert os.geteuid()==0 and inputs['action'] in ('plan','apply')
checkout=Path('/home/dflanag3/webhost-sites/sites/ksu.codes')
git=lambda *args:run(['runuser','-u','dflanag3','--','git','-C',checkout,*args])
assert git('rev-parse','HEAD')==inputs['commit'] and not git('status','--porcelain')
assert digest((checkout/'tools/codiserver/file-service-lifecycle/scripts/activate-private-files.py').read_bytes())==inputs['activationSHA256']
worker_files={*('gateway_service/'+n for n in ['__init__.py','auth.py','policy.py','user_store.py','http.py','transfers.py','client.mjs']),'codiserver-server-v0.3.0/codiauth/__init__.py','codiserver-server-v0.3.0/codiauth/jose.py','scripts/serve-user-files.py','requirements.lock'}
worker=source(checkout/'tools/codiserver/file-service-candidates'/inputs['worker'],'files-service.json',inputs['worker'],worker_files)
operator=source(checkout/'tools/codiserver/file-operator-candidates'/inputs['operator'],'file-operator.json',inputs['operator'],{'file_service/__init__.py','file_service/operator.py','scripts/manage-user-files.py'})
assert not git('status','--porcelain')
native=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text())
assert native['release']=='/srv/codi-connected/releases/native10-7705a87e09c44e22' and native['basePath']=='/hidden' and native['origin']=='https://ksu.codes'
def pids():return {role:run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','--value']) for role in ['issuer','steward','guest']}
before_pids=pids();assert before_pids=={'issuer':'227448','steward':'227450','guest':'227451'}
website=Path('/srv/webapps/ksu.codes/current').resolve()
files=[Path('/etc/caddy/Caddyfile'),checkout.parent.parent/'ops/common.py',checkout.parent.parent/'sites.toml',Path('/etc/codi-connected/ksu/managed.json')]
files.extend(website/'public/desktop'/name for name in ['release.json','app.js','config.json'])
snapshots=lambda:{str(p):digest(p.read_bytes()) for p in files}
before=snapshots()
who=pwd.getpwnam('codi-gateway');state=Path('/var/lib/codi-gateway/ksu');data=Path('/var/lib/codi-user-files/ksu')
for p in [state,data]:protected(p,True,owner=who.pw_uid,mode=0o700)
database=state/'permissions.sqlite3';assert database.stat().st_uid==who.pw_uid and stat.S_IMODE(database.stat().st_mode)==0o600 and not database.is_symlink()
def data_metadata():
 values=[]
 for p in [data,*data.rglob('*')]:
  info=p.lstat();assert not stat.S_ISLNK(info.st_mode) and info.st_uid==who.pw_uid
  assert p.is_dir() or stat.S_ISREG(info.st_mode) and info.st_nlink==1
  assert not p.name.startswith('.save-'),'Review retained save transaction before activation'
  values.append((str(p.relative_to(data)),info.st_mode,info.st_size,info.st_ino,info.st_mtime_ns))
  assert len(values)<=100002
 return digest(json.dumps(sorted(values),separators=(',',':')).encode())
data_before=data_metadata()
policy=json.loads((Path(native['stateRoot'])/'public/origin-discovery.json').read_text())['identity']
connection=http.client.HTTPConnection('127.0.0.1',native['ports']['issuer'],timeout=5)
try:
 connection.request('GET','/config.json',headers={'Host':'ksu.codes'});response=connection.getresponse();assert response.status==200
 assert json.loads(response.read(65537))['identity']==policy
finally:connection.close()
raw_policy=(json.dumps(policy,sort_keys=True,indent=2)+'\n').encode()
python=Path('/srv/codi-connected/venvs/517179c/bin/python')
expected={line.strip().lower() for line in worker['requirements.lock'].decode().splitlines() if line.strip()}
assert expected=={line.lower() for line in run([python,'-I','-B','-m','pip','freeze']).splitlines()}
control=Path('/etc/codi-user-files/ksu');release=Path('/srv/codi-gateway/releases')/inputs['worker'];operator_root=Path('/srv/codi-gateway/operators')/inputs['operator']
assert not (control/'managed.json').exists(),'One-time activation already configured; use the installed managed operator for lifecycle/recovery'
with socket.socket() as probe:probe.bind(('127.0.0.1',8140))
result={'status':'PASS','action':inputs['action'],'sourceCommit':inputs['commit'],'workerManifestSHA256':inputs['worker'],'operatorManifestSHA256':inputs['operator'],'nativePids':before_pids,'publicRouteInstalled':False,'frontendInstalled':False,'routerFirewallOrBootChanged':False,'personalFileContentsRead':False}
if inputs['action']=='apply':
 install(release,worker);install(operator_root,operator)
 for p in [control.parent,control]:mkdir(p)
 # Only immutable root code is imported/executed after byte-for-byte install.
 sys.path.insert(0,str(operator_root));from file_service.operator import Manager,atomic,verify_worker,account
 m=Manager(control)
 try:
  with m.locked('codi-files-ksu-hidden'):
   atomic(control/'issuer-policy.json',raw_policy,0o644)
   configured=m.configure(instance='codi-files-ksu-hidden',user='codi-gateway',release=release,manifest_sha256=inputs['worker'],python=python,state_root=state,data_root=data,issuer_policy=control/'issuer-policy.json',base_path='/hidden',port=8140)
   initialized=m.initialize();started=m.start();config=m.load();states=m.states(config)
   values={}
   for unit in m.names(config)[:2]:
    pid=int(states[unit]['MainPID']);status=dict(line.split(':',1) for line in Path('/proc',str(pid),'status').read_text().splitlines())
    assert int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
    uid=set(map(int,status['Uid'].split()));assert len(uid)==1 and 0 not in uid
    values[unit]={'pid':pid,'uid':next(iter(uid)),'netns':os.readlink('/proc/'+str(pid)+'/ns/net')}
   assert len({v['netns'] for v in values.values()})==1 and len({v['uid'] for v in values.values()})==2
   assert next(iter(values.values()))['netns']!=os.readlink('/proc/self/ns/net')
   assert all(s['UnitFileState']=='static' for s in states.values())
   connection=http.client.HTTPConnection('127.0.0.1',8140,timeout=5)
   try:
    connection.request('POST','/gateway/use',body=b'{}',headers={'Host':'ksu.codes','Origin':'https://ksu.codes','Content-Type':'application/json'})
    response=connection.getresponse();assert response.status==401;response.read(1024)
   finally:connection.close()
   result.update(installedRelease=str(release),installedOperator=str(operator_root),privateServiceConfig=str(m.config_path),migration=initialized,processes=values,unauthenticatedUseRefused=True,staticUnits=True)
 except BaseException:
  subprocess.run(['systemctl','stop',*reversed(['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service','codi-files-ksu-hidden-proxy.socket'])],capture_output=True)
  raise
assert snapshots()==before and pids()==before_pids and data_metadata()==data_before
result.update(hostingNativeAndPrototypeUnchanged=True,existingUserFileMetadataPreserved=True)
if inputs['action']=='apply':
 receipt=Path('/srv/codi-gateway')/('private-files-activation-'+str(time.time_ns())+'-result.json')
 fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 result.update(rootReceipt=str(receipt),rootReceiptSHA256=digest(receipt.read_bytes()))
print(json.dumps(result))
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--commit',required=True);p.add_argument('--worker-sha256',required=True);p.add_argument('--operator-sha256',required=True);p.add_argument('--action',choices=['plan','apply'],default='plan');args=p.parse_args()
    if not re.fullmatch('[0-9a-f]{40}',args.commit) or any(not re.fullmatch('[0-9a-f]{64}',s) for s in [args.worker_sha256,args.operator_sha256]):p.error('Exact reviewed source commit and manifest hashes required')
    inputs={'commit':args.commit,'worker':args.worker_sha256,'operator':args.operator_sha256,'action':args.action,'activationSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(inputs),capture_output=True,text=True,timeout=180)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    value=json.loads(child.stdout);value['activationSourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/'.build/checks'/('private-files-webhost-'+args.action+'-result.json')).write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
