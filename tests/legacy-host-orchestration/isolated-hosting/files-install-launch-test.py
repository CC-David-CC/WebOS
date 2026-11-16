#!/usr/bin/env python3
"""Execute fixed-path launcher with only fixture path/hostname substitutions."""
import fcntl,hashlib,os,pathlib,shutil,signal,subprocess,sys,tempfile
assert os.geteuid()==0
p=pathlib.Path(__file__).resolve().parents[1];root=pathlib.Path(tempfile.mkdtemp(prefix='files-installer-',dir='/run'))
try:
 inp=root/'input';shutil.copytree(p,inp,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for x in [inp,*inp.rglob('*')]:
  if not x.is_symlink(): x.chmod(0o755 if x.is_dir() else 0o644)
 host=root/'host';(host/'ops').mkdir(parents=True);state=root/'state';state.mkdir(mode=0o700)
 target=host/'ops/webctl.py';shutil.copyfile(inp/'ops/webctl_live.py',target);os.chown(target,1000,1000);target.chmod(0o644)
 lock=host/'.controller.lock';lock.touch(mode=0o644);lock.chmod(0o644)
 launcher=inp/'ops/files_install_launch.py';s=launcher.read_text()
 substitutions={"Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472')":f'Path({str(inp)!r})',"Path('/srv/codi-connected/operators/files-bundle-ce18b7794adc2472')":f'Path({str(root/"bundle")!r})',"Path('/home/dflanag3/webhost-sites')":f'Path({str(host)!r})',"Path('/var/lib/webhost-ops')":f'Path({str(state)!r})',"socket.gethostname()!='box-webhost'":"False","if host.ROOT!=HOST: raise ValueError('hosting path mismatch')":"host.ROOT=HOST"}
 for old,new in substitutions.items(): assert old in s;s=s.replace(old,new)
 launcher.write_text(s);launcher.chmod(0o644)
 def run(action,ok=True):
  x=subprocess.run([sys.executable,'-I','-B',str(launcher),action],capture_output=True,text=True,timeout=30)
  if (x.returncode==0)!=ok: raise AssertionError((action,x.returncode,x.stdout,x.stderr))
  return x
 run('plan');run('install');run('install');run('recover')
 bundle=root/'bundle';assert (bundle/'ops/beta_files_launch.py').exists()
 (state/'opfs-floor.json').touch();before=target.read_bytes();run('install',False);assert target.read_bytes()==before
 (state/'opfs-floor.json').unlink();target.chmod(0o664);run('plan',False);target.chmod(0o644)
 os.chown(target,0,0);run('plan',False);os.chown(target,1000,1000)
 subprocess.run(['setfacl','-m','u:daemon:r--',str(target)],check=True);run('plan',False)
 subprocess.run(['setfacl','-b',str(target)],check=True)
 fd=os.open(lock,os.O_RDONLY);fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 try: run('plan',False)
 finally: os.close(fd)
 lock.chmod(0o664);run('plan',False);lock.chmod(0o644)
 # Execute a test-only fault-instrumented helper; restore the exact pinned
 # helper before invoking the actual mapped recovery executable.
 helper=inp/'ops/files_install_candidate.py';original=helper.read_bytes()
 source=original.decode().replace('os.replace(name,path);syncdir(path.parent)',"os.replace(name,path);syncdir(path.parent)\n  if path.name=='files-install-guard.json': os.kill(os.getpid(),9)")
 helper.write_text(source);launcher_original=launcher.read_text();launcher.write_text(launcher_original.replace(hashlib.sha256(original).hexdigest(),hashlib.sha256(source.encode()).hexdigest()))
 target.write_bytes((inp/'ops/webctl_live.py').read_bytes());os.chown(target,1000,1000);target.chmod(0o644)
 killed=run('install',False);assert killed.returncode==-signal.SIGKILL
 assert (state/'files-install-guard.json').exists()
 helper.write_bytes(original);launcher.write_text(launcher_original)
 run('recover');assert not (state/'files-install-guard.json').exists()
 (bundle/'ops/beta_files_launch.py').chmod(0o644);(bundle/'ops/beta_files_launch.py').write_text('modified');run('plan',False)
 print('PASS: mapped fixed-path executable plan/install/recover, floor, owner/mode and bundle drift controls')
finally: shutil.rmtree(root)
