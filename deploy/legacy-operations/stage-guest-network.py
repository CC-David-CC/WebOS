#!/usr/bin/env python3
"""Git-first, inactive guest network operator preparation on box-webhost.

Installs no native12, public route or active kernel policy. The existing issuer,
steward, guest, files, website and boot states must remain unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
WORKER='7f5de0c7525b81391448069708ee972cca304792baaf274b4aa1151e181a9759'
OPERATOR='8411c84aab2b284418951371b2ee9822797a70599c016c375bb409cb40f641d1'
REMOTE=r'''
import fcntl,hashlib,ipaddress,json,os,pathlib,pwd,shutil,socket,sqlite3,stat,subprocess,sys,tempfile,urllib.request
Path=pathlib.Path;inputs=json.load(sys.stdin);assert os.geteuid()==0 and inputs['action'] in ('plan','install')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=60,check=True).stdout.strip()
def protected(file,directory=False,mode=None):
 file=Path(file)
 for parent in file.parents:
  info=parent.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
 info=file.lstat();assert info.st_uid==0 and not info.st_mode&0o022 and (mode is None or stat.S_IMODE(info.st_mode)==mode)
 if directory:assert stat.S_ISDIR(info.st_mode)
 else:assert stat.S_ISREG(info.st_mode) and info.st_nlink==1
 return file
def directory(file):
 file=Path(file)
 if not file.exists():protected(file.parent,True,0o755);file.mkdir(mode=0o755)
 return protected(file,True,0o755)
def source_file(file,record):
 for part in [file,*file.parents]:assert not part.is_symlink()
 with os.fdopen(os.open(file,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as stream:
  info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==record['bytes'] and 0<=info.st_size<=262144
  raw=stream.read(info.st_size+1);assert len(raw)==info.st_size and sha(raw)==record['sha256'];return raw
checkout=Path('/home/dflanag3/webhost-sites/sites/ksu.codes');hosting=checkout.parent.parent
assert run(['runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==inputs['commit']
assert not run(['runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
packages={}
base=checkout/'tools/codiserver/guest-network'
for kind,folder,manifest,key,version,count in [('worker',base/'workers'/inputs['worker'],'guest-wire.json',inputs['worker'],'codi-guest-wire-runtime/1',12),('operator',base/'operators'/inputs['operator'],'guest-operator.json',inputs['operator'],'codi-guest-network-operator/1',10)]:
 raw=(folder/manifest).read_bytes();assert sha(raw)==key;metadata=json.loads(raw);assert set(metadata)=={'version','files'} and metadata['version']==version and len(metadata['files'])==count
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==set(metadata['files'])|{manifest}
 for name,record in metadata['files'].items():assert not Path(name).is_absolute() and all(p not in ('','.','..') for p in name.split('/'));source_file(folder/name,record)
 packages[kind]={'source':folder,'manifest':manifest,'raw':raw,'metadata':metadata,'destination':Path('/srv/codi-guest-network')/('workers' if kind=='worker' else 'operators')/key}
config=Path('/etc/codi-connected/ksu/managed.json');native=json.loads(protected(config,mode=0o600).read_text());python=Path('/srv/codi-connected/venvs/517179c/bin/python')
assert native['version']=='codi-managed-instance/4' and native['manifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
assert native['instance']=='codi-ksu-hidden' and native['origin']=='https://ksu.codes' and native['basePath']=='/hidden' and native['ports']=={'issuer':8118,'steward':8119,'guest':8132} and native.get('userFiles')
def pids():return {name:run(['systemctl','show',name,'-p','MainPID','--value']) for name in ['codi-ksu-hidden-issuer.service','codi-ksu-hidden-steward.service','codi-ksu-hidden-guest.service','codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']}
before_pids=pids();assert {r:before_pids['codi-ksu-hidden-'+r+'.service'] for r in ['issuer','steward','guest']}=={'issuer':'240953','steward':'239112','guest':'239113'}
assert before_pids['codi-files-ksu-hidden.service']=='236763' and before_pids['codi-files-ksu-hidden-proxy.service']=='236765'
before={str(p):sha(p.read_bytes()) for p in [config,hosting/'ops/common.py',hosting/'sites.toml',Path('/etc/caddy/Caddyfile')]}
assert list(before.values())==['194205c485f80abed1e5aec3de7cb89387502748421070aa0135013ae2523786','b8944e87534792e4255643f9abe4f10d9e72e3a4adceeb8ba646e931ddead4e1','799bab541b18541c9d43d859889d34b94da768f91f38dee2bd43d50601ad2526','8467252aea4bb8cc87faf35403f385fbe0664b746739839956308c14eeca0ab7']
before_tables=run(['nft','list','tables']);assert 'codi_guest_egress' not in before_tables
before_tuning={k:Path('/proc/sys/net/ipv4/'+k).read_bytes() for k in ['ping_group_range','ip_forward']};assert before_tuning['ping_group_range'].split()==[b'1000',b'1001'] and before_tuning['ip_forward'].strip()==b'0'
website=Path('/srv/webapps/ksu.codes/current').resolve();assert website==Path('/srv/webapps/ksu.codes/releases/20261023T043853468523Z-314447db');prototype=website/'public/desktop'
assert sha((prototype/'release.json').read_bytes())=='d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9';prototype_manifest=json.loads((prototype/'release.json').read_text())
for name,record in prototype_manifest['files'].items():
 assert not Path(name).is_absolute() and all(v not in ('','.','..') for v in name.split('/'));assert record=={'bytes':(prototype/name).stat().st_size,'sha256':sha((prototype/name).read_bytes())}
source_policy=json.loads((Path(native['stateRoot'])/'public/origin-discovery.json').read_text())['identity'];assert source_policy['issuer']=='https://ksu.codes' and source_policy['apiBase']=='/hidden/api/v1'
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with opener.open('https://api4.ipify.org',timeout=12) as response:wan=str(ipaddress.IPv4Address(response.read(128).decode().strip()))
assert ipaddress.IPv4Address(wan).is_global
dns=sorted({v[4][0] for v in socket.getaddrinfo('ksu.codes',443,socket.AF_INET,socket.SOCK_STREAM)})
own=sorted({wan,*[v for v in dns if ipaddress.IPv4Address(v).is_global]});policy={'version':'codi-guest-egress-policy/1','ownPublicIPv4':own,'dnsIPv4':['1.1.1.1','9.9.9.9']}
result={'status':'PASS','action':inputs['action'],'workerManifestSHA256':inputs['worker'],'operatorManifestSHA256':inputs['operator'],'ownPublicIPv4':own,'serverWANIPv4':wan,'domainIPv4':dns,'nativeManifestSHA256':native['manifestSHA256'],'liveFrontendManifestSHA256':'6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787','servicesRestarted':False,'kernelRulesActivated':False,'native12Installed':False,'prototypeDeclaredFilesVerified':len(prototype_manifest['files'])}
if inputs['action']=='install':
 locks=[]
 try:
  for lock in [hosting/'.controller.lock',config.parent/'.operator.lock',Path('/run/codi-service-operators/codi-ksu-hidden.lock')]:
   fd=os.open(lock,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);locks.append(fd);info=os.fstat(fd);assert info.st_uid==0 and stat.S_ISREG(info.st_mode) and info.st_nlink==1
   fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  for p,h in before.items():assert sha(Path(p).read_bytes())==h
  assert pids()==before_pids
  directory('/srv/codi-guest-network')
  for kind,package in packages.items():
   destination=package['destination'];directory(destination.parent)
   if not destination.exists():
    stage=Path(tempfile.mkdtemp(prefix='.guest-stage-',dir=destination.parent))
    try:
     for name,record in package['metadata']['files'].items():
      file=stage/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(source_file(package['source']/name,record));file.chmod(0o644)
     (stage/package['manifest']).write_bytes(package['raw']);(stage/package['manifest']).chmod(0o644)
     for folder in [stage,*[v for v in stage.rglob('*') if v.is_dir()]]:folder.chmod(0o755)
     stage.rename(destination)
    finally:
     if stage.exists():shutil.rmtree(stage)
   protected(destination,True,0o755);assert sha(protected(destination/package['manifest'],mode=0o644).read_bytes())==sha(package['raw'])
   for name,record in package['metadata']['files'].items():assert source_file(protected(destination/name,mode=0o644),record)
  for name in ['codi-net-anonymous','codi-net-registered']:
   try:pwd.getpwnam(name)
   except KeyError:run(['useradd','--system','--user-group','--home-dir','/nonexistent','--no-create-home','--shell','/usr/sbin/nologin',name])
  directory('/etc/codi-guest-network');control=directory('/etc/codi-guest-network/ksu');directory('/var/lib/codi-guest-network')
  file=control/'issuer-input.json';raw=(json.dumps(source_policy,sort_keys=True,indent=2)+'\n').encode()
  if file.exists():assert protected(file,mode=0o644).read_bytes()==raw
  else:file.write_bytes(raw);file.chmod(0o644)
  file=control/'egress-input.json';raw=(json.dumps(policy,sort_keys=True,indent=2)+'\n').encode()
  if file.exists():assert protected(file,mode=0o644).read_bytes()==raw
  else:file.write_bytes(raw);file.chmod(0o644)
  script=packages['operator']['destination']/'scripts/manage-guest-network.py'
  arguments=[python,'-I','-B',script,'configure','--config-dir',control,'--instance','codi-net-ksu-hidden','--worker',packages['worker']['destination'],'--worker-sha256',inputs['worker'],'--python',python,'--state-root','/var/lib/codi-guest-network/ksu','--issuer-policy',control/'issuer-input.json','--egress-policy',control/'egress-input.json','--base-path','/hidden']
  pending=control/'pending.json'
  if pending.exists():run([python,'-I','-B',script,'recover','--config-dir',control])
  result['configure']=json.loads(run(arguments));status=json.loads(run([python,'-I','-B',script,'status','--config-dir',control]));assert not status['active'] and not status['kernelMatches'] and not status['guardFault']
  for name,values in status['units'].items():assert values['ActiveState']=='inactive' and values.get('MainPID','0')=='0' and values['UnitFileState']=='static'
  result['units']=status['units'];result['preparedIdentities']={r:pwd.getpwnam('codi-net-'+r).pw_uid for r in ['anonymous','registered']};result['managedConfigSHA256']=sha((control/'managed.json').read_bytes())
  for role in ['anonymous','registered']:
   with sqlite3.connect('file:/var/lib/codi-guest-network/ksu/'+role+'/usage.sqlite3?mode=ro',uri=True) as db:assert all(db.execute('SELECT count(*) FROM '+table).fetchone()[0]==0 for table in ['usage','wires','starts'])
  result['usageLedgersEmpty']=True
 finally:
  for fd in reversed(locks):os.close(fd)
for p,h in before.items():assert sha(Path(p).read_bytes())==h
assert pids()==before_pids and run(['nft','list','tables'])==before_tables and before_tuning=={k:Path('/proc/sys/net/ipv4/'+k).read_bytes() for k in before_tuning}
assert Path('/srv/webapps/ksu.codes/current').resolve()==website
for name,record in prototype_manifest['files'].items():assert record=={'bytes':(prototype/name).stat().st_size,'sha256':sha((prototype/name).read_bytes())}
result['protectedSHA256']=before;result['nativeAndFilesPIDs']=before_pids;result['hostFirewallAndSysctlsUnchanged']=True
if inputs['action']=='install':
 receipt=Path('/srv/codi-guest-network')/('standby-'+inputs['operator']+'-result.json');receipt.write_text(json.dumps(result,indent=2)+'\n');receipt.chmod(0o600)
print(json.dumps(result,indent=2))
'''

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['plan','install']);parser.add_argument('--commit',required=True);args=parser.parse_args()
    value={'action':args.action,'commit':args.commit,'worker':WORKER,'operator':OPERATOR}
    result=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(value),capture_output=True,text=True,timeout=180)
    if result.returncode:raise SystemExit(result.stderr or result.stdout)
    report=json.loads(result.stdout);report['wrapperSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT/'.build/checks'/('guest-network-standby-'+args.action+'-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
