"""Beta-only service plan. Installation is intentionally not implemented.

This module renders candidate units, not authorization to install/start them.
The direct loopback topology does not prevent a compromised beta process from
connecting to other local ports. Real systemd/kernel, account-custody,
recovery and end-to-end qualification remain outstanding.
"""
import base64,grp,hashlib,hmac,json,os,pwd,re,stat,subprocess
from pathlib import Path

ORIGIN='https://beta.ksu.codes'
PORTS={'issuer':28118,'frontend':28132,'gateway':28140}
USERS={'issuer':'codi-beta-issuer','gateway':'codi-beta-gateway','frontend':'codi-beta-frontend'}
GATEWAY_MANIFEST='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'
GUEST_SOURCE='4ff040270a2a48fcef6f70c98d574338ba2502e35a29486cd6dead78f2916a5a'
MAIN_FORBIDDEN=('/var/lib/codi-connected/ksu','/var/lib/codi-connected/guest-cookie-codi-ksu-hidden','/var/lib/codi-gateway/ksu','/var/lib/codi-user-files/ksu','/var/lib/codi-guest-network/ksu','/etc/codi-connected/ksu','/etc/codi-user-files/ksu','/etc/codi-guest-network/ksu')
PATHS={'issuer_state':'/var/lib/codi-connected/beta','gateway_state':'/var/lib/codi-gateway/beta','user_files':'/var/lib/codi-user-files/beta','issuer_config':'/etc/codi-connected/beta','gateway_config':'/etc/codi-user-files/beta'}

def _path(value,prefix):
 if not isinstance(value,str) or not value.startswith(prefix+'/') or not re.fullmatch(r'/[A-Za-z0-9_./-]+',value) or '..' in Path(value).parts:raise ValueError('unsafe protected release path')
 return value
def _hash(value):
 if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('exact SHA-256 required')
 return value
def _quote(value):
 if not isinstance(value,str) or any(c in value for c in ('\n','\r','%','"','\\')):raise ValueError('unsafe systemd argument')
 return '"'+value+'"'

def verify_private_issuer_key(path,uid,identity):
 """Check beta's protected private key matches its public issuer policy."""
 from cryptography.hazmat.primitives import serialization
 from cryptography.hazmat.primitives.asymmetric import ec
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=uid or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1 or not 0<info.st_size<=16384:raise ValueError('protected issuer key required')
  raw=os.read(fd,16385)
  if len(raw)!=info.st_size:raise ValueError('issuer key read failed')
  key=serialization.load_pem_private_key(raw,password=None)
  if not isinstance(key,ec.EllipticCurvePrivateKey) or not isinstance(key.curve,ec.SECP256R1):raise ValueError('P-256 issuer key required')
  n=key.public_key().public_numbers();b64=lambda x:base64.urlsafe_b64encode(x.to_bytes(32,'big')).rstrip(b'=').decode('ascii')
  public={'kty':'EC','crv':'P-256','x':b64(n.x),'y':b64(n.y)}
  if not any(item.get('jwk')==public for item in identity.get('authorityKeys',[])):raise ValueError('issuer private key does not match beta policy')
 finally:os.close(fd)

def verify_guest_cookie_separation(file_operator,beta,main):
 beta_raw=file_operator.read(beta,0o600,128);main_raw=file_operator.read(main,0o600,128)
 if not re.fullmatch(rb'[A-Za-z0-9_-]{43,128}',beta_raw) or not re.fullmatch(rb'[A-Za-z0-9_-]{43,128}',main_raw):raise ValueError('bounded guest cookie secret required')
 if hmac.compare_digest(beta_raw,main_raw):raise ValueError('beta and main guest secrets must differ')

def verify_accounts():
 """Read-only preflight; no accounts or groups are created or changed."""
 main=[pwd.getpwnam(name) for name in ('codi-issuer','codi-steward','codi-gateway','codi-guest','codi-net-registered','codi-net-anonymous')]
 beta=[pwd.getpwnam(USERS[role]) for role in ('issuer','gateway','frontend')]
 if len({u.pw_uid for u in beta})!=3 or len({u.pw_gid for u in beta})!=3 or {u.pw_uid for u in beta}&{u.pw_uid for u in main} or {u.pw_gid for u in beta}&{u.pw_gid for u in main}:raise ValueError('Beta accounts and groups must be distinct from one another and main')
 for user in beta:
  if any(other.pw_name!=user.pw_name and (other.pw_uid==user.pw_uid or other.pw_gid==user.pw_gid) for other in pwd.getpwall()):raise ValueError('Beta UID and primary group must be exclusive')
  group=grp.getgrgid(user.pw_gid)
  if user.pw_uid==0 or user.pw_gid==0 or user.pw_dir!='/nonexistent' or user.pw_shell!='/usr/sbin/nologin' or group.gr_name!=user.pw_name or set(group.gr_mem)-{user.pw_name} or set(os.getgrouplist(user.pw_name,user.pw_gid))!={user.pw_gid}:raise ValueError('Dedicated non-login account without extra groups required')
  result=subprocess.run(['/usr/bin/passwd','-S',user.pw_name],check=True,capture_output=True,text=True,timeout=5).stdout.split()
  if len(result)<2 or result[0]!=user.pw_name or result[1]!='L':raise ValueError('Locked beta service account required')
 return {role:{'uid':u.pw_uid,'gid':u.pw_gid} for role,u in zip(('issuer','gateway','frontend'),beta)}

