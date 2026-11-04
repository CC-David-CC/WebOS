#!/usr/bin/env python3
"""Disposable exact-launcher namespace experiment. See SIGNED-PROBE-NOTES.md.

Requires noninteractive sudo, mount namespaces, the public sealed input paths,
ports 19771–19775 free, and the specified pinned Caddy/Python executables.
Never points at live private state or modifies host paths outside its temp dirs.
"""
import argparse,hashlib,json,os,select,shlex,signal,socket,stat,subprocess,sys,tempfile,time
from pathlib import Path
MAIN=Path(__file__).resolve().parent;HERE=MAIN.parent/'beta-isolated-hosting/tests';OPS=HERE.parent/'ops';CAND='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';NATIVE='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21';GW='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1';BASE='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020';OVERLAYS=('1d6b8f4e72e4c3f533afeea10589ac931a3dfe56d4bbaf03abec6d7d99a55d5a','bc3c7e659d40f853ed31bfec257079d65cd92c86011b1b1b86e80f32dd7a9c1c')
p=argparse.ArgumentParser();
for n in ('baseline','overlays','candidate','native-old','native-new','gateway','python','caddy'):p.add_argument('--'+n,required=True)
p.add_argument('--successor-bundle',required=True);p.add_argument('--main-release',required=True);p.add_argument('--enabled-release',required=True)
p.add_argument('--real-caddy',action='store_true');p.add_argument('--real-systemd',action='store_true');p.add_argument('--real-services',action='store_true');p.add_argument('--gate-faults',action='store_true')
p.add_argument('--kill-stage',choices=('unit-write','reload','restart','timer-stopped'),default='unit-write')
p.add_argument('--caddy-port',type=int,default=19936);p.add_argument('--caddy-admin-port',type=int,default=19937)
a=p.parse_args()
if a.gate_faults and not a.real_caddy:p.error('--gate-faults requires --real-caddy')
if a.real_services and not (a.real_caddy and a.real_systemd):p.error('--real-services requires --real-caddy and --real-systemd')
if a.kill_stage=='timer-stopped' and not a.real_services:p.error('timer-stopped requires --real-services')
if not (1024<=a.caddy_port<=65535 and 1024<=a.caddy_admin_port<=65535) or a.caddy_port==a.caddy_admin_port or a.caddy_port in range(19771,19777) or a.caddy_admin_port in range(19771,19777):p.error('distinct unprivileged Caddy fixture ports outside the issuer range required')
for v in (a.baseline,a.overlays,a.candidate,a.native_old,a.native_new,a.gateway,a.python,a.caddy):
 if not Path(v).is_absolute() or not Path(v).exists():p.error('all inputs must be existing absolute paths')
for port in list(range(19771,19777 if a.real_services else 19776))+([a.caddy_port,a.caddy_admin_port] if a.real_caddy else []):
 with socket.socket() as s:
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  try:s.bind(('127.0.0.1',port))
  except OSError:p.error('fixture port unavailable: '+str(port))
def call(*cmd,timeout=300):
 try:return subprocess.run([str(v) for v in cmd],check=True,timeout=timeout,capture_output=True,text=True)
 except subprocess.CalledProcessError as e:raise RuntimeError('fixture command failed: '+e.stderr[-8000:]) from e
def verify_tree(root,manifest,pin):
 raw=(root/manifest).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('fixture manifest pin mismatch')
 records=json.loads(raw)['files'];seen=set()
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   path=Path(parent)/name
   info=path.lstat()
   if path.is_symlink() or info.st_uid!=0 or info.st_mode&0o022 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):raise ValueError('unsafe fixture release entry')
  for name in files:
   path=Path(parent)/name;relative=path.relative_to(root).as_posix();seen.add(relative)
   if path.stat().st_nlink!=1:raise ValueError('fixture release has linked file')
   if relative==manifest:continue
   h=hashlib.sha256();size=0
   with path.open('rb') as stream:
    while chunk:=stream.read(1024*1024):h.update(chunk);size+=len(chunk)
   if records.get(relative)!={'bytes':size,'sha256':h.hexdigest()}:raise ValueError('fixture release inventory mismatch')
 if seen!=set(records)|{manifest}:raise ValueError('fixture release has missing or extra files')
