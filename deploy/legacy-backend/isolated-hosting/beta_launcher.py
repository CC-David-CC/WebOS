#!/usr/bin/env python3
"""Candidate protected beta-hosting launcher. DO NOT RUN before review.

This stage is not installed. It accepts the explicitly documented residual
check-to-rename race in the existing user-writable hosting-lock hierarchy.
Run only from a separately root-protected, reviewed bundle with `python -I -B`.
"""
import argparse,contextlib,copy,fcntl,grp,hashlib,hmac,http.client,json,os,pwd,socket,stat,subprocess,sys,tempfile,tomllib,types,urllib.error,urllib.request
from pathlib import Path
ROOT=Path('/home/dflanag3/webhost-sites');PKG=Path(__file__).absolute().parent
RELEASE='0965a0cbdd022f588061cdc23e10eb6b18fa5977cc3f6a05569439eaf11d2020';GW='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1';NATIVE='1666491de4fe097285f02a5b6f7602fe57e4b9d3b2995bf016d4a9e809e36a51'
PINS={'common.py':'d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0','common_live.py':'d4f05bbb709e056354a5d2eb4d3a78741cbd044e4d100b965b91ec9a428a5ad0','webctl_live.py':'e012fb1d838e06c6a2e382c85d249fc10a3f8753f0b9f9abd3247230e7f40d0c','scaffold_live.py':'28054ff66acf1450104b88f25afd41ce3a2d4b9cd9c3aecb49dd237f18e1fedd','microduck_hosting.py':'0adc990bb2beb801520fa9382e2924517f5bdd399e187cad6bcda9f3d57551fc','hardware_hosting.py':'34bea543dc4ac80702d68a43e361d9bfa291b831f37c48cc44a2a42f1cc0928f','cardboard_hosting.py':'9aff2ac2a91a743a4b0e6a7a876a775ac6de6515e0fd5c219d5e2261c33d9767','render_inventory.py':'f02218afad23e1fd610b3753e976916dddc689c89f46ef77b5da83f9efea1ae2','sites_live.toml':'9bf8afdaab7d321940cc01b9275af81ba2b1ad558a3b966f24e05c6561a317b5'}
UNIT={'codi-beta-issuer.service':'e6b8279c32a89f38ee4a3b2ba6c27777413c13b1b98611e78ff9b0d52dca1244','codi-beta-gateway.service':'f7fe40291ed89df101e511673b201b5606ba526333b1f55743fdec8ed069b47e','codi-beta-frontend.service':'4b909882dfd879235e10bf3cbb004bd3e61db1786cfd99e122b7abbd39be5f78'}
PINS['beta_transaction.py']='0c1eb1a9a4cf41e8b0c56c68e09428a453eccf108a378a7e20dd3028f8d6174d'
PINS['beta_service_operator.py']='e16449cf68484736f89ca07e936ab9b79bb9e8bbb557f372f8433ec6028680ac'
PINS['beta_worker_adapter.py']='f6e81e114672a0c736853d7425982521fe9858902c496689eef8a75e74a2e5ca'
SITES={'python.coach':200,'code.contractors':200,'ksu.codes':200,'arpa.net.ai':200,'plastic.download':200,'official.bid':200,'does.trade':200,'codi.codes':200,'cardboard.ksu.codes':200,'hardware.ksu.codes':401}
def sha(data):return hashlib.sha256(data).hexdigest()
def protected(p):
 for x in [p,*p.parents]:
  st=x.lstat()
  if x.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('Unprotected root path: '+str(x))
