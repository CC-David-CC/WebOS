import copy,os,sys,tomllib
from pathlib import Path
ops=Path(os.environ['CODI_FILES_FIXTURE_BUNDLE'])/'ops';sys.path.insert(0,str(ops))
import common_live as common,render_inventory,beta_service_operator as svc,beta_issuer_switch as issuer
root=Path('/home/dflanag3/webhost-sites');root.mkdir(parents=True,exist_ok=True);(root/'ops').mkdir(exist_ok=True);os.chown(root,1000,1000);os.chown(root/'ops',1000,1000)
source=(ops/'common_live.py').read_bytes();(root/'ops/common.py').write_bytes(source);os.chown(root/'ops/common.py',1000,1000);os.chmod(root/'ops/common.py',0o644)
manifest=(ops/'sites_live.toml').read_bytes();(root/'sites.toml').write_bytes(manifest);os.chown(root/'sites.toml',1000,1000);os.chmod(root/'sites.toml',0o644)
data=tomllib.loads(manifest.decode());normal=copy.deepcopy(data);normal['codi_beta_maintenance']=False
inv=render_inventory.RenderInventory(root,'/etc/caddy',common,common,data,normal,owner_uid=1000,owner_gid=1000,caddy_uid=0,caddy_gid=1001,normalize_maintenance=True)
for path,(before,after,meta) in inv.targets.items():
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(before);os.chown(path,meta[0],meta[1]);os.chmod(path,meta[2])
 for p in path.parents:
  if p==root:break
  if p.is_relative_to(root):os.chown(p,1000,1000)
active=Path('/etc/caddy/Caddyfile');active.write_text(common.caddy(data,'production'));os.chown(active,0,1001);os.chmod(active,0o640)
plan={'origin':svc.ORIGIN,'ports':svc.PORTS,'network':'disabled','native_release':'/srv/codi-connected/releases/microduck-issuer-'+issuer.OLD,'native_manifest':issuer.OLD,'worker_release':'/srv/codi-gateway/releases/'+svc.GATEWAY_MANIFEST,'worker_manifest':svc.GATEWAY_MANIFEST,'python':'/srv/codi-connected/venvs/517179c/bin/python','issuer_policy_sha256':'71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca','guest_source_sha256':svc.GUEST_SOURCE}
for name,value in svc.render_units(plan).items():
 p=Path('/etc/systemd/system')/name;p.write_text(value);p.chmod(0o644)
print('fixture generated hosting and pinned unit baseline')