call('sudo','-n','true');root=Path(tempfile.mkdtemp(prefix='codi-files-ns-'));bundle=Path(call('sudo','-n','mktemp','-d','/root/codi-files-bundle.XXXXXXXX').stdout.strip());issuer=None;proc=None;units=[];timer_units=[];fixture_mounts=[];mount_root=None;initial_issuer_pid=None
q=shlex.quote
try:
 def sudo(*args):return call('sudo','-n',*args)
 def mkdir(path,mode='755'):sudo('mkdir','-p',path);sudo('chmod',mode,path)
 r=root/'root';srv=r/'srv';home=r/'home';var=r/'varlib';etc=r/'etc';backs=r/'varbackups';logs=r/'varlog'
 for path in (srv/'codi-connected/simplified',srv/'codi-connected/beta-overlays',srv/'data/codi-beta-opfs',srv/'data/codi-beta-native',srv/'codi-gateway/releases',home/'dflanag3/webhost-sites/ops',var/'webhost-ops/beta-files-probe',etc/'caddy/private',etc/'systemd/system',etc/'codi-user-files/beta',backs/'webhost-sites',logs/'caddy'):mkdir(path)
 for src,dst in ((a.baseline,srv/'codi-connected/simplified'/BASE),(a.candidate,srv/'data/codi-beta-opfs'/CAND),(a.native_new,srv/'data/codi-beta-native'/NATIVE),(a.gateway,srv/'codi-gateway/releases'/GW)):
  sudo('cp','-a','--reflink=auto',src,dst)
 if a.real_services:sudo('cp','-a','--reflink=auto',a.native_old,srv/'data/codi-beta-native/1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51')
 for n in OVERLAYS:sudo('cp','-a','--reflink=auto',Path(a.overlays)/n,srv/'codi-connected/beta-overlays'/n)
 sudo('chown','-R','root:root',srv);sudo('chmod','-R','go-w',srv)
 if a.real_services:
  sudo('chmod','711',root);sudo('mkdir',root/'coord');sudo('chmod','755',root/'coord');sudo('chmod','-R','a+rX',srv/'data/codi-beta-native',srv/'codi-gateway/releases'/GW)
  verify_tree(srv/'data/codi-beta-native/1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51','connected-release.json','1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51')
  verify_tree(srv/'data/codi-beta-native'/NATIVE,'connected-release.json',NATIVE)
  verify_tree(srv/'codi-gateway/releases'/GW,'files-service.json',GW)
 sudo('cp','-a',OPS,bundle/'ops');sudo('cp',HERE.parent/'OPFS-ROUTE-TABLE.json',bundle/'OPFS-ROUTE-TABLE.json');sudo('chown','-R','root:root',bundle);sudo('chmod','-R','go-w',bundle)
 for path in (var/'webhost-ops',var/'webhost-ops/beta-files-probe',backs/'webhost-sites'):sudo('chmod','700',path)
 sudo('chown','root:root',var,var/'webhost-ops',var/'webhost-ops/beta-files-probe',backs/'webhost-sites')
 users=[('root',0,0,'/root','/bin/bash'),('dflanag3',1000,1000,'/home/dflanag3','/bin/bash'),('caddy',1001,1001,'/nonexistent','/usr/sbin/nologin')]
 for i,n in enumerate(('codi-issuer','codi-steward','codi-gateway','codi-guest','codi-net-registered','codi-net-anonymous','codi-beta-issuer','codi-beta-gateway','codi-beta-frontend')):users.append((n,21001+i,21001+i,'/nonexistent','/usr/sbin/nologin'))
 acct=root/'accounts';acct.mkdir()
 (acct/'passwd').write_text(''.join(f'{n}:x:{u}:{g}::{h}:{s}\n' for n,u,g,h,s in users));(acct/'group').write_text(''.join(f'{n}:x:{g}:\n' for n,u,g,h,s in users));(acct/'shadow').write_text(''.join(f'{n}:!:19000:0:99999:7:::\n' for n,u,g,h,s in users))
 for n in ('passwd','group','shadow'):sudo('cp',acct/n,etc/n)
 sudo('chmod','600',etc/'shadow')
 if a.real_services:sudo('chown','root:root',root)
 for beta,main,uid in (('codi-connected/beta/issuer','codi-connected/ksu/issuer',21007),('codi-gateway/beta','codi-gateway/ksu',21008),('codi-user-files/beta','codi-user-files/ksu',21008)):
  mkdir(var/beta,'700');mkdir(var/main,'700');sudo('chown',f'{uid}:{uid}',var/beta)
 lock=home/'dflanag3/webhost-sites/.controller.lock';sudo('touch',lock);sudo('chmod','644',lock)
 sudo('cp',OPS/'webctl_floor_candidate.py',home/'dflanag3/webhost-sites/ops/webctl.py');sudo('chown',f'{os.getuid()}:{os.getgid()}',home/'dflanag3/webhost-sites/ops/webctl.py');sudo('chmod','644',home/'dflanag3/webhost-sites/ops/webctl.py')
 boot=root/'bootstrap.py';setup=root/'setup.py';caddy_helper=root/'caddy-helper.py';sudo('cp',MAIN/'main-release-ns-bootstrap.py',boot);sudo('cp',HERE/'beta-files-launch-ns-setup.py',setup);sudo('cp',HERE/'beta-files-launch-ns-caddy.py',caddy_helper);sudo('chown','root:root',boot,setup,caddy_helper);sudo('chmod','600',boot,setup,caddy_helper)
 service_helper=root/'systemd-service.py'
 unit_mapper=root/'systemd-map.py'
 if a.real_services:
  sudo('cp',HERE/'beta-files-launch-systemd-service.py',service_helper);sudo('cp',HERE/'beta-files-launch-systemd-map.py',unit_mapper);sudo('chown','root:root',service_helper,unit_mapper);sudo('chmod','755',service_helper,unit_mapper)
 mounts=((srv,'/srv'),(var,'/var/lib'),(backs,'/var/backups'),(logs,'/var/log'),(home,'/home'),(etc,'/etc'))
 prefix=' && '.join('mount --bind '+q(str(src))+' '+q(dst) for src,dst in mounts)+' && '
 env={'CODI_FILES_FIXTURE_ROOT':str(root),'CODI_FILES_FIXTURE_BUNDLE':str(bundle),'CODI_FILES_KILL_STAGE':a.kill_stage}
 if a.real_caddy:env.update(CODI_FILES_REAL_CADDY='1',CODI_FILES_FIXTURE_CADDY=a.caddy,CODI_FILES_CADDY_HELPER=str(caddy_helper),CODI_FILES_CADDY_PORT=str(a.caddy_port),CODI_FILES_CADDY_ADMIN=str(a.caddy_admin_port))
 if a.real_systemd:
  unit_prefix='codi-files-test-'+str(os.getpid())+'-'+os.urandom(4).hex();env['CODI_FILES_SYSTEMD_PREFIX']=unit_prefix
  names=[unit_prefix+'-'+x+'.service' for x in ('issuer','frontend','gateway')];planned_units=[Path('/run/systemd/system')/n for n in names]
  if a.real_services:
   env['CODI_FILES_REAL_SERVICES']='1';env['CODI_FILES_REAL_TIMER']='1';env['CODI_FILES_UNIT_MAPPER']=str(unit_mapper)
   timer_names=[unit_prefix+'-renew.service',unit_prefix+'-renew.timer'];planned_timer=[Path('/run/systemd/system')/n for n in timer_names]
   mount_root=Path('/run')/(unit_prefix+'-inputs');sudo('mkdir',mount_root);sudo('chmod','755',mount_root)
   for name,source in (('old',srv/'data/codi-beta-native/1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'),('new',srv/'data/codi-beta-native'/NATIVE),('gateway',srv/'codi-gateway/releases'/GW),('venv',Path(a.python).parent.parent),('coord',root/'coord')):
    target=mount_root/name;sudo('mkdir',target);sudo('mount','--bind',source,target);fixture_mounts.append(target);sudo('mount','-o','remount,bind,ro',target)
   # Nominal capacity exceeds the gateway's 5 GiB floor; tmpfs is sparse and
   # this fixture writes only small disposable probe records, not 128 MiB.
   sudo('mkdir',mount_root/'data');sudo('mount','-t','tmpfs','-o','size=5200M,mode=1777','tmpfs',mount_root/'data');fixture_mounts.append(mount_root/'data')
   sudo('cp',service_helper,mount_root/'service.py');sudo('chmod','755',mount_root/'service.py')
   system_python=str(mount_root/'venv/bin/python');system_helper=str(mount_root/'service.py')
   for path in (system_python,system_helper,str(mount_root),unit_prefix):
    if any(ch.isspace() or ch in '%\\"' for ch in path):raise ValueError('systemd fixture paths must not require escaping')
   old=str(mount_root/'old');new=str(mount_root/'new');gateway=str(mount_root/'gateway')
   def unit(role):
    depends='' if role=='issuer' else 'Requires='+names[0]+'\nAfter='+names[0]+'\n'
    args=' '.join((system_python,'-B',system_helper,role,system_python,old,new,gateway,str(mount_root/'coord'),unit_prefix,str(mount_root/'data'),'old'))
    extra='Environment=TMPDIR='+str(mount_root/'data/tmp')+'\nReadWritePaths='+str(mount_root/'data')+'\n' if role=='gateway' else ''
    return '[Unit]\nDescription=Disposable Files '+role+'\nStartLimitIntervalSec=0\n'+depends+'[Service]\nType=exec\nDynamicUser=yes\nRuntimeDirectory='+unit_prefix+'-'+role+'\nRuntimeDirectoryMode=0700\nRuntimeDirectoryPreserve=yes\nNoNewPrivileges=yes\nStandardOutput=null\nStandardError=null\n'+extra+'ExecStart='+args+'\n'
   payload=json.dumps({str(planned_units[i]):unit(role) for i,role in enumerate(('issuer','frontend','gateway'))}|{str(planned_timer[0]):'[Unit]\nDescription=Disposable Files timer service\n[Service]\nType=oneshot\nExecStart=/usr/bin/true\n',str(planned_timer[1]):'[Unit]\nDescription=Disposable Files timer\n[Timer]\nOnActiveSec=1d\nUnit='+timer_names[0]+'\n[Install]\nWantedBy=timers.target\n'})
  else:
   issuer_unit='[Unit]\nDescription=Disposable Files issuer\nStartLimitIntervalSec=0\n[Service]\nType=simple\nExecStart=/usr/bin/sleep infinity\n'
   def unit(role):return '[Unit]\nDescription=Disposable Files '+role+'\nStartLimitIntervalSec=0\nRequires='+names[0]+'\nAfter='+names[0]+'\n[Service]\nType=simple\nExecStart=/usr/bin/sleep infinity\n'
   payload=json.dumps({str(planned_units[0]):issuer_unit,str(planned_units[1]):unit('frontend'),str(planned_units[2]):unit('gateway')})
  code='''import json,os,sys
created=[]
try:
 for p,v in json.loads(sys.argv[1]).items():
  fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644);created.append(p)
  with os.fdopen(fd,'wb') as f:f.write(v.encode());f.flush();os.fsync(f.fileno())
except BaseException:
 for p in created:os.unlink(p)
 raise'''
  sudo('python3','-I','-B','-c',code,payload);units=planned_units;timer_units=planned_timer if a.real_services else [];sudo('systemctl','daemon-reload')
  if a.real_services:sudo('systemctl','start',timer_names[1])
  else:
   sudo('systemctl','start',*names);initial_issuer_pid=call('systemctl','show',names[0],'-p','MainPID','--value').stdout.strip()
   if not initial_issuer_pid.isdigit() or initial_issuer_pid=='0':raise AssertionError('fixture issuer did not start')
 def command(script,action=None):
  opts=' '.join(q(k+'='+v) for k,v in env.items()); tail='exec env '+opts+' '+q(a.python)+' -I -B '+q(str(script))+((' '+q(action)) if action else '')
  if a.real_caddy and script==boot:
   cmd='env '+opts+' '+q(a.python)+' -I -B '+q(str(caddy_helper))
   tail=cmd+' render /etc/caddy/Caddyfile && '+q(a.caddy)+' run --config '+q(str(root/'loopback-caddyfile'))+' --adapter caddyfile >/dev/null 2>&1 & cpid=$!; trap \"kill $cpid 2>/dev/null; wait $cpid 2>/dev/null\" EXIT; '+cmd+' wait && env '+opts+' '+q(a.python)+' -I -B '+q(str(script))+' '+q(action)
  return ['sudo','-n','unshare','-m','sh','-c',prefix+'{ '+tail+'; }']
 def ns(script,action=None):return call(*command(script,action),timeout=300)
 fixture_env=os.environ.copy();fixture_env.update(CODI_NATIVE_BASE=a.native_old,CODI_NATIVE_NEXT=a.native_new,CODI_GATEWAY_ROOT=a.gateway,CODI_BASELINE=a.baseline,CODI_PYTHON=a.python,CODI_CADDY=a.caddy)
 if a.real_services:fixture_env.update(CODI_REAL_SERVICES_PREFIX=unit_prefix,CODI_REAL_SERVICES_POLICY=str(root/'coord/fixture-systemd-policy.json'))
 def start_issuer():
  global issuer,initial_issuer_pid
  proc=subprocess.Popen([a.python,'-B',str(HERE/'beta-signed-native-fixture.py')],env=fixture_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  issuer=proc
  ready,_,_=select.select([proc.stdout],[],[],30)
  first=proc.stdout.readline() if ready else ''
  if not first.startswith('ready '):
   try:rest=proc.communicate(timeout=3)[0]
   except subprocess.TimeoutExpired:
    proc.terminate()
    try:rest=proc.communicate(timeout=15)[0]
    except subprocess.TimeoutExpired:proc.kill();rest=proc.communicate()[0]
   issuer=None;raise RuntimeError('signed issuer fixture did not start: '+(first+rest)[-2000:])
  if a.real_services:
   pids=[call('systemctl','show',unit.name,'-p','MainPID','--value').stdout.strip() for unit in units]
   if any(not value.isdigit() or value=='0' for value in pids):raise AssertionError('sealed fixture service did not start')
   uids=[]
   for pid in pids:
    status=Path('/proc')/pid/'status';line=next(line for line in status.read_text().splitlines() if line.startswith('Uid:'));uids.append(int(line.split()[1]))
   if len(set(uids))!=3 or any(uid in (0,os.getuid()) for uid in uids):raise AssertionError('fixture DynamicUser identities overlap')
   expected=(str(mount_root/'old/scripts/serve-connected.py'),str(mount_root/'old/guest-relay/server.py'),str(mount_root/'gateway/scripts/serve-user-files.py'))
   for pid,path in zip(pids,expected):
    if path.encode() not in (Path('/proc')/pid/'cmdline').read_bytes():raise AssertionError('unexpected fixture service executable')
   # An old unit cannot be reported as 853, and a corrupt operator unit
   # must not modify the mapped fixture systemd unit.
   import http.client
   c=http.client.HTTPConnection('127.0.0.1',19774,timeout=5);c.request('GET','/restart');response=c.getresponse();response.read();c.close()
   if response.status!=500:raise AssertionError('old issuer falsely satisfied 853 health')
   bad=root/'bad-issuer-unit';sudo('cp',etc/'systemd/system/codi-beta-issuer.service',bad);sudo('chmod','644',bad)
   sudo('python3','-I','-B','-c','import sys;open(sys.argv[1],"ab").write(b"\\n# invalid\\n")',bad)
   before=call('sudo','-n','sha256sum',units[0]).stdout.split()[0]
   rejected=subprocess.run(['sudo','-n',a.python,'-I','-B',str(unit_mapper),str(bad),str(units[0])],capture_output=True,text=True,timeout=15)
   after=call('sudo','-n','sha256sum',units[0]).stdout.split()[0];sudo('unlink',bad)
   if rejected.returncode==0 or before!=after:raise AssertionError('corrupt operator unit changed fixture ExecStart')
   initial_issuer_pid=pids[0]
  return proc
 def stop_issuer():
  global issuer
  if issuer is None:return
  issuer.send_signal(signal.SIGINT)
  out=issuer.communicate(timeout=30)[0];code=issuer.returncode;issuer=None
  if code!=0 or 'PASS complete native and gateway inventories after fixture' not in out:raise RuntimeError('signed fixture cleanup/inventory verification failed')
 def provision():
  code='''import http.client,json,sys\nfrom pathlib import Path\nsys.path[:0]=[sys.argv[1]+"/ops",sys.argv[2]+"/codiserver-server-v0.3.0"]\nfrom beta_signed_probe import provision_private\nfrom codiauth import jose\nc=http.client.HTTPConnection("127.0.0.1",19772);c.request("GET","/config.json",headers={"Host":"127.0.0.1:19771"});r=c.getresponse();v=json.loads(r.read());c.close()\np=Path(sys.argv[3]);p.write_text(json.dumps({"identity":v["identity"]}));p.chmod(0o644)\nprovision_private(sys.argv[4],origin="http://127.0.0.1:19771",issuer_port=19772,gateway_port=19771,policy=v["identity"],jose=jose)'''
  try:sudo(a.python,'-I','-B','-c',code,bundle,a.gateway,etc/'codi-user-files/beta/issuer-policy.json',var/'webhost-ops/beta-files-probe')
  except subprocess.CalledProcessError as error:raise RuntimeError('disposable signed probe provisioning failed: '+error.stderr[-1500:]) from error
 def reset():
  paths=[root/'timer.json',root/'issuer-switched',root/'coord/fixture-systemd-policy.json',root/'block',root/'block-gate',root/'blocked-pid',root/'fail-final-health']+[var/'webhost-ops'/n for n in ('opfs-floor.json','opfs-transition.json','files-issuer-switch.json','files-inner-hosting.json','files-normalization.json','files-emergency-gate.json','beta-files-probe/probe.json')]
  code='from pathlib import Path; import sys; [Path(x).unlink(missing_ok=True) for x in sys.argv[1:]]'
  sudo('python3','-I','-B','-c',code,*paths)
  if a.real_services:
   code='import shutil,sys; from pathlib import Path; [shutil.rmtree(p) for x in sys.argv[1:] if (p:=Path(x)).exists()]'
   sudo('python3','-I','-B','-c',code,*[mount_root/'data'/name for name in ('state','data','tmp')])
  ns(setup)
  if a.real_services:
   sudo(a.python,'-I','-B',unit_mapper,etc/'systemd/system/codi-beta-issuer.service',units[0]);sudo('systemctl','daemon-reload')
 def check_final():
  output=call('sudo','-n','ls','-1',var/'webhost-ops').stdout.splitlines()
  if sorted(output)!=['beta-files-probe','opfs-floor.json']:raise AssertionError('unexpected remaining journals')
  manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
  if (root/'main-e7-seeded').exists() and 'e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480' not in manifest:raise AssertionError('recovery changed the e7 main selector')
  if 'codi_beta_maintenance = false' not in manifest or ('codi_beta_opfs = "'+CAND+'"') not in manifest:raise AssertionError('wrong final routes')
  digest=call('sudo','-n','sha256sum',etc/'systemd/system/codi-beta-issuer.service').stdout.split()[0]
  if digest!='d3ed82ddf87ff643288baac0a7476b35ed701a016b3d297ccb4a10cfaec224e4':raise AssertionError('wrong final issuer')
  if a.real_systemd and call('systemctl','is-active',*[p.name for p in units]).stdout.splitlines()!=['active']*3:raise AssertionError('fixture systemd dependents did not recover')
  if a.real_systemd and call('systemctl','show',units[0].name,'-p','MainPID','--value').stdout.strip() in ('0',initial_issuer_pid):raise AssertionError('fixture issuer did not restart')
  if a.real_services:
   pid=call('systemctl','show',units[0].name,'-p','MainPID','--value').stdout.strip()
   if str(mount_root/'new/scripts/serve-connected.py').encode() not in (Path('/proc')/pid/'cmdline').read_bytes():raise AssertionError('fixture issuer is not running sealed 853')
   if call('systemctl','is-active',timer_units[1].name).stdout.strip()!='active':raise AssertionError('fixture timer not restored')
   enabled=subprocess.run(['systemctl','is-enabled',timer_units[1].name],capture_output=True,text=True)
   if enabled.stdout.strip()!='disabled':raise AssertionError('fixture timer enablement changed')
 reset();issuer=start_issuer();provision();assert '"PASS"' in ns(boot,'apply').stdout;check_final()
 # Fixture-only staging of the protected candidate inputs; no host paths are used.
 successor=Path(a.successor_bundle);mainrelease=Path(a.main_release)
 if not mainrelease.is_absolute() or not mainrelease.is_dir():raise ValueError('Absolute main candidate required')
 guard=home/'dflanag3/webhost-sites/ops/webctl.py';sudo('cp',MAIN/'webctl-main-guard.py',guard);sudo('chown',f'{os.getuid()}:{os.getgid()}',guard);sudo('chmod','644',guard)
 operators=srv/'codi-connected/operators';mkdir(operators)
 successor_dest=operators/'beta-recovery-e7-v1';sudo('cp','-a',successor,successor_dest);sudo('chown','-R','root:root',successor_dest);sudo('chmod','-R','go-w',successor_dest)
 beta_input=operators/'files-install-input-ce18b7794adc2472';sudo('mkdir',beta_input);sudo('cp','-a',OPS,beta_input/'ops');sudo('chown','-R','root:root',beta_input);sudo('chmod','-R','go-w',beta_input)
 main=operators/'main-qualified-e7e8-v1';sudo('mkdir',main)
 for name in ('main-successor-preflight.py','forward-transaction.py','render-inventory.py'):sudo('cp',MAIN/name,main/name)
 enabled=Path(a.enabled_release)/'main-launcher.py'
 if hashlib.sha256(enabled.read_bytes()).hexdigest()!='6469eb631aec6e9d37496dd1547a04dbbda9ea112e280b695c8ea426368f8642':raise ValueError('enabled launcher pin mismatch')
 sudo('cp',enabled,main/'main-launcher.py')
 sudo('chown','-R','root:root',main);sudo('chmod','-R','go-w',main)
 candidate=srv/'codi-connected/simplified/e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480';sudo('cp','-a','--reflink=auto',mainrelease,candidate);sudo('chown','-R','root:root',candidate);sudo('chmod','-R','go-w',candidate)
 env['CODI_MAIN_LAUNCH']='1';env['CODI_MAIN_LAUNCHER_SHA256']='6469eb631aec6e9d37496dd1547a04dbbda9ea112e280b695c8ea426368f8642'
 assert '"PASS"' in ns(boot,'plan').stdout
 # Kill at the actual controller reload after the forward journal is durable.
 sudo('touch',root/'block-main');proc=subprocess.Popen(command(boot,'apply'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True);deadline=time.monotonic()+240
 while time.monotonic()<deadline and not (root/'blocked-pid').exists():
  if proc.poll() is not None:raise RuntimeError('main apply failed before interruption: '+proc.communicate()[0][-5000:])
  time.sleep(.1)
 if not (root/'blocked-pid').exists():raise RuntimeError('main interruption timeout')
 pid=(root/'blocked-pid').read_text().strip()
 if not pid.isdigit() or str(boot).encode() not in (Path('/proc')/pid/'cmdline').read_bytes():raise ValueError('main process identity changed')
 if subprocess.run(['sudo','-n','test','-f',str(var/'webhost-ops/main-restriction-journal.json')]).returncode:raise AssertionError('main forward journal missing')
 sudo('kill','-KILL',pid);proc.communicate(timeout=30);sudo('unlink',root/'block-main')
 recovered=ns(boot,'recover').stdout
 if '"PASS"' not in recovered:raise AssertionError('main forward recovery failed: '+recovered)
 if subprocess.run(['sudo','-n','test','-e',str(var/'webhost-ops/main-restriction-journal.json')]).returncode==0:raise AssertionError('main journal not cleared')
 manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
 if 'e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480' not in manifest or 'codi_beta_opfs = "'+CAND+'"' not in manifest:raise AssertionError('wrong final main/beta selectors')
 check_final()

 stop_issuer()
 passed=True
finally:
 if proc is not None and proc.poll() is None:
  blocked=root/'blocked-pid'
  if blocked.exists():
   pid=blocked.read_text().strip()
   if pid.isdigit():
    try:
     if str(boot).encode() in (Path('/proc')/pid/'cmdline').read_bytes():subprocess.run(['sudo','-n','kill','-KILL',pid],capture_output=True)
    except OSError:pass
  try:proc.communicate(timeout=15)
  except subprocess.TimeoutExpired:
   subprocess.run(['sudo','-n','kill','-KILL','--','-'+str(proc.pid)],capture_output=True);proc.communicate(timeout=15)
 if issuer is not None:
  issuer.send_signal(signal.SIGINT)
  try:issuer.communicate(timeout=30)
  except subprocess.TimeoutExpired:issuer.kill();issuer.communicate()
 cleanup_errors=[]
 if timer_units:
  if subprocess.run(['sudo','-n','systemctl','stop',timer_units[1].name,timer_units[0].name],capture_output=True,timeout=40).returncode:cleanup_errors.append('fixture timer stop')
 if units:
  for operation in ('stop',):
   if subprocess.run(['sudo','-n','systemctl',operation,*[p.name for p in units]],capture_output=True,timeout=40).returncode:cleanup_errors.append('systemd '+operation)
  for unit in units:
   state=subprocess.run(['systemctl','show',unit.name,'-p','ActiveState','--value'],capture_output=True,text=True,timeout=20)
   if state.stdout.strip()=='failed' and subprocess.run(['sudo','-n','systemctl','reset-failed',unit.name],capture_output=True,timeout=40).returncode:cleanup_errors.append('systemd failed-state cleanup')
  if a.real_services:
   for unit in units:
    runtime='/run/'+unit.name.removesuffix('.service')
    if subprocess.run(['sudo','-n','test','-e',runtime]).returncode==0 and subprocess.run(['sudo','-n','systemctl','clean','--what=runtime',unit.name],capture_output=True,timeout=40).returncode:cleanup_errors.append('fixture runtime cleanup')
  for unit in units+timer_units:
   if subprocess.run(['sudo','-n','unlink',str(unit)],capture_output=True).returncode:cleanup_errors.append('fixture unit removal')
  if subprocess.run(['sudo','-n','systemctl','daemon-reload'],capture_output=True,timeout=40).returncode:cleanup_errors.append('systemd reload')
 for target in reversed(fixture_mounts):
  if subprocess.run(['sudo','-n','umount',str(target)],capture_output=True,timeout=40).returncode:cleanup_errors.append('fixture bind unmount')
 if mount_root:
  for name in ('service.py','data','coord','venv','gateway','new','old'):
   path=mount_root/name
   if subprocess.run(['sudo','-n','rm' if name=='service.py' else 'rmdir',str(path)],capture_output=True).returncode:cleanup_errors.append('fixture bind path removal')
  if subprocess.run(['sudo','-n','rmdir',str(mount_root)],capture_output=True).returncode:cleanup_errors.append('fixture bind root removal')
 # Only the two paths returned by this process's mkdtemp calls are removed.
 code='import shutil,sys; [shutil.rmtree(p) for p in sys.argv[1:]]'
 try:sudo('python3','-I','-B','-c',code,root,bundle)
 except Exception as e:raise RuntimeError('fixture cleanup failed; inspect only the two generated temp paths') from e
 if cleanup_errors:raise RuntimeError('fixture cleanup failed: '+', '.join(cleanup_errors))
if passed:print('PASS literal pinned enabled main launcher: real Caddy main forward interruption and recovery; main/beta selectors preserved; health/service substitutions apply')