def read(path,limit=4*1024*1024):
 path=Path(path)
 if not path.is_absolute() or '..' in path.parts:raise ValueError('Absolute path required')
 d=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
 try:
  for part in path.parts[1:-1]:
   n=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=d);os.close(d);d=n
  fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=d)
  try:
   a=os.fstat(fd)
   if not stat.S_ISREG(a.st_mode) or a.st_nlink!=1 or a.st_size>limit:raise ValueError('Unsafe bounded input')
   chunks=[];size=0
   while size<=limit:
    x=os.read(fd,min(65536,limit+1-size))
    if not x:break
    chunks.append(x);size+=len(x)
   b=os.fstat(fd)
   if size!=a.st_size or (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise ValueError('Input changed')
   return b''.join(chunks)
  finally:os.close(fd)
 finally:os.close(d)
def module(name,filename,expected,fake_file=None):
 data=read(PKG/filename)
 if sha(data)!=expected:raise ValueError('Bundle source pin changed: '+filename)
 m=types.ModuleType(name);m.__file__=str(fake_file or (PKG/filename));sys.modules[name]=m;exec(compile(data,m.__file__,'exec'),m.__dict__);return m
def protected_module(name,path,expected):
 protected(path);data=read(path)
 if sha(data)!=expected:raise ValueError('Protected module pin changed: '+str(path))
 m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m;exec(compile(data,str(path),'exec'),m.__dict__);return m

def service_preflight():
 # Load only the pinned protected verifiers, never ambient user modules.
 op_root=Path('/srv/codi-gateway/operators/8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7');protected(op_root)
 manifest=read(op_root/'file-operator.json')
 if sha(manifest)!='8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7':raise ValueError('File operator manifest changed')
 record=json.loads(manifest);found=set()
 for item in op_root.rglob('*'):
  info=item.lstat()
  if item.is_symlink() or info.st_uid!=0 or info.st_mode&0o022 or not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):raise ValueError('Unsafe file operator')
  if item.is_file() and item.name!='file-operator.json':
   name=item.relative_to(op_root).as_posix();data=read(item)
   if record['files'].get(name)!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('File operator source changed')
   found.add(name)
 if found!=set(record['files']):raise ValueError('File operator inventory changed')
 package=types.ModuleType('file_service');package.__path__=[];sys.modules['file_service']=package
 package.operator=protected_module('file_service.operator',op_root/'file_service/operator.py','a503ca0af5ead0d715005714dada13306796f264b8e3ec4c2b9877d65eb89517')
 native=Path('/srv/codi-connected/releases')/('microduck-issuer-'+NATIVE)
 package=types.ModuleType('origin_service');package.__path__=[];sys.modules['origin_service']=package
 package.release=protected_module('origin_service.release',native/'origin_service/release.py','0a1fb0b964b4baa7c5e10faa2efc290f9d851fdccd14276b848ef10b4571544d')
 beta=module('beta_service_preflight','beta_service_operator.py',PINS['beta_service_operator.py'])
 plan={'origin':'https://beta.ksu.codes','ports':{'issuer':28118,'frontend':28132,'gateway':28140},'network':'disabled','native_release':str(native),'native_manifest':NATIVE,'worker_release':str(Path('/srv/codi-gateway/releases')/GW),'worker_manifest':GW,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','guest_source_sha256':'4ff040270a2a48fcef6f70c98d574338ba2502e35a29486cd6dead78f2916a5a'}
 beta.verify_inputs(plan,worker_verify=verify_beta_worker)

def run(args):return subprocess.run(args,check=True,capture_output=True,text=True,timeout=15).stdout
class HostLock:
 def __init__(self):self.fd=None;self.path=ROOT/'.controller.lock'
 @contextlib.contextmanager
 def held(self):
  self.fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:
   st=os.fstat(self.fd)
   if not stat.S_ISREG(st.st_mode) or st.st_uid!=0 or st.st_nlink!=1 or st.st_mode&0o022:raise ValueError('Unsafe controller lock')
   fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB);self.check();yield
  finally:os.close(self.fd);self.fd=None
 def check(self):
  if self.fd is None:raise ValueError('Hosting lock not held')
  a=os.fstat(self.fd);b=self.path.lstat()
  if self.path.is_symlink() or (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError('Hosting lock changed')
def unit_state(name):
 text=run(['/usr/bin/systemctl','show',name,'-p','ActiveState','-p','MainPID','-p','FragmentPath','-p','DropInPaths','-p','User','-p','Group','-p','UnitFileState','-p','NeedDaemonReload'])
 return dict(line.split('=',1) for line in text.splitlines())
def get(port,path,host='beta.ksu.codes'):
 c=http.client.HTTPConnection('127.0.0.1',port,timeout=3)
 try:
  c.request('GET',path,headers={'Host':host});r=c.getresponse();body=r.read(65537)
  if len(body)>65536:raise ValueError('Unbounded service response')
  return r.status,body
 finally:c.close()
def main_ready():
 native=Path('/etc/codi-connected/ksu/managed.json');files=Path('/etc/codi-user-files/ksu/managed.json');protected(native);protected(files)
 if sha(read(native))!='6d72467c7dfabcdc65bc1216a31cf67bc6156b1d08f7a6c5d69778a595b2e6b8' or sha(read(files))!='8111fa0c926fbdb1878910aa7ba59b3d33426a7939569f60152dce0c565140d5':raise ValueError('Main managed config changed')
 for unit in ('codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service','codi-ksu-hidden-issuer.service','codi-ksu-hidden-guest.service'):
  state=unit_state(unit)
  if state.get('ActiveState')!='active' or state.get('MainPID') in (None,'0') or state.get('NeedDaemonReload')!='no':raise ValueError('Main service unavailable: '+unit)
 if any((native.parent/name).exists() or (native.parent/name).is_symlink() for name in ('private-file-code.json','native-rollout.json','site-cutover.json','maintenance.json')):raise ValueError('Main managed journal pending')
 status,raw=get(8132,'/config.json','ksu.codes');guest=json.loads(raw)
 other_status,raw=get(8118,'/config.json','ksu.codes');issuer=json.loads(raw)
 if status!=200 or other_status!=200 or guest.get('identity',{}).get('issuer')!='https://ksu.codes' or guest.get('identity')!=issuer.get('identity'):raise ValueError('Main guest/issuer configuration unavailable')
def public_health(include_beta=False):
 sites=dict(SITES)
 if include_beta:sites['beta.ksu.codes']=200
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for domain,expected in sites.items():
  try:
   with opener.open('https://'+domain+'/',timeout=8) as r:status=r.status
  except urllib.error.HTTPError as e:status=e.code
  if status!=expected:raise ValueError('Unexpected public status for '+domain)
def verify_beta_worker(worker,pin):
 protected(worker);raw=read(worker/'files-service.json');manifest=json.loads(raw)
 if sha(raw)!=pin or set(manifest)!={'files','version'} or manifest['version']!='codi-private-file-service/1' or not isinstance(manifest['files'],dict):raise ValueError('Beta worker manifest changed')
 found=set()
 for path in worker.rglob('*'):
  st=path.lstat()
  if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022 or not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):raise ValueError('Unsafe beta worker')
  if path.is_file() and path.relative_to(worker).as_posix()!='files-service.json':
   rel=path.relative_to(worker).as_posix();data=read(path)
   if manifest['files'].get(rel)!={'bytes':len(data),'sha256':sha(data)}:raise ValueError('Beta worker file changed')
   found.add(rel)
 if found!=set(manifest['files']):raise ValueError('Beta worker inventory changed')
