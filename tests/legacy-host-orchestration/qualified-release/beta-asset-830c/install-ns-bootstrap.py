"""Fixture-only host substitution; executes literal pinned installer bytes."""
import builtins,hashlib,os,runpy,socket,subprocess,sys,types
from pathlib import Path
socket.gethostname=lambda:'box-webhost'
realsha=hashlib.sha256
class FakeHash:
 def __init__(self,value):self.value=value
 def hexdigest(self):return self.value
def sha(data=b''):
 if data==b'fixture timer\n':return FakeHash('fe8fdcab3889ec2fb51a063e90487ed9f2efc9fccd185a9825c715c1d40a4718')
 if data==b'fixture service\n':return FakeHash('abb4716e957f856f171e35cb0e97a64386e6a76c7068b0779bf3c993878c8870')
 return realsha(data)
hashlib.sha256=sha
realrun=subprocess.run
def run(args,*a,**kw):
 if args[:2]==['/usr/bin/systemctl','show']:
  name=args[2];active='active' if os.environ.get('CODI_TIMER_ACTIVE')=='1' and name.endswith('.timer') else 'inactive';text='ActiveState='+active+'\nMainPID=0\nControlPID=0\nFragmentPath=/etc/systemd/system/'+name+'\nDropInPaths=\nNeedDaemonReload=no\n'
  return types.SimpleNamespace(stdout=text,returncode=0)
 return realrun(args,*a,**kw)
subprocess.run=run
realexec=builtins.exec
def wrapped(code,globals=None,locals=None):
 result=realexec(code,globals,locals)
 if globals and globals.get('__name__')=='main_install' and os.environ.get('CODI_INSTALL_STOP'):
  original=globals['install']
  def injected(**kw):
   def phase(name):
    if name==os.environ['CODI_INSTALL_STOP']:os.kill(os.getpid(),9)
   kw['phase']=phase;return original(**kw)
  globals['install']=injected
 return result
builtins.exec=wrapped
sys.argv=['main-install-launch.py',sys.argv[1]]
runpy.run_path('/srv/codi-connected/operators/beta-files-830c-installer-v1/main-install-launch.py',run_name='__main__')
