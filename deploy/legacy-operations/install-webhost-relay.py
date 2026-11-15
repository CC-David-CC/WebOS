#!/usr/bin/env python3
"""Guarded installation of a private relay and certificate job; no public route."""
import argparse
import json
import re
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import fcntl,hashlib,http.client,json,os,pathlib,pwd,shutil,socket,ssl,stat,subprocess,sys
Path=pathlib.Path;inputs=json.load(sys.stdin);root=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(root/'ops'));import common
def run(args,check=True):return subprocess.run(list(map(str,args)),check=check,capture_output=True,text=True,timeout=90)
def digest(raw):return hashlib.sha256(raw).hexdigest()
checkout=root/'sites/ksu.codes';operator_key='53ad5058662dbb0113caf43b900bcb77cbfdf0923e62477f899abe006d56c52b';runtime_key='69ce8817cef7b4a1d99a30be1d5548e92eb0bfeaa2ee6ae6fb165180a5ea4e4b'
assert os.geteuid()==0
assert run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD']).stdout.strip()==inputs['commit']
assert not run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain']).stdout.strip()
operator_source=checkout/'tools/codiserver/relay-operator';runtime_source=checkout/'tools/codiserver/relay-runtime'
operator_manifest=(operator_source/'relay-operator.json').read_bytes();runtime_manifest=(runtime_source/'runtime.json').read_bytes()
assert digest(operator_manifest)==operator_key and digest(runtime_manifest)==runtime_key
op=json.loads(operator_manifest);rt=json.loads(runtime_manifest)
assert set(op)=={'version','files'} and op['version']=='codi-relay-operator/2' and set(op['files'])=={'relay_service/__init__.py','relay_service/manager.py','relay_service/certificates.py','scripts/manage-relay.py','requirements.lock'}
assert rt['version']=='codi-coturn-runtime/1' and rt['upstreamRelease']=='4.18.0' and rt['upstreamCommit']=='23c6c1d32a3d2b21a56cee65d3203bcc4ea82d2b' and set(rt['files'])=={'turnserver','LICENSE-coturn'}
def exact(folder,manifest_name,manifest_key,records,protected=False):
 assert not folder.is_symlink();found=set()
 for item in [folder,*folder.rglob('*')]:
  info=item.lstat();assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
  if protected:assert info.st_uid==info.st_gid==0 and stat.S_IMODE(info.st_mode)==(0o755 if item.is_dir() or item.name=='turnserver' else 0o644)
  if item.is_dir():continue
  assert info.st_nlink==1;name=str(item.relative_to(folder));raw=item.read_bytes()
  if name==manifest_name:assert digest(raw)==manifest_key
  else:assert records[name]=={'bytes':len(raw),'sha256':digest(raw)};found.add(name)
 assert found==set(records) and (folder/manifest_name).is_file()
exact(operator_source,'relay-operator.json',operator_key,op['files']);exact(runtime_source,'runtime.json',runtime_key,rt['files'])
data=common.load();assert common.caddy(data,'production')==Path('/etc/caddy/Caddyfile').read_text()
domains=[s['domain'] for s in data['sites'] if s['enabled']];assert 'ksu.codes' in domains
def pids():
 names=[s['service'] for s in data['sites'] if s['enabled']]+['caddy.service',*['codi-ksu-hidden-'+r+'.service' for r in ['issuer','steward','guest']]]
 return {n:run(['systemctl','show',n,'-p','MainPID','--value']).stdout.strip() for n in names}
before=pids();assert all(int(v)>0 for v in before.values())
hosting={str(p):p.read_bytes() for p in [root/'ops/common.py',root/'sites.toml',Path('/etc/caddy/Caddyfile')]}
config=Path('/etc/codi-connected/ksu/managed.json');before_config=config.read_bytes()
def https(path):
 client=http.client.HTTPSConnection('ksu.codes',timeout=15);client.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname='ksu.codes')
 try:client.request('GET',path);response=client.getresponse();raw=response.read(524289);assert len(raw)<=524288;return response.status,dict(response.headers),raw
 finally:client.close()
status,headers,index=https('/hidden/');assert status==200;cookie=headers['Set-Cookie'].split(';',1)[0]
prototype={n:digest(https('/desktop/'+n)[2]) for n in ['release.json','app.js','config.json']}
frontend={n:digest(https('/hidden/'+n)[2]) for n in ['app.js','style.css','terminal.js']}
python=Path('/srv/codi-connected/venvs/517179c/bin/python');venv=python.parent.parent
for item in [venv,*venv.rglob('*')]:
 info=item.lstat();assert info.st_uid==0 and (item.is_symlink() or not info.st_mode&0o022)
