#!/usr/bin/env python3
"""Stage, but do not activate, a pinned issuer release on box-webhost.

Input is a JSON map of three base64-encoded candidate files. The exact verified
live release supplies every other file; account and runtime state are separate.
"""
import base64
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile

BASE=Path('/srv/codi-connected/releases/browser-issuer-profile28-r3')
DEST=BASE.parent/'browser-issuer-profile28-large-r3'
OLD='957e6fec98101f5a57c7f8ebab633050d27759d5c0d673049b4da3527d39715d'
NEW='0aaf61849fa03e41376d63a36496c83e83adbc97c14aeafe366100ff9e530af2'
PINS={'connected-release.json':NEW,
      'scripts/serve-connected.py':'1fd62a6b87d7c85a39af1a61524fe4e523f664aa6dfcd0080a0484f25ba65650',
      'origin_service/files_management.py':'cfcb14bb66c39fe4976426c87fb6b107e0699e25d86b9a4cd0d0fa2ce6d34750'}
def digest(data):return hashlib.sha256(data).hexdigest()
def verifier(root):
    spec=importlib.util.spec_from_file_location('codi_live_release_verifier',root/'origin_service/release.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if DEST.exists() or DEST.is_symlink():raise ValueError('Destination exists; do not overwrite a release')
    if BASE.is_symlink() or BASE.stat().st_uid!=0 or BASE.stat().st_mode&0o022:raise ValueError('Unsafe baseline')
    if verifier(BASE).verify(BASE)['manifestSHA256']!=OLD:raise ValueError('Baseline release changed')
    payload=json.load(sys.stdin)
    if set(payload)!=set(PINS):raise ValueError('Unexpected candidate files')
    files={name:base64.b64decode(raw,validate=True) for name,raw in payload.items()}
    if any(digest(files[name])!=pin for name,pin in PINS.items()):raise ValueError('Candidate inputs changed')
    manifest=json.loads(files['connected-release.json']);old=json.loads((BASE/'connected-release.json').read_text())
    for name in PINS:
        if name!='connected-release.json':old['files'][name]=manifest['files'][name]
    if old!=manifest:raise ValueError('Candidate changes more than the reviewed files')
    stage=Path(tempfile.mkdtemp(prefix='.issuer-large-r3-',dir=BASE.parent))
    try:
        shutil.copytree(BASE,stage,dirs_exist_ok=True,symlinks=True)
        for name,raw in files.items():
            path=stage/name
            if path.is_symlink() or not path.is_file():raise ValueError('Unsafe candidate path')
            path.write_bytes(raw);os.chmod(path,0o644)
        if verifier(stage).verify(stage)['manifestSHA256']!=NEW:raise ValueError('Candidate failed release verification')
        for path in [stage,*stage.rglob('*')]:
            if path.lstat().st_uid!=0 or path.lstat().st_mode&0o022:raise ValueError('Candidate is not root-owned and immutable')
        os.chmod(stage,0o755);os.rename(stage,DEST)
    except BaseException:
        shutil.rmtree(stage);raise
    print(json.dumps({'status':'staged','release':str(DEST),'manifestSHA256':NEW}))


if __name__=='__main__':main()
