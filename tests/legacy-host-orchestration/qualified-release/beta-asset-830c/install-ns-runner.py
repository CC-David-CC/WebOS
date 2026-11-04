#!/usr/bin/env python3
"""Literal installer in disposable mount namespace, with explicit timer stubs."""
import hashlib,json,os,shlex,shutil,subprocess,sys,tempfile
from pathlib import Path
assert os.geteuid()==0,'run as root in disposable fixture only'
here=Path(__file__).resolve().parent;main=here.parent;ops=main.parent/'beta-isolated-hosting/ops';source=Path(sys.argv[1]);generated=Path(sys.argv[2]);assert source.is_absolute() and generated.is_absolute()
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
 for n in ('main-install-launch.py','main-install.py','main-successor-preflight.py','webctl-main-guard.py'):shutil.copyfile(generated/n,pkg/n);(pkg/n).chmod(0o644)
 for n in ('beta_launcher.py','files_install_candidate.py','beta_files_preflight.py'):shutil.copyfile(ops/n,beta/n);(beta/n).chmod(0o644)
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
 # Reset only this disposable fixture to exercise the later crash boundary.
 shutil.rmtree(dest);shutil.copyfile(main/'webctl-main-guard.py',target);target.chmod(0o644);os.chown(target,1000,1000)
 result=invoke('install','guard-replaced');assert result.returncode and (private/'main-restriction-journal.json').exists()
 assert hashlib.sha256(target.read_bytes()).hexdigest()=='ca25bb27799f0f306d7d901188d894d39ad22ea99ea2c1f1d224a2c6446ab8b9'
 assert (target.stat().st_uid,target.stat().st_gid,target.stat().st_mode&0o777)==(1000,1000,0o644)
 require(invoke('recover'),'installed');assert not (private/'main-restriction-journal.json').exists()
 require(invoke('recover'),'already-installed');assert json.loads(floor.read_text())['candidate']=='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
 print('PASS literal fixed-path installer plan, timer/process/journal refusal, SIGKILL staging and guard replacement recovery; timer hashes/state simulated')
