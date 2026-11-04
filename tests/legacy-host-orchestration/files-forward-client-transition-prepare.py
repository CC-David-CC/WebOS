#!/usr/bin/env python3
"""Create disposable public-only trees from already pinned closed artifacts."""
import argparse, hashlib, importlib.util, json, pathlib, shutil
p=argparse.ArgumentParser();p.add_argument('--parent',type=pathlib.Path,required=True);p.add_argument('--candidate',type=pathlib.Path,required=True);p.add_argument('--public-base',type=pathlib.Path,required=True);p.add_argument('--gateway',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
spec=importlib.util.spec_from_file_location('builder',pathlib.Path(__file__).resolve().parents[1]/'research/beta-files-forward/build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.sealed(a.parent,b.PARENT,'codi-beta-opfs-candidate/1');b.sealed(a.candidate,'830ca4f174a37cd499a05e07c373a0412fd94c3e6f232234a87645662170a1f0',b.FORMAT)
cache=json.loads((a.parent/'assets/desktop/cache-manifest.json').read_bytes())['files'];base=a.public_base.resolve(strict=True)
for f in base.rglob('*'):
 if f.is_symlink():raise ValueError('Public base symlink')
 if f.is_file():
  rel=f.relative_to(base).as_posix();rec=cache.get(rel);data=f.read_bytes()
  if not rec or len(data)!=rec['bytes'] or hashlib.sha256(data).hexdigest()!=rec['sha256']:raise ValueError('Unverified base '+rel)
if a.output.exists() or a.output.is_symlink():raise ValueError('Fresh output required')
sdk=(a.gateway/'gateway_service/client.mjs').read_bytes()
if hashlib.sha256(sdk).hexdigest()!='44da83bdccf43a2b36ae4b3f48eaf94fc1006b88180456e26faba61aae344869':raise ValueError('SDK mismatch')
a.output.mkdir()
for label,overlay in (('old',a.parent),('new',a.candidate)):
 target=a.output/label;shutil.copytree(base,target)
 for section in ('assets','storage'):shutil.copytree(overlay/section,target/section,dirs_exist_ok=True)
 for source,dest in (('shell/app.js','app.js'),('shell/desktop-apps.js','desktop-apps.js')):shutil.copyfile(overlay/source,target/dest)
 (target/'gateway').mkdir(exist_ok=True);(target/'gateway/client.mjs').write_bytes(sdk)
print('PASS verified public baseline, closed 3ad and 830 inputs')
