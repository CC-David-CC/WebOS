#!/usr/bin/env python3
"""Mapped protected entrypoint against real disposable sealed issuer/gateway."""
import fcntl,hashlib,json,os,pathlib,shutil,signal,subprocess,sys,tempfile,time
assert os.geteuid()==0
source=pathlib.Path(__file__).resolve().parents[1];public=pathlib.Path(tempfile.mkdtemp(prefix='codi-probe-entry-',dir='/run'));private=pathlib.Path(tempfile.mkdtemp(prefix='codi-probe-state-',dir='/tmp'));fixture=None
python=os.environ.get('CODI_PROBE_TEST_PYTHON','/tmp/codi-audio-upload-19584-venv/bin/python');native=os.environ.get('CODI_PROBE_TEST_NATIVE','/tmp/codi-beta-issuer-base-1666491d-retest');worker_src=os.environ.get('CODI_PROBE_TEST_WORKER','/tmp/codi-beta-client-44da-built')
def verify(root,manifest,pin):
 root=pathlib.Path(root);raw=(root/manifest).read_bytes();assert hashlib.sha256(raw).hexdigest()==pin;records=json.loads(raw)['files'];found=set()
 for path in root.rglob('*'):
  assert not path.is_symlink()
  if path.is_dir():continue
  assert path.is_file() and path.stat().st_nlink==1
  name=path.relative_to(root).as_posix();found.add(name)
  if name==manifest:continue
  b=path.read_bytes();assert records.get(name)=={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 assert found==set(records)|{manifest}
try:
 verify(native,'connected-release.json','1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51')
 verify(worker_src,'files-service.json','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')
 worker=public/'worker';shutil.copytree(worker_src,worker,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for x in [worker,*worker.rglob('*')]:
  if not x.is_symlink():x.chmod(0o755 if x.is_dir() else 0o644)
 inputdir=public/'input';inputdir.mkdir();
 for name in ('beta_launcher.py','beta_files_preflight.py','beta_signed_probe.py'):shutil.copyfile(source/'ops'/name,inputdir/name);(inputdir/name).chmod(0o644)
 host=public/'host';(host/'ops').mkdir(parents=True);(host/'.controller.lock').touch(mode=0o644)
 state=public/'state';state.mkdir(mode=0o700)
 fixture=subprocess.Popen([python,'-B',str(source/'tests/beta-probe-real-fixture.py'),str(private),native,str(worker)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 for _ in range(300):
  if fixture.poll() is not None:raise RuntimeError('real service fixture failed')
  if (private/'ready.json').exists():break
  time.sleep(.05)
 else:raise RuntimeError('real service fixture timed out')
 ready=json.loads((private/'ready.json').read_text());policy=public/'policy.json';shutil.copyfile(private/'policy.json',policy);policy.chmod(0o644)
 script=public/'entry.py';code=(source/'ops/beta_probe_entry.py').read_text();target=state/'beta-files-probe'
 mappings={"Path('/srv/codi-connected/operators/beta-files-probe-entry-v1.py')":f'Path({str(script)!r})',"Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops')":f'Path({str(inputdir)!r})',"Path('/var/lib/webhost-ops')":f'Path({str(state)!r})',"Path('/etc/codi-user-files/beta/issuer-policy.json')":f'Path({str(policy)!r})',"Path('/srv/codi-gateway/releases/dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')":f'Path({str(worker)!r})',"ORIGIN='https://beta.ksu.codes';ISSUER=28118;FRONTEND=28132;GATEWAY=28140":f"ORIGIN={ready['origin']!r};ISSUER={ready['issuer']};FRONTEND={ready['issuer']};GATEWAY={ready['gateway']}","POLICY_PIN='71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca'":f"POLICY_PIN='{hashlib.sha256(policy.read_bytes()).hexdigest()}'","socket.gethostname()!='box-webhost'":"False"}
 for old,new in mappings.items():assert old in code;code=code.replace(old,new)
 # Explicit fixture substitutions: service identities/systemd and main health
 # are not modeled. The real sealed gateway verifier and signed calls still run.
 needle="pre=load('beta_files_preflight'";inject=f"host.ROOT=Path({str(host)!r});host.verify_native=lambda:None;host.service_preflight=lambda:None;host.beta_ready=lambda:None;host.main_ready=lambda:None;host.UNIT={{}}\n original_get=host.get;host.get=lambda port,path:original_get(port,path,host=ORIGIN.split('://',1)[1])\n "
 assert needle in code;code=code.replace(needle,inject+needle);script.write_text(code);script.chmod(0o644)
 def run(action,ok=True):
  result=subprocess.run([python,'-I','-B',str(script),action],text=True,capture_output=True,timeout=40)
  if (result.returncode==0)!=ok:raise AssertionError((action,result.returncode,result.stdout,result.stderr))
  return result
 assert run('inspect').stdout.strip()=='probe absent'
 assert 'provisioned' in run('provision').stdout
 assert (target/'probe.json').stat().st_mode&0o777==0o600
 assert run('inspect').stdout.strip()=='probe configuration present'
 run('provision',False)
 # Fresh private root, test-only instrumented probe drops a successful signed
 # registration reply. The persisted journal must block retries and inspection.
 shutil.rmtree(target);module=inputdir/'beta_signed_probe.py';original=module.read_bytes();modified=original.decode().replace("session=self._post(self.issuer,'/api/v1/auth',request);identity=session['identity']","session=self._post(self.issuer,'/api/v1/auth',request);raise ProbeError('fixture dropped reply');identity=session['identity']")
 assert modified.encode()!=original;module.write_text(modified);updated=code.replace(hashlib.sha256(original).hexdigest(),hashlib.sha256(modified.encode()).hexdigest());assert updated!=code;script.write_text(updated)
 result=run('provision',False);assert not result.stdout and (target/'probe-provision.json').exists() and not (target/'probe.json').exists()
 module.write_bytes(original);script.write_text(code);run('provision',False);run('inspect',False)
 shutil.rmtree(target)
 replace_from="try:return self._post(self.gateway,'/gateway/use',{},token=authorization,raw=raw)"
 replace_to="try:\n   result=self._post(self.gateway,'/gateway/use',{},token=authorization,raw=raw)\n   if operation=='create':raise ProbeError('fixture dropped committed create reply')\n   return result"
 modified=original.decode().replace(replace_from,replace_to);assert modified.encode()!=original
 module.write_text(modified);script.write_text(code.replace(hashlib.sha256(original).hexdigest(),hashlib.sha256(modified.encode()).hexdigest()))
 run('provision',False);record=json.loads((target/'probe-provision.json').read_text());assert record['phase']=='create-intent'
 module.write_bytes(original);script.write_text(code);run('provision',False);run('inspect',False)
 # Refuse lock contention and a pending floor before contacting services.
 shutil.rmtree(target);fd=os.open(host/'.controller.lock',os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try:run('provision',False);assert not target.exists()
 finally:os.close(fd)
 (state/'opfs-floor.json').touch();run('provision',False);assert not target.exists();(state/'opfs-floor.json').unlink()
 verify(native,'connected-release.json','1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51')
 verify(worker_src,'files-service.json','dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1')
 print('PASS real sealed issuer/gateway signed probe, private custody, uncertain registration/create and lock/floor refusal')
finally:
 if fixture and fixture.poll() is None:fixture.send_signal(signal.SIGINT);fixture.wait(timeout=15)
 shutil.rmtree(public);shutil.rmtree(private)
