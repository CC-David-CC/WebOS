#!/usr/bin/env python3
"""Worker runtime export allowlist and mutation refusal on real artifacts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import unittest

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('guest_worker_export',ROOT/'scripts/export-guest-wire.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)

class ExportChecks(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/'.build/guest-workers'/('export-check-'+secrets.token_hex(5));self.root.mkdir(parents=True);self.addCleanup(shutil.rmtree,self.root)
        self.target=self.root/'runtime';self.record=exporter.export(self.target)
    def test_exact_runtime_excludes_accounts_credentials_frontend_and_installer(self):
        self.assertEqual(exporter.verify(self.target),self.record)
        for forbidden in ['app.js','guest_service/client.mjs','guest_service/coordinator.py','accounts.sqlite3','issuer.pem','managed.json','wire.secret','scripts/manage-services.py']:
            self.assertNotIn(forbidden,self.record['files']);self.assertFalse((self.target/forbidden).exists())
        self.assertEqual(len(self.record['files']),12)
    def test_changed_runtime_input_refused(self):
        file=self.target/'guest_service/worker.py';file.write_bytes(file.read_bytes()+b'\n# changed\n')
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_private_file_cannot_be_smuggled_by_updating_manifest(self):
        file=self.target/'wire.secret';file.write_text('fixture non-secret');manifest=self.target/'guest-wire.json';value=json.loads(manifest.read_text());value['files']['wire.secret']=exporter.record(file);manifest.write_text(json.dumps(value))
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_required_code_cannot_be_removed_from_manifest(self):
        name='guest_service/usage.py';(self.target/name).unlink();manifest=self.target/'guest-wire.json';value=json.loads(manifest.read_text());del value['files'][name];manifest.write_text(json.dumps(value))
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_symlink_refused(self):
        file=self.target/'requirements.lock';saved=self.root/'lock';file.rename(saved);file.symlink_to(saved)
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_hardlink_refused(self):
        import os
        os.link(self.target/'requirements.lock',self.root/'linked')
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_existing_artifact_is_not_overwritten(self):
        before=(self.target/'guest-wire.json').read_bytes()
        with self.assertRaises(ValueError):exporter.export(self.target)
        self.assertEqual((self.target/'guest-wire.json').read_bytes(),before)
    def test_public_output_refused_before_writing(self):
        forbidden=ROOT/'assets/guest-worker-forbidden'
        self.assertFalse(forbidden.exists())
        with self.assertRaises(ValueError):exporter.export(forbidden)
        self.assertFalse(forbidden.exists())

if __name__=='__main__':
    tests=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(ExportChecks))
    report={'status':'PASS' if tests.wasSuccessful() else 'FAIL','tests':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors),'scope':__doc__,'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['guest_service/installation.py','scripts/export-guest-wire.py','scripts/guest-worker-export-check.py']}}
    (ROOT/'.build/checks/guest-worker-export-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if tests.wasSuccessful() else 1)