def beta_ready():
 for name,digest in UNIT.items():
  path=Path('/etc/systemd/system')/name;protected(path)
  if sha(read(path))!=digest:raise ValueError('Beta unit pin changed: '+name)
  state=unit_state(name);role=name.removeprefix('codi-beta-').removesuffix('.service');user='codi-beta-'+role
  if state.get('ActiveState')!='active' or state.get('UnitFileState')!='enabled' or state.get('NeedDaemonReload')!='no' or state.get('MainPID') in (None,'0') or state.get('FragmentPath')!=str(path) or state.get('DropInPaths') or state.get('User')!=user or state.get('Group')!=user:raise ValueError('Beta service changed: '+name)
  if role=='gateway':
   adapter=module('beta_worker_adapter','beta_worker_adapter.py',PINS['beta_worker_adapter.py'])
   adapter.Adapter(None,lambda *_:None)._process_state(int(state['MainPID']),GW)
 policy=Path('/etc/codi-user-files/beta/issuer-policy.json');protected(policy)
 policy_raw=read(policy,32768)
 if sha(policy_raw)!='71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca':raise ValueError('Beta policy changed')
 policy_value=json.loads(policy_raw);policy_identity=policy_value.get('identity',policy_value)
 verify_beta_worker(Path('/srv/codi-gateway/releases')/GW,GW)
 status,raw=get(28132,'/config.json');config=json.loads(raw)
 if status!=200 or config.get('identity',{}).get('issuer')!='https://beta.ksu.codes' or 'guestNetwork' in config or config.get('gateway',{}).get('basePath')!='/gateway':raise ValueError('Beta frontend configuration changed')
 status,raw=get(28118,'/config.json');issuer=json.loads(raw)
 if status!=200 or issuer.get('identity',{}).get('issuer')!='https://beta.ksu.codes' or config.get('identity')!=issuer.get('identity') or issuer.get('identity')!=policy_identity:raise ValueError('Beta issuer, frontend and gateway identity differ')
 if get(28132,'/guest-network')[0] not in (403,404):raise ValueError('Beta guest network is not disabled')
 status,raw=get(28140,'/healthz')
 if status!=200 or json.loads(raw)!={'status':'ok','scope':'personal-files'}:raise ValueError('Beta gateway health failed')
 status,raw=get(8132,'/config.json','ksu.codes');main=json.loads(raw)
 def keys(c):return {json.dumps(k['jwk'],sort_keys=True,separators=(',',':')) for k in c['identity']['authorityKeys']}
 if status!=200 or not keys(main) or not keys(config) or keys(main)&keys(config):raise ValueError('Beta and main identity keys overlap')
 users=[pwd.getpwnam(n) for n in ('codi-beta-issuer','codi-beta-gateway','codi-beta-frontend')];main_users=[pwd.getpwnam(n) for n in ('codi-issuer','codi-gateway','codi-guest')]
 main_groups={gid for user in main_users for gid in os.getgrouplist(user.pw_name,user.pw_gid)}
 if any(not u.pw_uid or not u.pw_gid for u in users) or len({u.pw_uid for u in users})!=3 or len({u.pw_gid for u in users})!=3 or {u.pw_uid for u in users}&{u.pw_uid for u in main_users} or {u.pw_gid for u in users}&main_groups or any(set(os.getgrouplist(u.pw_name,u.pw_gid))!={u.pw_gid} for u in users):raise ValueError('Beta service identities overlap')
 for beta,mainpath,uid in [('/var/lib/codi-connected/beta/issuer','/var/lib/codi-connected/ksu/issuer',users[0].pw_uid),('/var/lib/codi-gateway/beta','/var/lib/codi-gateway/ksu',users[1].pw_uid),('/var/lib/codi-user-files/beta','/var/lib/codi-user-files/ksu',users[1].pw_uid)]:
  path=Path(beta);x=path.lstat();y=Path(mainpath).stat()
  if path.is_symlink() or not stat.S_ISDIR(x.st_mode) or x.st_uid!=uid or stat.S_IMODE(x.st_mode)!=0o700 or (x.st_dev,x.st_ino)==(y.st_dev,y.st_ino):raise ValueError('Beta state custody or isolation changed')
 first=Path('/etc/codi-connected/beta/guest-cookie.secret');second=Path('/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret')
 for path in (first,second):
  protected(path)
  if stat.S_IMODE(path.stat().st_mode)!=0o600:raise ValueError('Guest cookie custody changed')
 if hmac.compare_digest(read(first,128),read(second,128)):raise ValueError('Beta and main guest secrets overlap')

