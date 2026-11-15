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
OLD_SOURCE='bb88688bdb94c5921ec08187d4605075772c0187b401e8e33342be19184e60d5'
NEW_SOURCE='2d04ab00dc0e17003f94155b4f812b640ed2f9ed897e4f3685b8cb2bbbda41cb'
MANIFEST='8351825cf04e6b1b1ff0a36fabfb56bb2a6a35aca6180c4884ea55098713e851'
OLD_CADDY='7e49a881f9ea0b6d46cc846ce270ec76f1aa996d91973c5513fc03893e014b42'
NEW_CADDY='e75ed8f025c95c7b372c3df1ec9e73254d13a1a2f57cfef43a74e05493282eaa'
ARCHIVE='codi-browser-source-29a71d717.tar.zst'
ARCHIVE_SHA='f231dfee54279c20c6bca77988b556d6fcad7c8886792eb78c63e1f9c10b680b'


def sha(value):return hashlib.sha256(value).hexdigest()


def main():
    if os.geteuid()!=0 or socket.gethostname()!='box-webhost':raise ValueError('Root on box-webhost required')
    if len(sys.argv)!=2 or sys.argv[1] not in ('exercise','apply','recover'):raise ValueError('Specify exercise, apply, or recover')
    if OPERATOR.is_symlink() or OPERATOR.stat().st_uid!=0 or OPERATOR.stat().st_mode&0o022 or sha(OPERATOR.read_bytes())!=OPERATOR_SHA:raise ValueError('Installed hosting operator changed')
    spec=importlib.util.spec_from_file_location('codi_source_operator',OPERATOR);op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
    op.JOURNAL=op.STATE/'browser-source-update-29a-journal.json';op.RECEIPT=op.STATE/'browser-source-update-29a-result.json'
    op.PINS.update(oldSource=OLD_SOURCE,newSource=NEW_SOURCE,oldManifest=MANIFEST,newManifest=MANIFEST,oldCaddy=OLD_CADDY,newCaddy=NEW_CADDY,notices='45ccd10bc607f1215e852ad3a9350634b50a3fd60fa431e33332f306f583d315')
    action=sys.argv[1]
    if action=='recover':sys.argv=[str(OPERATOR),action];op.main();return
    source=sys.stdin.buffer.read(1048577);old=op.SOURCE.read_bytes();archive=op.FILES/ARCHIVE
    if sha(old)!=OLD_SOURCE or sha(source)!=NEW_SOURCE:raise ValueError('Hosting source changed')
    previous=b'/codi-browser-source-485928f3f.tar.zst';new=b'/'+ARCHIVE.encode()
    if old.count(previous)!=1 or new in old or source!=old.replace(previous,previous+b' '+new,1):raise ValueError('Candidate changes more than the archive allowlist')
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_uid!=0 or archive.stat().st_mode&0o022 or op.filehash(archive)!=ARCHIVE_SHA:raise ValueError('New archive missing or changed')
    with tempfile.TemporaryDirectory(prefix='codi-browser-source-update-') as directory:
        path=Path(directory);(path/'common.py').write_bytes(source);(path/'sites.toml').write_bytes(op.MANIFEST.read_bytes())
        sys.argv=[str(OPERATOR),action,'--inputs',str(path)];op.main()


if __name__=='__main__':main()
