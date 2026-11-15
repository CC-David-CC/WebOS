#!/usr/bin/env python3
"""Create a pinned live-derived issuer with a 128 MiB advertised file limit."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

BASE='957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d'
CHANGES={
 'scripts/serve-connected.py':"if a.user_files:config['gateway']={'version':'codi-user-files/1','basePath':a.base_path+'/gateway','fileBytes':8*1024*1024}",
 'origin_service/files_management.py':"expected={'version':'codi-user-files/1','basePath':config['basePath']+'/gateway','fileBytes':8*1024*1024}",
}
HEALTH_REPLACEMENT='''issuer_source=(Path(config['release'])/'scripts/serve-connected.py').read_text()
    old_limit="if a.user_files:config['gateway']={'version':'codi-user-files/1','basePath':a.base_path+'/gateway','fileBytes':8*1024*1024}"
    new_limit=old_limit.replace('8*1024*1024','128*1024*1024')
    if issuer_source.count(old_limit)+issuer_source.count(new_limit)!=1:raise ValueError('Unexpected issuer file limit')
    limit=128*1024*1024 if new_limit in issuer_source else 8*1024*1024
    expected={'version':'codi-user-files/1','basePath':config['basePath']+'/gateway','fileBytes':limit}'''


def verifier(root):
    spec=importlib.util.spec_from_file_location('codi_issuer_release',root/'origin_service/release.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    base=a.base.resolve();out=a.output.absolute()
    if out.exists() or out.is_symlink() or not out.parent.is_dir() or base in out.parents or out in base.parents:raise ValueError('Choose a new, disjoint output')
    if verifier(base).verify(base)['manifestSHA256']!=BASE:raise ValueError('Issuer baseline is not the exact live release')
    texts={name:(base/name).read_text() for name in CHANGES}
    if any(texts[name].count(old)!=1 for name,old in CHANGES.items()):raise ValueError('Unexpected file limit source')
    shutil.copytree(base,out)
    manifest_path=out/'connected-release.json';manifest=json.loads(manifest_path.read_text())
    for name,old in CHANGES.items():
        replacement=HEALTH_REPLACEMENT if name=='origin_service/files_management.py' else old.replace('8*1024*1024','128*1024*1024')
        path=out/name;path.write_text(texts[name].replace(old,replacement,1));raw=path.read_bytes()
        manifest['files'][name]={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(verifier(out).verify(out),indent=2))


if __name__=='__main__':sys.dont_write_bytecode=True;main()
