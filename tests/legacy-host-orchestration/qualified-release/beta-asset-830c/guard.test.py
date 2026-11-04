#!/usr/bin/env python3
"""Exact derived guard/floor controls with isolated filesystem only."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile,tomllib
from pathlib import Path
here=Path(__file__).resolve().parent;ops=here.parents[1]/'beta-isolated-hosting/ops';sys.path.insert(0,str(ops))
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
with tempfile.TemporaryDirectory(prefix='830c-guard-') as d:
 t=Path(d);subprocess.run([sys.executable,'-B',str(here/'build-generator.py'),'--old',sys.argv[1],'--new',sys.argv[2],'--out',str(t/'generator')],check=True,capture_output=True);subprocess.run([sys.executable,'-B',str(here/'build-guard.py'),str(t/'guard')],check=True,capture_output=True)
 gen=load('common',t/'generator/common.py');load('scaffold',ops/'scaffold_live.py');guard=load('asset_guard',t/'guard/webctl.py')
 old='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';new='830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0';data=tomllib.loads((ops/'sites_live.toml').read_text());data['codi_beta_maintenance']=False;data['codi_beta_opfs']=old
 guard.ASSET_FLOOR=t/'files-asset-floor.json';guard.ASSET_JOURNAL=t/'files-asset-transition.json';guard.ACTIVE_CADDY=t/'Caddyfile';guard._floor_guard_active=True;guard.ACTIVE_CADDY.write_text(gen.caddy(data,'production'));guard.ACTIVE_CADDY.chmod(0o644);guard._assert_v2_beta(data)
 rec={'version':1,'baseline':old,'candidate':new};guard.ASSET_FLOOR.write_text(json.dumps(rec));guard.ASSET_FLOOR.chmod(0o600)
 try:guard._assert_v2_beta(data);raise AssertionError('post-floor old route accepted')
 except ValueError:pass
 data['codi_beta_opfs']=new;guard.ACTIVE_CADDY.write_text(gen.caddy(data,'production'));guard._assert_v2_beta(data)
 guard.ASSET_FLOOR.write_text(json.dumps({**rec,'version':True}))
 try:guard._assert_v2_beta(data);raise AssertionError('boolean floor version accepted')
 except ValueError:pass
 guard.ASSET_FLOOR.write_text(json.dumps(rec));guard._floor_guard_active=False
 try:guard._assert_v2_beta(data);raise AssertionError('missing original floor accepted')
 except ValueError:pass
 guard._floor_guard_active=True;guard.ASSET_FLOOR.unlink();guard.ASSET_FLOOR.symlink_to(t/'missing')
 try:guard._assert_v2_beta(data);raise AssertionError('floor symlink accepted')
 except OSError:pass
 guard.ASSET_FLOOR.unlink();guard.ROOT=t;guard.BETA_FILES_JOURNAL=t/'beta-journal';guard.MAIN_RESTRICTION_JOURNAL=t/'main-journal';guard.BETA_FILES_FLOOR=t/'old-floor';guard.root_required=lambda:None;guard.load=lambda:(_ for _ in ()).throw(AssertionError('loaded before fence'));(t/'.controller.lock').touch();guard.ASSET_JOURNAL.touch();sys.argv=['webctl.py','render']
 try:guard.main();raise AssertionError('pending asset journal accepted')
 except RuntimeError as e:assert 'pending beta asset transition' in str(e)
print('PASS 3ad/830c exact guard, asset-floor custody, old-route and pending-journal refusal; no live host')
