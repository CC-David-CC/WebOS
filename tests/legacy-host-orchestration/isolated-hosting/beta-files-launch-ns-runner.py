#!/usr/bin/env python3
"""Disposable exact-launcher namespace experiment. See SIGNED-PROBE-NOTES.md.

Requires noninteractive sudo, mount namespaces, the public sealed input paths,
ports 19771–19775 free, and the specified pinned Caddy/Python executables.
Never points at live private state or modifies host paths outside its temp dirs.
"""
import argparse,hashlib,json,os,select,shlex,signal,socket,subprocess,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;OPS=HERE.parent/'ops';CAND='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';NATIVE='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21';GW='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1';BASE='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020';OVERLAYS=('1d6b8f4e72e4c3f533afeea10589ac931a3dfe56d4bbaf03abec6d7d99a55d5a','bc3c7e659d40f853ed31bfec257079d65cd92c86011b1b1b86e80f32dd7a9c1c')
p=argparse.ArgumentParser();
for n in ('baseline','overlays','candidate','native-old','native-new','gateway','python','caddy'):p.add_argument('--'+n,required=True)
p.add_argument('--real-caddy',action='store_true');p.add_argument('--real-systemd',action='store_true');p.add_argument('--gate-faults',action='store_true')
p.add_argument('--caddy-port',type=int,default=19936);p.add_argument('--caddy-admin-port',type=int,default=19937)
a=p.parse_args()
if a.gate_faults and not (a.real_caddy and a.real_systemd):p.error('--gate-faults requires --real-caddy and --real-systemd')
if not (1024<=a.caddy_port<=65535 and 1024<=a.caddy_admin_port<=65535) or a.caddy_port==a.caddy_admin_port or a.caddy_port in range(19771,19776) or a.caddy_admin_port in range(19771,19776):p.error('distinct unprivileged Caddy fixture ports outside the issuer range required')
for v in (a.baseline,a.overlays,a.candidate,a.native_old,a.native_new,a.gateway,a.python,a.caddy):
 if not Path(v).is_absolute() or not Path(v).exists():p.error('all inputs must be existing absolute paths')
for port in list(range(19771,19776))+([a.caddy_port,a.caddy_admin_port] if a.real_caddy else []):
 with socket.socket() as s:
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  try:s.bind(('127.0.0.1',port))
  except OSError:p.error('fixture port unavailable: '+str(port))
