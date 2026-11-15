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
OLD_SOURCE='8423607ec727d587a2140ca9e0157c982f1b38837496ffa48bdfb6c314444a45'
NEW_SOURCE='22e8ceb89f38aecb62f153311e31be13bc62f07bebdf4d0d420e5add661b8cfd'
MANIFEST='793c2f272ed5e1c4a3cdc237cc0b82b60b6e25ede6103a29a7678da3bcffe878'
OLD_CADDY='c3de6b467defabc6530ce349023ceba4fd1194d5aee02840d5bc2f6139d38d1d'
NEW_CADDY='74da11995d0c730ff55af31a7109b42323911149e34a27a43cf5cbe040a51a2b'
ARCHIVE='codi-browser-source-9fe78a273.tar.zst'
ARCHIVE_SHA='eb1405b13bc172920170259ee87e59594b977ea2498fa3daa08ec705b2fa627f'


def sha(value):return hashlib.sha256(value).hexdigest()


def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply, or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed hosting operator changed')
    spec=importlib.util.spec_from_file_location('codi_source_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.JOURNAL=op.STATE/'browser-source-update-9fe-journal.json';op.RECEIPT=op.STATE/'browser-source-update-9fe-result.json'
    op.PINS.update(oldSource=OLD_SOURCE,newSource=NEW_SOURCE,oldManifest=MANIFEST,newManifest=MANIFEST,oldCaddy=OLD_CADDY,newCaddy=NEW_CADDY,notices='d90b13a3239ca8da1dbd3450d14f02ff177a9b7e90949751db8947b14f238616')
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    source=sys.stdin.buffer.read(1048577);old=op.SOURCE.read_bytes();archive=op.FILES/ARCHIVE
    if sha(old)!=OLD_SOURCE or sha(source)!=NEW_SOURCE:raise ValueError('Hosting source changed')
    previous=b'/codi-browser-source-1f6f3c159.tar.zst';new=b'/'+ARCHIVE.encode()
    if old.count(previous)!=1 or new in old or source!=old.replace(previous,previous+b' '+new,1):raise ValueError('Candidate changes more than the archive allowlist')
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_uid!=0 or archive.stat().st_mode&0o022 or op.filehash(archive)!=ARCHIVE_SHA:raise ValueError('New archive missing or changed')
    with tempfile.TemporaryDirectory(prefix='codi-browser-source-update-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(source);(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
