import builtins,hashlib,http.client,inspect,json,os,runpy,socket,subprocess,sys,time,tomllib,types,urllib.request
from pathlib import Path
socket.gethostname=lambda:'box-webhost'
ROOT=Path(os.environ['CODI_FILES_FIXTURE_ROOT']);policy_raw=Path('/etc/codi-user-files/beta/issuer-policy.json').read_bytes();policy=json.loads(policy_raw)['identity'];identity_pin=hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(',',':')).encode()).hexdigest()
state=ROOT/'timer.json'
if not state.exists():state.write_text(json.dumps({'active':True,'enabled':True}))
orig_exec=builtins.exec

def systemctl(args):
 prefix=os.environ.get('CODI_FILES_SYSTEMD_PREFIX')
 if args[0]=='show':
  n=args[1]
  if prefix:
   mapped=prefix+'-'+n.removeprefix('codi-beta-')
   p=subprocess.run(['/usr/bin/systemctl','show',mapped,'-p','ActiveState','-p','DropInPaths','-p','NeedDaemonReload'],capture_output=True,text=True,check=True,timeout=30)
   return p.stdout+'FragmentPath=/etc/systemd/system/'+n+'\n'
  return f'ActiveState=active\nFragmentPath=/etc/systemd/system/{n}\nDropInPaths=\nNeedDaemonReload=no\n'
 if args[0]=='daemon-reload':
  if (ROOT/'block').exists():(ROOT/'blocked-pid').write_text(str(os.getpid()))
  while (ROOT/'block').exists():time.sleep(.05)
  if prefix:subprocess.run(['/usr/bin/systemctl','daemon-reload'],check=True,timeout=30)
  return ''
 if args[0]=='restart':
  if prefix:subprocess.run(['/usr/bin/systemctl','restart',prefix+'-issuer.service'],check=True,timeout=30)
  if not (ROOT/'issuer-switched').exists():
   c=http.client.HTTPConnection('127.0.0.1',19774,timeout=30);c.request('GET','/restart');r=c.getresponse();assert r.status==200;r.read();c.close();(ROOT/'issuer-switched').touch()
  return ''
 if args[0]=='start':
  if prefix:subprocess.run(['/usr/bin/systemctl','start',prefix+'-'+args[1].removeprefix('codi-beta-')],check=True,timeout=30)
  return ''
 raise AssertionError(args)
def hostrun(args):
 args=list(args);n=args[2] if len(args)>2 else ''
 if args[1]=='show' and n.endswith('.timer'):
  v=json.loads(state.read_text());return 'ActiveState='+('active' if v['active'] else 'inactive')+'\nUnitFileState='+('enabled' if v['enabled'] else 'disabled')+'\n'
 if args[1]=='show':return 'ActiveState=inactive\nMainPID=0\nControlPID=0\n'
 if args[1] in ('start','stop'):
  v=json.loads(state.read_text());v['active']=args[1]=='start';state.write_text(json.dumps(v));return ''
 raise AssertionError(args)
class Response:
 def __init__(self,body,status=200):self.body=body;self.status=status
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def read(self,n=-1):return self.body if n<0 else self.body[:n]
class Opener:
 def open(self,url,timeout=8):
  if os.environ.get('CODI_FILES_REAL_CADDY')=='1':
   from urllib.parse import urlsplit
   parsed=urlsplit(url);path=parsed.path or '/'
   if parsed.query:path+='?'+parsed.query
   c=http.client.HTTPConnection('127.0.0.1',int(os.environ['CODI_FILES_CADDY_PORT']),timeout=timeout);c.request('GET',path,headers={'Host':'beta.ksu.codes'});r=c.getresponse();body=r.read();status=r.status;c.close()
   if status>=400:raise urllib.error.HTTPError(url,status,'fixture Caddy',None,None)
   return Response(body,status)
  data=tomllib.loads(Path('/home/dflanag3/webhost-sites/sites.toml').read_text())
  if data.get('codi_beta_maintenance'):
   if url.endswith('/'):return Response(b'Beta maintenance')
   raise urllib.error.HTTPError(url,503,'fixture gate',None,None)
  if '/app.js?simplified=1' in url:
   return Response(Path('/srv/data/codi-beta-opfs/3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc/shell/app.js').read_bytes())
  return Response(b'fixture')