provider=Path('/var/lib/caddy/.local/share/caddy/certificates/acme-v02.api.letsencrypt.org-directory/turn.ksu.codes');uid=pwd.getpwnam('caddy').pw_uid
def provider_input(suffix):
 file=provider/('turn.ksu.codes.'+suffix)
 with os.fdopen(os.open(file,os.O_RDONLY|os.O_NOFOLLOW),'rb') as stream:
  info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_uid==uid and info.st_nlink==1 and stat.S_IMODE(info.st_mode)==0o600;raw=stream.read(262145)
 assert len(raw)<=262144;return raw
cert,key=provider_input('crt'),provider_input('key')
name='codi-relay-ksu-hidden';config_dir=Path('/etc/codi-relay/ksu');base=Path('/srv/codi-relay');operator=base/'operators'/operator_key;runtime=base/'runtimes'/runtime_key
unit_names=[name+'.service',name+'-proxy.service',name+'-proxy.socket',name+'-certificate-refresh.service',name+'-certificate-refresh.timer']
for unit in unit_names:
 assert not (Path('/etc/systemd/system')/unit).exists() and not (Path('/run/systemd/system')/unit).exists()
 info=run(['systemctl','show',unit,'-p','ActiveState','-p','FragmentPath','-p','DropInPaths'],False).stdout
 assert 'ActiveState=active' not in info and not any(line.split('=',1)[1] for line in info.splitlines() if line.startswith(('FragmentPath=','DropInPaths=')))
assert not config_dir.exists()
with socket.socket() as probe:probe.bind(('127.0.0.1',13479))
if not inputs['apply']:
 print(json.dumps({'status':'PASS','scope':'Exact source bundles, current hosting/native/prototype state, protected Python/Caddy provider and free private socket; no live change','domainsPreserved':domains,'operatorManifestSHA256':operator_key,'runtimeManifestSHA256':runtime_key}));raise SystemExit(0)
def parent(directory):
 for item in [*reversed(directory.parents),directory]:
  if not item.exists():item.mkdir(mode=0o755)
  info=item.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
