#!/usr/bin/env python3
"""Execute actual launcher main with explicitly mapped host operations.

Requires the documented dev-issuer/Caddy fixture, Chrome, and source registry.
Systemd starts real sealed dd8/a626 gateways; no production unit is touched.
"""
import contextlib,fcntl,hashlib,importlib.util,io,json,multiprocessing,os,pathlib,secrets,shutil,socket,subprocess,sys,tempfile,time,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];source=root/'research/cad-source-access';spec=importlib.util.spec_from_file_location('cad_switch',source/'beta-switch.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert os.geteuid()==0
oldroot=pathlib.Path('/tmp/codi-native-continuity-gateway-clean');newroot=pathlib.Path('/tmp/codi-cad-source-gateway-r2');python='/tmp/codi-audio-upload-19584-venv/bin/python';registry='/var/lib/codi-cad-source-exact-test';pin='e304a1c451a380d21caebb306e47803a4b5de8a098d31cdaa3d60241367551a6'
for p,want in ((oldroot,'dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'),(newroot,m.WORKER)):
 raw=(p/'files-service.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==want
 for n,v in json.loads(raw)['files'].items():
  b=(p/n).read_bytes();assert v=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
name='codi-cad-launcher-test-'+secrets.token_hex(5)+'.service';systemunit=pathlib.Path('/run/systemd/system')/name;worker_lock=pathlib.Path('/run/lock')/(name+'.lock')
def ctl(*args):subprocess.run(['/usr/bin/systemctl',*args],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=60)
def status():
 req=urllib.request.Request('http://127.0.0.1:20089/healthz',headers={'Host':'127.0.0.1:20080'})
 with urllib.request.urlopen(req,timeout=2) as r:assert r.status==200
def wait():
 for _ in range(100):
  try:status();return
  except OSError:time.sleep(.1)
 raise RuntimeError('mapped gateway unavailable')
def protect_tree(p):
 for parent,dirs,files in os.walk(p):
  os.chmod(parent,0o755)
  for n in files:os.chmod(pathlib.Path(parent)/n,0o644)
with tempfile.TemporaryDirectory(prefix='codi-cad-launcher-',dir='/run') as tmp:
 d=pathlib.Path(tmp);os.chmod(d,0o755);bundle=d/'bundle';bundle.mkdir()
 for n in ('beta-switch.py','beta-transition.py'):shutil.copy2(source/n,bundle/n)
 protect_tree(bundle)
 for src,dest in ((pathlib.Path('/tmp/codi-cad-beta-actor-base'),d/'oldactor'),(pathlib.Path('/tmp/codi-cad-beta-actor-v2'),d/'newactor')):shutil.copytree(src,dest);protect_tree(dest)
 hostroot=d/'host';hostroot.mkdir();(hostroot/'.controller.lock').write_bytes(b'');(hostroot/'.controller.lock').chmod(0o600)
 workerroot=d/'worker';workerroot.mkdir(mode=0o700);state=d/'state';state.mkdir(mode=0o700);data=d/'data';data.mkdir(mode=0o700)
 with urllib.request.urlopen('http://127.0.0.1:20080/config.json',timeout=5) as r:identity=json.load(r)['identity']
 policy=d/'policy.json';raw=json.dumps(identity,sort_keys=True).encode();policy.write_bytes(raw);policy.chmod(0o600);policyhash=hashlib.sha256(raw).hexdigest()
 args=['--state-root',str(state),'--data-root',str(data),'--issuer-policy',str(policy),'--issuer-policy-sha256',policyhash,'--port','20089','--base-path','']
 subprocess.run([python,'-I','-B',str(oldroot/'scripts/serve-user-files.py'),'initialize',*args],check=True,capture_output=True)
 def mapped_unit(release):
  command=[python,'-I','-B',str(release/'scripts/serve-user-files.py'),'serve',*args]
  if release==newroot:command+=['--cad-source-root',registry,'--cad-source-manifest-sha256',pin]
  return ('[Unit]\nDescription=Disposable CAD mapped gateway\nStartLimitIntervalSec=0\n[Service]\nType=exec\nExecStart='+' '.join('"'+x+'"' for x in command)+'\n').encode()
 old=(source/'beta-unit-f7fe.txt').read_bytes();unit=d/'gateway.unit';unit.write_bytes(old);unit.chmod(0o644)
 # All following mappings are test-only; runtime modules/actor pins are actual.
 m.__file__=str(bundle/'beta-switch.py');m.HERE=bundle;m.OLD_ACTOR=d/'oldactor';m.NEW_ACTOR=d/'newactor';m.UNIT=unit;m.JOURNAL=d/'main-restriction-journal.json';m.socket.gethostname=lambda:'box-webhost'
 original_actor=m.actor
 def mapped_actor(path,digest):
  actor=original_actor(path,digest);load=actor.load
  def mapped_load(key,*a,**kw):
   result=load(key,*a,**kw)
   if key=='beta_launcher':result.ROOT=hostroot
   if key=='beta_worker_adapter':result.ROOT=workerroot;result.LOCK=worker_lock
   return result
  actor.load=mapped_load;return actor
 m.actor=mapped_actor
 m.Host.guards=lambda self:{'fixture-policy':policyhash}
 m.Host.verify_candidate=lambda self:(pathlib.Path(registry)/'manifest.json').read_bytes()
 m.Host.health=lambda self,actor:(status(),ctl('is-active','--quiet',name))
 orig_write=m.Host.write_unit;orig_check=m.Host.check_guards;phase={'name':''}
 def write(self,value):
  orig_write(self,value)
  if phase['name']=='after-write':os._exit(88)
 def check(self,value):
  orig_check(self,value)
  if phase['name']=='after-journal':os._exit(88)
 def restart(self):
  self.check();selected=oldroot if unit.read_bytes()==old else newroot
  # Actual fixture systemd unit maps release paths and drops production-only sandboxing.
  systemunit.write_bytes(mapped_unit(selected));systemunit.chmod(0o644);ctl('daemon-reload');ctl('restart',name);wait()
  if phase['name']=='after-restart':os._exit(88)
 m.Host.write_unit=write;m.Host.check_guards=check;m.Host.restart=restart
 def invoke(action,exit_on_error=False):
  sys.argv=['beta-switch.py',action]
  try:
   output=io.StringIO()
   with contextlib.redirect_stdout(output):m.main()
   value=json.loads(output.getvalue());expected=m.NEW_ACTOR if action=='apply' else m.OLD_ACTOR
   assert value['recoveryActor']==str(expected/'ops/asset-launch.py') and value['action']==action
  except BaseException:
   if exit_on_error:os._exit(77)
   raise
 def child(action,stage):phase['name']=stage;invoke(action,True)
 try:
  systemunit.write_bytes(mapped_unit(oldroot));systemunit.chmod(0o644);ctl('daemon-reload');ctl('start',name);wait();invoke('plan')
  for stage in ('after-journal','after-write','after-restart'):
   proc=multiprocessing.Process(target=child,args=('apply',stage));proc.start();proc.join(90);assert proc.exitcode==88,(stage,proc.exitcode)
   assert m.JOURNAL.exists();phase['name']='';invoke('recover');assert unit.read_bytes()==old and not m.JOURNAL.exists()
  # Real kernel flocks on both production lock implementations prevent entry.
  fd=os.open(hostroot/'.controller.lock',os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  proc=multiprocessing.Process(target=child,args=('plan',''));proc.start();proc.join(30);assert proc.exitcode==77;os.close(fd)
  assert not m.JOURNAL.exists()
  # Real kernel flock on the precise worker-lock adapter prevents entry.
  fd=os.open(worker_lock,os.O_CREAT|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  proc=multiprocessing.Process(target=child,args=('plan',''));proc.start();proc.join(30);assert proc.exitcode==77;os.close(fd)
  assert not m.JOURNAL.exists()
  unit.write_bytes(b'bad unit');unit.chmod(0o644)
  try:invoke('plan');raise AssertionError('wrong unit accepted')
  except ValueError:pass
  unit.write_bytes(old);unit.chmod(0o644)
  saved=m.OLD_INV;m.OLD_INV='0'*64
  try:invoke('plan');raise AssertionError('wrong actor pin accepted')
  except ValueError:pass
  m.OLD_INV=saved;phase['name']='';invoke('apply');assert not m.JOURNAL.exists() and unit.read_bytes()!=old
  env=dict(os.environ,NODE_PATH='/tmp/codi-occt-release-control/node_modules',CODI_TEST_URL='http://127.0.0.1:20080/',CODI_TEST_CDP='http://127.0.0.1:20085')
  subprocess.run(['/tmp/codi-files-move-node/bin/node',str(root/'tests/cad-source-exact-signed.test.cjs')],env=env,check=True,timeout=180)
  print('PASS mapped actual launcher plan/apply/recover, flock contention, wrong unit/actor pin, real gateways and signed exact source')
 finally:
  subprocess.run(['/usr/bin/systemctl','stop',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if systemunit.exists():systemunit.unlink()
  subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if worker_lock.exists():worker_lock.unlink()
