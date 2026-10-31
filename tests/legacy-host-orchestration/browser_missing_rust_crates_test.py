"""Exercise registry checksum verification and root/nested notice detection."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('missing_rust_crates',ROOT/'apps/system/browser/tools/audit_missing_rust_crates.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Response:
    def __init__(self,data):self.data=data
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):return self.data[:limit]

class AuditTest(unittest.TestCase):
    def test_locked_archive_and_both_notice_spellings(self):
        buf=io.BytesIO()
        with tarfile.open(fileobj=buf,mode='w:gz') as archive:
            for name in ('fixture-1.0/LICENCE-MIT','fixture-1.0/docs/LICENSE'):
                data=b'example';info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
        blob=buf.getvalue();checksum=hashlib.sha256(blob).hexdigest()
        lock=f'[[package]]\nname="fixture"\nversion="1.0"\nsource="registry+example"\nchecksum="{checksum}"\n'.encode()
        manifest={'version':'codi-rust-missing-registry/1','cargoLockSHA256':hashlib.sha256(lock).hexdigest(),'packages':[{'name':'fixture','version':'1.0','checksum':checksum}]}
        with tempfile.TemporaryDirectory() as folder:
            lockfile=Path(folder)/'Cargo.lock';lockfile.write_bytes(lock);listing=Path(folder)/'manifest.json';listing.write_text(json.dumps(manifest))
            with patch.object(module,'urlopen',return_value=Response(blob)):
                result=module.audit(lockfile,listing)[0]
                self.assertEqual(result['rootLicenseFiles'],['LICENCE-MIT']);self.assertEqual(result['nestedLicenseFiles'],['docs/LICENSE'])
            with patch.object(module,'urlopen',return_value=Response(b'bad')):
                with self.assertRaisesRegex(ValueError,'checksum differs'):module.audit(lockfile,listing)

if __name__=='__main__':unittest.main()
