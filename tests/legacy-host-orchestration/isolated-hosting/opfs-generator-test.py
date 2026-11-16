#!/usr/bin/env python3
"""Exact beta-only static route candidate; no live host."""
import copy,importlib.util,sys,tempfile,tomllib,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
import common
p=root/'ops/common_live.py';spec=importlib.util.spec_from_file_location('baseline_generator',p);baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
old=tomllib.loads((root/'ops/sites_live.toml').read_text());new=copy.deepcopy(old);new['codi_beta_opfs']='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';common.validate(new);assert tomllib.loads(common.dump(new))==new
assert common.caddy(old,'production')==baseline.caddy(old,'production')
def without_beta(s):
 a=s.index('beta.ksu.codes {');b=s.index('\n}\n',a)+3;return s[:a]+s[b:]
r=common.caddy(new,'production');assert without_beta(r)==without_beta(common.caddy(old,'production'))
assert r.count('path /desktop-apps.js')>=1 and r.count('\n\t@beta_opfs_desktop {')==1 and '@beta_overlay_loader {' not in r
for q in ('/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/*','/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/*','mirror.cbfafe53eae1afdac1f2a9af0bfdbd26cae59b1be8f5d96f6bebec2a56c158ed.mjs'):assert q in r,q
for bad in ('a'*64,True,'../x'):
 x=copy.deepcopy(new);x['codi_beta_opfs']=bad
 try:common.validate(x);raise AssertionError('bad candidate accepted')
 except ValueError:pass
try:common.validate_beta_overlay_transition(new,old);raise AssertionError('v2 route removal accepted')
except ValueError:pass
gated=copy.deepcopy(new);gated['codi_beta_maintenance']=True;assert '@beta_opfs_desktop' not in common.caddy(gated,'production')
with tempfile.TemporaryDirectory(prefix='opfs-gen-check-') as temp:
 logs=Path(temp)/'logs';logs.mkdir();f=Path(temp)/'Caddyfile';f.write_text(r.replace('/var/log/caddy/',str(logs)+'/').replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS'));subprocess.run(['/tmp/codi-microduck-hosting-evidence/caddy','validate','--config',str(f),'--adapter','caddyfile'],check=True,capture_output=True)
print('PASS exact OPFS route candidate, retained v1 URLs, beta gate and unchanged non-beta generation')