def validate_plan(plan):
 expected={'origin','ports','network','native_release','native_manifest','worker_release','worker_manifest','python','issuer_policy_sha256','guest_source_sha256'}
 if not isinstance(plan,dict) or set(plan)!=expected:raise ValueError('exact beta plan required')
 if plan['origin']!=ORIGIN or plan['ports']!=PORTS or plan['network']!='disabled':raise ValueError('beta origin, ports and disabled networking required')
 _path(plan['native_release'],'/srv/codi-connected/releases');_hash(plan['native_manifest'])
 if Path(plan['native_release']).name not in (plan['native_manifest'],'microduck-issuer-'+plan['native_manifest']):raise ValueError('native release must match its manifest pin')
 _path(plan['worker_release'],'/srv/codi-gateway/releases')
 if plan['worker_manifest']!=GATEWAY_MANIFEST or Path(plan['worker_release']).name!=GATEWAY_MANIFEST:raise ValueError('exact beta worker required')
 _path(plan['python'],'/srv/codi-connected/venvs');_hash(plan['issuer_policy_sha256'])
 if not plan['python'].endswith('/bin/python'):raise ValueError('explicit protected virtualenv interpreter required')
 if plan['guest_source_sha256']!=GUEST_SOURCE:raise ValueError('exact disabled-network frontend source required')
 return True

def verify_inputs(plan,*,worker_verify):
 """Read-only protected artifact/account preflight; never initializes state."""
 validate_plan(plan)
 from file_service import operator as file_operator
 from origin_service.release import verify as verify_native
 identities=verify_accounts()
 native_root=file_operator.protected(plan['native_release'],directory=True)
 # The launcher has already checked every native file against the pinned
 # manifest and enforced root ownership/no symlinks, including @ license paths.
 native=verify_native(native_root)
 if native['manifestSHA256']!=plan['native_manifest']:raise ValueError('native manifest changed')
 verify_guest_source(Path(plan['native_release'])/'guest-relay/server.py')
 # The hosting launcher supplies its pinned full-inventory verifier; the
 # older managed file operator's allowlist excludes the incremental modules.
 worker_verify(Path(plan['worker_release']),plan['worker_manifest'])
 file_operator.verify_python(plan['python'],plan['worker_release'])
 policy_path=Path(PATHS['gateway_config'])/'issuer-policy.json'
 raw=file_operator.read(policy_path,0o644,32768)
 if hashlib.sha256(raw).hexdigest()!=plan['issuer_policy_sha256']:raise ValueError('beta issuer policy pin changed')
 value=json.loads(raw);identity=value.get('identity',value)
 if file_operator.context(identity,'')!=ORIGIN:raise ValueError('issuer policy is not beta')
 protected=[(Path(PATHS['issuer_state'])/'issuer',identities['issuer']['uid']),(Path(PATHS['gateway_state']),identities['gateway']['uid']),(Path(PATHS['user_files']),identities['gateway']['uid'])]
 for path,uid in protected:file_operator.protected(path,mode=0o700,directory=True,uid=uid)
 for path in (Path(PATHS['issuer_config']),Path(PATHS['gateway_config'])):file_operator.protected(path,mode=0o700,directory=True)
 for path,uid in [(Path(PATHS['issuer_state'])/'issuer/state/issuer.pem',identities['issuer']['uid']),(Path(PATHS['issuer_state'])/'issuer/state/accounts.sqlite3',identities['issuer']['uid']),(Path(PATHS['gateway_state'])/'permissions.sqlite3',identities['gateway']['uid']),(Path(PATHS['issuer_config'])/'guest-cookie.secret',0)]:file_operator.protected(path,mode=0o600,uid=uid)
 main=file_operator.read(Path('/var/lib/codi-connected/ksu/public/origin-discovery.json'),0o444,65536)
 def keys(policy):
  entries=policy.get('authorityKeys')
  if not isinstance(entries,list) or not entries:raise ValueError('issuer public keys unavailable')
  try:return {json.dumps(item['jwk'],sort_keys=True,separators=(',',':')) for item in entries}
  except (KeyError,TypeError):raise ValueError('issuer public keys malformed') from None
 if keys(identity)&keys(json.loads(main)['identity']):raise ValueError('beta and main issuer keys overlap')
 verify_private_issuer_key(Path(PATHS['issuer_state'])/'issuer/state/issuer.pem',identities['issuer']['uid'],identity)
 verify_guest_cookie_separation(file_operator,Path(PATHS['issuer_config'])/'guest-cookie.secret',Path('/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret'))
 beta_ids={(path.stat().st_dev,path.stat().st_ino) for path,_ in protected}
 if len(beta_ids)!=len(protected):raise ValueError('beta state roots alias')
 for main in MAIN_FORBIDDEN:
  p=Path(main)
  if p.exists() and (p.stat().st_dev,p.stat().st_ino) in beta_ids:raise ValueError('main and beta state alias')
 return {'origin':ORIGIN,'native_manifest':plan['native_manifest'],'worker_manifest':plan['worker_manifest'],'accounts':identities,'network':'disabled'}

