#!/usr/bin/env python3
"""Pinned managed controller and Caddy using disposable translated routes."""
import contextlib,fcntl,hashlib,importlib.util,json,os,re,subprocess,sys,tempfile,threading,time,types,urllib.error,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
here=Path(__file__).resolve().parent;ops=here.parents[1]/'beta-isolated-hosting/ops';sys.path[:0]=[str(ops),str(here.parent)]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
old=load('common',ops/'common_live.py');v2=load('v2',ops/'common.py');load('scaffold',ops/'scaffold_live.py');ctl=load('ctl',ops/'webctl_live.py');snap=load('snap',ops/'beta_files_snapshots.py');successor=load('beta_successor',here.parent/'beta-successor.py');rm=load('asset_router',here/'asset-router.py');fm=load('asset_floor',here/'asset-floor.py')
from opfs_managed import ManagedBinding
from opfs_gate_rescue import GateRescue
OLD=Path(sys.argv[1]);NEW=Path(sys.argv[2]);CADDY=Path(sys.argv[3]);stage=os.environ.get('CODI_ASSET_KILL','floor');port=int(os.environ.get('CODI_ASSET_CONTROLLER_PORT','19881'));admin=port+1
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b'fixture main service')
 def log_message(self,*args):pass
backend=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=backend.serve_forever,daemon=True);thread.start()
try:
 with tempfile.TemporaryDirectory(prefix='830c-controller-') as d:
  t=Path(d);t.chmod(0o700);hosting=t/'hosting';hosting.mkdir();etc=t/'etc';etc.mkdir();logs=t/'logs';logs.mkdir();(t/'lock').touch()
  subprocess.run([sys.executable,'-B',str(here/'build-generator.py'),'--old',str(OLD),'--new',str(NEW),'--out',str(t/'gen')],check=True,capture_output=True);subprocess.run([sys.executable,'-B',str(here/'build-inventory.py'),str(t/'inv')],check=True,capture_output=True)
  asset=load('asset_common',t/'gen/common.py');inv=load('asset_inventory',t/'inv/render_inventory.py')
  def bound(path,module):return types.SimpleNamespace(source=path.read_bytes(),module=module)
  a=bound(ops/'common_live.py',old);b=bound(ops/'common.py',v2);c=bound(t/'gen/common.py',asset)
  x=rm.snapshots(snap=snap,successor=successor,oldgen=a,v2gen=b,newgen=c,manifest=(ops/'sites_live.toml').read_bytes(),old_manifest=(ops/'beta_files_candidate.json').read_bytes(),new_manifest=(NEW/'manifest.json').read_bytes(),table=(ops.parent/'OPFS-ROUTE-TABLE.json').read_bytes(),selector='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480')
  def translated(module,data,mode):
   raw=module.caddy(data,mode);end=raw.index('\n}\n\n(site_defaults)')+3;raw=raw[:raw.index('{\n')]+'{\n admin 127.0.0.1:'+str(admin)+'\n auto_https off\n default_bind 127.0.0.1\n}\n'+raw[end:]
   raw=re.sub(r'(?m)^(?:http://)?([a-zA-Z0-9.-]+) \{',lambda m:'http://'+m.group(1)+':'+str(port)+' {',raw);raw=re.sub(r'127\.0\.0\.1:(?:80[0-9]{2}|81[0-9]{2}|28[0-9]{3})',f'127.0.0.1:{backend.server_port}',raw)
   return raw.replace('/var/log/caddy/',str(logs)+'/').replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS').replace('/srv/data/codi-beta-opfs/'+rm.OLD,str(OLD)).replace('/srv/data/codi-beta-opfs/'+rm.NEW,str(NEW))
  def wrap(g):
   m=g.module;return types.SimpleNamespace(source=g.source,module=types.SimpleNamespace(caddy=lambda data,mode:translated(m,data,mode),unit=m.unit,validate=m.validate,dump=m.dump))
  ga,gb,gc=map(wrap,(a,b,c))
  for n,g in (('baseline',gb),('gate',ga),('candidate',gc)):x[n]['caddy']=g.module.caddy(x[n+'Data'],'production').encode()
  class OSProxy:
   def __getattr__(self,n):return getattr(os,n)
   def chown(self,path,uid,gid):assert Path(path).is_relative_to(t)
  ctl.os=OSProxy();ctl.ROOT=hosting;ctl.owner=lambda:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid());ctl.pwd=types.SimpleNamespace(getpwnam=lambda _:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()));realpath=Path
  def safe(value):
   s=str(value)
   if s=='/var/log/caddy':return logs
   if s.startswith('/etc/caddy/'):return etc/s[len('/etc/caddy/'):]
   p=realpath(value)
   if not p.is_relative_to(t):raise ValueError('fixture path escape')
   return p
  ctl.Path=safe;ctl.BACKUPS=t/'backups';ctl.snapshot=lambda p:(t/'backups').mkdir(exist_ok=True);ctl.caddy=gb.module.caddy;ctl.unit=v2.unit
  class SubprocessProxy:
   DEVNULL=subprocess.DEVNULL
   def run(self,args,**kw):
    if args[:3]==['systemctl','is-active','--quiet']:return types.SimpleNamespace(returncode=0)
    raise AssertionError(args)
  ctl.subprocess=SubprocessProxy()
  def run(args,**kw):
   if args[:2]==['systemctl','reload']:
    if stage=='inner-before' and not (t/'files-asset-floor.json').exists():os._exit(17)
    if stage=='inner-after' and (t/'files-asset-floor.json').exists():os._exit(17)
    return subprocess.run([str(CADDY),'reload','--address','127.0.0.1:'+str(admin),'--config',str(etc/'Caddyfile'),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   if args[:4]==['runuser','-u','caddy','--']:return subprocess.run([str(CADDY),'validate',*map(str,args[5:])],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   raise AssertionError(args)
  ctl.run=run
  initial=inv.RenderInventory(hosting,etc,gb.module,ga.module,x['baselineData'],x['gateData'],owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),opfs_to_gate=True)
  for path,(before,after,metadata) in initial.targets.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(before);path.chmod(metadata[2])
  paths={'common':hosting/'common.py','manifest':hosting/'sites.toml','caddy':etc/'Caddyfile'}
  for name in paths:paths[name].write_bytes(x['baseline'][name])
  paths['caddy'].chmod(0o640);floor=t/'opfs-floor.json';floor.write_text(json.dumps({'version':1,'baseline':fm.ORIGINAL_BASE,'candidate':fm.OLD}));floor.chmod(0o600);floor_hash=hashlib.sha256(floor.read_bytes()).hexdigest()
  proc=subprocess.Popen([str(CADDY),'run','--config',str(paths['caddy']),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  def get(host,path):
   with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,headers={'Host':host}),timeout=5) as r:return r.status,r.read()
  try:
   for _ in range(100):
    if proc.poll() is not None:raise RuntimeError(proc.stderr.read().decode())
    try:get('ksu.codes','/healthz');break
    except OSError:time.sleep(.05)
   fd=[None]
   @contextlib.contextmanager
   def held():
    if fd[0] is not None:raise ValueError('lock reentry')
    fd[0]=os.open(t/'lock',os.O_RDWR);fcntl.flock(fd[0],fcntl.LOCK_EX)
    try:yield
    finally:os.close(fd[0]);fd[0]=None
   def check():
    if fd[0] is None:raise ValueError('lock required')
   class Timer:
    def __init__(self):self.s={'active':True,'enabled':True}
    def snapshot(self):return dict(self.s)
    def stop_if_active(self,v):self.s['active']=False
    def assert_quiescent(self):pass
    def assert_recoverable(self,v):pass
    def restore(self,v):self.s=dict(v)
   def main_health():assert get('ksu.codes','/healthz')==(200,b'fixture main service')
   def gate_health():
    main_health()
    try:get('beta.ksu.codes','/desktop-apps.js?simplified=1')
    except urllib.error.HTTPError as e:
     if e.code==503:return
     raise
    raise AssertionError('maintenance gate did not deny beta loader')
   def health(name):
    main_health()
    if name=='gate':gate_health()
    elif name=='candidate':
     status,body=get('beta.ksu.codes','/desktop-apps.js?simplified=1');assert status==200 and hashlib.sha256(body).hexdigest()==json.loads((NEW/'manifest.json').read_bytes())['files']['shell/desktop-apps.js']['sha256']
   def backup(values):
    path=t/'backup';path.mkdir(exist_ok=True,mode=0o700)
    for n,data in values.items():(path/n).write_bytes(data)
    return str(path)
   timer=Timer();r=rm.Router(snapshots=x,baseline_gen=gb,gate_gen=ga,candidate_gen=gc,inventory=inv.RenderInventory,ctl=ctl,paths=paths,hosting_root=hosting,caddy_dir=etc,uid=os.getuid(),gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),timer=timer,lock=held,check_lock=check,beta_ready=check,gate_ready=check,main_health=main_health,route_health=health,caddy_active=lambda:(os.kill(proc.pid,0),main_health()),backup=backup,nested_journal=t/'nested.json')
   asset_floor=t/'files-asset-floor.json';rescue=GateRescue(r.adapter(x['candidate'],x['gate']),check,t/'rescue.json',x['candidate'],x['gate'],check,check)
   binding=ManagedBinding(held,check,{n:x[n] for n in ('baseline','gate','candidate')},r.transaction,r.read,r.prepare,lambda:asset_floor.exists(),lambda rec,mode:check(),gate_health,lambda rec:health('candidate'),lambda rec:main_health(),lambda rec:check(),rescue)
   txn=fm.AssetFloor(binding,t);pid=os.fork()
   if pid==0:
    try:txn.apply_exact(phase=lambda n:os._exit(17) if n==stage else None)
    except BaseException:
     import traceback;traceback.print_exc();os._exit(18)
    os._exit(19)
   _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17,stage
   # Only the killed child injects the fault; recovery must perform real reloads.
   killed_stage=stage;post=killed_stage in ('floor','forward','healthy','inner-after');assert asset_floor.exists()==post
   stage='recovery';txn.recover_exact();assert r.read()==x['candidate' if post else 'baseline']
   assert hashlib.sha256(floor.read_bytes()).hexdigest()==floor_hash and not txn.journal.exists();main_health()
   print('PASS pinned controller and real Caddy, original floor and e7 main after '+killed_stage+' kill; fixture timer/health')
  finally:proc.terminate();proc.wait(timeout=10)
finally:backend.shutdown();backend.server_close();thread.join(2)
