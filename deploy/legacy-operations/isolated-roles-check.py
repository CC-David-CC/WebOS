#!/usr/bin/env python3
"""Disposable real systemd DynamicUser issuer/steward integration.

Requires existing sudo authorization. No persistent users, public listeners,
router changes, trust-store changes or changes to existing previews. The guest
relay is deliberately outside this check: its egress policy needs its own role.
"""
import argparse,hashlib,importlib.util,json,os,secrets,shutil,socket,ssl,stat,subprocess,sys,tempfile,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from origin_service.mount import validate_base_path
from codiauth import jose
from codiauth.service import PROOF_TYPE
from cryptography.hazmat.primitives.asymmetric import ec

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--release-dir',required=True,type=Path)
 parser.add_argument('--base-path',default='/hidden',type=validate_base_path)
 args=parser.parse_args();base=args.base_path
 spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
 original=exporter.verify(args.release_dir)
 for port in [8118,8119,8446]:
  with socket.socket() as probe:
   probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   probe.bind(('127.0.0.1',port))
 checks=ROOT/'.build/checks';checks.mkdir(parents=True,exist_ok=True)
 run=Path(tempfile.mkdtemp(prefix='isolated-roles-',dir=checks));run.chmod(0o700)
 stage=Path(tempfile.mkdtemp(prefix='codi-roles-',dir='/var/tmp'));stage.chmod(0o755)
 token=secrets.token_hex(6);names={r:'codi-check-'+token+'-'+r for r in ['issuer','steward']}
 runtimes={r:Path('/run')/names[r] for r in names};units=[];processes=[]
 release=stage/'release';python=stage/'venv/bin/python';public=stage/'public';bundle=public/'steward/bundle.json';policy=public/'origin-discovery.json'
 operator=stage/'operator';operator_runtime=operator/'runtime';authority=operator/'root';private=operator_runtime/'steward-private/provisioned';steward_private=runtimes['steward']/'private'
 origin='https://127.0.0.1:8446';url=origin+base+'/'
 result={'status':'FAIL','scope':'Actual separate systemd DynamicUser accounts, native private-file denials and local HTTPS/WSS/RTC browsers; no guest Internet, public deployment or WAN claim','fixtureDirectory':str(run),'basePath':base,'release':original}
 def command(argv,**kwargs):
  return subprocess.run([str(x) for x in argv],check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45,**kwargs).stdout
 def sudo(*argv):return command(['sudo','-n',*argv])
 def wait_for(check,seconds=20):
  end=time.monotonic()+seconds;last=None
  while time.monotonic()<end:
   try:
    value=check()
    if value:return value
   except (OSError,ValueError,KeyError,urllib.error.URLError) as error:last=error
   time.sleep(.1)
  raise RuntimeError('Readiness deadline exceeded: '+str(last))
 def state(role):
  raw=sudo('systemctl','show',names[role]+'.service','-p','MainPID','-p','ActiveState','-p','DynamicUser','-p','ProtectSystem','-p','ProtectHome','-p','NoNewPrivileges','-p','RuntimeDirectory')
  record=dict(line.split('=',1) for line in raw.splitlines());pid=int(record['MainPID'])
  if not pid or record['ActiveState']!='active':raise ValueError(role+' is not active')
  status=Path('/proc',str(pid),'status').read_text();uid=int(next(line for line in status.splitlines() if line.startswith('Uid:')).split()[2]);gid=int(next(line for line in status.splitlines() if line.startswith('Gid:')).split()[2])
  if uid in (0,os.geteuid()) or record['DynamicUser']!='yes' or record['ProtectSystem']!='strict' or record['ProtectHome']!='yes' or record['NoNewPrivileges']!='yes':raise ValueError('Role sandbox properties missing')
  return record|{'uid':uid,'gid':gid,'pid':pid}
 def start(role,argv,writable=None):
  props={'DynamicUser':'yes','RuntimeDirectory':names[role],'RuntimeDirectoryMode':'0700','ProtectSystem':'strict','ProtectHome':'yes','NoNewPrivileges':'yes','PrivateTmp':'yes','BindReadOnlyPaths':str(stage),'RestrictSUIDSGID':'yes','LockPersonality':'yes','UMask':'0077','RestrictAddressFamilies':'AF_UNIX AF_INET AF_INET6','TimeoutStopSec':'8s','WorkingDirectory':str(release)}
  if writable:props['ReadWritePaths']=str(writable)
  options=[piece for key,value in props.items() for piece in ['--property',key+'='+value]]
  if names[role] not in units:units.append(names[role])
  sudo('systemd-run','--quiet','--collect','--service-type=exec','--unit',names[role],*options,python,'-B',*argv)
  return wait_for(lambda:state(role))
 def stop(role):
  stopped=subprocess.run(['sudo','-n','systemctl','stop',names[role]+'.service'],text=True,capture_output=True,timeout=15)
  if stopped.returncode not in (0,5):raise RuntimeError(stopped.stderr)
  wait_for(lambda:sudo('systemctl','show',names[role]+'.service','-p','MainPID','--value').strip()=='0')
 def config():
  request=urllib.request.Request('http://127.0.0.1:8118/config.json',headers={'Host':'127.0.0.1:8446'})
  with urllib.request.urlopen(request,timeout=2) as response:return json.load(response)
 def post(route,data):
  request=urllib.request.Request('http://127.0.0.1:8118'+route,data=jose.dumps(data).encode(),headers={'Host':'127.0.0.1:8446','Origin':origin,'Content-Type':'application/json'})
  with urllib.request.urlopen(request,timeout=5) as response:return json.load(response)
 username='role_'+secrets.token_hex(8);password=secrets.token_urlsafe(32)
 def account(secret):
  key=ec.generate_private_key(ec.SECP256R1());route=base+'/api/v1/auth'
  challenge=post('/api/v1/challenge',{'key':jose.public_jwk(key),'path':route});now=int(time.time());body=jose.dumps({'username':username,'password':secret})
  proof=jose.sign({'v':1,'nonce':challenge['nonce'],'iss':'isolated-role-fixture','aud':origin,'method':'POST','path':route,'iat':now,'exp':now+60,'request_sha256':jose.digest(body)},key,PROOF_TYPE)
  return post('/api/v1/auth',{'request':body,'proof':proof})['identity']
 def operator_command(action):
  argv=[python,'-B',release/'scripts/provision-connected.py',action,'--runtime-dir',operator_runtime,'--root-dir',authority]
  if action=='init':argv+=['--origin',origin,'--endpoint',origin.replace('https:','wss:')+base+'/rendezvous','--base-path',base,'--issuer-config',operator/'issuer-config.json']
  return json.loads(sudo(*argv))
 def install_provision(first=False):
  if first:
   sudo('cp','-a',private,steward_private)
   sudo('chown','-R',str(steward['uid'])+':'+str(steward['gid']),steward_private)
  else:
   # Replace only the signed policy. Never copy a stale publisher ledger.
   temporary=steward_private/'provision.next'
   sudo('install','-m','0600','-o',str(steward['uid']),'-g',str(steward['gid']),private/'provision.json',temporary)
   sudo('mv','-T',temporary,steward_private/'provision.json')
 def probe(role,paths):
  # Probe the actual service credentials outside its mount sandbox as well:
  # denials here prove Unix ownership rather than only read-only mounts.
  code='''import errno,json,os,sys
out=[]
for item in json.loads(sys.argv[1]):
 record=dict(item)
 try:
  fd=os.open(item['path'],os.O_WRONLY|os.O_APPEND if item['write'] else os.O_RDONLY);os.close(fd);record['allowed']=True
 except OSError as error:
  if error.errno not in (errno.EACCES,errno.EPERM,errno.EROFS):raise
  record['allowed']=False
 if record['allowed']!=item['expected']:raise RuntimeError('Unexpected access: '+str(record))
 out.append(record)
print(json.dumps(out))'''
  who=state(role)
  return json.loads(sudo('setpriv','--reuid',str(who['uid']),'--regid',str(who['gid']),'--clear-groups','/usr/bin/python3','-B','-c',code,json.dumps(paths)))
 try:
  shutil.copytree(args.release_dir,release);shutil.copytree(ROOT/'.venv',stage/'venv',symlinks=True)
  # Keep the unit and its UID alive while restarting only the actual issuer.
  # DynamicUser+preserved RuntimeDirectory introduces a symlink; ordinary
  # RuntimeDirectory is real, strictly checked and automatically removed.
  (stage/'issuer-worker.py').write_text('''import pathlib,signal,subprocess,sys,time
policy,bundle=map(pathlib.Path,sys.argv[1:3]);argv=sys.argv[3:];child=None;stopping=False
def stop(*args):
 global stopping
 stopping=True
signal.signal(signal.SIGTERM,stop)
def reap():
 if child is not None and child.poll() is None:
  child.terminate()
  try:child.wait(5)
  except subprocess.TimeoutExpired:child.kill();child.wait();raise RuntimeError('Forced issuer shutdown')
try:
 child=subprocess.Popen([sys.executable,'-B',*argv])
 while not stopping and child.poll() is None and not (policy.is_file() and bundle.is_file()):time.sleep(.1)
 if not stopping:
  if child.poll() is not None:raise RuntimeError('Bootstrap issuer exited')
  reap();child=subprocess.Popen([sys.executable,'-B',*argv,'--discovery-policy',str(policy),'--discovery-bundle',str(bundle)])
  while not stopping and child.poll() is None:time.sleep(.1)
  if not stopping:raise RuntimeError('Connected issuer exited')
finally:reap()
''')
  for path in [stage,*stage.rglob('*')]:
   if not path.is_symlink():path.chmod(0o755 if path.is_dir() or path.stat().st_mode&0o111 else 0o644)
  (public/'steward').mkdir(parents=True,mode=0o755);operator.mkdir(mode=0o700)
  sudo('chown','-R','root:root',stage)
  issuer_args=[release/'scripts/serve-connected.py','--port','8118','--runtime-dir',runtimes['issuer'],'--origin',origin,'--base-path',base]
  issuer=start('issuer',[stage/'issuer-worker.py',policy,bundle,*issuer_args]);initial=wait_for(config)
  before_account=account(password)
  input_file=run/'issuer-config.json';input_file.write_text(json.dumps(initial));input_file.chmod(0o600)
  sudo('install','-m','0600',input_file,operator/'issuer-config.json');input_file.unlink()
  operator_command('init')
  # Provisioning from public issuer metadata must not create another issuer key.
  assert sudo('find',operator_runtime/'state','-type','f').strip()==''
  steward=start('steward',[release/'scripts/serve-steward.py','serve','--port','8119','--state',steward_private/'ledger','--key',steward_private/'service.pem','--provision',steward_private/'provision.json','--bundle-out',bundle,'--wait-for-provision','30'],public/'steward')
  assert issuer['uid']!=steward['uid']
  sudo('chown',str(steward['uid'])+':'+str(steward['gid']),public/'steward');install_provision(first=True)
  wait_for(lambda:bundle.is_file())
  sudo('install','-m','0444',private/'origin-discovery.json',policy)
  connected=wait_for(lambda:(value if 'discovery' in (value:=config()) else None))
  assert initial['identity']==connected['identity'] and issuer['uid']!=steward['uid']
  after_account=account(password)
  assert before_account['sub']==after_account['sub'] and before_account['sid']!=after_account['sid'] and before_account['key']!=after_account['key']
  try:account(password+'wrong')
  except urllib.error.HTTPError as error:assert error.code==401
  else:raise AssertionError('Wrong password accepted after issuer restart')
  children=Path('/proc',str(issuer['pid']),'task',str(issuer['pid']),'children').read_text().split()
  assert len(children)==1
  native=int(children[0]);raw=Path('/proc',str(native),'cmdline').read_bytes().removesuffix(b'\0').split(b'\0')
  assert raw==[os.fsencode(x) for x in [python,'-B',*issuer_args,'--discovery-policy',policy,'--discovery-bundle',bundle]]
  native_uid=int(next(line for line in Path('/proc',str(native),'status').read_text().splitlines() if line.startswith('Uid:')).split()[2]);assert native_uid==issuer['uid']
  issuer['nativePid']=native;issuer['nativeUid']=native_uid
  result.update(roles={'issuer':issuer,'steward':steward},issuerPublicIdentityPreservedAcrossRestart=True,operatorUsesOnlyIssuerPublicMetadata=True)
  result['registeredAccountSurvivesIssuerRestartWithFreshSessionAndKey']=True
  result['wrongPasswordRejectedAfterRestart']=True
  records={}
  for role in ['issuer','steward']:
   paths=[]
   for path,owner in [(runtimes['issuer']/'state/issuer.pem','issuer'),(runtimes['issuer']/'state/accounts.sqlite3','issuer'),(steward_private/'service.pem','steward'),(steward_private/'ledger/publisher.sqlite3','steward'),(authority/'root.pem','operator')]:
    for write in [False,True]:paths.append({'path':str(path),'write':write,'expected':role==owner})
   for path,can_write in [(bundle,role=='steward'),(policy,False),(release/'origin_service/discovery.py',False)]:
    paths.extend([{'path':str(path),'write':False,'expected':True},{'path':str(path),'write':True,'expected':can_write}])
   records[role]=probe(role,paths)
  result['unixCredentialAccessProbes']=records
  result['separateNonRootServiceUids']=True
  revision=lambda:json.loads(__import__('base64').urlsafe_b64decode(config()['discovery']['seed'].split('.')[1]+'==='))['revision']
  assert revision()==1
  renewal=operator_command('renew');assert renewal['revision']==2;install_provision()
  wait_for(lambda:revision()==2,40)
  result['explicitRenewalThroughPublicBundle']=True
  # TLS runs as the invoking developer, with no access to service-private data.
  command([sys.executable,'-B',ROOT/'scripts/prepare-tls-preview.py','--output-dir',run/'tls','--base-path',base])
  tls=run/'tls';log=(run/'caddy.log').open('wb')
  child=subprocess.Popen([str(ROOT.parent/'.build/tools/caddy'),'run','--config',str(tls/'Caddyfile.combined'),'--adapter','caddyfile'],stdout=log,stderr=subprocess.STDOUT);log.close();processes.append(child)
  context=ssl.create_default_context(cafile=str(tls/'cert.pem'))
  def https_ready():
   with urllib.request.urlopen(url+'config.json',context=context,timeout=2) as response:return json.load(response)['discovery']
  wait_for(https_ready)
  for name,argv,timeout in [
   ('identity',[ROOT/'scripts/identity-check.py','--url',url,'--tls-spki-file',tls/'spki.txt','--ca-file',tls/'cert.pem'],160),
   ('browser',[ROOT/'scripts/tls-discovery-check.py','--url',url,'--spki-file',tls/'spki.txt','--ca-file',tls/'cert.pem','--require-trust','test-server'],220)]:
   with (run/(name+'.log')).open('wb') as output:
    check=subprocess.run([str(x) for x in [sys.executable,'-B',*argv]],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=output,stderr=subprocess.STDOUT,timeout=timeout)
   if check.returncode:raise RuntimeError(name+' check failed; inspect '+str(run/(name+'.log')))
   result[name]=json.loads((checks/('identity-result.json' if name=='identity' else 'tls-discovery-result.json')).read_text())
  stop('steward')
  assert account(password)['sub']==before_account['sub'] and config()['identity']==initial['identity']
  result['issuerAccountLoginWorksWithStewardStopped']=True
  result['status']='PASS'
 except BaseException as error:
  result['error']=str(error)
  if isinstance(error,subprocess.CalledProcessError):result['commandError']=(error.stderr or '')[-3000:]
 finally:
  cleanup=[]
  for role,unit in names.items():
   if unit in units:
    try:
     (run/(role+'.log')).write_text(sudo('journalctl','--no-pager','-o','cat','-u',unit+'.service'))
     stop(role)
     assert sudo('systemctl','show',unit+'.service','-p','MainPID','--value').strip()=='0'
    except (OSError,subprocess.SubprocessError,AssertionError) as error:cleanup.append(str(error))
  for child in reversed(processes):
   if child.poll() is None:
    child.terminate()
    try:child.wait(8)
    except subprocess.TimeoutExpired:child.kill();child.wait();cleanup.append('Forced Caddy shutdown')
  if not cleanup:
   try:
    staged=exporter.verify(release)
    assert {k:v for k,v in staged.items() if k!='directory'}=={k:v for k,v in original.items() if k!='directory'}
    result['onlineReleaseAfterExecutionVerified']=True
   except (OSError,ValueError,AssertionError) as error:cleanup.append('Online release verification: '+str(error))
  if not cleanup:
   try:
    sudo('rm','-rf','--',stage,*runtimes.values())
    assert not stage.exists() and all(not path.exists() for path in runtimes.values())
    result['disposablePrivateStateRemoved']=True
   except (OSError,subprocess.SubprocessError,AssertionError) as error:cleanup.append(str(error))
  try:
   assert exporter.verify(args.release_dir)==original
   result['originalReleaseUnchanged']=True
  except (OSError,ValueError,AssertionError) as error:cleanup.append('Release verification: '+str(error))
  result['cleanupErrors']=cleanup
  if cleanup:result['status']='FAIL'
  result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/isolated-roles-check.py','scripts/serve-connected.py','scripts/serve-steward.py','scripts/provision-connected.py','origin_service/discovery.py']}
  serialized=json.dumps(result,indent=2)+'\n'
  (checks/'isolated-roles-result.json').write_text(serialized)
  (checks/('isolated-roles-hidden-result.json' if base else 'isolated-roles-root-result.json')).write_text(serialized)
  print(json.dumps({k:v for k,v in result.items() if k not in ['identity','browser','unixCredentialAccessProbes','sha256']},indent=2))
 return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