def verify_native():
 root=Path('/srv/codi-connected/releases')/('microduck-issuer-'+NATIVE);protected(root)
 raw=read(root/'connected-release.json');manifest=json.loads(raw)
 if sha(raw)!=NATIVE or not isinstance(manifest.get('files'),dict):raise ValueError('Native manifest changed')
 found=set()
 for path in root.rglob('*'):
  st=path.lstat()
  if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022 or not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):raise ValueError('Unsafe native release')
  if not path.is_file() or path.name=='connected-release.json':continue
  if st.st_nlink!=1:raise ValueError('Linked native release file')
  name=path.relative_to(root).as_posix();h=hashlib.sha256();size=0
  with path.open('rb') as f:
   while chunk:=f.read(1024*1024):h.update(chunk);size+=len(chunk)
  if manifest['files'].get(name)!={'bytes':size,'sha256':h.hexdigest()}:raise ValueError('Native release file changed: '+name)
  found.add(name)
 if found!=set(manifest['files']):raise ValueError('Native release inventory changed')

def backup(old):
 parent=Path('/var/backups/webhost-sites');protected(parent)
 if stat.S_IMODE(parent.stat().st_mode)!=0o700:raise ValueError('Private backup directory required')
 folder=Path(tempfile.mkdtemp(prefix='beta-hosting-',dir=parent));os.chmod(folder,0o700)
 for key,value in old.items():
  fd=os.open(folder/(key+'.bak'),os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb') as f:f.write(value);f.flush();os.fsync(f.fileno())
 for p in (folder,parent):
  fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC)
  try:os.fsync(fd)
  finally:os.close(fd)
 return str(folder)

