#!/usr/bin/env python3
"""Export only the reviewed desktop assets and matching independent-shell guest; never service state."""
import argparse,hashlib,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
FILES=('app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz','desktop-apps.js','networking.js')
def export(target,compat_r15=False):
 target=Path(target).absolute()
 if target.exists() or target.is_symlink():raise ValueError('Choose a new frontend export directory')
 target.parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix='.frontend-',dir=target.parent))
 try:
  records={}
  if compat_r15:
   old=ROOT/'.build/frontends/private-files-r15';native=ROOT/'.build/releases/connected-files-r2'
   if hashlib.sha256((old/'frontend.json').read_bytes()).hexdigest()!='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787' or hashlib.sha256((native/'connected-release.json').read_bytes()).hexdigest()!='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0':raise ValueError('Exact live R15/native11 inputs required')
   old_records=json.loads((old/'frontend.json').read_text())['files'];native_records=json.loads((native/'connected-release.json').read_text())['files']
  for name in FILES:
   source=(native if name in ('desktop-apps.js','networking.js') else old)/name if compat_r15 else ROOT/name
   if source.is_symlink() or not source.is_file():raise ValueError('Regular public frontend source required')
   raw=source.read_bytes();(stage/name).parent.mkdir(parents=True,exist_ok=True);(stage/name).write_bytes(raw);(stage/name).chmod(0o644);records[name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
   if compat_r15 and records[name]!=(native_records if name in ('desktop-apps.js','networking.js') else old_records)[name]:raise ValueError('Compatibility input changed')
  raw=(json.dumps({'version':'codi-frontend-assets/3','files':records},indent=2)+'\n').encode();(stage/'frontend.json').write_bytes(raw);(stage/'frontend.json').chmod(0o644);stage.chmod(0o755);stage.rename(target)
  return {'directory':str(target),'manifestSHA256':hashlib.sha256(raw).hexdigest(),'files':records}
 finally:
  if stage.exists():shutil.rmtree(stage)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--compat-r15',action='store_true',help='Freeze the six currently live R15/native11 files before the modular native upgrade');a=p.parse_args();print(json.dumps(export(a.output,a.compat_r15),indent=2))
