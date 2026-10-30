#!/usr/bin/env python3
"""Three locked, persistent service identities with disposable local state.

Requires existing sudo authorization. No persistent users, public listeners,
router changes, trust-store changes or changes to existing previews. An explicit
option permits adding just the guest GID adjacent to the current ping range for
this test, restoring it afterward. Service accounts are prepared separately.
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
 parser.add_argument('--temporary-ping-group-policy',action='store_true',help='Temporarily permit exactly the adjacent guest GID; restore the original range afterward')
 args=parser.parse_args();base=args.base_path
 spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
 original=exporter.verify(args.release_dir)
 for port in [8118,8119,8132,8446]:
  with socket.socket() as probe:
   probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
   probe.bind(('127.0.0.1',port))
 checks=ROOT/'.build/checks';checks.mkdir(parents=True,exist_ok=True)
 run=Path(tempfile.mkdtemp(prefix='managed-roles-',dir=checks));run.chmod(0o700)
 stage=Path(tempfile.mkdtemp(prefix='codi-managed-',dir='/var/tmp'));stage.chmod(0o755)
 token=secrets.token_hex(6);names={r:'codi-managed-'+token+'-'+r for r in ['issuer','steward','guest']}
 runtimes={r:Path('/run')/names[r] for r in names};units=[];processes=[]
 release=stage/'release';python=stage/'venv/bin/python';public=stage/'public';bundle=public/'steward/bundle.json';policy=public/'origin-discovery.json'
 operator=stage/'operator';operator_runtime=operator/'runtime';authority=operator/'root';private=operator_runtime/'steward-private/provisioned';steward_private=runtimes['steward']/'private'
 origin='https://127.0.0.1:8446';url=origin+base+'/'
 ping_file=Path('/proc/sys/net/ipv4/ping_group_range');original_ping=ping_file.read_text().split();applied_ping=None
 original_forward=Path('/proc/sys/net/ipv4/ip_forward').read_text();observed_qemu={};accounts={}
 result={'status':'FAIL','scope':'Three actual locked persistent service accounts, native ownership/capability probes, local HTTPS/WSS/RTC and real guest Internet; no public deployment or WAN claim','fixtureDirectory':str(run),'basePath':base,'release':original}
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
  raw=sudo('systemctl','show',names[role]+'.service','-p','MainPID','-p','ActiveState','-p','User','-p','Group','-p','ProtectSystem','-p','ProtectHome','-p','NoNewPrivileges','-p','RuntimeDirectory','-p','CapabilityBoundingSet','-p','AmbientCapabilities')
  record=dict(line.split('=',1) for line in raw.splitlines());pid=int(record['MainPID'])
  if not pid or record['ActiveState']!='active':raise ValueError(role+' is not active')
  status=Path('/proc',str(pid),'status').read_text();uid=int(next(line for line in status.splitlines() if line.startswith('Uid:')).split()[2]);gid=int(next(line for line in status.splitlines() if line.startswith('Gid:')).split()[2])
  if uid in (0,os.geteuid()) or uid!=accounts[role]['uid'] or gid!=accounts[role]['gid'] or record['ProtectSystem']!='strict' or record['ProtectHome']!='yes' or record['NoNewPrivileges']!='yes' or record['CapabilityBoundingSet'] or record['AmbientCapabilities']:raise ValueError('Role sandbox properties missing')
  return record|{'uid':uid,'gid':gid,'pid':pid}
 def start(role,argv,writable=None):
  props={'User':'codi-'+role,'Group':'codi-'+role,'RuntimeDirectory':names[role],'RuntimeDirectoryMode':'0700','RuntimeDirectoryPreserve':'yes','ProtectSystem':'strict','ProtectHome':'yes','NoNewPrivileges':'yes','PrivateTmp':'yes','PrivateDevices':'yes','BindReadOnlyPaths':str(stage),'RestrictSUIDSGID':'yes','LockPersonality':'yes','ProtectKernelTunables':'yes','ProtectKernelModules':'yes','ProtectControlGroups':'yes','RestrictNamespaces':'yes','CapabilityBoundingSet':'','AmbientCapabilities':'','MemoryMax':'384M','TasksMax':'64','LimitNOFILE':'512','UMask':'0077','RestrictAddressFamilies':'AF_UNIX AF_INET AF_INET6','TimeoutStopSec':'8s','WorkingDirectory':str(release)}
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
  for path in [stage,*stage.rglob('*')]:
   if not path.is_symlink():path.chmod(0o755 if path.is_dir() or path.stat().st_mode&0o111 else 0o644)
  (public/'steward').mkdir(parents=True,mode=0o755);operator.mkdir(mode=0o700)
  sudo('chown','-R','root:root',stage)
  import grp
  guest_gid=grp.getgrnam('codi-guest').gr_gid
  account_record=json.loads(sudo('/usr/bin/python3','-B',release/'scripts/install-service-accounts.py','--guest-gid',str(guest_gid)))
  accounts=account_record['accounts'];assert all(record['locked'] for record in accounts.values())
  assert len({record['uid'] for record in accounts.values()})==len({record['gid'] for record in accounts.values()})==3
  result['accounts']=account_record
  issuer_args=[release/'scripts/serve-connected.py','--port','8118','--runtime-dir',runtimes['issuer'],'--origin',origin,'--base-path',base]
  issuer=start('issuer',issuer_args);initial=wait_for(config)
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
  original_issuer_pid=issuer['pid'];stop('issuer')
  assert not Path('/proc',str(original_issuer_pid)).exists()
  issuer=start('issuer',issuer_args+['--discovery-policy',policy,'--discovery-bundle',bundle])
  connected=wait_for(lambda:(value if 'discovery' in (value:=config()) else None))
  assert initial['identity']==connected['identity'] and issuer['uid']!=steward['uid']
  after_account=account(password)
  assert before_account['sub']==after_account['sub'] and before_account['sid']!=after_account['sid'] and before_account['key']!=after_account['key']
  try:account(password+'wrong')
  except urllib.error.HTTPError as error:assert error.code==401
  else:raise AssertionError('Wrong password accepted after issuer restart')
  native=issuer['pid'];raw=Path('/proc',str(native),'cmdline').read_bytes().removesuffix(b'\0').split(b'\0')
  assert raw==[os.fsencode(x) for x in [python,'-B',*issuer_args,'--discovery-policy',policy,'--discovery-bundle',bundle]]
  native_uid=int(next(line for line in Path('/proc',str(native),'status').read_text().splitlines() if line.startswith('Uid:')).split()[2]);assert native_uid==issuer['uid']
  issuer['nativePid']=native;issuer['nativeUid']=native_uid
  result.update(roles={'issuer':issuer,'steward':steward},issuerPublicIdentityPreservedAcrossRestart=True,operatorUsesOnlyIssuerPublicMetadata=True,completeIssuerUnitRestart=True)
  result['registeredAccountSurvivesIssuerRestartWithFreshSessionAndKey']=True
  result['wrongPasswordRejectedAfterRestart']=True
  # Exact group range: preserve the existing developer permission and add only
  # the adjacent dedicated relay group. Refuse a broad or ambiguous expansion.
  low,high=map(int,original_ping)
  if not low<=guest_gid<=high:
   if not args.temporary_ping_group_policy or low!=high or low!=os.getgid() or abs(guest_gid-low)!=1:raise ValueError('Explicit adjacent-only temporary ping policy required')
   denied=subprocess.run(['sudo','-n','setpriv','--reuid',str(accounts['guest']['uid']),'--regid',str(guest_gid),'--clear-groups',str(python),'-B',str(release/'guest-relay/server.py'),'--origin',origin,'--port','8132','--require-ping'],cwd=release,text=True,capture_output=True,timeout=15)
   assert denied.returncode!=0 and 'allowed service group' in denied.stderr
   result['missingPingPermissionRefusesStartup']=True
   applied_ping=[str(min(low,guest_gid)),str(max(high,guest_gid))]
   sudo('sysctl','-q','-w','net.ipv4.ping_group_range='+' '.join(applied_ping));assert ping_file.read_text().split()==applied_ping
  guest=start('guest',[release/'guest-relay/server.py','--port','8132','--origin',origin,'--identity-config-port','8118','--base-path',base,'--require-ping'])
  result['roles']['guest']=guest
  marker=run/'guest-state-marker';marker.write_text('private test marker');marker.chmod(0o600)
  sudo('install','-m','0600','-o',str(guest['uid']),'-g',str(guest['gid']),marker,runtimes['guest']/'private-marker');marker.unlink()
  records={}
  for role in names:
   paths=[]
   for path,owner in [(runtimes['issuer']/'state/issuer.pem','issuer'),(runtimes['issuer']/'state/accounts.sqlite3','issuer'),(steward_private/'service.pem','steward'),(steward_private/'ledger/publisher.sqlite3','steward'),(authority/'root.pem','operator'),(runtimes['guest']/'private-marker','guest')]:
    for write in [False,True]:paths.append({'path':str(path),'write':write,'expected':role==owner})
   for path,can_write in [(bundle,role=='steward'),(policy,False),(release/'origin_service/discovery.py',False)]:
    paths.extend([{'path':str(path),'write':False,'expected':True},{'path':str(path),'write':True,'expected':can_write}])
   paths.append({'path':str(Path.home()),'write':False,'expected':False})
   records[role]=probe(role,paths)
  result['unixCredentialAccessProbes']=records
  result['separateNonRootServiceUids']=True
  sockets={}
  for role in names:
   code='''import errno,json,os,socket
out={'uid':os.geteuid(),'gid':os.getegid(),'groups':os.getgroups()}
for name,kind in [('ping',socket.SOCK_DGRAM),('raw',socket.SOCK_RAW)]:
 try:
  with socket.socket(socket.AF_INET,kind,socket.IPPROTO_ICMP):pass
  out[name]=True
 except PermissionError:out[name]=False
print(json.dumps(out))'''
   who=state(role);sockets[role]=json.loads(sudo('setpriv','--reuid',str(who['uid']),'--regid',str(who['gid']),'--clear-groups','/usr/bin/python3','-B','-c',code))
   assert sockets[role]['ping']==(role=='guest') and not sockets[role]['raw'] and not sockets[role]['groups']
  result['nativeSocketPermissions']=sockets
  revision=lambda:json.loads(__import__('base64').urlsafe_b64decode(config()['discovery']['seed'].split('.')[1]+'==='))['revision']
  assert revision()==1
  renewal=operator_command('renew');assert renewal['revision']==2;install_provision()
  wait_for(lambda:revision()==2,40)
  result['explicitRenewalThroughPublicBundle']=True
  # TLS runs as the invoking developer, with no access to service-private data.
  command([sys.executable,'-B',ROOT/'scripts/prepare-tls-preview.py','--output-dir',run/'tls','--base-path',base])
  tls=run/'tls';log=(run/'caddy.log').open('wb')
  child=subprocess.Popen([str(ROOT.parent/'.build/tools/caddy'),'run','--config',str(tls/'Caddyfile.active'),'--adapter','caddyfile'],stdout=log,stderr=subprocess.STDOUT);log.close();processes.append(child)
  context=ssl.create_default_context(cafile=str(tls/'cert.pem'))
  def https_ready():
   with urllib.request.urlopen(url+'config.json',context=context,timeout=2) as response:return json.load(response)['discovery']
  wait_for(https_ready)
  for name,argv,timeout in [
   ('identity',[ROOT/'scripts/identity-check.py','--url',url,'--tls-spki-file',tls/'spki.txt','--ca-file',tls/'cert.pem'],160),
   ('browser',[ROOT/'scripts/tls-discovery-check.py','--url',url,'--spki-file',tls/'spki.txt','--ca-file',tls/'cert.pem','--require-trust','test-server','--guest-internet'],240)]:
   with (run/(name+'.log')).open('wb') as output:
    check=subprocess.Popen([str(x) for x in [sys.executable,'-B',*argv]],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=output,stderr=subprocess.STDOUT);processes.append(check)
    until=time.monotonic()+timeout
    while check.poll() is None:
     if time.monotonic()>until:raise RuntimeError(name+' check deadline exceeded')
     # Observe real QEMU children while the disposable browsers keep them live.
     for pid in Path('/proc',str(guest['pid']),'task',str(guest['pid']),'children').read_text().split():
      if pid in observed_qemu:continue
      try:
       command_line=Path('/proc',pid,'cmdline').read_bytes().split(b'\0')
       if not command_line or command_line[0]!=b'qemu-system-i386':continue
       status=dict(line.split(':',1) for line in Path('/proc',pid,'status').read_text().splitlines())
      except FileNotFoundError:continue
      evidence={'pid':int(pid),'uid':int(status['Uid'].split()[1]),'gid':int(status['Gid'].split()[1]),'groups':[int(group) for group in status['Groups'].split()],'effectiveCapabilities':status['CapEff'].strip(),'noNewPrivileges':status['NoNewPrivs'].strip()}
      assert evidence['uid']==guest['uid'] and evidence['gid']==guest_gid and set(evidence['groups'])<={guest_gid} and int(evidence['effectiveCapabilities'],16)==0 and evidence['noNewPrivileges']=='1'
      observed_qemu[pid]=evidence
     time.sleep(.1)
   if check.returncode:raise RuntimeError(name+' check failed; inspect '+str(run/(name+'.log')))
   result[name]=json.loads((checks/('identity-result.json' if name=='identity' else 'tls-discovery-result.json')).read_text())
  stop('steward')
  assert account(password)['sub']==before_account['sub'] and config()['identity']==initial['identity']
  result['issuerAccountLoginWorksWithStewardStopped']=True
  assert len(observed_qemu)>=2
  result['qemuChildrenUnderGuestAccount']=list(observed_qemu.values())
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
  try:
   if applied_ping is not None:
    if ping_file.read_text().split()!=applied_ping:raise ValueError('Ping policy changed concurrently; refusing to replace unrelated policy')
    sudo('sysctl','-q','-w','net.ipv4.ping_group_range='+' '.join(original_ping))
   result['pingGroupPolicy']={'before':original_ping,'during':applied_ping or original_ping,'after':ping_file.read_text().split(),'persistentSettingWritten':False}
   assert result['pingGroupPolicy']['after']==original_ping
   assert Path('/proc/sys/net/ipv4/ip_forward').read_text()==original_forward
   assert all(not Path('/proc',pid).exists() for pid in observed_qemu)
   result['pingPolicyRestoredAndForwardingUnchanged']=True
   result['observedQemuChildrenReaped']=True
  except (OSError,ValueError,subprocess.SubprocessError,AssertionError) as error:cleanup.append('Network/process cleanup: '+str(error))
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
  result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/managed-roles-check.py','scripts/install-service-accounts.py','scripts/serve-connected.py','scripts/serve-steward.py','scripts/provision-connected.py','origin_service/discovery.py','guest-relay/server.py','scripts/export-connected.py']}
  serialized=json.dumps(result,indent=2)+'\n'
  (checks/'managed-roles-result.json').write_text(serialized)
  (checks/('managed-roles-hidden-result.json' if base else 'managed-roles-root-result.json')).write_text(serialized)
  print(json.dumps({k:v for k,v in result.items() if k not in ['identity','browser','unixCredentialAccessProbes','sha256']},indent=2))
 return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
