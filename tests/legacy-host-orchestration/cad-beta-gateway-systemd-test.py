#!/usr/bin/env python3
"""Disposable systemd units with exact dd8/a626 gateway and dev issuer fixture."""
import hashlib,importlib.util,json,multiprocessing,os,pathlib,secrets,subprocess,tempfile,time,urllib.request
root=pathlib.Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('transition',root/'research/cad-source-access/beta-transition.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
if os.geteuid()!=0:raise SystemExit('Root required for disposable systemd test')
oldroot=pathlib.Path(os.environ.get('CAD_TEST_OLD_GATEWAY','/tmp/codi-native-continuity-gateway-clean'));newroot=pathlib.Path(os.environ.get('CAD_TEST_NEW_GATEWAY','/tmp/codi-cad-source-gateway-r2'));python='/tmp/codi-audio-upload-19584-venv/bin/python';source='/var/lib/codi-cad-source-exact-test';sourcepin='e304a1c451a380d21caebb306e47803a4b5de8a098d31cdaa3d60241367551a6'
for p,want in ((oldroot,'dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'),(newroot,'a626ef11bf57a039529abc806a4b39a5881f470557d49f8c715a742c06b5ae08')):
 raw=(p/'files-service.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==want
 for n,v in json.loads(raw)['files'].items():
  b=(p/n).read_bytes();assert {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}==v
name='codi-cad-gateway-test-'+secrets.token_hex(5)+'.service';unit=pathlib.Path('/run/systemd/system')/name
port=20089
def ctl(*a):return subprocess.run(['/usr/bin/systemctl',*a],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60).stdout
def http(path):
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,headers={'Host':'127.0.0.1:20080'}),timeout=2) as r:return r.status,r.read()
with tempfile.TemporaryDirectory(prefix='codi-cad-gateway-',dir='/run') as tmp:
 d=pathlib.Path(tmp);state=d/'state';data=d/'data';state.mkdir(mode=0o700);data.mkdir(mode=0o700)
 with urllib.request.urlopen('http://127.0.0.1:20080/config.json',timeout=5) as r:identity=json.load(r)['identity']
 policy=d/'issuer-policy.json';raw=json.dumps(identity,sort_keys=True).encode();policy.write_bytes(raw);policy.chmod(0o600);pin=hashlib.sha256(raw).hexdigest()
 common=['serve','--state-root',str(state),'--data-root',str(data),'--issuer-policy',str(policy),'--issuer-policy-sha256',pin,'--port',str(port),'--base-path','']
 init=[python,'-I','-B',str(oldroot/'scripts/serve-user-files.py'),'initialize',*common[1:]];subprocess.run(init,check=True,capture_output=True)
 def blob(release,extra):
  args=[python,'-I','-B',str(release/'scripts/serve-user-files.py'),*common,*extra]
  return ('[Unit]\nDescription=Disposable CAD real gateway fixture\nStartLimitIntervalSec=0\n[Service]\nType=exec\nExecStart='+' '.join('"'+x+'"' for x in args)+'\n').encode()
 old=blob(oldroot,[]);new=blob(newroot,['--cad-source-root',source,'--cad-source-manifest-sha256',sourcepin]);t.OLD=t.sha(old);t.NEW=t.sha(new)
 class A:
  def __init__(self,stage=None):self.stage=stage
  def check(self):pass
  def require_no_other_journals(self):pass
  def units(self):return old,new
  def read_unit(self):return unit.read_bytes()
  def verify_candidate(self):assert newroot.exists() and pathlib.Path(source).exists()
  def wait(self):
   for _ in range(100):
    try:
     if http('/healthz')[0]==200:return
    except OSError:pass
    time.sleep(.1)
   raise RuntimeError('real gateway did not start')
  def verify_old(self):assert self.read_unit()==old;self.wait()
  def verify_new(self):assert self.read_unit()==new;self.wait()
  def guards(self):return {'identity':pin}
  def check_guards(self,g):
   assert g==self.guards()
   if self.stage=='after-journal':os._exit(88)
  def write_unit(self,b):
   t.atomic(unit,b,0o644)
   if self.stage=='after-write':os._exit(88)
  def restart(self):
   ctl('daemon-reload');ctl('restart',name);self.wait()
   if self.stage=='after-restart':os._exit(88)
 def child(journal,phase):t.Transition(A(phase),journal).apply()
 try:
  t.atomic(unit,old,0o644);ctl('daemon-reload');ctl('start',name);A().wait();journal=d/'journal'
  for phase in ('after-journal','after-write','after-restart'):
   proc=multiprocessing.Process(target=child,args=(journal,phase));proc.start();proc.join(90);assert proc.exitcode==88,(phase,proc.exitcode)
   t.Transition(A(),journal).recover();assert unit.read_bytes()==old and not journal.exists()
  t.Transition(A(),journal).apply();assert unit.read_bytes()==new and not journal.exists()
  env=dict(os.environ,NODE_PATH='/tmp/codi-occt-release-control/node_modules',CODI_TEST_URL='http://127.0.0.1:20080/',CODI_TEST_CDP='http://127.0.0.1:20085')
  subprocess.run(['/tmp/codi-files-move-node/bin/node',str(root/'tests/cad-source-exact-signed.test.cjs')],env=env,check=True,timeout=180)
  print('PASS real dd8/a626 isolated systemd gateways, three child deaths/recovery, and post-switch two-account signed exact source reads')
 finally:
  subprocess.run(['/usr/bin/systemctl','stop',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if unit.exists():unit.unlink()
  subprocess.run(['/usr/bin/systemctl','daemon-reload'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