def verify_static():
 root=Path('/srv/codi-connected/simplified')/RELEASE;protected(root)
 raw=read(root/'assets/desktop/cache-manifest.json');manifest=json.loads(raw)
 if sha(json.dumps(manifest['files'],sort_keys=True,separators=(',',':')).encode())!=RELEASE or manifest.get('id')!=RELEASE:raise ValueError('Desktop manifest changed')
 if sha(raw)!='18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720' or sha(read(root/'assets/desktop/offline-worker.js'))!='e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c':raise ValueError('Desktop cache worker changed')
 found=set();excluded={'assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js'}
 for path in root.rglob('*'):
  st=path.lstat()
  if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022 or not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):raise ValueError('Unsafe static release')
  if not path.is_file():continue
  name=path.relative_to(root).as_posix()
  if name in excluded:continue
  h=hashlib.sha256();size=0
  with path.open('rb') as f:
   while chunk:=f.read(1024*1024):h.update(chunk);size+=len(chunk)
  if manifest['files'].get(name)!={'bytes':size,'sha256':h.hexdigest()}:raise ValueError('Desktop asset changed: '+name)
  found.add(name)
 if found!=set(manifest['files']):raise ValueError('Desktop inventory changed')

OLD_OVERLAY='bc3c7e659d40f853ed31bfec257079d65cd92c86011b1b1b86e80f32dd7a9c1c'
OLD_DESKTOP='0b9e14ead8e2be0ffb0f08d59fc2ee7aacc5bb1eb66bbac25edbcc32b2754088'
OLD_MIRROR='2044b7585672ebf015a55d0b5cc6f40d56a3c4bd2d22b57a162f56f9c64e2234'
OVERLAY='1d6b8f4e72e4c3f533afeea10589ac931a3dfe56d4bbaf03abec6d7d99a55d5a'
DESKTOP='0d1cbcb4e6b23beb0c6b7eecce8b35244438fb4341c2e325203c739c64118b81'
MIRROR='cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed'
def verify_overlay_package(overlay,desktop,mirror):
 root=Path('/srv/codi-connected/beta-overlays')/overlay;protected(root)
 raw=read(root/'manifest.json');value=json.loads(raw)
 if sha(raw)!=overlay or value.get('version')!='codi-beta-overlay/1' or value.get('baseline_release')!=RELEASE or value.get('desktopSHA256')!=desktop or value.get('mirrorSHA256')!=mirror:raise ValueError('Beta overlay manifest changed')
 expected={'assets/desktop/desktop-apps.'+desktop+'.js':desktop,'storage/browser/mirror.'+mirror+'.mjs':mirror};seen=set();dirs=set();expected_dirs={'assets','assets/desktop','storage','storage/browser'}
 if set(value.get('files',{}))!=set(expected):raise ValueError('Beta overlay inventory differs')
 for path in root.rglob('*'):
  st=path.lstat()
  if path.is_symlink() or st.st_uid!=0 or st.st_mode&0o022 or not (stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode)):raise ValueError('Unsafe beta overlay')
  name=path.relative_to(root).as_posix()
  if path.is_dir():dirs.add(name);continue
  if not path.is_file():continue
  if name=='manifest.json':continue
  if name not in expected:raise ValueError('Unexpected beta overlay file')
  raw=read(path)
  if sha(raw)!=expected[name] or value['files'].get(name)!={'bytes':len(raw),'sha256':sha(raw)}:raise ValueError('Beta overlay file changed')
  seen.add(name)
 if seen!=set(expected) or dirs!=expected_dirs:raise ValueError('Beta overlay incomplete')
