#!/usr/bin/env python3
"""Uninstalled protected launcher candidate: never execute on a live host yet."""
import argparse,copy,hashlib,json,os,pwd,socket,stat,sys,types,urllib.request
from pathlib import Path
PKG=Path('/srv/codi-connected/operators/main-qualified-e7e8-v1')
BETA=Path('/srv/codi-connected/operators/files-install-input-ce18b7794adc2472/ops')
RELEASE='e7e8fb9fc1f964ec1b206462468f91b60e8bac1d8117ed29c5f1099abdac3480'
SUCCESSOR=Path('/srv/codi-connected/operators/beta-recovery-e7-v1')
SUCCESSOR_PREFLIGHT='9bbfd5e256a70fd385286a008af92d3928f6ea1511ad19062b60e14ac526df83'
PINS={'beta_launcher.py':'9c1b32ecb71993649a2bd8e61f652486448543842a06c1654d685055959b9a95','beta_transaction.py':'8b365d054c423cc8af3460ad9fffdb6bb1808ab5e79b7b7068a86145eae4ff6a','common.py':'d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1','scaffold_live.py':'28054ff66acf1450104b88f25afd41ce3a2d4b9cd9c3aecb49dd237f18e1fedd','microduck_hosting.py':'0adc990bb2beb801520fa9382e2924517f5bdd399e187cad6bcda9f3d57551fc','hardware_hosting.py':'34bea543dc4ac80702d68a43e361d9bfa291b831f37c48cc44a2a42f1cc0928f','cardboard_hosting.py':'9aff2ac2a91a743a4b0e6a7a876a775ac8de6515e0fd5e2261c33d9767','render_inventory.py':'c6a14a1d3ddbe52a592ecc2e519d430ca654056af99b3af1a92e43dcbb4c0c35','beta_files_preflight.py':'4f9bdcd5d47f6d2e0bf02c80bdb181dd36c62ce7b2046cb0bc0d960fa7cd05ff','beta_files_host_health.py':'d7ec08eabae1b13492c8fd533565da096e35dbed164f29dc4d61b91ee41f43ca','beta_signed_health.py':'ba8186d9b7fb44443914fecdf0da67989215f0b56fe13620bbad15639f029a81','beta_signed_probe.py':'e38cc2007b085666b0279259b7ec4143a7ad67a7d15d87655add57be6851257a','forward-transaction.py':'538d7e7438f61ab39f0449ab1e44f9af3df4db824cb0bca026fb8eb352cf8508','render-inventory.py':'e4f139b6956b0315b2728d82c1036aaaccf2e2d9313bd49f6fe8229a887fd3a8'}
GUARD='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783'
def sha(x):return hashlib.sha256(x).hexdigest()
def protected(path):
 path=Path(path)
 for p in (path,*path.parents):
  v=p.lstat()
  if p.is_symlink() or v.st_uid!=0 or v.st_mode&0o022:raise ValueError('Unprotected code path: '+str(p))