urllib.request.build_opener=lambda *a,**k:Opener()

def fixture_exec(code,globals=None,locals=None):
 result=orig_exec(code,globals,locals)
 if not globals:return result
 name=globals.get('__name__')
 if name=='beta_launcher':
  globals['main_ready']=lambda:None;globals['public_health']=lambda *a,**k:None;globals['run']=hostrun
  def unit(n):return {'ActiveState':'active','MainPID':'123','UnitFileState':'enabled','NeedDaemonReload':'no'}
  globals['unit_state']=unit;globals['beta_ready']=lambda:None
  realsha=globals['sha'];globals['sha']=lambda x:'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca' if x==policy_raw else realsha(x)
 if name=='beta_issuer_switch':
  globals['run_systemctl']=systemctl;globals['IssuerSwitch'].__init__.__kwdefaults__['run']=systemctl
 if name=='beta_signed_health':
  real=globals['SignedHealth']
  class Signed(real):
   def __init__(self,**kw):kw.update(origin='http://127.0.0.1:19771',issuer_port=19772,gateway_port=19771,policy=policy,policy_sha256=identity_pin);super().__init__(**kw)
  globals['SignedHealth']=Signed
 if name=='beta_files_host_health':
  def create(*,lock,launcher,preflight,signed_health,jose):
   def custody():lock.check();launcher.protected(Path('/var/lib/webhost-ops/beta-files-probe/probe.json'));preflight.protected_ancestors('/var/lib/webhost-ops/beta-files-probe');launcher.verify_beta_worker(Path('/srv/codi-gateway/releases')/launcher.GW,launcher.GW);preflight.tree('/srv/data/codi-beta-native/853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21','connected-release.json','853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21');lock.check()
   def health():
    marker=ROOT/'fail-final-health'
    if marker.exists() and any(frame.function=='finalize' for frame in inspect.stack()):
     marker.unlink();raise ValueError('injected finalization health failure')
    return signed_health.SignedHealth(check_lock=lock.check,check_custody=custody,origin='http://127.0.0.1:19771',issuer_port=19772,gateway_port=19771,policy=policy,policy_sha256=identity_pin,credential_path=Path('/var/lib/webhost-ops/beta-files-probe/probe.json'),jose=jose)()
   return health
  globals['create']=create
 if name=='files_webctl':
  def fixture_run(args,**kw):
   if os.environ.get('CODI_FILES_REAL_CADDY')=='1':
    if args[:4]==['runuser','-u','caddy','--']:operation,path='validate',args[args.index('--config')+1]
    elif args[:2]==['systemctl','reload']:
     operation,path='reload','/etc/caddy/Caddyfile'
     if (ROOT/'block-gate').exists() and tomllib.loads(Path('/home/dflanag3/webhost-sites/sites.toml').read_text()).get('codi_beta_maintenance'):
      (ROOT/'blocked-pid').write_text(str(os.getpid()))
      while (ROOT/'block-gate').exists():time.sleep(.05)
    else:raise AssertionError(args)
    subprocess.run([sys.executable,'-I','-B',os.environ['CODI_FILES_CADDY_HELPER'],operation,str(path)],check=True,timeout=45)
   return types.SimpleNamespace(returncode=0,stdout='')
  globals['run']=fixture_run
  globals['subprocess']=types.SimpleNamespace(run=lambda *a,**k:types.SimpleNamespace(returncode=0),DEVNULL=None)
 return result
builtins.exec=fixture_exec
sys.argv=['launch',sys.argv[1]]
runpy.run_path(str(Path(os.environ['CODI_FILES_FIXTURE_BUNDLE'])/'ops/beta_files_launch.py'),run_name='__main__')