with Path('/run/lock/codi-relay-install.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);os.chmod(lock.name,0o600)
 # Recheck exclusive resources after acquiring the installation lock. A
 # failed or interrupted earlier attempt needs deliberate recovery, not an
 # implicit overwrite of an existing configuration or unit.
 assert not config_dir.exists() and not config_dir.is_symlink()
 for unit in unit_names:
  assert not (Path('/etc/systemd/system')/unit).exists() and not (Path('/run/systemd/system')/unit).exists()
 with socket.socket() as probe:probe.bind(('127.0.0.1',13479))
 assert pids()==before and config.read_bytes()==before_config and all(Path(p).read_bytes()==raw for p,raw in hosting.items())
 for source,destination,manifest_name,pin,records in [(operator_source,operator,'relay-operator.json',operator_key,op['files']),(runtime_source,runtime,'runtime.json',runtime_key,rt['files'])]:
  parent(destination.parent)
  if not destination.exists():
   shutil.copytree(source,destination)
   for item in [destination,*destination.rglob('*')]:os.chown(item,0,0);item.chmod(0o755 if item.is_dir() or item.name=='turnserver' else 0o644)
  exact(destination,manifest_name,pin,records,True)
 assert run([runtime/'turnserver','--version']).stdout.strip()=='4.18.0'
 assert 'not found' not in run(['ldd',runtime/'turnserver']).stdout
 sys.path.insert(0,str(operator));from relay_service.manager import Manager,atomic,certificate;from relay_service import certificates
 certificate(cert,key,'turn.ksu.codes',48*3600)
 parent(config_dir.parent);manager=Manager(config_dir);started=False
 try:
  with manager.locked():
   manager.configure(instance=name,hostname='turn.ksu.codes',binary=runtime/'turnserver',cert=cert,key=key,port=13479,unit_dir='/etc/systemd/system')
   certificates.bind(manager,provider,uid);rendered=certificates.refresh_units(manager,operator,python)
   for unit,body in rendered['units'].items():atomic(Path('/etc/systemd/system')/unit,body.encode(),0o644)
   run(['systemd-analyze','verify',*[Path('/etc/systemd/system')/unit for unit in unit_names]])
   run(['systemctl','daemon-reload']);manager.start();started=True
  # Exercise the exact production job, not an equivalent in-process call.
  run(['systemctl','start',name+'-certificate-refresh.service'])
  run(['systemctl','start',name+'-certificate-refresh.timer'])
  with manager.locked():
   value=manager.load();manager.installed(value);ready=manager.ready(value);state=manager.status()
   tls=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',13479),5),server_hostname='turn.ksu.codes')
   with tls:assert digest(tls.getpeercert(binary_form=True))==ready['pinnedTLSLeaf']
   processes={}
   for unit in manager.names(value)[:2]:
    raw=run(['systemctl','show',unit,'-p','MainPID','-p','ActiveState','-p','CapabilityBoundingSet','-p','NoNewPrivileges','-p','UnitFileState']).stdout;props=dict(line.split('=',1) for line in raw.splitlines());pid=int(props['MainPID'])
    info=dict(line.split(':',1) for line in (Path('/proc')/str(pid)/'status').read_text().splitlines());uids=set(map(int,info['Uid'].split()));assert len(uids)==1 and 0 not in uids and int(info['CapEff'],16)==0 and info['NoNewPrivs'].strip()=='1' and props['CapabilityBoundingSet']=='' and props['UnitFileState']=='static'
    namespace=os.readlink('/proc/'+str(pid)+'/ns/net');assert namespace!=os.readlink('/proc/self/ns/net');processes[unit]={'pid':pid,'uid':next(iter(uids)),'namespace':namespace,'noCapabilities':True,'noNewPrivileges':True}
   assert len({p['namespace'] for p in processes.values()})==1 and len({p['uid'] for p in processes.values()})==2
   pid=next(iter(processes.values()))['pid']
   assert [i['ifname'] for i in json.loads(run(['nsenter','-t',pid,'-n','ip','-j','address','show']).stdout)]==['lo']
   probe="import errno,json,socket\ndef check(h,p):\n with socket.socket() as s:s.settimeout(1);return s.connect_ex((h,p))\na=check('1.1.1.1',443);b=check('127.0.0.1',8118);assert a==errno.ENETUNREACH and b==errno.ECONNREFUSED;print(json.dumps({'internetError':a,'hostIssuerError':b}))"
   probes=json.loads(run(['nsenter','-t',pid,'-n','/usr/bin/python3','-B','-c',probe]).stdout)
  assert all(run(['systemctl','is-enabled',unit],False).stdout.strip()=='static' for unit in unit_names)
  assert run(['systemctl','is-active',name+'-certificate-refresh.timer']).stdout.strip()=='active'
  assert pids()==before and config.read_bytes()==before_config and all(Path(p).read_bytes()==raw for p,raw in hosting.items())
  status,headers,body=https('/hidden/');assert status==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie
  assert prototype=={n:digest(https('/desktop/'+n)[2]) for n in prototype} and frontend=={n:digest(https('/hidden/'+n)[2]) for n in frontend}
  smoke=root/'reports/private/codi-private-relay-20261023.json';run(['/usr/bin/python3',root/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke])
  results=json.loads(smoke.read_text());assert set(results['sites'])==set(domains) and all(s['result']=='PASS' for s in results['sites'].values())
  report={'status':'PASS','scope':'Protected private TURN installed with Caddy certificate provider and actual static refresh job/timer; no public route or issuer policy changed','sourceCommit':inputs['commit'],'operator':str(operator),'operatorManifestSHA256':operator_key,'runtime':str(runtime),'runtimeManifestSHA256':runtime_key,'runtimeBinarySHA256':rt['files']['turnserver']['sha256'],'configDirectory':str(config_dir),'processes':processes,'namespaceProbes':probes,'onlyLoopbackInterface':True,'defaultTrustedTLS':True,'unauthenticatedAllocation401':ready['unauthenticatedAllocation401'],'certificate':state['certificate'],'certificateRefreshJobPassed':True,'certificateTimerActive':True,'normalUnitsEnabledForBoot':False,'existingServicePidsUnchanged':before,'nativeConfigUnchanged':True,'hostingSHA256':{str(p):digest(raw) for p,raw in hosting.items()},'desktopSHA256':prototype,'frontendSHA256':frontend,'indexAndGuestCookieUnchanged':True,'allSiteSmoke':str(smoke),'siteDomains':domains,'publicTurnConfigured':False,'routerFirewallAndPortsChanged':False}
  receipt=base/'ksu-private-relay-install-result.json';assert not receipt.exists();fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as out:json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
  print(json.dumps(report))
 except BaseException:
  # Keep new root-private credentials/journal for deliberate recovery. Only
  # these new relay units are stopped; existing sites/native roles are untouched.
  run(['systemctl','stop',name+'-certificate-refresh.timer',name+'-certificate-refresh.service'],False)
  with manager.locked():
   if manager.config.exists() and not manager.journal.exists():manager.stop()
  raise
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.commit):parser.error('Full reviewed source commit required')
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'box-webhost', 'sudo', '-n', '/srv/codi-connected/venvs/517179c/bin/python', '-B', '-c', shlex.quote(REMOTE)], input=json.dumps({'commit':args.commit, 'apply':args.apply}), text=True, capture_output=True, timeout=360)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    report = json.loads(child.stdout.strip().splitlines()[-1])
    (ROOT / '.build/checks' / ('webhost-private-relay-install-result.json' if args.apply else 'webhost-private-relay-preflight-result.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
