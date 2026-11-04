import builtins,hashlib,http.client,inspect,json,os,runpy,socket,subprocess,sys,time,tomllib,types,urllib.request
from pathlib import Path
socket.gethostname=lambda:'box-webhost'
ROOT=Path(os.environ['CODI_FILES_FIXTURE_ROOT']);policy_raw=Path('/etc/codi-user-files/beta/issuer-policy.json').read_bytes();policy=json.loads(policy_raw)['identity'];identity_pin=hashlib.sha256(json.dumps(policy,sort_keys=True,separators=(',',':')).encode()).hexdigest()
state=ROOT/'timer.json'
if not state.exists():state.write_text(json.dumps({'active':True,'enabled':True}))
orig_exec=builtins.exec

def pause_at(stage):
 if (ROOT/'block').exists() and os.environ.get('CODI_FILES_KILL_STAGE','unit-write')==stage:
  (ROOT/'blocked-pid').write_text(str(os.getpid()))
  while (ROOT/'block').exists():time.sleep(.05)

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
  pause_at('unit-write')
  if prefix and os.environ.get('CODI_FILES_REAL_SERVICES')=='1':
   subprocess.run([sys.executable,'-I','-B',os.environ['CODI_FILES_UNIT_MAPPER'],'/etc/systemd/system/codi-beta-issuer.service','/run/systemd/system/'+prefix+'-issuer.service'],check=True,timeout=30)
  if prefix:subprocess.run(['/usr/bin/systemctl','daemon-reload'],check=True,timeout=30)
  pause_at('reload')
  return ''
 if args[0]=='restart':
  if prefix:subprocess.run(['/usr/bin/systemctl','restart',prefix+'-issuer.service'],check=True,timeout=30)
  if os.environ.get('CODI_FILES_REAL_SERVICES')=='1' or not (ROOT/'issuer-switched').exists():
   c=http.client.HTTPConnection('127.0.0.1',19774,timeout=30);c.request('GET','/restart');r=c.getresponse();assert r.status==200;r.read();c.close();(ROOT/'issuer-switched').touch()
  pause_at('restart')
  return ''
 if args[0]=='start':
  if prefix:subprocess.run(['/usr/bin/systemctl','start',prefix+'-'+args[1].removeprefix('codi-beta-')],check=True,timeout=30)
  if os.environ.get('CODI_FILES_REAL_SERVICES')=='1':
   port,path=(19773,'/config.json') if args[1].endswith('frontend.service') else (19776,'/healthz')
   for _ in range(200):
    try:
     c=http.client.HTTPConnection('127.0.0.1',port,timeout=.2);c.request('GET',path,headers={'Host':'127.0.0.1:19771'});r=c.getresponse();r.read();c.close()
     if r.status==200:break
    except OSError:pass
    time.sleep(.05)
   else:raise RuntimeError('disposable dependent did not become ready')
  return ''
 raise AssertionError(args)
def hostrun(args):
 args=list(args);n=args[2] if len(args)>2 else ''
 if os.environ.get('CODI_FILES_REAL_TIMER')=='1':
  prefix=os.environ['CODI_FILES_SYSTEMD_PREFIX'];mapped=prefix+('-renew.timer' if n.endswith('.timer') else '-renew.service')
  result=subprocess.run([args[0],args[1],mapped,*args[3:]],check=True,capture_output=True,text=True,timeout=30)
  if args[1]=='stop' and mapped.endswith('.timer'):pause_at('timer-stopped')
  return result.stdout
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
   c=http.client.HTTPConnection('127.0.0.1',int(os.environ['CODI_FILES_CADDY_PORT']),timeout=timeout);c.request('GET',path,headers={'Host':parsed.hostname});r=c.getresponse();body=r.read();status=r.status;c.close()
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
 if name in ('files_webctl','main_webctl'):
  def fixture_run(args,**kw):
   if os.environ.get('CODI_FILES_REAL_CADDY')=='1':
    if args[:4]==['runuser','-u','caddy','--']:operation,path='validate',args[args.index('--config')+1]
    elif args[:2]==['systemctl','reload']:
     operation,path='reload','/etc/caddy/Caddyfile'
     if (ROOT/'block-gate').exists() and tomllib.loads(Path('/home/dflanag3/webhost-sites/sites.toml').read_text()).get('codi_beta_maintenance'):
      (ROOT/'blocked-pid').write_text(str(os.getpid()))
      while (ROOT/'block-gate').exists():time.sleep(.05)
     if (ROOT/'block-forward').exists() and tomllib.loads(Path('/home/dflanag3/webhost-sites/sites.toml').read_text()).get('codi_beta_opfs'):
      (ROOT/'blocked-pid').write_text(str(os.getpid()))
      while (ROOT/'block-forward').exists():time.sleep(.05)
     if (ROOT/'block-main').exists() and any(site.get('domain')=='ksu.codes' and site.get('codi_simplified')=='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480' for site in tomllib.loads(Path('/home/dflanag3/webhost-sites/sites.toml').read_text())['sites']):
      (ROOT/'blocked-pid').write_text(str(os.getpid()))
      while (ROOT/'block-main').exists():time.sleep(.05)
    else:raise AssertionError(args)
    subprocess.run([sys.executable,'-I','-B',os.environ['CODI_FILES_CADDY_HELPER'],operation,str(path)],check=True,timeout=45)
   return types.SimpleNamespace(returncode=0,stdout='')
  globals['run']=fixture_run
  globals['subprocess']=types.SimpleNamespace(run=lambda *a,**k:types.SimpleNamespace(returncode=0),DEVNULL=None)
 return result
builtins.exec=fixture_exec
action=sys.argv[1]
sys.argv=['launch',action]
if os.environ.get('CODI_MAIN_LAUNCH')=='1':
 target=Path('/srv/codi-connected/operators/main-qualified-e7e8-v1/main-launcher.py')
 raw=target.read_bytes()
 expected=os.environ['CODI_MAIN_LAUNCHER_SHA256']
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Fixture launcher source changed')
 source=raw.decode();anchor=" raise ValueError('Research launcher disabled until coordinated beta successor and qualification')\n"
 if source.count(anchor)!=1:raise ValueError('Fixture requires exact hard-disable')
 # Python eliminates code after the unconditional raise at compile time. Only
 # this disposable in-memory derivative removes that exact line; disk and
 # production source remain untouched.
 source=source.replace(anchor,'',1)
 namespace={'__name__':'__main__','__file__':str(target),'__package__':None,'__builtins__':builtins.__dict__}
 exec(compile(source,str(target),'exec'),namespace)
else:runpy.run_path(str(Path(os.environ['CODI_FILES_FIXTURE_BUNDLE'])/'ops/beta_files_launch.py'),run_name='__main__')
