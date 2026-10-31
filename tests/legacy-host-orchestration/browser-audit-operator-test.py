#!/usr/bin/env python3
"""Exercise protected audit key provisioning without touching live state."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('browser_audit_operator',ROOT/'active-system/scripts/manage-browser-audit.py')
operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)

class OperatorTest(unittest.TestCase):
    def test_key_is_stable_and_not_replaced_when_ledger_exists(self):
        with tempfile.TemporaryDirectory(prefix='codi-audit-operator-') as folder:
            root=Path(folder);key=root/'private'/'key';database=root/'ledger.sqlite3'
            def protect(path,*,directory=False,mode=None):
                self.assertFalse(path.is_symlink());self.assertTrue(path.is_dir() if directory else path.is_file())
                if mode is not None:self.assertEqual(path.stat().st_mode&0o777,mode)
            with patch.object(operator,'KEY',key),patch.object(operator,'DB',database),patch.object(operator,'protected',side_effect=protect):
                operator.credential(True);original=key.read_bytes();self.assertEqual(len(original),32)
                operator.credential(True);self.assertEqual(key.read_bytes(),original)
                database.write_bytes(b'existing ledger');key.unlink()
                with self.assertRaisesRegex(ValueError,'restore the original key'):operator.credential(True)
                self.assertFalse(key.exists());self.assertEqual(database.read_bytes(),b'existing ledger')

if __name__=='__main__':unittest.main(verbosity=2)
