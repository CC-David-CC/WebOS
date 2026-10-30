#!/usr/bin/env python3
"""Verify source-only runtime export and rejection of mutations."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
builder=load('runtime_builder',ROOT/'active-system/scripts/build-browser-relay-runtime.py')
runner=load('runtime_runner',ROOT/'active-system/scripts/serve-browser-relay.py')

class Runtime(unittest.TestCase):
    def test_exact_runtime_and_tampering(self):
        with tempfile.TemporaryDirectory(prefix='codi-browser-export-') as folder:
            dest=Path(folder)/'runtime';result=builder.build(dest);old_root=runner.ROOT;runner.ROOT=dest/'active-system'
            try:
                self.assertEqual(runner.verify_runtime(result['manifestSHA256'])['sourceCommit'],result['sourceCommit'])
                with self.assertRaises(ValueError):runner.verify_runtime('0'*64)
                target=dest/'apps/system/browser/relay/wisp.py';original=target.read_bytes();target.write_bytes(original+b'\n# changed\n')
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                target.write_bytes(original);extra=dest/'extra.py';extra.write_text('unexpected')
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                extra.unlink();link=dest/'bad-link';link.symlink_to(target)
                with self.assertRaises(ValueError):runner.verify_runtime(result['manifestSHA256'])
                link.unlink();self.assertEqual(runner.verify_runtime(result['manifestSHA256'])['version'],'codi-browser-relay-runtime/1')
            finally:runner.ROOT=old_root

if __name__=='__main__':unittest.main(verbosity=2)
