#!/usr/bin/env python3
"""Loopback fixture using copied webctl.caddy_apply, actual generators and inventory."""
import contextlib,copy,fcntl,hashlib,importlib.util,json,os,re,socket,subprocess,sys,tempfile,threading,time,tomllib,types,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
root=Path(__file__).resolve().parents[1];ops=root/'ops';sys.path.insert(0,str(ops))
for n,pin in {'common_live.py':'d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0','webctl_live.py':'e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c','hardware_hosting.py':'34bea543dc4ac80702d68a43e361d9bfa291b831f37c48cc44a2a42f1cc0928f','microduck_hosting.py':'0adc990bb2beb801520fa9382e2924517f5bdd399e187cad6bcda9f3d57551fc','cardboard_hosting.py':'9aff2ac2a91a743a4b0e6a7a876a775ac6de6515e0fd5c219d5e2261c33d9767','scaffold_live.py':'28054ff66acf1450104b88f25afd41ce3a2d4b9cd9c3aecb49dd237f18e1fedd'}.items():assert hashlib.sha256((ops/n).read_bytes()).hexdigest()==pin,n
assert hashlib.sha256((ops/'sites_live.toml').read_bytes()).hexdigest()=='9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'
common_spec=importlib.util.spec_from_file_location('common',ops/'common_live.py');common=importlib.util.module_from_spec(common_spec);sys.modules['common']=common;common_spec.loader.exec_module(common)
new_spec=importlib.util.spec_from_file_location('opfs_candidate_common',ops/'common.py');new_common=importlib.util.module_from_spec(new_spec);new_spec.loader.exec_module(new_common)
import render_inventory
from beta_transaction import Transaction,ManagedWebctlAdapter,_encode
from opfs_managed import HeldAdapter
from beta_files_router import FilesRouter
from opfs_floor import FloorJournal
from opfs_managed import ManagedBinding
from opfs_gate_rescue import GateRescue
from beta_files_assembly import FilesAssembly,IssuerInstall
import beta_issuer_switch as issuer,beta_service_operator as svc
scaffold_spec=importlib.util.spec_from_file_location('scaffold',ops/'scaffold_live.py');scaffold=importlib.util.module_from_spec(scaffold_spec);sys.modules['scaffold']=scaffold;scaffold_spec.loader.exec_module(scaffold)
spec=importlib.util.spec_from_file_location('fixture_webctl',ops/'webctl_live.py');ctl=importlib.util.module_from_spec(spec);spec.loader.exec_module(ctl)
CADDY=os.environ.get('CODI_CADDY','/tmp/codi-microduck-hosting-evidence/caddy');ADMIN=19847;PORT=19848;KILL=os.environ.get('CODI_KILL_STAGE','issuer-unit-written')
class Backend(BaseHTTPRequestHandler):
 def do_GET(self):
  body=b'fixture main service';self.send_response(200);self.end_headers();self.wfile.write(body)
 def log_message(self,*a):pass
