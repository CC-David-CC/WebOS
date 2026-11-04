"""Actual pinned 84c/d117 controller floor and rollback test, redirected temp paths.

Fixture uses fake systemd/reload and generator inputs, not a real Caddy service.
"""
import copy,hashlib,importlib.util,json,os,sys,tempfile,tomllib,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';sys.path.insert(0,str(OPS))
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
assert hashlib.sha256((OPS/'common.py').read_bytes()).hexdigest()=='d11755a183bc5c12803b6fdc84fa54f4803c0f10c415c07bb9eecc82699132a1'
assert hashlib.sha256((OPS/'webctl_floor_candidate.py').read_bytes()).hexdigest()=='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'
common=load('common',OPS/'common.py');load('scaffold',OPS/'scaffold_live.py');ctl=load('fixture_webctl',OPS/'webctl_floor_candidate.py');main=load('main_forward',Path(__file__).with_name('forward-transaction.py'))
data=tomllib.loads((OPS/'sites_live.toml').read_text());data['codi_beta_maintenance']=False;data['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';target=copy.deepcopy(data);next(s for s in target['sites'] if s['domain']=='ksu.codes')['codi_simplified']=main.NEW_SELECTOR
common.validate(data);common.validate(target)
assert ctl._beta_block(common.caddy(data,'production'))==ctl._beta_block(common.caddy(target,'production'))
with tempfile.TemporaryDirectory(prefix='main-forward-actual-webctl-') as temp:
 t=Path(temp);hosting=t/'hosting';hosting.mkdir();etc=t/'etc';etc.mkdir();state=t/'state';state.mkdir(mode=0o700);floor=state/'opfs-floor.json';floor.write_text(json.dumps({'version':1,'baseline':'0'*64,'candidate':data['codi_beta_opfs']}));floor.chmod(0o600)
 caddy=etc/'Caddyfile';caddy.write_text(common.caddy(data,'production'));caddy.chmod(0o600);manifest=hosting/'sites.toml';manifest.write_text(common.dump(data))
 ctl.BETA_FILES_FLOOR=floor;ctl.ACTIVE_CADDY=caddy;ctl.BETA_V2_BLOCK_SHA=hashlib.sha256(ctl._beta_block(caddy.read_text()).encode()).hexdigest();ctl.ROOT=hosting;ctl.MANIFEST=manifest;ctl.BACKUPS=t/'backups';ctl.BACKUPS.mkdir(mode=0o700)
 realPath=Path
 def mapPath(value):
  value=str(value)
  if value=='/etc/caddy/Caddyfile':return caddy
  if value.startswith('/etc/caddy/'):return etc/value.removeprefix('/etc/caddy/')
  if value=='/var/log/caddy':return t/'logs'
  return realPath(value)
 ctl.Path=mapPath
 class OSProxy:
  def __getattr__(self,k):return getattr(os,k)
  def chown(self,path,uid,gid):assert realPath(path).is_relative_to(t)
 ctl.os=OSProxy();ctl.owner=lambda:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid());ctl.pwd=types.SimpleNamespace(getpwnam=lambda _:types.SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()));ctl.caddy_validate=lambda _:None;ctl.subprocess=types.SimpleNamespace(run=lambda *a,**k:types.SimpleNamespace(returncode=0));calls=[]
 def run(args,**kwargs):
  calls.append([str(x) for x in args]);raise RuntimeError('simulated reload failure')
 ctl.run=run
 class Inner:
  def __init__(self):self.ctl=ctl;self.paths={'manifest':manifest,'caddy':caddy,'common':OPS/'common.py'}
  def check_lock(self):pass
  def read(self):return {k:Path(v).read_bytes() for k,v in self.paths.items()}
  def apply_caddy(self,manifest_bytes,common_bytes,recovery=False):ctl.caddy_apply(tomllib.loads(manifest_bytes.decode()),'production')
 inner=Inner();adapter=main.ForwardAdapter(inner,lambda:None,lambda:None)
 try:adapter.apply_caddy(common.dump(target).encode(),(OPS/'common.py').read_bytes())
 except RuntimeError as e:assert 'Refused Caddy rollback' in str(e),str(e)
 else:raise AssertionError('rollback not refused')
 assert caddy.read_text()==common.caddy(target,'production');assert len(calls)==1 and calls[0]==['systemctl','reload','caddy'];assert floor.exists();print('PASS pinned actual webctl floor checks and rollback interception; simulated reload and redirected fixture')
