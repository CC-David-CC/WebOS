#!/usr/bin/env python3
"""Create a public-only static release from a baseline and reviewed app bundles.

This stages files only; activation remains the hosting controller's job. Run on
the webhost where both the baseline release and uploaded app batch are local.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--batch',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--apps',nargs='+',required=True)
p.add_argument('--new-apps',nargs='*',default=[],help='Explicitly approved new app IDs in this batch')
p.add_argument('--desktop-app',type=Path,help='Reviewed desktop app.js to include with the batch')
p.add_argument('--desktop-base-sha256',help='Expected SHA-256 of the baseline app.js when replacing it')
p.add_argument('--desktop-apps',type=Path,help='Reviewed desktop-apps.js to include with the batch')
p.add_argument('--desktop-apps-base-sha256',help='Expected SHA-256 of the baseline desktop-apps.js when replacing it')
p.add_argument('--mirror',type=Path,help='Reviewed browser mirror module to include')
p.add_argument('--mirror-base-sha256',help='Expected SHA-256 of the baseline browser mirror module')
a=p.parse_args();base=a.baseline;batch=a.batch;out=a.output;expected=set(a.apps)
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  while chunk:=stream.read(1024*1024):h.update(chunk)
 return h.hexdigest()
if len(expected)!=len(a.apps) or any(not re.fullmatch(r'[a-z][a-z0-9-]{0,31}',x) for x in expected):raise ValueError('Invalid app selection')
if out.exists() or out.is_symlink():raise ValueError('Choose a new staging directory')
if bool(a.desktop_app)!=bool(a.desktop_base_sha256):raise ValueError('Supply both desktop app and its baseline hash')
if a.desktop_app and (not re.fullmatch('[0-9a-f]{64}',a.desktop_base_sha256) or a.desktop_app.is_symlink() or not a.desktop_app.is_file() or a.desktop_app.stat().st_size>4*1024*1024 or digest(base/'app.js')!=a.desktop_base_sha256):raise ValueError('Desktop app or baseline hash mismatch')
if bool(a.desktop_apps)!=bool(a.desktop_apps_base_sha256):raise ValueError('Supply both desktop-apps and its baseline hash')
if a.desktop_apps and (not re.fullmatch('[0-9a-f]{64}',a.desktop_apps_base_sha256) or a.desktop_apps.is_symlink() or not a.desktop_apps.is_file() or a.desktop_apps.stat().st_size>4*1024*1024 or digest(base/'desktop-apps.js')!=a.desktop_apps_base_sha256):raise ValueError('Desktop apps or baseline hash mismatch')
if bool(a.mirror)!=bool(a.mirror_base_sha256):raise ValueError('Supply both mirror module and its baseline hash')
if a.mirror and (not re.fullmatch('[0-9a-f]{64}',a.mirror_base_sha256) or a.mirror.is_symlink() or not a.mirror.is_file() or a.mirror.stat().st_size>4*1024*1024 or digest(base/'storage/browser/mirror.mjs')!=a.mirror_base_sha256):raise ValueError('Mirror module or baseline hash mismatch')
old=json.loads((base/'assets/desktop/cache-manifest.json').read_text())
if not re.fullmatch('[0-9a-f]{64}',base.name) or old['id']!=base.name:raise ValueError('Baseline release does not match its manifest')
catalog=json.loads((base/'assets/desktop/apps.json').read_text());incoming=json.loads((batch/'apps.json').read_text());records={r['id']:r for r in incoming['apps']};existing={r['id'] for r in catalog['apps']};new=set(a.new_apps)
if len(records)!=len(incoming['apps']) or len(existing)!=len(catalog['apps']) or len(new)!=len(a.new_apps) or set(records)!=expected or expected-existing!=new or not new.issubset(expected):raise ValueError('Unexpected app catalog')
for app,record in records.items():
 sha=record['bundleSHA256']
 if not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('Invalid bundle hash')
 root=batch/'apps'/app/sha
 if not root.is_dir() or root.is_symlink():raise ValueError('Missing bundle')
 if any(path.is_symlink() for path in root.rglob('*')):raise ValueError('Symlink in bundle')
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
 if actual!=set(record['files']):raise ValueError('Bundle file list differs')
 for name,info in record['files'].items():
  path=root/name
  if path.is_symlink() or path.stat().st_size!=info['bytes'] or digest(path)!=info['sha256']:raise ValueError('Bundle file mismatch: '+name)
if base.is_symlink() or any(path.is_symlink() for path in base.rglob('*')):raise ValueError('Symlink in baseline')
shutil.copytree(base,out,symlinks=False);appdir=out/'assets/desktop/apps'
if a.desktop_app:shutil.copyfile(a.desktop_app,out/'app.js')
if a.desktop_apps:shutil.copyfile(a.desktop_apps,out/'desktop-apps.js')
if a.mirror:shutil.copyfile(a.mirror,out/'storage/browser/mirror.mjs')
for app,record in records.items():
 if app in existing:shutil.rmtree(appdir/app)
 elif (appdir/app).exists() or (appdir/app).is_symlink():raise ValueError('Unexpected directory for new app')
 (appdir/app).mkdir();shutil.copytree(batch/'apps'/app/record['bundleSHA256'],appdir/app/record['bundleSHA256'])
catalog['apps']=[records.get(r['id'],r) for r in catalog['apps']]+[records[app] for app in a.apps if app in new]
(out/'assets/desktop/apps.json').write_text(json.dumps(catalog,separators=(',',':')))
files={}
for path in sorted(out.rglob('*')):
 if path.is_symlink():raise ValueError('Unexpected symlink in output')
 if not path.is_file():continue
 name=path.relative_to(out).as_posix()
 if name in ('assets/desktop/offline-worker.js','assets/desktop/cache-manifest.json'):continue
 files[name]={'bytes':path.stat().st_size,'sha256':digest(path)}
manifest={'version':'codi-public-cache/1','id':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'files':files}
(out/'assets/desktop/cache-manifest.json').write_text(json.dumps(manifest,separators=(',',':')))
worker=out/'assets/desktop/offline-worker.js';lines=worker.read_text().splitlines(keepends=True)
if not lines[1].startswith('const RELEASE=') or old['id'] not in lines[1]:raise ValueError('Unexpected cache worker')
lines[1]='const RELEASE='+json.dumps(manifest,separators=(',',':'))+';\n';worker.write_text(''.join(lines))
# The builder's temporary bundle directories can be private. Normalize the
# staging copy before activation so Caddy can traverse every app asset.
out.chmod(0o755)
for path in out.rglob('*'):path.chmod(0o755 if path.is_dir() else 0o644)
print(json.dumps({'release':manifest['id'],'apps':{k:r['bundleSHA256'] for k,r in records.items()},'files':len(files)}))
