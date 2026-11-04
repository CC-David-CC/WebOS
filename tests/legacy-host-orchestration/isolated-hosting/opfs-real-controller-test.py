#!/usr/bin/env python3
"""Loopback fixture using copied webctl.caddy_apply, actual generators and inventory."""
import contextlib,copy,fcntl,hashlib,importlib.util,os,re,socket,subprocess,sys,tempfile,threading,time,tomllib,types,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
root=Path(__file__).resolve().parents[1];ops=root/'ops';sys.path.insert(0,str(ops))
for n,pin in {'common_live.py':'d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0','webctl_live.py':'e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c','hardware_hosting.py':'34bea543dc4ac80702d68a43e361d9bfa291b831f37c48cc44a2a42f1cc0928f','microduck_hosting.py':'0adc990bb2beb801520fa9382e2924517f5bdd399e187cad6bcda9f3d57551fc','cardboard_hosting.py':'9aff2ac2a91a743a4b0e6a7a876a775ac6de6515e0fd5c219d5e2261c33d9767','scaffold_live.py':'28054ff66acf1450104b88f25afd41ce3a2d4b9cd9c3aecb49dd237f18e1fedd'}.items():assert hashlib.sha256((ops/n).read_bytes()).hexdigest()==pin,n
assert hashlib.sha256((ops/'sites_live.toml').read_bytes()).hexdigest()=='9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'
common_spec=importlib.util.spec_from_file_location('common',ops/'common_live.py');common=importlib.util.module_from_spec(common_spec);sys.modules['common']=common;common_spec.loader.exec_module(common)
import render_inventory
from beta_transaction import Transaction,ManagedWebctlAdapter
from opfs_managed import HeldAdapter
scaffold_spec=importlib.util.spec_from_file_location('scaffold',ops/'scaffold_live.py');scaffold=importlib.util.module_from_spec(scaffold_spec);sys.modules['scaffold']=scaffold;scaffold_spec.loader.exec_module(scaffold)
spec=importlib.util.spec_from_file_location('fixture_webctl',ops/'webctl_live.py');ctl=importlib.util.module_from_spec(spec);spec.loader.exec_module(ctl)
CADDY=os.environ.get('CODI_CADDY','/tmp/codi-microduck-hosting-evidence/caddy');ADMIN=19973;PORT=19974
class Backend(BaseHTTPRequestHandler):
 def do_GET(self):
  body=b'fixture main service';self.send_response(200);self.end_headers();self.wfile.write(body)
 def log_message(self,*a):pass