def verify_overlay():
 verify_overlay_package(OLD_OVERLAY,OLD_DESKTOP,OLD_MIRROR);verify_overlay_package(OVERLAY,DESKTOP,MIRROR)
def public_guarded():
 public_health(True);opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 for path,digest in (('/desktop-apps.js?simplified=1',DESKTOP),('/storage/browser/mirror.'+MIRROR+'.mjs',MIRROR),('/assets/desktop/desktop-apps.'+DESKTOP+'.js',DESKTOP),('/storage/browser/mirror.'+OLD_MIRROR+'.mjs',OLD_MIRROR),('/assets/desktop/desktop-apps.'+OLD_DESKTOP+'.js',OLD_DESKTOP)):
  with opener.open('https://beta.ksu.codes'+path,timeout=8) as response:
   raw=response.read(4*1024*1024+1)
   if len(raw)>4*1024*1024 or sha(raw)!=digest:raise ValueError('Public beta overlay mismatch')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('action',choices=('plan','apply','recover'));args=parser.parse_args()
 if args.action!='plan':raise ValueError('This rebased baseline supports read-only plan only')
 if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
 protected(PKG);protected(Path(__file__).absolute())
 # Isolated, pinned module bytes are compiled from this protected bundle. The
 # legacy controller receives the original host filename so ROOT stays correct.
 for name in ('microduck_hosting','hardware_hosting','cardboard_hosting'):module(name,name+'.py',PINS[name+'.py'])
 old=module('common','common_live.py',PINS['common_live.py'],ROOT/'ops/common.py');candidate=module('beta_candidate','common.py',PINS['common.py'],ROOT/'ops/common.py')
 old.ROOT=candidate.ROOT=ROOT;old.MANIFEST=candidate.MANIFEST=ROOT/'sites.toml'
 module('scaffold','scaffold_live.py',PINS['scaffold_live.py'],ROOT/'ops/scaffold.py')
 ctl=module('beta_webctl','webctl_live.py',PINS['webctl_live.py'],ROOT/'ops/webctl.py')
 transaction=module('beta_transaction','beta_transaction.py',PINS['beta_transaction.py']);inventory_module=module('render_inventory','render_inventory.py',PINS['render_inventory.py'])
 for host,bundle in [('common.py','common_live.py'),('webctl.py','webctl_live.py'),('scaffold.py','scaffold_live.py'),('microduck_hosting.py','microduck_hosting.py'),('hardware_hosting.py','hardware_hosting.py'),('cardboard_hosting.py','cardboard_hosting.py')]:
  if sha(read(ROOT/'ops'/host))!=PINS[bundle] and not (host=='common.py' and args.action=='recover' and sha(read(ROOT/'ops'/host))==PINS['common.py']):raise ValueError('Hosting source changed: '+host)
 old_manifest=read(PKG/'sites_live.toml')
 if sha(old_manifest)!=PINS['sites_live.toml']:raise ValueError('Hosting manifest baseline changed')
 olddata=tomllib.loads(old_manifest.decode());newdata=copy.deepcopy(olddata);newdata['codi_beta_simplified']=RELEASE;candidate.validate(newdata)
 old_bytes={'common':read(PKG/'common_live.py'),'manifest':old_manifest,'caddy':old.caddy(olddata,'production').encode()}
 new_bytes={'common':read(PKG/'common.py'),'manifest':candidate.dump(newdata).encode(),'caddy':candidate.caddy(newdata,'production').encode()}
 paths={'common':ROOT/'ops/common.py','manifest':ROOT/'sites.toml','caddy':Path('/etc/caddy/Caddyfile')}
 owner=pwd.getpwuid(ROOT.stat().st_uid);caddy=pwd.getpwnam('caddy');renders=inventory_module.RenderInventory(ROOT,'/etc/caddy',old,candidate,olddata,newdata,owner_uid=owner.pw_uid,owner_gid=owner.pw_gid,caddy_gid=caddy.pw_gid,baseline_only=True)
 # Ensure the known-good auxiliary targets match before any mutating operation.
 def caddy_active():
  state=unit_state('caddy.service')
  if state.get('ActiveState')!='active' or state.get('MainPID') in (None,'0') or state.get('UnitFileState')!='enabled' or state.get('NeedDaemonReload')!='no':raise ValueError('Caddy must already be active and enabled')
 lock=HostLock();timer=transaction.SystemdTimer(run)
 old_bound=types.SimpleNamespace(source=old_bytes['common'],module=old);new_bound=types.SimpleNamespace(source=new_bytes['common'],module=candidate)
 def ready():main_ready();beta_ready()
 def health():main_ready();public_health(True)
 def main_health():main_ready();public_health()
 adapter=transaction.ManagedWebctlAdapter(ctl,old_bound,new_bound,paths,timer,lock.held,lock.check,ready,health,main_health,renders.check,caddy_active,backup)
 journal=Path('/var/lib/webhost-ops/beta-hosting-journal.json');protected(journal.parent)
 if stat.S_IMODE(journal.parent.stat().st_mode)!=0o700:raise ValueError('Private journal directory required')
 if args.action=='plan':
  with lock.held():
   if journal.exists() or journal.is_symlink():raise ValueError('Pending beta journal')
   if adapter.read()!=old_bytes:raise ValueError('Unexpected live hosting baseline')
   free=os.statvfs('/');
   if free.f_bavail*free.f_frsize<5*1024**3:raise ValueError('Insufficient disk headroom')
   caddy_active();renders.check(newdata);main_ready();beta_ready();verify_native();service_preflight();verify_static();verify_overlay();public_guarded()
   print(json.dumps({'status':'PASS','action':'plan','release':RELEASE,'runtimeChanged':False}))
 elif args.action=='apply':
  free=os.statvfs('/')
  if free.f_bavail*free.f_frsize<5*1024**3:raise ValueError('Insufficient disk headroom')
  verify_native();service_preflight();verify_static();transaction.Transaction(adapter,journal).apply(old_bytes,new_bytes);print(json.dumps({'status':'PASS','action':'apply','release':RELEASE}))
 else:
  if journal.is_symlink() or not journal.is_file():raise ValueError('Protected beta journal required')
  protected(journal);info=journal.lstat()
  if stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:raise ValueError('Unsafe journal custody')
  pending=json.loads(read(journal))
  if transaction._decode(pending['old'])!=old_bytes or transaction._decode(pending['new'])!=new_bytes:raise ValueError('Journal does not match the pinned beta change')
  if pending.get('phase')=='committed':verify_native();service_preflight();verify_static()
  transaction.Transaction(adapter,journal).recover();print(json.dumps({'status':'PASS','action':'recover'}))
if __name__=='__main__':main()