def load(path,pin,alias):
 protected(path);raw=path.read_bytes()
 if sha(raw)!=pin:raise ValueError('Code pin changed: '+str(path))
 m=types.ModuleType(alias);m.__file__=str(path);sys.modules[alias]=m;exec(compile(raw,str(path),'exec'),m.__dict__);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=('plan','apply','recover'));args=p.parse_args()
 raise ValueError('Research launcher disabled until coordinated beta successor and qualification')
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost' or Path(__file__).absolute()!=PKG/'main-launcher.py':raise ValueError('Protected fixed-path root launcher required')
 protected(PKG);protected(Path(__file__).absolute());protected(BETA)
 def b(name,alias=None):return load(BETA/name,PINS[name],alias or name.removesuffix('.py'))
 host=b('beta_launcher.py');txmod=b('beta_transaction.py');pre=b('beta_files_preflight.py');b('beta_signed_probe.py');signedmod=b('beta_signed_health.py');healthmod=b('beta_files_host_health.py')
 for name in ('microduck_hosting.py','hardware_hosting.py','cardboard_hosting.py'):b(name)
 gen=b('common.py','common');b('scaffold_live.py','scaffold');b('render_inventory.py');invmod=load(PKG/'render-inventory.py',PINS['render-inventory.py'],'main_inventory');forward=load(PKG/'forward-transaction.py',PINS['forward-transaction.py'],'main_forward');successor=load(PKG/'main-successor-preflight.py',SUCCESSOR_PREFLIGHT,'main_successor_preflight')
 root=host.ROOT;lock=host.HostLock();private=Path('/var/lib/webhost-ops');host.protected(private)
 if stat.S_IMODE(private.stat().st_mode)!=0o700:raise ValueError('Unsafe journal directory')
 journal=private/'main-restriction-journal.json';candidate=Path('/srv/codi-connected/simplified')/RELEASE;worker=Path('/srv/codi-gateway/releases')/healthmod.WORKER
 def verify_candidate():
  lock.check();pre.protected_ancestors(candidate);raw=host.read(candidate/'assets/desktop/cache-manifest.json');v=json.loads(raw)
  if sha(raw)!='0bc92c08d01c945a6f5d3da22279761aa2ba2a26157d45396d13c4a2d54ee122' or v.get('id')!=RELEASE or sha(json.dumps(v['files'],sort_keys=True,separators=(',',':')).encode())!=RELEASE:raise ValueError('Candidate manifest mismatch')
  special={'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'};found=set()
  for f in candidate.rglob('*'):
   st=f.lstat()
   if f.is_symlink() or st.st_uid!=0 or not(stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)) or (stat.S_ISREG(st.st_mode) and (st.st_nlink!=1 or stat.S_IMODE(st.st_mode)!=0o644)) or (stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode)!=0o755) or os.listxattr(f):raise ValueError('Unsafe candidate entry')
   if not f.is_file():continue
   name=f.relative_to(candidate).as_posix();found.add(name)
   if name in special:continue
   h=hashlib.sha256();n=0
   with f.open('rb') as stream:
    while chunk:=stream.read(1024*1024):h.update(chunk);n+=len(chunk)
   if v['files'].get(name)!={'bytes':n,'sha256':h.hexdigest()}:raise ValueError('Candidate file mismatch')
  if found!=set(v['files'])|special or sha(host.read(candidate/'assets/desktop/offline-worker.js'))!='3ff9fb3c79c4fc71cc8be3156330b4a5891c813ec08c59bb2ab118d0daca4240':raise ValueError('Candidate inventory mismatch')
  fs=os.statvfs('/var/lib/codi-user-files/ksu')
  if fs.f_bavail*fs.f_frsize<5*1024**3:raise ValueError('Account filesystem below reserve')
  lock.check()
 def installed_code():
  lock.check();pre.protected_ancestors(root/'ops')
  if sha(host.read(root/'ops/common.py'))!=PINS['common.py'] or sha(host.read(root/'ops/webctl.py'))!=GUARD:raise ValueError('Installed hosting code drift')
  protected(SUCCESSOR);successor.verify(SUCCESSOR,host.read,lock.check)
 def floor():
  lock.check();ctl._floor_guard_active=True;ctl._check_floor_record()
  for n in ('opfs-transition.json','files-inner-hosting.json','files-issuer-switch.json','files-emergency-gate.json','files-normalization.json','beta-hosting-journal.json'):
   q=private/n
   if q.exists() or q.is_symlink():raise ValueError('Other hosting transaction pending: '+n)
 def caddy_active():
  x=host.unit_state('caddy.service')
  if x.get('ActiveState')!='active' or x.get('MainPID') in (None,'0') or x.get('NeedDaemonReload')!='no':raise ValueError('Caddy unavailable')
 class LazyJose:
  value=None
  def __getattr__(self,name):
   lock.check()
   if self.value is None:
    host.verify_beta_worker(worker,healthmod.WORKER);path=worker/'codiserver-server-v0.3.0/codiauth/jose.py';host.protected(path);m=types.ModuleType('main_pinned_jose');m.__file__=str(path);exec(compile(host.read(path),str(path),'exec'),m.__dict__);self.value=m
   return getattr(self.value,name)
 signed=healthmod.create(lock=lock,launcher=host,preflight=pre,signed_health=signedmod,jose=LazyJose())
 def readiness():installed_code();floor();verify_candidate();caddy_active();host.main_ready();signed();lock.check()
 def health():
  readiness();host.public_health(include_beta=True)
  opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open('https://ksu.codes/app.js?simplified=1',timeout=8) as response:body=response.read(4*1024*1024+1)
  if sha(body)!='10774564316c596b2b65abc62eae6c3fda1bbd7aaa3eb615c18a8a2599acf49f':raise ValueError('Served main app differs from candidate')
 with lock.held():
  installed_code()
  # Compile only the exact guarded controller bytes while the lock is held.
  raw=host.read(root/'ops/webctl.py');ctl=types.ModuleType('main_webctl');ctl.__file__=str(root/'ops/webctl.py');exec(compile(raw,ctl.__file__,'exec'),ctl.__dict__);ctl.ROOT=root;ctl.MANIFEST=root/'sites.toml';gen.ROOT=root;gen.MANIFEST=root/'sites.toml'
  floor();verify_candidate();caddy_active();host.main_ready();signed()
  live=ctl.load();old=copy.deepcopy(live);new=copy.deepcopy(live);a=[s for s in old['sites'] if s.get('domain')=='ksu.codes'];b=[s for s in new['sites'] if s.get('domain')=='ksu.codes']
  if len(a)!=1 or len(b)!=1 or a[0].get('codi_simplified') not in (forward.OLD_SELECTOR,forward.NEW_SELECTOR):raise ValueError('Unexpected main selector')
  a[0]['codi_simplified']=forward.OLD_SELECTOR;b[0]['codi_simplified']=forward.NEW_SELECTOR;raw=host.read(root/'ops/common.py')
  oldpoint={'common':raw,'manifest':gen.dump(old).encode(),'caddy':gen.caddy(old,'production').encode()};newpoint={'common':raw,'manifest':gen.dump(new).encode(),'caddy':gen.caddy(new,'production').encode()};forward.validate_endpoints(ctl,oldpoint,newpoint,forward.OLD_SELECTOR,forward.NEW_SELECTOR)
  owner=pwd.getpwuid(root.stat().st_uid);caddy=pwd.getpwnam('caddy');inventory=invmod.MainRenderInventory(root,'/etc/caddy',gen,old,new,forward.OLD_SELECTOR,forward.NEW_SELECTOR,owner_uid=owner.pw_uid,owner_gid=owner.pw_gid,caddy_gid=caddy.pw_gid)
  bound=types.SimpleNamespace(source=raw,module=gen);paths={'common':root/'ops/common.py','manifest':root/'sites.toml','caddy':Path('/etc/caddy/Caddyfile')};timer=txmod.SystemdTimer(host.run)
  inner=txmod.ManagedWebctlAdapter(ctl,bound,bound,paths,timer,lock.held,lock.check,readiness,health,health,inventory.check,caddy_active,host.backup);adapter=forward.ForwardAdapter(inner,verify_candidate,lambda:(floor(),installed_code()));tx=txmod.Transaction(adapter,journal)
  if args.action=='plan':
   if journal.exists() or journal.is_symlink() or adapter.read()!=oldpoint:raise ValueError('Pending or unexpected hosting state')
   inventory.check(old);print(json.dumps({'action':'plan','status':'PASS','candidate':RELEASE,'productionQualified':False}));return
  if args.action=='apply':forward.apply(tx,adapter,oldpoint,newpoint,forward.OLD_SELECTOR,forward.NEW_SELECTOR);print(json.dumps({'action':'apply','status':'PASS'}));return
  if journal.is_symlink() or not journal.is_file():raise ValueError('Protected main journal required')
  host.protected(journal);v=journal.lstat()
  if v.st_nlink!=1 or stat.S_IMODE(v.st_mode)!=0o600:raise ValueError('Unsafe main journal')
  forward.recover(tx,adapter,oldpoint,newpoint,forward.OLD_SELECTOR,forward.NEW_SELECTOR);print(json.dumps({'action':'recover','status':'PASS'}))
if __name__=='__main__':main()
