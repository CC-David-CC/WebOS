#!/usr/bin/env python3
"""Export an allowlisted development release, without state, venv or test tools.

Backend sources are included for native execution, never as a public web root.
The launcher stages a separate public tree in its private external runtime.
"""
import argparse,hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from origin_service.release import PUBLIC,NETWORK,RUNTIME,V1_NATIVE,V2_NATIVE,V3_NATIVE,V4_NATIVE,NATIVE,V15_NATIVE,record,public_name,verify

def export(destination,glibc_notice=None,*,official_candidate=False):
 destination=Path(destination).absolute()
 if destination.exists() or destination.is_symlink():raise ValueError('Destination already exists; choose a new release directory')
 if destination.is_relative_to(ROOT/'assets') or destination.is_relative_to(ROOT/'.build/v86'):raise ValueError('Release output must not be a public source input')
 destination.parent.mkdir(parents=True,exist_ok=True)
 temporary=Path(tempfile.mkdtemp(prefix='.connected-export-',dir=destination.parent))
 try:
  spec=importlib.util.spec_from_file_location('public_export',ROOT/'scripts/export-desktop.py');public_export=importlib.util.module_from_spec(spec);spec.loader.exec_module(public_export)
  release=temporary/'release';public_export.export(release,glibc_notice)
  for name in sorted(V15_NATIVE if official_candidate else NATIVE):
   source=ROOT/name
   if not source.is_file() or source.is_symlink() or any(p.is_symlink() for p in source.parents if p.is_relative_to(ROOT)):raise ValueError('Missing or linked native input: '+name)
   target=release/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);target.chmod(0o644)
  files={str(p.relative_to(release)):record(p) for p in sorted(release.rglob('*')) if p.is_file()}
  (release/'connected-release.json').write_text(json.dumps({'version':'codi-connected-development/'+('15' if official_candidate else '14'),'authorityClass':'development','mount':'configurable','guestEgress':'relay-host','files':files},indent=2)+'\n')
  for path in release.rglob('*'):
   path.chmod(0o755 if path.is_dir() else 0o644)
  verify(release);release.rename(destination)
 finally:shutil.rmtree(temporary)
 return verify(destination)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--output',type=Path);action.add_argument('--verify',type=Path);parser.add_argument('--glibc-notice',type=Path);parser.add_argument('--official-candidate',action='store_true');args=parser.parse_args()
 try:print(json.dumps(verify(args.verify) if args.verify else export(args.output,args.glibc_notice,official_candidate=args.official_candidate),indent=2))
 except (ValueError,OSError) as error:parser.error(str(error))