backend=ThreadingHTTPServer(('127.0.0.1',0),Backend);th=threading.Thread(target=backend.serve_forever,daemon=True);th.start();bp=backend.server_port
with tempfile.TemporaryDirectory(prefix='opfs-controller-integration-') as temp:
 t=Path(temp);os.chmod(t,0o700);hosting=t/'hosting';hosting.mkdir();etc=t/'etc-caddy';etc.mkdir();logs=t/'logs';logs.mkdir();(t/'lock').touch();source=(ops/'common_live.py').read_bytes();initial=tomllib.loads((ops/'sites_live.toml').read_text());assert 'codi_beta_maintenance' not in initial;old=copy.deepcopy(initial);old['codi_beta_maintenance']=False;gate=copy.deepcopy(old);gate['codi_beta_maintenance']=True
 # Compare untouched, pinned generator bytes outside beta, before the fixture's
 # port/path transformations needed to keep Caddy on loopback and off /etc.
 def without_beta(text):
  start=text.index('beta.ksu.codes {');end=text.index('\n}\n',start)+3;return text[:start]+text[end:]
 assert all(common.caddy(initial,mode)==common.caddy(old,mode) for mode in ('prepare','production'))
 assert without_beta(common.caddy(old,'production'))==without_beta(common.caddy(gate,'production'))
 def render(data,mode):
  raw=common.caddy(data,mode);end=raw.index('\n}\n\n(site_defaults)')+3;raw=raw[:raw.index('{\n')]+'{\n admin 127.0.0.1:'+str(ADMIN)+'\n auto_https off\n default_bind 127.0.0.1\n}\n'+raw[end:]
  raw=re.sub(r'(?m)^(?:http://)?([a-zA-Z0-9.-]+) \{',lambda m:'http://'+m.group(1)+':'+str(PORT)+' {',raw)
  raw=re.sub(r'127\.0\.0\.1:(?:80[0-9]{2}|81[0-9]{2}|28[0-9]{3})',f'127.0.0.1:{bp}',raw)
  raw=raw.replace('/var/log/caddy/',str(logs)+'/').replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS')
  return raw
 gen=types.SimpleNamespace(caddy=render,unit=common.unit,validate=common.validate,dump=common.dump)
 class OsProxy:
  def __getattr__(self,n):return getattr(os,n)
  def chown(self,path,uid,gid):
   assert Path(path).is_relative_to(t)
 ctl.os=OsProxy();ctl.ROOT=hosting;ctl.owner=lambda:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid());ctl.pwd=types.SimpleNamespace(getpwnam=lambda name:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()))
 def safe_path(value):
  s=str(value)
  if s=='/var/log/caddy':return logs
  if s.startswith('/etc/caddy/'):return etc/s[len('/etc/caddy/'):]
  p=Path(value)
  if not p.is_relative_to(t):raise ValueError('Fixture path escaped: '+s)
  return p
 ctl.Path=safe_path
 real_subprocess=subprocess
 class SubprocessProxy:
  DEVNULL=subprocess.DEVNULL
  def run(self,args,**kw):
   if args[:3]==['systemctl','is-active','--quiet']:return types.SimpleNamespace(returncode=0)
   raise AssertionError('unexpected process '+str(args))
 ctl.subprocess=SubprocessProxy()
 def run(args,**kw):
  if args[:2]==['systemctl','reload']:
   return real_subprocess.run([CADDY,'reload','--address',f'127.0.0.1:{ADMIN}','--config',str(etc/'Caddyfile'),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  if args[:4]==['runuser','-u','caddy','--']:
   return real_subprocess.run([CADDY,'validate',*map(str,args[5:])],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  raise AssertionError('unexpected run '+str(args))
 ctl.run=run;ctl.BACKUPS=t/'backups';ctl.caddy=render;ctl.unit=common.unit
 # Keep Caddy-generated backups confined to the test directory.
 ctl.snapshot=lambda p:(t/'backups').mkdir(exist_ok=True)
 norminv=render_inventory.RenderInventory(hosting,etc,gen,gen,initial,old,owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),normalize_maintenance=True)
 inv=render_inventory.RenderInventory(hosting,etc,gen,gen,old,gate,owner_uid=os.getuid(),owner_gid=os.getgid(),caddy_uid=os.getuid(),caddy_gid=os.getgid(),maintenance_only=True)
 for path,(before,after,meta) in norminv.targets.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(before);path.chmod(meta[2])
 paths={'common':hosting/'common.py','manifest':hosting/'sites.toml','caddy':etc/'Caddyfile'};paths['common'].write_bytes(source);paths['manifest'].write_text(common.dump(initial));paths['caddy'].write_text(render(initial,'production'));paths['caddy'].chmod(0o640)
 proc=subprocess.Popen([CADDY,'run','--config',str(paths['caddy']),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 def request(host,path):
  req=urllib.request.Request(f'http://127.0.0.1:{PORT}'+path,headers={'Host':host});
  with urllib.request.urlopen(req,timeout=3) as r:return r.status,r.read()
 try:
  for _ in range(100):
   if proc.poll() is not None:raise RuntimeError(proc.stderr.read().decode())
   try:
    if request('ksu.codes','/healthz')[1]==b'fixture main service':break
   except OSError:time.sleep(.05)
  else:raise RuntimeError('Caddy did not start')
  fd=None
  @contextlib.contextmanager
  def held():
   global fd
   if fd is not None:raise ValueError('lock reacquired')
   fd=os.open(t/'lock',os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX)
   try:yield
   finally:os.close(fd);fd=None
  def check():
   if fd is None:raise ValueError('lock not held')
  class Timer:
   def __init__(self):self.s={'active':True,'enabled':True}
   def snapshot(self):return dict(self.s)
   def stop_if_active(self,v):assert self.s==v;self.s['active']=False
   def assert_quiescent(self):pass
   def assert_recoverable(self,v):assert self.s in (v,{**v,'active':False})
   def restore(self,v):self.s=dict(v)
  def main_health():assert request('ksu.codes','/healthz')==(200,b'fixture main service')
  def gate_health():main_health();assert request('beta.ksu.codes','/')[1].startswith(b'<!doctype html><title>Beta maintenance')
  def ready():
   with urllib.request.urlopen(f'http://127.0.0.1:{bp}/health',timeout=2) as r:assert r.read()==b'fixture main service'
  def active():
   os.kill(proc.pid,0);main_health()
  def backup(values):
   folder=t/'protected-backup';folder.mkdir(mode=0o700,exist_ok=True)
   for name,data in values.items():
    path=folder/name;path.write_bytes(data);path.chmod(0o600)
    with path.open('rb') as f:os.fsync(f.fileno())
   fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
   return str(folder)
  timer=Timer();bound=types.SimpleNamespace(source=source,module=gen);adapter=ManagedWebctlAdapter(ctl,bound,bound,paths,timer,held,check,ready,main_health,main_health,norminv.check,active,backup)
  original={'common':source,'manifest':common.dump(initial).encode(),'caddy':render(initial,'production').encode()};normalized={'common':source,'manifest':common.dump(old).encode(),'caddy':render(old,'production').encode()};assert original['caddy']==normalized['caddy'];normal_journal=t/'normalization.json';normal_tx=Transaction(HeldAdapter(adapter,check),normal_journal);floor=t/'opfs-floor.json'
  # A real child exits after changing the manifest; generic pre-floor recovery
  # must restore absent-key source and must not create a v2 floor.
  pid=os.fork()
  if pid==0:
   try:
    with held():normal_tx.apply(original,normalized,phase=lambda x:os._exit(19) if x=='manifest-written' else None)
   except BaseException:
    import traceback;traceback.print_exc();os._exit(20)
  _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==19
  assert normal_journal.exists() and not floor.exists()
  with held():normal_tx.recover()
  assert adapter.read()==original and not normal_journal.exists() and not floor.exists();norminv.check(initial,after=True);main_health()
  def unavailable():raise ValueError('injected readiness failure')
  adapter._ready=unavailable
  try:
   with held():normal_tx.apply(original,normalized)
   raise AssertionError('failed readiness accepted')
  except ValueError as error:assert 'injected readiness failure' in str(error)
  assert adapter.read()==original and not normal_journal.exists() and not floor.exists()
  adapter._ready=ready
  with held():
   if floor.exists() or floor.is_symlink():raise ValueError('Normalization refused after v2 floor')
   normal_tx.apply(original,normalized)
  assert adapter.read()==normalized and not floor.exists();norminv.check(old,after=True);main_health()
  adapter._render_targets_check=inv.check;adapter._health=gate_health
  old_snapshot={'common':source,'manifest':common.dump(old).encode(),'caddy':render(old,'production').encode()};new_snapshot={'common':source,'manifest':common.dump(gate).encode(),'caddy':render(gate,'production').encode()};journal=t/'emergency.json';tx=Transaction(HeldAdapter(adapter,check),journal)
  pid=os.fork()
  if pid==0:
   try:
    with held():tx.apply_gate(old_snapshot,new_snapshot,phase=lambda x:os._exit(17) if x=='caddy-applied' else None)
   except BaseException as e:
    import traceback;traceback.print_exc();os._exit(18)
  _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17
  assert journal.exists();stored=journal.read_bytes();assert request('beta.ksu.codes','/')[1].startswith(b'<!doctype html><title>Beta maintenance')
  assert all((t/'protected-backup'/name).read_bytes()==value for name,value in old_snapshot.items())
  assert (t/'protected-backup').stat().st_mode&0o777==0o700
  paths['manifest'].write_text('external-drift')
  try:
   with held():tx.recover_gate(old_snapshot,new_snapshot)
   raise AssertionError('untrusted source accepted')
  except ValueError as error:assert 'drift' in str(error)
  assert journal.read_bytes()==stored and paths['manifest'].read_text()=='external-drift'
  paths['manifest'].write_bytes(new_snapshot['manifest'])
  with held():tx.recover_gate(old_snapshot,new_snapshot)
  assert not journal.exists();inv.check(gate,after=True);assert request('ksu.codes','/healthz')==(200,b'fixture main service');assert request('beta.ksu.codes','/')[1].startswith(b'<!doctype html><title>Beta maintenance')
  print('PASS interrupted ordinary pre-floor normalization and pinned recovery; actual copied webctl, inventory and real Caddy gate recovery preserve non-beta bytes and main response')
 finally:proc.terminate();proc.wait(timeout=10);backend.shutdown();backend.server_close();th.join(2)
