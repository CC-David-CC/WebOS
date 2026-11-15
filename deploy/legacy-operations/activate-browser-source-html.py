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
OLD_SOURCE='1e3ca517ece6a2c9617f8a4728d24bf7605dbc805de23a2e2912e833c7a189ef'
NEW_SOURCE='f01b3fb88a37f15e130ce18a4afeabf785a59c3d76512ea558e344442aeb4dc6'
MANIFEST='e0a7c48bec1a5495742514d5120f5ebcb6432fef91265f9df8cea55f97329a4a'
OLD_CADDY='48f77ec2a65f828c0eaea9d23d46df0087816396e6bf094babf6c73c38d571a7'
NEW_CADDY='986d9d2dc1dbb605c99b2eaf443357d5fb095cb0bc2d2096f3d9ce0e35f89ca2'
ARCHIVE='codi-browser-source-1573b1ffc.tar.zst'
ARCHIVE_SHA='4f376d5619d916adf902c7818bc2f8a577c2849a830db27790aa045d00f3f4a5'


def sha(value):return hashlib.sha256(value).hexdigest()


def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply, or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed hosting operator changed')
    spec=importlib.util.spec_from_file_location('codi_source_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.JOURNAL=op.STATE/'browser-source-update-1573-journal.json';op.RECEIPT=op.STATE/'browser-source-update-1573-result.json'
    op.PINS.update(oldSource=OLD_SOURCE,newSource=NEW_SOURCE,oldManifest=MANIFEST,newManifest=MANIFEST,oldCaddy=OLD_CADDY,newCaddy=NEW_CADDY,notices='2bbc58cc430284b074c112c8cf758c20f18390981500b79857dcf8eb17274916')
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    source=sys.stdin.buffer.read(1048577);old=op.SOURCE.read_bytes();archive=op.FILES/ARCHIVE
    if sha(old)!=OLD_SOURCE or sha(source)!=NEW_SOURCE:raise ValueError('Hosting source changed')
    previous=b'/codi-browser-source-808fac040.tar.zst';new=b'/'+ARCHIVE.encode()
    if old.count(previous)!=1 or new in old or source!=old.replace(previous,previous+b' '+new,1):raise ValueError('Candidate changes more than the archive allowlist')
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_uid!=0 or archive.stat().st_mode&0o022 or op.filehash(archive)!=ARCHIVE_SHA:raise ValueError('New archive missing or changed')
    with tempfile.TemporaryDirectory(prefix='codi-browser-source-update-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(source);(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
