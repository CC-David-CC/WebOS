#!/usr/bin/env python3
"""Candidate protected Files entrypoint. Not installed; requires lead review.

Run via the root-protected venv as `python -I -B beta_files_launch.py plan|apply|recover`.
Only this host's reviewed beta transaction is accepted; no path/port overrides.
"""
import argparse,hashlib,json,os,pwd,socket,stat,sys,types,urllib.error,urllib.request
from pathlib import Path
PKG=Path(__file__).absolute().parent
PINS={
 'beta_launcher':'9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95',
 'beta_files_preflight':'4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff',
 'beta_files_host_health':'d7ec08eabae1b13492c8fd533565da096e35dbed164f29dc4d61b91ee41f43ca',
 'beta_signed_health':'ba8186d9b7fb44443914fecdf0da67989215f0b56fe13620bbad15639f029a81',
 'beta_signed_probe':'e38cc2007b085666b0279259b7ec4143a7ad67a7d15d87655add57be6851257a',
 'beta_files_router':'4adcb333a35aa806c9a365158085f9fbffdc1a277ce52d725292cdebf9b0c82c',
 'beta_files_assembly':'d1652d5624dc63b7de03ed4c0388f4fc1a80ed5b2d54e95e1ed84d66c732b732',
 'beta_files_snapshots':'0bb2dc596120e973b0827749d600806313d2b5899cab19a7737174044d8008a8',
 'beta_issuer_switch':'a276aa9dc23c2b3ef3ac2cebb6796b9943ea54d48688ecf599e5915fbdd7c9fb',
 'beta_service_operator':'e16449cf68484736f89ca07e936ab9b79bb9e8bbb557f372f8433ec6028680ac',
 'beta_transaction':'8b365d054c423cc8af3460ad9fffdb6bb1808ab5e79b7b7068a86145eae4ff6a',
 'opfs_floor':'acf693d769a31cfe8a34ae173281474eb5cc1c28c7817ba74bbd466e63f8975e',
 'opfs_managed':'9db8a944745e99a11f9dff2ebdb2298d98fa8a0e2982171bbc3e17757ba7dd6f',
 'opfs_gate_rescue':'60ffee45211d6572808119ace7dff0119440991e7b091a82b98c3a3ce83fd294',
 'render_inventory':'c6a14a1d3ddbe52a592ecc2e519d430ca654056af99b3af1a92e43dcbb4c0c35',
 'webctl_live':'e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c',
 'scaffold_live':'28054ff66acf1450104b88f25afd41ce3a2d4b9cd9c3aecb49dd237f18e1fedd',
 'hardware_hosting':'34bea543dc4ac80702d68a43e361d9bfa291b831f37c48cc44a2a42f1cc0928f',
 'microduck_hosting':'0adc990bb2beb801520fa9382e2924517f5bdd399e187cad6bcda9f3d57551fc',
 'cardboard_hosting':'9aff2ac2a91a743a4b0e6a7a876a775ac6de6515e0fd5c219d5e2261c33d9767',
 'beta_worker_adapter':'f6e81e114672a0c736853d7425982521fe9858902c496689eef8a75e74a2e5ca',
 'common_live':'d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0',
 'common':'d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1',
}
def safe(path):
 path=Path(path)
 for p in (path,*path.parents):
  st=p.lstat()
  if p.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('unprotected launcher path: '+str(p))
def read(path,limit=8*1024*1024):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_uid!=0 or a.st_nlink!=1 or a.st_mode&0o022 or a.st_size>limit:raise ValueError('unsafe bundle input')
  chunks=[];left=a.st_size
  while left:
   part=os.read(fd,min(left,65536))
   if not part:raise ValueError('short read')
   chunks.append(part);left-=len(part)
  b=os.fstat(fd)
  if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise ValueError('bundle changed')
  return b''.join(chunks)
 finally:os.close(fd)