def render_units(plan):
 validate_plan(plan)
 release=plan['native_release'];worker=plan['worker_release'];python=plan['python'];state=PATHS['issuer_state']
 commands={
  'issuer':[python,'-I','-B',release+'/scripts/serve-connected.py','--port',str(PORTS['issuer']),'--runtime-dir',state+'/issuer','--origin',ORIGIN,'--base-path','','--user-files'],
  'gateway':[python,'-I','-B',worker+'/scripts/serve-user-files.py','serve','--state-root',PATHS['gateway_state'],'--data-root',PATHS['user_files'],'--issuer-policy','/run/credentials/codi-beta-gateway.service/issuer-policy.json','--issuer-policy-sha256',plan['issuer_policy_sha256'],'--base-path','','--port',str(PORTS['gateway'])],
  'frontend':[python,'-I','-B',release+'/guest-relay/server.py','--port',str(PORTS['frontend']),'--origin',ORIGIN,'--identity-config-port',str(PORTS['issuer']),'--base-path','','--no-guest-network','--cookie-secret-file','/run/credentials/codi-beta-frontend.service/guest-cookie.secret'],
 }
 common={'UMask':'0077','ProtectSystem':'strict','ProtectHome':'yes','PrivateTmp':'yes','PrivateDevices':'yes','NoNewPrivileges':'yes','ProtectKernelTunables':'yes','ProtectKernelModules':'yes','ProtectControlGroups':'yes','RestrictSUIDSGID':'yes','RestrictNamespaces':'yes','LockPersonality':'yes','RestrictAddressFamilies':'AF_UNIX AF_INET','IPAddressDeny':'any','IPAddressAllow':'127.0.0.0/8','CapabilityBoundingSet':'','AmbientCapabilities':'','MemoryMax':'384M','TasksMax':'64','LimitNOFILE':'256','KillMode':'control-group','Restart':'on-failure','RestartSec':'2s','TimeoutStopSec':'12s','Environment':'PYTHONDONTWRITEBYTECODE=1'}
 result={}
 for role in ('issuer','gateway','frontend'):
  name='codi-beta-'+role+'.service';depends='' if role=='issuer' else 'Requires=codi-beta-issuer.service\nAfter=codi-beta-issuer.service\n'
  settings={**common,'Type':'exec','User':USERS[role],'Group':USERS[role],'ExecStart':' '.join(_quote(x) for x in commands[role]),'InaccessiblePaths':' '.join('-'+p for p in MAIN_FORBIDDEN)}
  if role=='issuer':settings['ReadWritePaths']=state+'/issuer'
  if role=='gateway':
   settings['ReadWritePaths']=PATHS['gateway_state']+' '+PATHS['user_files'];settings['LoadCredential']='issuer-policy.json:'+PATHS['gateway_config']+'/issuer-policy.json'
  if role=='frontend':settings['LoadCredential']='guest-cookie.secret:'+PATHS['issuer_config']+'/guest-cookie.secret'
  result[name]='[Unit]\nDescription=Codi isolated beta '+role+'\n'+depends+'\n[Service]\n'+''.join(k+'='+str(v)+'\n' for k,v in settings.items())+'\n[Install]\nWantedBy=multi-user.target\n'
 return result

def verify_guest_source(path):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('absolute frontend path required')
 for parent in path.parents:
  info=parent.lstat()
  if not stat.S_ISDIR(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022:raise ValueError('protected frontend ancestors required')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  info=os.fstat(fd)
  if not stat.S_ISREG(info.st_mode) or info.st_uid!=0 or info.st_mode&0o022 or info.st_nlink!=1 or info.st_size>262144:raise ValueError('protected bounded frontend required')
  raw=b''
  while len(raw)<=262144:
   chunk=os.read(fd,min(65536,262145-len(raw)))
   if not chunk:break
   raw+=chunk
  after=os.fstat(fd)
  if len(raw)!=info.st_size or (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('frontend changed while reading')
  if hashlib.sha256(raw).hexdigest()!=GUEST_SOURCE:raise ValueError('disabled-network frontend pin changed')
 finally:os.close(fd)
 return True

def install(*_args,**_kwargs):
 raise RuntimeError('Beta unit installation is not yet qualified; plan only')
