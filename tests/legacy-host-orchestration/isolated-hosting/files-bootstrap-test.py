#!/usr/bin/env python3
"""Disposable root-owned exact bootstrap with fixed fixture path mapping."""
import hashlib,os,pathlib,shutil,signal,subprocess,sys,tempfile
assert os.geteuid()==0
p=pathlib.Path(__file__).resolve().parents[1];root=pathlib.Path(tempfile.mkdtemp(prefix='files-bootstrap-',dir='/run'))
try:
 source=root/'source';shutil.copytree(p,source,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for x in [source,*source.rglob('*')]:
  if not x.is_symlink(): x.chmod(0o755 if x.is_dir() else 0o644)
 launcher=root/'bootstrap.py';dest=root/'input';s=(p/'ops/files_bootstrap_candidate.py').read_text()
 maps={"Path('/home/dflanag3/files-bootstrap-source')":f'Path({str(source)!r})',"Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472')":f'Path({str(dest)!r})',"Path('/srv/codi-connected/operators/files-bootstrap-v1.py')":f'Path({str(launcher)!r})',"socket.gethostname()!='box-webhost'":"False"}
 for old,new in maps.items(): assert old in s;s=s.replace(old,new)
 launcher.write_text(s);launcher.chmod(0o644)
 def run(ok=True):
  x=subprocess.run([sys.executable,'-I','-B',str(launcher)],capture_output=True,text=True,timeout=30)
  if (x.returncode==0)!=ok:raise AssertionError((x.returncode,x.stdout,x.stderr))
  return x
 # Bad pin and symlink are rejected with no published directory.
 data=source/'ops/beta_files_launch.py';original=data.read_bytes();data.write_bytes(original+b'x');run(False);assert not dest.exists();data.write_bytes(original)
 data.unlink();data.symlink_to(source/'ops/webctl_live.py');run(False);assert not dest.exists();data.unlink();data.write_bytes(original);data.chmod(0o644)
 # Source files can be copied as data by the trusted administrator UID.
 for item in [source,*source.rglob('*')]:
  if not item.is_symlink(): os.chown(item,1000,1000)
 # Test-only instrumented executable dies mid-copy; its mapped unmodified
 # successor can publish a complete generation and verify idempotently.
 launcher.write_text(s.replace('syncdir(stage/\'ops\');syncdir(stage);verify(stage,files)',"os.kill(os.getpid(),9)"));x=run(False);assert x.returncode==-signal.SIGKILL and not dest.exists()
 # Owner and ACL changes fail closed before publication.
 launcher.write_text(s);os.chown(data,1,1);run(False);assert not dest.exists();os.chown(data,0,0)
 subprocess.run(['setfacl','-m','u:daemon:r--',str(data)],check=True);run(False);assert not dest.exists();subprocess.run(['setfacl','-b',str(data)],check=True)
 # A kill just after fsynced publish is recoverable by verification.
 launcher.write_text(s.replace("syncdir(DEST.parent);verify(DEST,files);print(","syncdir(DEST.parent);os.kill(os.getpid(),9);verify(DEST,files);print("));x=run(False);assert x.returncode==-signal.SIGKILL and dest.exists()
 launcher.write_text(s);run();run();assert (dest/'ops/files_install_launch.py').is_file()
 assert set(x.relative_to(dest).as_posix() for x in dest.rglob('*') if x.is_file())==set(line.split('  ')[1] for line in (source/'ops/files_bootstrap_pins.txt').read_text().splitlines())
 # Existing generation is never replaced, even when corrupt.
 target=dest/'ops/files_install_launch.py';target.chmod(0o644);target.write_text('changed');run(False);assert target.read_text()=='changed'
 print('PASS: checked bootstrap closure, pin/symlink rejection, killed copy, no-replace and idempotence')
finally:shutil.rmtree(root)