def call(*cmd,timeout=300):return subprocess.run([str(v) for v in cmd],check=True,timeout=timeout,capture_output=True,text=True)
call('sudo','-n','true');root=Path(tempfile.mkdtemp(prefix='codi-files-ns-'));bundle=Path(call('sudo','-n','mktemp','-d','/root/codi-files-bundle.XXXXXXXX').stdout.strip());issuer=None;proc=None;units=[];initial_issuer_pid=None
q=shlex.quote
try:
 def sudo(*args):return call('sudo','-n',*args)
 def mkdir(path,mode='755'):sudo('mkdir','-p',path);sudo('chmod',mode,path)
 r=root/'root';srv=r/'srv';home=r/'home';var=r/'varlib';etc=r/'etc';backs=r/'varbackups';logs=r/'varlog'
 for path in (srv/'codi-connected/simplified',srv/'codi-connected/beta-overlays',srv/'data/codi-beta-opfs',srv/'data/codi-beta-native',srv/'codi-gateway/releases',home/'dflanag3/webhost-sites/ops',var/'webhost-ops/beta-files-probe',etc/'caddy/private',etc/'systemd/system',etc/'codi-user-files/beta',backs/'webhost-sites',logs/'caddy'):mkdir(path)
 for src,dst in ((a.baseline,srv/'codi-connected/simplified'/BASE),(a.candidate,srv/'data/codi-beta-opfs'/CAND),(a.native_new,srv/'data/codi-beta-native'/NATIVE),(a.gateway,srv/'codi-gateway/releases'/GW)):
  sudo('cp','-a','--reflink=auto',src,dst)
 for n in OVERLAYS:sudo('cp','-a','--reflink=auto',Path(a.overlays)/n,srv/'codi-connected/beta-overlays'/n)
 sudo('chown','-R','root:root',srv);sudo('chmod','-R','go-w',srv)
 sudo('cp','-a',OPS,bundle/'ops');sudo('cp',HERE.parent/'OPFS-ROUTE-TABLE.json',bundle/'OPFS-ROUTE-TABLE.json');sudo('chown','-R','root:root',bundle);sudo('chmod','-R','go-w',bundle)
 for path in (var/'webhost-ops',var/'webhost-ops/beta-files-probe',backs/'webhost-sites'):sudo('chmod','700',path)
 sudo('chown','root:root',var,var/'webhost-ops',var/'webhost-ops/beta-files-probe',backs/'webhost-sites')
 users=[('root',0,0,'/root','/bin/bash'),('dflanag3',1000,1000,'/home/dflanag3','/bin/bash'),('caddy',1001,1001,'/nonexistent','/usr/sbin/nologin')]
 for i,n in enumerate(('codi-issuer','codi-steward','codi-gateway','codi-guest','codi-net-registered','codi-net-anonymous','codi-beta-issuer','codi-beta-gateway','codi-beta-frontend')):users.append((n,21001+i,21001+i,'/nonexistent','/usr/sbin/nologin'))
 acct=root/'accounts';acct.mkdir()
 (acct/'passwd').write_text(''.join(f'{n}:x:{u}:{g}::{h}:{s}\n' for n,u,g,h,s in users));(acct/'group').write_text(''.join(f'{n}:x:{g}:\n' for n,u,g,h,s in users));(acct/'shadow').write_text(''.join(f'{n}:!:19000:0:99999:7:::\n' for n,u,g,h,s in users))
 for n in ('passwd','group','shadow'):sudo('cp',acct/n,etc/n)
 sudo('chmod','600',etc/'shadow')
 for beta,main,uid in (('codi-connected/beta/issuer','codi-connected/ksu/issuer',21007),('codi-gateway/beta','codi-gateway/ksu',21008),('codi-user-files/beta','codi-user-files/ksu',21008)):
  mkdir(var/beta,'700');mkdir(var/main,'700');sudo('chown',f'{uid}:{uid}',var/beta)
 lock=home/'dflanag3/webhost-sites/.controller.lock';sudo('touch',lock);sudo('chmod','644',lock)
 sudo('cp',OPS/'webctl_floor_candidate.py',home/'dflanag3/webhost-sites/ops/webctl.py');sudo('chown',f'{os.getuid()}:{os.getgid()}',home/'dflanag3/webhost-sites/ops/webctl.py');sudo('chmod','644',home/'dflanag3/webhost-sites/ops/webctl.py')
 boot=root/'bootstrap.py';setup=root/'setup.py';caddy_helper=root/'caddy-helper.py';sudo('cp',HERE/'beta-files-launch-ns-bootstrap.py',boot);sudo('cp',HERE/'beta-files-launch-ns-setup.py',setup);sudo('cp',HERE/'beta-files-launch-ns-caddy.py',caddy_helper);sudo('chown','root:root',boot,setup,caddy_helper);sudo('chmod','600',boot,setup,caddy_helper)
 mounts=((srv,'/srv'),(var,'/var/lib'),(backs,'/var/backups'),(logs,'/var/log'),(home,'/home'),(etc,'/etc'))
 prefix=' && '.join('mount --bind '+q(str(src))+' '+q(dst) for src,dst in mounts)+' && '
 env={'CODI_FILES_FIXTURE_ROOT':str(root),'CODI_FILES_FIXTURE_BUNDLE':str(bundle)}
 if a.real_caddy:env.update(CODI_FILES_REAL_CADDY='1',CODI_FILES_FIXTURE_CADDY=a.caddy,CODI_FILES_CADDY_HELPER=str(caddy_helper),CODI_FILES_CADDY_PORT=str(a.caddy_port),CODI_FILES_CADDY_ADMIN=str(a.caddy_admin_port))
 if a.real_systemd:
  unit_prefix='codi-files-test-'+str(os.getpid())+'-'+os.urandom(4).hex();env['CODI_FILES_SYSTEMD_PREFIX']=unit_prefix
  names=[unit_prefix+'-'+x+'.service' for x in ('issuer','frontend','gateway')];planned_units=[Path('/run/systemd/system')/n for n in names]
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
  sudo('python3','-I','-B','-c',code,payload);units=planned_units;sudo('systemctl','daemon-reload');sudo('systemctl','start',*names)
  initial_issuer_pid=call('systemctl','show',names[0],'-p','MainPID','--value').stdout.strip()
  if not initial_issuer_pid.isdigit() or initial_issuer_pid=='0':raise AssertionError('fixture issuer did not start')
 def command(script,action=None):
  opts=' '.join(q(k+'='+v) for k,v in env.items()); tail='exec env '+opts+' '+q(a.python)+' -I -B '+q(str(script))+((' '+q(action)) if action else '')
  if a.real_caddy and script==boot:
   cmd='env '+opts+' '+q(a.python)+' -I -B '+q(str(caddy_helper))
   tail=cmd+' render /etc/caddy/Caddyfile && '+q(a.caddy)+' run --config '+q(str(root/'loopback-caddyfile'))+' --adapter caddyfile >/dev/null 2>&1 & cpid=$!; trap \"kill $cpid 2>/dev/null; wait $cpid 2>/dev/null\" EXIT; '+cmd+' wait && env '+opts+' '+q(a.python)+' -I -B '+q(str(script))+' '+q(action)
  return ['sudo','-n','unshare','-m','sh','-c',prefix+'{ '+tail+'; }']
 def ns(script,action=None):return call(*command(script,action),timeout=300)
 fixture_env=os.environ.copy();fixture_env.update(CODI_NATIVE_BASE=a.native_old,CODI_NATIVE_NEXT=a.native_new,CODI_GATEWAY_ROOT=a.gateway,CODI_BASELINE=a.baseline,CODI_PYTHON=a.python,CODI_CADDY=a.caddy)
 def start_issuer():
  proc=subprocess.Popen([a.python,'-B',str(HERE/'beta-signed-native-fixture.py')],env=fixture_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  ready,_,_=select.select([proc.stdout],[],[],30)
  if not ready or not proc.stdout.readline().startswith('ready '):
   proc.terminate()
   try:proc.communicate(timeout=15)
   except subprocess.TimeoutExpired:proc.kill();proc.communicate()
   raise RuntimeError('signed issuer fixture did not start')
  return proc
 def stop_issuer():
  global issuer
  if issuer is None:return
  issuer.send_signal(signal.SIGINT)
  out=issuer.communicate(timeout=30)[0];code=issuer.returncode;issuer=None
  if code!=0 or 'PASS complete native and gateway inventories after fixture' not in out:raise RuntimeError('signed fixture cleanup/inventory verification failed')
 def provision():
  code='''import http.client,json,sys\nfrom pathlib import Path\nsys.path[:0]=[sys.argv[1]+"/ops",sys.argv[2]+"/codiserver-server-v0.3.0"]\nfrom beta_signed_probe import provision_private\nfrom codiauth import jose\nc=http.client.HTTPConnection("127.0.0.1",19772);c.request("GET","/config.json",headers={"Host":"127.0.0.1:19771"});r=c.getresponse();v=json.loads(r.read());c.close()\np=Path(sys.argv[3]);p.write_text(json.dumps({"identity":v["identity"]}));p.chmod(0o644)\nprovision_private(sys.argv[4],origin="http://127.0.0.1:19771",issuer_port=19772,gateway_port=19771,policy=v["identity"],jose=jose)'''
  sudo(a.python,'-I','-B','-c',code,bundle,a.gateway,etc/'codi-user-files/beta/issuer-policy.json',var/'webhost-ops/beta-files-probe')
 def reset():
  paths=[root/'timer.json',root/'issuer-switched',root/'block',root/'block-gate',root/'blocked-pid',root/'fail-final-health']+[var/'webhost-ops'/n for n in ('opfs-floor.json','opfs-transition.json','files-issuer-switch.json','files-inner-hosting.json','files-normalization.json','files-emergency-gate.json','beta-files-probe/probe.json')]
  code='from pathlib import Path; import sys; [Path(x).unlink(missing_ok=True) for x in sys.argv[1:]]'
  sudo('python3','-I','-B','-c',code,*paths);ns(setup)
 def check_final():
  output=call('sudo','-n','ls','-1',var/'webhost-ops').stdout.splitlines()
  if sorted(output)!=['beta-files-probe','opfs-floor.json']:raise AssertionError('unexpected remaining journals')
  manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
  if 'codi_beta_maintenance = false' not in manifest or ('codi_beta_opfs = "'+CAND+'"') not in manifest:raise AssertionError('wrong final routes')
  digest=call('sudo','-n','sha256sum',etc/'systemd/system/codi-beta-issuer.service').stdout.split()[0]
  if digest!='d3ed82ddf87ff643288baac0a7476b35ed701a016b3d297ccb4a10cfaec224e4':raise AssertionError('wrong final issuer')
  if a.real_systemd and call('systemctl','is-active',*[p.name for p in units]).stdout.splitlines()!=['active']*3:raise AssertionError('fixture systemd dependents did not recover')
  if a.real_systemd and call('systemctl','show',units[0].name,'-p','MainPID','--value').stdout.strip() in ('0',initial_issuer_pid):raise AssertionError('fixture issuer did not restart')
 reset();issuer=start_issuer();provision();assert '"PASS"' in ns(boot,'plan').stdout
 if a.gate_faults:
  for artifact in (srv/'data/codi-beta-opfs'/CAND,srv/'data/codi-beta-native'/NATIVE):
   offline=artifact.with_name(artifact.name+'.fixture-offline');sudo('mv',artifact,offline)
   try:
    result=subprocess.run(command(boot,'apply'),capture_output=True,text=True,timeout=180)
    if result.returncode==0 or subprocess.run(['sudo','-n','test','-e',str(var/'webhost-ops/opfs-floor.json')]).returncode==0:raise AssertionError('missing forward artifact accepted before floor')
    if 'codi_beta_opfs' in (home/'dflanag3/webhost-sites/sites.toml').read_text():raise AssertionError('v2 exposed before floor')
   finally:sudo('mv',offline,artifact)
 sudo('touch',root/'block');proc=subprocess.Popen(command(boot,'apply'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
 deadline=time.monotonic()+180
 while time.monotonic()<deadline and not (root/'blocked-pid').exists():
  if proc.poll() is not None:raise RuntimeError('apply ended before interruption: '+proc.communicate()[0][-2500:])
  time.sleep(.1)
 if not (root/'blocked-pid').exists():proc.terminate();raise RuntimeError('interruption point timeout')
 if subprocess.run(['sudo','-n','test','-f',str(var/'webhost-ops/opfs-floor.json')]).returncode or subprocess.run(['sudo','-n','test','-f',str(var/'webhost-ops/files-issuer-switch.json')]).returncode:raise AssertionError('floor/issuer journal missing')
 pid=(root/'blocked-pid').read_text().strip()
 if not pid.isdigit():raise ValueError('invalid blocked pid')
 cmdline=Path('/proc')/pid/'cmdline'
 if str(boot).encode() not in cmdline.read_bytes():raise ValueError('blocked process identity changed')
 sudo('kill','-KILL',pid);proc.communicate(timeout=30);sudo('unlink',root/'block')
 if a.gate_faults:
  for artifact in (srv/'data/codi-beta-opfs'/CAND,srv/'data/codi-beta-native'/NATIVE):
   offline=artifact.with_name(artifact.name+'.fixture-offline');sudo('mv',artifact,offline)
   try:
    result=subprocess.run(command(boot,'recover'),capture_output=True,text=True,timeout=180)
    if result.returncode==0:raise AssertionError('missing forward artifact accepted after floor')
    manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
    if 'codi_beta_maintenance = true' not in manifest or 'codi_beta_opfs' in manifest:raise AssertionError('missing post-floor artifact did not retain gate')
   finally:sudo('mv',offline,artifact)
 assert 'v2-verified' in ns(boot,'recover').stdout;check_final();stop_issuer()
 reset();issuer=start_issuer();provision();assert '"PASS"' in ns(boot,'apply').stdout;check_final();assert 'v2-verified' in ns(boot,'recover').stdout
 if a.gate_faults:
  # An unavailable candidate closes the verified gate; restore and re-open
  # only after the pinned candidate and signed issuer pass forward checks.
  artifact=srv/'data/codi-beta-opfs'/CAND;offline=artifact.with_name(artifact.name+'.fixture-offline');sudo('mv',artifact,offline)
  try:
   guard=home/'dflanag3/webhost-sites/ops/webctl.py';guard_offline=guard.with_name('webctl.py.fixture-offline');sudo('mv',guard,guard_offline)
   try:
    result=subprocess.run(command(boot,'recover'),capture_output=True,text=True,timeout=180)
    if result.returncode==0 or 'gate closure unverified' not in result.stderr:raise AssertionError('missing controller falsely reported verified gate: '+result.stderr[-1500:])
    if 'codi_beta_opfs' not in (home/'dflanag3/webhost-sites/sites.toml').read_text():raise AssertionError('unavailable controller unexpectedly changed routes')
   finally:sudo('mv',guard_offline,guard)
   result=subprocess.run(command(boot,'recover'),capture_output=True,text=True,timeout=180)
   if result.returncode==0 or 'maintenance gate verified' not in result.stderr:raise AssertionError('missing candidate did not verify gate: '+result.stderr[-1500:])
   manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
   if 'codi_beta_maintenance = true' not in manifest or 'codi_beta_opfs' in manifest:raise AssertionError('unavailable candidate did not persist gate')
  finally:sudo('mv',offline,artifact)
  assert 'v2-verified' in ns(boot,'recover').stdout;check_final()
  # A non-app.js loss and a missing worker must also close the gate.
  for artifact,offline in ((srv/'data/codi-beta-opfs'/CAND/'assets/desktop/apps.json',srv/'data/codi-beta-opfs/fixture-offline-apps.json'),(srv/'codi-gateway/releases'/GW,srv/'codi-gateway/releases/fixture-offline-worker')):
   sudo('mv',artifact,offline)
   try:
    result=subprocess.run(command(boot,'recover'),capture_output=True,text=True,timeout=180)
    if result.returncode==0 or 'maintenance gate verified' not in result.stderr:raise AssertionError('partial candidate/worker loss did not verify gate: '+result.stderr[-1500:])
    manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
    if 'codi_beta_maintenance = true' not in manifest or 'codi_beta_opfs' in manifest:raise AssertionError('partial candidate/worker loss did not persist gate')
   finally:sudo('mv',offline,artifact)
   assert 'v2-verified' in ns(boot,'recover').stdout;check_final()
  # Kill an actual launcher during the gate-only Caddy reload with the 853
  # tree unavailable. Recovery must converge to gate, never restore v1.
  artifact=srv/'data/codi-beta-native'/NATIVE;offline=artifact.with_name(artifact.name+'.fixture-offline');sudo('mv',artifact,offline);sudo('touch',root/'block-gate')
  try:
   proc=subprocess.Popen(command(boot,'recover'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True);deadline=time.monotonic()+180
   while time.monotonic()<deadline and not (root/'blocked-pid').exists():
    if proc.poll() is not None:raise RuntimeError('gate transition ended before interruption: '+proc.communicate()[0][-2500:])
    time.sleep(.1)
   if not (root/'blocked-pid').exists():raise RuntimeError('gate interruption timeout')
   pid=(root/'blocked-pid').read_text().strip()
   if not pid.isdigit() or str(boot).encode() not in (Path('/proc')/pid/'cmdline').read_bytes():raise ValueError('gate process identity changed')
   sudo('kill','-KILL',pid);proc.communicate(timeout=30);sudo('unlink',root/'block-gate')
   result=subprocess.run(command(boot,'recover'),capture_output=True,text=True,timeout=180)
   if result.returncode==0:raise AssertionError('missing native accepted for forward activation')
   manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
   if 'codi_beta_maintenance = true' not in manifest or 'codi_beta_opfs' in manifest:raise AssertionError('interrupted gate recovery did not preserve gate')
  finally:
   if (root/'block-gate').exists():sudo('unlink',root/'block-gate')
   sudo('mv',offline,artifact)
  assert 'v2-verified' in ns(boot,'recover').stdout;check_final()
 stop_issuer()
 if a.gate_faults:
  # Failure after floor.apply has cleared its journal must still close gate.
  reset();issuer=start_issuer();provision();sudo('touch',root/'fail-final-health')
  result=subprocess.run(command(boot,'apply'),capture_output=True,text=True,timeout=180)
  if result.returncode==0 or 'maintenance gate verified' not in result.stderr:raise AssertionError('apply final-health failure did not verify gate: '+result.stderr[-1500:])
  manifest=(home/'dflanag3/webhost-sites/sites.toml').read_text()
  if 'codi_beta_maintenance = true' not in manifest or 'codi_beta_opfs' in manifest:raise AssertionError('apply final-health failure did not persist gate')
  if subprocess.run(['sudo','-n','test','-e',str(var/'webhost-ops/opfs-transition.json')]).returncode==0:raise AssertionError('outer journal was not yet cleared at injected failure')
  if subprocess.run(['sudo','-n','test','-f',str(var/'webhost-ops/files-issuer-switch.json')]).returncode:raise AssertionError('issuer recovery journal missing')
  assert 'v2-verified' in ns(boot,'recover').stdout;check_final();stop_issuer()
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
 if units:
  for operation in ('stop',):
   if subprocess.run(['sudo','-n','systemctl',operation,*[p.name for p in units]],capture_output=True,timeout=40).returncode:cleanup_errors.append('systemd '+operation)
  for unit in units:
   if subprocess.run(['sudo','-n','unlink',str(unit)],capture_output=True).returncode:cleanup_errors.append('fixture unit removal')
  if subprocess.run(['sudo','-n','systemctl','daemon-reload'],capture_output=True,timeout=40).returncode:cleanup_errors.append('systemd reload')
 # Only the two paths returned by this process's mkdtemp calls are removed.
 code='import shutil,sys; [shutil.rmtree(p) for p in sys.argv[1:]]'
 try:sudo('python3','-I','-B','-c',code,root,bundle)
 except Exception as e:raise RuntimeError('fixture cleanup failed; inspect only the two generated temp paths') from e
 if cleanup_errors:raise RuntimeError('fixture cleanup failed: '+', '.join(cleanup_errors))
if passed:print('PASS exact protected launcher: clean apply, killed issuer transition, forward recovery and idempotent recovery; real Caddy='+str(a.real_caddy)+', real systemd='+str(a.real_systemd)+', gate faults='+str(a.gate_faults)+'; other simulations listed in notes')