backend=ThreadingHTTPServer(('127.0.0.1',0),Backend);th=threading.Thread(target=backend.serve_forever,daemon=True);th.start();bp=backend.server_port
with tempfile.TemporaryDirectory(prefix='opfs-controller-integration-') as temp:
 t=Path(temp);os.chmod(t,0o700);hosting=t/'hosting';hosting.mkdir();etc=t/'etc-caddy';etc.mkdir();logs=t/'logs';logs.mkdir();(t/'lock').touch();source=(ops/'common_live.py').read_bytes();new_source=(ops/'common.py').read_bytes();initial=tomllib.loads((ops/'sites_live.toml').read_text());assert 'codi_beta_maintenance' not in initial;old=copy.deepcopy(initial);old['codi_beta_maintenance']=False;gate=copy.deepcopy(old);gate['codi_beta_maintenance']=True
 # Compare untouched, pinned generator bytes outside beta, before the fixture's
 # port/path transformations needed to keep Caddy on loopback and off /etc.
 def without_beta(text):
  start=text.index('beta.ksu.codes {');end=text.index('\n}\n',start)+3;return text[:start]+text[end:]
 assert all(common.caddy(initial,mode)==common.caddy(old,mode) for mode in ('prepare','production'))
 assert without_beta(common.caddy(old,'production'))==without_beta(common.caddy(gate,'production'))
 def render_with(generator,data,mode):
  raw=generator.caddy(data,mode);end=raw.index('\n}\n\n(site_defaults)')+3;raw=raw[:raw.index('{\n')]+'{\n admin 127.0.0.1:'+str(ADMIN)+'\n auto_https off\n default_bind 127.0.0.1\n}\n'+raw[end:]
  raw=re.sub(r'(?m)^(?:http://)?([a-zA-Z0-9.-]+) \{',lambda m:'http://'+m.group(1)+':'+str(PORT)+' {',raw)
  raw=re.sub(r'127\.0\.0\.1:(?:80[0-9]{2}|81[0-9]{2}|28[0-9]{3})',f'127.0.0.1:{bp}',raw)
  raw=raw.replace('/var/log/caddy/',str(logs)+'/').replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS').replace('/srv/data/codi-beta-opfs/3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc','/tmp/codi-beta-opfs-transition-candidate')
  return raw
 def render(data,mode):return render_with(common,data,mode)
 def render_new(data,mode):return render_with(new_common,data,mode)
 gen=types.SimpleNamespace(caddy=render,unit=common.unit,validate=common.validate,dump=common.dump)
 gen_new=types.SimpleNamespace(caddy=render_new,unit=new_common.unit,validate=new_common.validate,dump=new_common.dump)
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
  timer=Timer();bound=types.SimpleNamespace(source=source,module=gen);newbound=types.SimpleNamespace(source=new_source,module=gen_new)
  candidate_data=copy.deepcopy(old);candidate_data['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc'
  original={'common':source,'manifest':common.dump(initial).encode(),'caddy':render(initial,'production').encode()};normalized={'common':source,'manifest':common.dump(old).encode(),'caddy':render(old,'production').encode()};gated={'common':source,'manifest':common.dump(gate).encode(),'caddy':render(gate,'production').encode()};v2={'common':new_source,'manifest':new_common.dump(candidate_data).encode(),'caddy':render_new(candidate_data,'production').encode()}
  x={'initial':original,'normalized':normalized,'gate':gated,'candidate':v2,'initialData':initial,'normalizedData':old,'gateData':gate,'candidateData':candidate_data}
  def v2health():
   main_health();status,body=request('beta.ksu.codes','/app.js?simplified=1');assert status==200 and hashlib.sha256(body).hexdigest()=='df957ec69e3930a741a1680c637c88e98a74bdaaa0dcd4abfc64f5ff264dc932'
  def route_health(name):
   if name=='gate':gate_health()
   elif name=='candidate':v2health()
   else:main_health()
  router=FilesRouter(snapshots=x,old_generator=bound,new_generator=newbound,ctl=ctl,paths=paths,hosting_root=hosting,caddy_dir=etc,uid=os.getuid(),gid=os.getgid(),caddy_gid=os.getgid(),caddy_uid=os.getuid(),timer=timer,lock=held,check_lock=check,beta_ready=ready,gate_ready=check,main_health=main_health,route_health=route_health,caddy_active=active,backup=backup,nested_journal=t/'router-journal')
  # Exact baseline unit bytes, simulated systemd state; no real beta service.
  plan={'origin':svc.ORIGIN,'ports':svc.PORTS,'network':'disabled','native_release':'/srv/codi-connected/releases/microduck-issuer-'+issuer.OLD,'native_manifest':issuer.OLD,'worker_release':'/srv/codi-gateway/releases/'+svc.GATEWAY_MANIFEST,'worker_manifest':svc.GATEWAY_MANIFEST,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','guest_source_sha256':svc.GUEST_SOURCE}
  units=t/'units';units.mkdir();unit_bytes=svc.render_units(plan)
  for name,value in unit_bytes.items():(units/name).write_text(value);(units/name).chmod(0o644)
  unitstate=t/'unitstate';unitstate.write_text(json.dumps({name:'active' for name in issuer.UNIT_NAMES}));old_unit=unit_bytes[issuer.UNIT_NAMES[0]].encode()
  def systemctl(args):
   states=json.loads(unitstate.read_text());name=args[1] if len(args)>1 else None
   if args[0]=='show':return f"ActiveState={states[name]}\nFragmentPath={units/name}\nDropInPaths=\nNeedDaemonReload=no\n"
   if args[0] in ('restart','start'):states[name]='active';unitstate.write_text(json.dumps(states));return ''
   if args==['daemon-reload']:return ''
   raise AssertionError(args)
  floorpath=t/'opfs-floor.json'
  def issuergate():check();assert floorpath.exists();gate_health()
  switch=issuer.IssuerSwitch(unit_dir=units,journal=t/'issuer-journal',check_lock=check,check_floor_gate=issuergate,verify_release=check,health=check,run=systemctl)
  orig_apply=switch.apply
  def injected_apply(*,retain=True,phase=lambda _:None):return orig_apply(retain=retain,phase=lambda x:os._exit(17) if KILL=='issuer-'+x else phase(x))
  switch.apply=injected_apply;installer=IssuerInstall(switch,old_unit)
  rescue=GateRescue(router.adapter(v2,gated),check,t/'emergency-journal',v2,gated,check,check)
  binding=ManagedBinding(held,check,{'baseline':normalized,'gate':gated,'candidate':v2},router.transaction,router.read,router.prepare,lambda:floorpath.exists(),lambda rec,mode:check(),gate_health,lambda rec:v2health(),lambda rec:main_health(),installer,rescue)
  floor=FloorJournal(binding,t)
  def complete_health():
   check();assert floorpath.exists();v2health();assert (units/issuer.UNIT_NAMES[0]).read_bytes()==issuer.derive(old_unit)
  assembly=FilesAssembly(floor=floor,issuer=switch,installer=installer,issuer_old=old_unit,normal_adapter=router.adapter(original,normalized),normal_journal=t/'normalization.json',normal_old=original,normal_new=normalized,v2_health=complete_health,pre_normalization=check,pre_normalization_recovery=check)
  pid=os.fork()
  if pid==0:
   try:assembly.apply('a'*64,candidate_data['codi_beta_opfs'],phase=lambda x:os._exit(17) if KILL==x else None)
   except BaseException:
    import traceback;traceback.print_exc();os._exit(18)
   os._exit(19)
  _,status=os.waitpid(pid,0);assert os.waitstatus_to_exitcode(status)==17
  if KILL in ('normalized','journaled','gated'):
   assert not floorpath.exists() and not switch.journal.exists()
   assert assembly.recover('a'*64,candidate_data['codi_beta_opfs'])=='pre-floor'
   assert not floorpath.exists() and not switch.journal.exists();main_health()
  else:
   assert floorpath.exists()
   if KILL=='issuer-unit-written':assert switch.journal.exists() and floor.journal.exists();gate_health()
   assert assembly.recover('a'*64,candidate_data['codi_beta_opfs'])=='v2-verified'
   assert not switch.journal.exists() and not floor.journal.exists() and floorpath.exists()
   with held():complete_health()
  print('PASS assembled copied controller, exact 3ad and real Caddy after kill '+KILL+'; fixture systemd and health')
 finally:proc.terminate();proc.wait(timeout=10);backend.shutdown();backend.server_close();th.join(2)