def load(name,alias=None,fake_file=None):
 path=PKG/(name+'.py');safe(path);raw=read(path)
 if hashlib.sha256(raw).hexdigest()!=PINS[name]:raise ValueError('bundle source pin mismatch: '+name)
 module=types.ModuleType(alias or name);module.__file__=str(fake_file or path);sys.modules[module.__name__]=module;exec(compile(raw,module.__file__,'exec'),module.__dict__);return module

def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=('plan','apply','recover'));args=parser.parse_args()
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('root on box-webhost required')
 safe(Path(__file__).absolute());safe(PKG)
 # All dependencies are compiled only after their embedded pin has matched.
 host=load('beta_launcher');preflight=load('beta_files_preflight')
 for name in ('microduck_hosting','hardware_hosting','cardboard_hosting'):load(name)
 root=host.ROOT;old=load('common_live','common',root/'ops/common.py');new=load('common','files_common',root/'ops/common.py')
 old.ROOT=new.ROOT=root;old.MANIFEST=new.MANIFEST=root/'sites.toml'
 load('scaffold_live','scaffold',root/'ops/scaffold.py');ctl=load('webctl_live','files_webctl',root/'ops/webctl.py')
 transaction=load('beta_transaction');load('render_inventory');load('opfs_managed');floor_mod=load('opfs_floor');rescue_mod=load('opfs_gate_rescue');load('beta_signed_probe');signed=load('beta_signed_health');hosthealth=load('beta_files_host_health');issuer=load('beta_issuer_switch');svc=load('beta_service_operator');snap=load('beta_files_snapshots');router_mod=load('beta_files_router');assembly_mod=load('beta_files_assembly')
 import opfs_managed
 lock=host.HostLock();check_lock=lock.check;journal=Path('/var/lib/webhost-ops');host.protected(journal)
 if stat.S_IMODE(journal.stat().st_mode)!=0o700:raise ValueError('private journal root required')
 candidate=Path('/srv/data/codi-beta-opfs')/snap.CANDIDATE
 # The protected bundle retains the exact signed-off public manifest. Gate
 # recovery must not depend on the availability of the forward asset tree.
 manifest=read(PKG/'sites_live.toml');candidate_manifest=read(PKG/'beta_files_candidate.json');table=read(PKG.parent/'OPFS-ROUTE-TABLE.json')
 old_bound=types.SimpleNamespace(source=read(PKG/'common_live.py'),module=old);new_bound=types.SimpleNamespace(source=read(PKG/'common.py'),module=new)
 x=snap.build(old=old_bound,new=new_bound,manifest=manifest,candidate_manifest=candidate_manifest,route_table=table)
 baseline=hashlib.sha256(x['normalized']['manifest']).hexdigest();floorpath=journal/'opfs-floor.json'
 # Do not make gateway availability a prerequisite for *closing* the gate.
 # Signed/forward operations load JOSE lazily from the verified release under
 # the same host lock; they never import it via an ambient search path.
 worker=Path('/srv/codi-gateway/releases')/host.GW
 class LazyJose:
  module=None
  def __getattr__(self,name):
   check_lock()
   if self.module is None:
    host.verify_beta_worker(worker,host.GW);jose_path=worker/'codiserver-server-v0.3.0/codiauth/jose.py';host.protected(jose_path)
    module=types.ModuleType('files_pinned_jose');module.__file__=str(jose_path);exec(compile(host.read(jose_path),str(jose_path),'exec'),module.__dict__);self.module=module
   return getattr(self.module,name)
 jose=LazyJose()
 signed_check=hosthealth.create(lock=lock,launcher=host,preflight=preflight,signed_health=signed,jose=jose)
 def reserve():
  f=os.statvfs('/var/lib/codi-user-files/beta')
  if f.f_bavail*f.f_frsize<5*1024**3:raise ValueError('beta account volume below 5 GiB reserve')
 def artifacts():
  check_lock();preflight.protected_ancestors(root/'ops')
  if host.sha(host.read(root/'ops/webctl.py'))!=preflight.GUARDED_WEBCTL:raise ValueError('guarded hosting entrypoints not installed')
  preflight.tree(candidate,'manifest.json',snap.CANDIDATE);preflight.tree('/srv/data/codi-beta-native/'+issuer.NEW,'connected-release.json',issuer.NEW);host.verify_beta_worker(worker,host.GW);host.verify_static();host.verify_overlay()
  identities=svc.verify_accounts()
  for beta,mainpath,role in (('/var/lib/codi-connected/beta/issuer','/var/lib/codi-connected/ksu/issuer','issuer'),('/var/lib/codi-gateway/beta','/var/lib/codi-gateway/ksu','gateway'),('/var/lib/codi-user-files/beta','/var/lib/codi-user-files/ksu','gateway')):
   path=Path(beta);a=path.lstat();b=Path(mainpath).stat()
   if path.is_symlink() or not stat.S_ISDIR(a.st_mode) or a.st_uid!=identities[role]['uid'] or stat.S_IMODE(a.st_mode)!=0o700 or (a.st_dev,a.st_ino)==(b.st_dev,b.st_ino):raise ValueError('beta state isolation changed')
  host.main_ready();check_lock()
 def public(path):
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  try:
   with opener.open('https://beta.ksu.codes'+path,timeout=8) as r:return r.status,r.read(4*1024*1024+1)
  except urllib.error.HTTPError as e:return e.code,e.read(65536)
 def gate_health():
  check_lock();host.main_ready();status,body=public('/')
  if status!=200 or b'Beta maintenance' not in body or public('/app.js?simplified=1')[0]!=503:raise ValueError('beta gate unavailable')
 def candidate_health():
  check_lock();artifacts();status,body=public('/app.js?simplified=1');route=json.loads(table)['routes'];expected=next(v['sha256'] for v in route if v['path']=='/app.js')
  if status!=200 or len(body)>4*1024*1024 or hashlib.sha256(body).hexdigest()!=expected:raise ValueError('beta candidate asset mismatch')
  signed_check()
 def signed_baseline():
  check_lock();policy_path=hosthealth.POLICY;host.protected(policy_path);raw=host.read(policy_path,32768)
  if host.sha(raw)!=hosthealth.POLICY_SHA:raise ValueError('beta policy changed')
  policy=json.loads(raw);identity=policy.get('identity',policy);pin=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  def custody():
   check_lock();host.protected(hosthealth.CREDENTIAL);preflight.protected_ancestors(hosthealth.CREDENTIAL.parent);host.verify_beta_worker(worker,host.GW);check_lock()
  return signed.SignedHealth(check_lock=check_lock,check_custody=custody,origin=hosthealth.ORIGIN,issuer_port=28118,gateway_port=28140,policy=identity,policy_sha256=pin,credential_path=hosthealth.CREDENTIAL,jose=jose)()
 def beta_ready():
  check_lock();unit=host.read('/etc/systemd/system/codi-beta-issuer.service');digest=host.sha(unit)
  if digest==issuer.PINS[issuer.UNIT_NAMES[0]]:host.beta_ready();signed_baseline()
  elif digest==hosthealth.UNITS[issuer.UNIT_NAMES[0]]:signed_check()
  else:raise ValueError('unrecognized beta issuer unit')
 def caddy_active():
  s=host.unit_state('caddy.service')
  if s.get('ActiveState')!='active' or s.get('MainPID') in (None,'0') or s.get('UnitFileState')!='enabled' or s.get('NeedDaemonReload')!='no':raise ValueError('Caddy unavailable')
 def gate_ready():
  # Keep gate closure dependent on the protected lock, controller and Caddy;
  # forward assets and signed issuer health are deliberately not inputs.
  check_lock();host.protected(journal);preflight.protected_ancestors(root/'ops')
  if host.sha(host.read(root/'ops/webctl.py'))!=preflight.GUARDED_WEBCTL:raise ValueError('guarded hosting entrypoints not installed')
  caddy_active();check_lock()
 def main_health():
  host.main_ready();host.public_health()
 def route_health(name):
  if name=='gate':gate_health()
  elif name=='candidate':candidate_health()
  else:main_health()
 owner=pwd.getpwuid(root.stat().st_uid);caddy=pwd.getpwnam('caddy');paths={'common':root/'ops/common.py','manifest':root/'sites.toml','caddy':Path('/etc/caddy/Caddyfile')};timer=transaction.SystemdTimer(host.run)
 router=router_mod.FilesRouter(snapshots=x,old_generator=old_bound,new_generator=new_bound,ctl=ctl,paths=paths,hosting_root=root,caddy_dir='/etc/caddy',uid=owner.pw_uid,gid=owner.pw_gid,caddy_gid=caddy.pw_gid,caddy_uid=0,timer=timer,lock=lock.held,check_lock=check_lock,beta_ready=beta_ready,gate_ready=gate_ready,main_health=main_health,route_health=route_health,caddy_active=caddy_active,backup=host.backup,nested_journal=journal/'files-inner-hosting.json')
 plan={'origin':svc.ORIGIN,'ports':svc.PORTS,'network':'disabled','native_release':'/srv/codi-connected/releases/microduck-issuer-'+issuer.OLD,'native_manifest':issuer.OLD,'worker_release':'/srv/codi-gateway/releases/'+svc.GATEWAY_MANIFEST,'worker_manifest':svc.GATEWAY_MANIFEST,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':hosthealth.POLICY_SHA,'guest_source_sha256':svc.GUEST_SOURCE};old_unit=svc.render_units(plan)[issuer.UNIT_NAMES[0]].encode()
 def issuer_gate():
  check_lock()
  if not floorpath.exists() or router.read()!=x['gate']:raise ValueError('durable floor and gate required')
  gate_health()
 switch=issuer.IssuerSwitch(unit_dir='/etc/systemd/system',journal=journal/'files-issuer-switch.json',check_lock=check_lock,check_floor_gate=issuer_gate,verify_release=lambda:(artifacts(),reserve()),health=signed_check);install=assembly_mod.IssuerInstall(switch,old_unit)
 rescue=rescue_mod.GateRescue(router.adapter(x['candidate'],x['gate']),check_lock,journal/'files-emergency-gate.json',x['candidate'],x['gate'],gate_ready,caddy_active)
 binding=opfs_managed.ManagedBinding(lock.held,check_lock,{'baseline':x['normalized'],'gate':x['gate'],'candidate':x['candidate']},router.transaction,router.read,router.prepare,lambda:floorpath.exists(),lambda rec,mode:(artifacts(),reserve()) if mode in ('initial','forward') else artifacts(),gate_health,lambda rec:candidate_health(),lambda rec:main_health(),install,rescue)
 floor=floor_mod.FloorJournal(binding,journal);assembly=assembly_mod.FilesAssembly(floor=floor,issuer=switch,installer=install,issuer_old=old_unit,normal_adapter=router.adapter(x['initial'],x['normalized']),normal_journal=journal/'files-normalization.json',normal_old=x['initial'],normal_new=x['normalized'],v2_health=candidate_health,pre_normalization=lambda:(artifacts(),reserve(),caddy_active(),beta_ready()),pre_normalization_recovery=lambda:(artifacts(),caddy_active()))
 if args.action=='plan':
  with lock.held():
   artifacts();reserve();caddy_active();beta_ready()
   if any((journal/name).exists() or (journal/name).is_symlink() for name in ('opfs-floor.json','opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json')):raise ValueError('transition or floor already exists')
   if router.read()!=x['initial']:raise ValueError('unrecognized initial hosting snapshot')
   router.adapter(x['initial'],x['normalized'])._render_targets_check(x['normalizedData'])
  print(json.dumps({'status':'PASS','action':'plan','candidate':snap.CANDIDATE}))
 elif args.action=='apply':assembly.apply(baseline,snap.CANDIDATE);print(json.dumps({'status':'PASS','action':'apply'}))
 else:print(json.dumps({'status':assembly.recover(baseline,snap.CANDIDATE),'action':'recover'}))
if __name__=='__main__':main()
