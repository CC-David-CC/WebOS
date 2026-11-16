#!/usr/bin/env python3
"""Literal installer in disposable mount namespace, with explicit timer stubs."""
import hashlib,json,os,shlex,shutil,subprocess,sys,tempfile
from pathlib import Path
assert os.geteuid()==0,'run as root in disposable fixture only'
here=Path(__file__).resolve().parent;main=here.parent;ops=main.parent/'beta-isolated-hosting/ops';source=Path(sys.argv[1]);generated=Path(sys.argv[2]);bc9=Path(sys.argv[3])/'ops/beta_files_recover.py';main_actor=Path(sys.argv[4])/'main-launcher.py';assert all(x.is_absolute() for x in (source,generated,bc9,main_actor))
with tempfile.TemporaryDirectory(prefix='codi-main-install-ns-',dir='/run') as d:
 root=Path(d);srv=root/'srv';home=root/'home';var=root/'var';etc=root/'etc'
 for p in (srv/'codi-connected/operators',home/'dflanag3/webhost-sites/ops',var/'webhost-ops',etc/'systemd/system'):p.mkdir(parents=True)
 (var/'webhost-ops').chmod(0o700);(home/'dflanag3/webhost-sites/.controller.lock').touch(mode=0o644)
 (etc/'passwd').write_text('root:x:0:0:root:/root:/bin/bash\ndflanag3:x:1000:1000:fixture:/home/dflanag3:/bin/bash\n');(etc/'group').write_text('root:x:0:\ndflanag3:x:1000:\n');(etc/'nsswitch.conf').write_text('passwd: files\ngroup: files\n')
 for unit,data in (('codi-ksu-live-root-renew.timer','fixture timer\n'),('codi-ksu-live-root-renew.service','fixture service\n')):(etc/'systemd/system'/unit).write_text(data)
 private=var/'webhost-ops';floor=private/'opfs-floor.json';floor.write_text(json.dumps({'version':1,'baseline':'e7a5e64272c1d6b78de73c46f5105b9963e2272f40450e39e86a038293d9fb3b','candidate':'3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'}));floor.chmod(0o600)
 target=home/'dflanag3/webhost-sites/ops/webctl.py';shutil.copyfile(main/'webctl-main-guard.py',target);target.chmod(0o644);os.chown(target,1000,1000)
 operators=srv/'codi-connected/operators';pkg=operators/'beta-files-830c-installer-v1';pkg.mkdir();beta=operators/'files-install-input-ce18b7794adc2472/ops';beta.mkdir(parents=True);src=operators/'beta-files-830c-input/actor';src.parent.mkdir();shutil.copytree(source,src)
 for p in src.rglob('*'):p.chmod(0o755 if p.is_dir() else 0o644)
 src.chmod(0o755)
 for n in ('main-install-launch.py','main-install.py','main-successor-preflight.py','webctl-main-guard.py','retirement.py'):shutil.copyfile(generated/n,pkg/n);(pkg/n).chmod(0o644)
 for n in ('beta_launcher.py','files_install_candidate.py','beta_files_preflight.py'):shutil.copyfile(ops/n,beta/n);(beta/n).chmod(0o644)
 legacy={'bc9':operators/'beta-recovery-e7-v1/ops/beta_files_recover.py','ce18-bundle':operators/'files-bundle-ce18b7794adc2472/ops/beta_files_launch.py','ce18-input':beta/'beta_files_launch.py','main-once':operators/'main-qualified-e7e8-v1/main-launcher.py'}
 for key,path in legacy.items():
  path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(bc9 if key=='bc9' else main_actor if key=='main-once' else ops/'beta_files_launch.py',path);path.chmod(0o444 if key.startswith('ce18') else 0o644)
 boot=root/'bootstrap.py';shutil.copyfile(here/'install-ns-bootstrap.py',boot);boot.chmod(0o644)
 def invoke(action,stop=None,timer_active=False):
  prefix=' && '.join('mount --bind '+shlex.quote(str(a))+' '+b for a,b in ((srv,'/srv'),(home,'/home'),(var,'/var/lib'),(etc,'/etc')))
  env=(('CODI_INSTALL_STOP='+shlex.quote(stop)+' ') if stop else '')+('CODI_TIMER_ACTIVE=1 ' if timer_active else '')
  cmd=prefix+' && exec env '+env+shlex.quote(sys.executable)+' -I -B '+shlex.quote(str(boot))+' '+action
  return subprocess.run(['unshare','-m','sh','-c',cmd],capture_output=True,text=True,timeout=120)
 def require(result,needle):
  if result.returncode or needle not in result.stdout:raise RuntimeError('fixture failed: '+result.stderr[-8000:])
 require(invoke('plan'),'PASS')
 result=invoke('plan',timer_active=True);assert result.returncode and 'not quiescent' in result.stderr
 # An identified known invoker is rejected; arbitrary renamed/embedded code
 # still relies on the separately coordinated trusted maintenance freeze.
 known=subprocess.Popen(['bash','-c','exec -a /fixture/webctl.py sleep 60'])
 try:
  result=invoke('plan');assert result.returncode and 'Known controller process remains' in result.stderr
 finally:known.terminate();known.wait(timeout=5)
 (private/'opfs-transition.json').touch(mode=0o600)
 result=invoke('plan');assert result.returncode and 'Conflicting hosting journal' in result.stderr
 (private/'opfs-transition.json').unlink()
 # A death after durable staging but before publication leaves old guard and
 # no selected successor; recovery builds a fresh verified generation.
 result=invoke('install','staged');assert result.returncode
 dest=operators/'beta-files-830c-v1';assert not dest.exists() and not (private/'main-restriction-journal.json').exists()
 assert hashlib.sha256(target.read_bytes()).hexdigest()=='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783'
 require(invoke('recover'),'installed');assert dest.exists()
 def reset_install():
  shutil.rmtree(dest)
  quarantine=operators/'retired-830c-actors-v1'
  for key,path in legacy.items():
   archived=quarantine/(key+'.data');assert archived.is_file();os.rename(archived,path);path.chmod(0o444 if key.startswith('ce18') else 0o644)
  quarantine.rmdir();shutil.copyfile(main/'webctl-main-guard.py',target);target.chmod(0o644);os.chown(target,1000,1000)
 for stop in ('retired-bc9','retired-ce18-bundle','retired-ce18-input','retired-main-once','guard-replaced'):
  reset_install();result=invoke('install',stop);assert result.returncode and (private/'main-restriction-journal.json').exists(),stop
  # A newly appeared asset floor must block resuming even a valid partial
  # retirement, before any additional source or route changes.
  marker=private/'files-asset-floor.json';marker.write_text(json.dumps({'version':1,'baseline':'3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc','candidate':'830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0'}));marker.chmod(0o600)
  before={k:path.exists() for k,path in legacy.items()};before_guard=hashlib.sha256(target.read_bytes()).hexdigest()
  result=invoke('recover');assert result.returncode and 'asset floor' in result.stderr,stop
  assert {k:path.exists() for k,path in legacy.items()}==before and hashlib.sha256(target.read_bytes()).hexdigest()==before_guard
  marker.unlink()
  require(invoke('recover'),'installed');assert not (private/'main-restriction-journal.json').exists()
  assert all(not path.exists() for path in legacy.values())
  assert hashlib.sha256(target.read_bytes()).hexdigest()=='ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9'
  assert (target.stat().st_uid,target.stat().st_gid,target.stat().st_mode&0o777)==(1000,1000,0o644)
 # After the asset floor, all former fixed paths are absent; attempting each
 # literal old entrypoint must fail before any original journal can appear.
 marker=private/'files-asset-floor.json';marker.write_text('{}');marker.chmod(0o600)
 for key,path in legacy.items():
  virtual='/srv/codi-connected/operators/'+str(path.relative_to(operators))
  prefix=' && '.join('mount --bind '+shlex.quote(str(a))+' '+b for a,b in ((srv,'/srv'),(home,'/home'),(var,'/var/lib'),(etc,'/etc')))
  result=subprocess.run(['unshare','-m','sh','-c',prefix+' && exec '+shlex.quote(sys.executable)+' -I -B '+shlex.quote(virtual)+' recover'],capture_output=True,text=True,timeout=30)
  assert result.returncode and not (private/'opfs-transition.json').exists(),key
 marker.unlink()
 require(invoke('recover'),'already-installed');assert json.loads(floor.read_text())['candidate']=='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
 print('PASS literal fixed-path installer plan, timer/process/journal refusal, SIGKILL staging, each retirement and guard replacement recovery, old entrypoint refusal; timer hashes/state simulated')
