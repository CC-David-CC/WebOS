#!/usr/bin/env python3
"""Actual root operator artifact allowlist, custody links and mutation refusal."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import unittest

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('operator_export_checks',ROOT/'scripts/export-guest-operator.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)

class Checks(unittest.TestCase):
    def setUp(self):
        self.root=ROOT/'.build/guest-operators'/('export-check-'+secrets.token_hex(5));self.root.mkdir(parents=True);self.addCleanup(shutil.rmtree,self.root)
        self.target=self.root/'operator';self.info=exporter.export(self.target)
    def test_exact_controller_without_configs_secrets_data_or_worker(self):
        self.assertEqual(exporter.verify(self.target),self.info);self.assertEqual(len(self.info['files']),10)
        for name in ['managed.json','pending.json','wire.secret','accounts.sqlite3','usage.sqlite3','issuer.pem','guest_service/worker.py','app.js']:
            self.assertNotIn(name,self.info['files']);self.assertFalse((self.target/name).exists())
    def test_changed_operator_source_refused(self):
        path=self.target/'guest_service/operator.py';path.write_bytes(path.read_bytes()+b'\n# changed\n')
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_missing_code_cannot_be_removed_from_manifest(self):
        name='guest_service/operator.py';(self.target/name).unlink();path=self.target/'guest-operator.json';value=json.loads(path.read_text());del value['files'][name];path.write_text(json.dumps(value))
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_private_input_cannot_be_added_to_manifest(self):
        path=self.target/'wire.secret';path.write_text('synthetic fixture');manifest=self.target/'guest-operator.json';value=json.loads(manifest.read_text());value['files']['wire.secret']=exporter.record(path);manifest.write_text(json.dumps(value))
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_linked_source_refused(self):
        path=self.target/'requirements.lock';saved=self.root/'saved.lock';path.rename(saved);path.symlink_to(saved)
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_linked_ancestor_refused(self):
        alias=self.root/'alias';alias.symlink_to(self.target, target_is_directory=True)
        with self.assertRaises(ValueError):exporter.verify(alias)
    def test_hardlink_refused(self):
        os.link(self.target/'requirements.lock',self.root/'linked.lock')
        with self.assertRaises(ValueError):exporter.verify(self.target)
    def test_no_overwrite_or_public_export(self):
        before=(self.target/'guest-operator.json').read_bytes()
        with self.assertRaises(ValueError):exporter.export(self.target)
        self.assertEqual((self.target/'guest-operator.json').read_bytes(),before)
        forbidden=ROOT/'assets/guest-operator-forbidden';self.assertFalse(forbidden.exists())
        with self.assertRaises(ValueError):exporter.export(forbidden)
        self.assertFalse(forbidden.exists())

if __name__=='__main__':
    tests=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    value={'status':'PASS' if tests.wasSuccessful() else 'FAIL','tests':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors),'scope':__doc__,'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['guest_service/operator.py','scripts/export-guest-operator.py','scripts/guest-operator-export-check.py']}}
    (ROOT/'.build/checks/guest-operator-export-result.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2));raise SystemExit(0 if tests.wasSuccessful() else 1)
