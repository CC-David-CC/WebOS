#!/usr/bin/env python3
"""Build an explicit public-only static desktop artifact; never overwrite a release."""
import argparse,hashlib,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from serve import PUBLIC,NETWORK,RUNTIME

def export(destination,glibc_notice=None):
 destination=Path(destination).absolute()
 if destination.exists() or destination.is_symlink():raise ValueError('Destination already exists; choose a new release directory')
 config=json.loads((ROOT/'config.json').read_text())
 if config.get('identity',{}).get('mode')!='local-development' or set(config)-{'protocol','identity','rtc','vm'}:raise ValueError('Static export requires explicit local-development configuration without service overrides')
 manifest={}
 for line in (ROOT/'.build/v86/MANIFEST.sha256').read_text().splitlines():
  digest,name=line.split();manifest[name]=digest
 if set(manifest)!=RUNTIME:raise ValueError('Runtime manifest does not match public runtime allowlist')
 for name,digest in manifest.items():
  if hashlib.sha256((ROOT/'.build/v86'/name).read_bytes()).hexdigest()!=digest:raise ValueError('Runtime hash mismatch: '+name)
 files={name:ROOT/name for name in PUBLIC}
 files.update({'network/'+name:ROOT/'network'/name for name in NETWORK})
 files.update({'.build/v86/'+name:ROOT/'.build/v86'/name for name in RUNTIME})
 for path in (ROOT/'assets').rglob('*'):
  if path.is_symlink():raise ValueError('Symlink in public assets')
  if path.is_dir():continue
  if not path.is_file() or any(p.startswith('.') for p in path.relative_to(ROOT/'assets').parts) or path.suffix.lower() in ('.pem','.key','.sqlite','.sqlite3','.db','.py','.env'):raise ValueError('Unexpected private/nonpublic asset')
  files[str(path.relative_to(ROOT))]=path
 for name in ('LICENSE-v86','LICENSE-bios','LICENSE-linux','LICENSE-busybox'):
  files['licenses/runtime/'+name]=ROOT/'.build/v86'/name
 files['licenses/runtime/LICENSE-glibc']=Path(glibc_notice) if glibc_notice is not None else ROOT.parents[1]/'downloads/desktop-v86-source/debian-root/usr/share/doc/libc6/copyright'
 for source in files.values():
  if not source.is_file() or source.is_symlink():raise ValueError('Missing or linked public input: '+source.name)
 destination.parent.mkdir(parents=True,exist_ok=True)
 temporary=Path(tempfile.mkdtemp(prefix='.desktop-export-',dir=destination.parent))
 try:
  records={}
  for name,source in sorted(files.items()):
   target=temporary/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);target.chmod(0o644)
   digest=hashlib.sha256(target.read_bytes()).hexdigest()
   if name.startswith('.build/v86/') and digest!=manifest[target.name]:raise ValueError('Runtime changed during export: '+target.name)
   records[name]={'bytes':target.stat().st_size,'sha256':digest}
  (temporary/'release.json').write_text(json.dumps({'version':'codi-static-desktop/1','identity':'Local / not server validated','guestNetwork':'loopback only','files':records},indent=2)+'\n')
  temporary.chmod(0o755);temporary.rename(destination)
 except BaseException:
  # Only our new private staging directory is disposable; never delete an existing release.
  shutil.rmtree(temporary);raise
 return {'directory':str(destination),'files':len(records),'bytes':sum(r['bytes'] for r in records.values()),'manifestSHA256':hashlib.sha256((destination/'release.json').read_bytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default=str(ROOT/'.build/releases/desktop-static'));p.add_argument('--glibc-notice',type=Path,help='Explicit guest glibc copyright input when building outside the original workspace');a=p.parse_args();print(json.dumps(export(a.output,a.glibc_notice),indent=2))
