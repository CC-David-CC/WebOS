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
OLD_SOURCE='2d04ab00dc0e17003f94155b4f812b640ed2f9ed897e4f3685b8cb2bbbda41cb'
NEW_SOURCE='29305c1d0d5387886816d156986dc53ad82e1e6b287ad6c7ea8b4b2559a8d7c2'
MANIFEST='1eff3c244aa5e528f0fe91962e835b2e551c77846a44a410d1066d6c606a7137'
OLD_CADDY='a34f149de23c2c88c61c3999035fb23fef758aca4ae6c33dface3ed75e3ece01'
NEW_CADDY='5a1052be870c92e98696464174e12f8b5faed66b8dfa535dd22e544a1b5a150f'
ARCHIVE='codi-browser-source-f4a43b30e.tar.zst'
ARCHIVE_SHA='3e090e5a9508f0ff53aae97791ff21c71dc38afb5d84bc9cc2cc54f304aeb42c'


def sha(value):return hashlib.sha256(value).hexdigest()


def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply, or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed hosting operator changed')
    spec=importlib.util.spec_from_file_location('codi_source_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.JOURNAL=op.STATE/'browser-source-update-f4a-journal.json';op.RECEIPT=op.STATE/'browser-source-update-f4a-result.json'
    op.PINS.update(oldSource=OLD_SOURCE,newSource=NEW_SOURCE,oldManifest=MANIFEST,newManifest=MANIFEST,oldCaddy=OLD_CADDY,newCaddy=NEW_CADDY,notices='58e6cddb46de45842fa96aaf0ef4c0da6eb1d4e0cf39faaac3a3dd290feeb4a5')
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    source=sys.stdin.buffer.read(1048577);old=op.SOURCE.read_bytes();archive=op.FILES/ARCHIVE
    if sha(old)!=OLD_SOURCE or sha(source)!=NEW_SOURCE:raise ValueError('Hosting source changed')
    previous=b'/codi-browser-source-29a71d717.tar.zst';new=b'/'+ARCHIVE.encode()
    if old.count(previous)!=1 or new in old or source!=old.replace(previous,previous+b' '+new,1):raise ValueError('Candidate changes more than the archive allowlist')
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_uid!=0 or archive.stat().st_mode&0o022 or op.filehash(archive)!=ARCHIVE_SHA:raise ValueError('New archive missing or changed')
    with tempfile.TemporaryDirectory(prefix='codi-browser-source-update-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(source);(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
