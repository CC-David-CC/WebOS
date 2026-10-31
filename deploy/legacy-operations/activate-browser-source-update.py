#!/usr/bin/env python3
"""Enable one exact additional Browser source archive on box-webhost.

Use the installed, pinned hosting operator for locking and rollback. The
candidate generator is read from standard input, and must be the exact
one-path addition to the active generator. The archive must already be staged
as a protected root-owned file; the existing notice page remains valid.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import socket
import sys
import tempfile

OPERATOR=Path('/srv/codi-browser/operators/sources-37218ff39/activate-browser-sources.py')
OPERATOR_SHA='d32d6513c1e3b3d5627dca4cf13235c772b41a1067cff827947e6f0a10bdab99'
OLD_SOURCE='19b71614139100907f21c6b28383532a163c06aa8b951e5d540e5d241e4c37f6'
NEW_SOURCE='2329d2b8925501ea5b59c9a0182b24db66e076b6abc1d4305ad820da45a4079b'
MANIFEST='a287d968a80cb8387295a4a5fb6a23cb039efc6e127aaebb7e7cb7d699481260'
OLD_CADDY='40df5f82ebbbf37ccc30d498a43a1a9f2480b120aad61d0f54b93b1affeef789'
NEW_CADDY='887fdcb7da1b2ba05c6d3204fa0c4cf38a8a8d4d4a9743cc3e269116283209c7'
ARCHIVE='codi-browser-source-802621ec2.tar.zst'
ARCHIVE_SHA='128c33ee16a6dde95f5c594b19ef6c8a05cb9b251024e95ac859f888b3a26c90'


def sha(value):return hashlib.sha256(value).hexdigest()


def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply, or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed hosting operator changed')
    spec=importlib.util.spec_from_file_location('codi_source_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.JOURNAL=op.STATE/'browser-source-update-802-journal.json';op.RECEIPT=op.STATE/'browser-source-update-802-result.json'
    op.PINS.update(oldSource=OLD_SOURCE,newSource=NEW_SOURCE,oldManifest=MANIFEST,newManifest=MANIFEST,oldCaddy=OLD_CADDY,newCaddy=NEW_CADDY,notices='201c2497704af5db821fa9e671e17ab4d73f3a78e0ecc538689169bf5cb1f43e')
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    source=sys.stdin.buffer.read(1048577);old=op.SOURCE.read_bytes();archive=op.FILES/ARCHIVE
    if sha(old)!=OLD_SOURCE or sha(source)!=NEW_SOURCE:raise ValueError('Hosting source changed')
    previous=b'/codi-browser-source-0488c275e.tar.zst';new=b'/'+ARCHIVE.encode()
    if old.count(previous)!=1 or new in old or source!=old.replace(previous,previous+b' '+new,1):raise ValueError('Candidate changes more than the archive allowlist')
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_uid!=0 or archive.stat().st_mode&0o022 or op.filehash(archive)!=ARCHIVE_SHA:raise ValueError('New archive missing or changed')
    with tempfile.TemporaryDirectory(prefix='codi-browser-source-update-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(source);(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
