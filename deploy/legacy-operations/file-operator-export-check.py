#!/usr/bin/env python3
"""Mutation/export path tests, using disposable code copies and output paths."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('file_operator_export',ROOT/'scripts/export-file-operator.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Export(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='codi-file-export-');self.root=Path(self.temp.name);self.before=module.ROOT;module.ROOT=self.root
        for name in module.FILES:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
        self.output=self.root/'.build/file-operators/candidate'
    def tearDown(self):module.ROOT=self.before;self.temp.cleanup()
    def test_actual_export_and_exact_manifest(self):
        result=module.export(self.output);self.assertEqual(result,module.verify(self.output));self.assertEqual(set(result['files']),module.FILES)
    def test_modified_file_refused(self):
        module.export(self.output);(self.output/'file_service/operator.py').write_text('mutated')
        with self.assertRaises(ValueError):module.verify(self.output)
    def test_extra_private_file_refused(self):
        module.export(self.output);(self.output/'state.sqlite3').write_bytes(b'fixture')
        with self.assertRaises(ValueError):module.verify(self.output)
    def test_missing_file_even_if_manifest_adjusted_refused(self):
        module.export(self.output);manifest=self.output/'file-operator.json';value=json.loads(manifest.read_text());name='file_service/operator.py';(self.output/name).unlink();del value['files'][name];manifest.write_text(json.dumps(value))
        with self.assertRaises(ValueError):module.verify(self.output)
    def test_linked_file_and_hardlink_refused(self):
        module.export(self.output);p=self.output/'file_service/operator.py';p.unlink();p.symlink_to(self.root/'file_service/operator.py')
        with self.assertRaises(ValueError):module.verify(self.output)
        p.unlink();os.link(self.root/'file_service/operator.py',p)
        with self.assertRaises(ValueError):module.verify(self.output)
    def test_output_parent_link_refused(self):
        self.output.parent.mkdir(parents=True);(self.output.parent/'alias').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):module.export(self.output.parent/'alias/escaped')
        self.assertFalse((self.root/'escaped').exists())
    def test_output_traversal_refused(self):
        with self.assertRaises(ValueError):module.export(self.root/'.build/file-operators/../../escaped')
        self.assertFalse((self.root/'escaped').exists())
    def test_linked_source_parent_refused(self):
        (self.root/'file_service').rename(self.root/'actual');(self.root/'file_service').symlink_to(self.root/'actual',target_is_directory=True)
        with self.assertRaises(ValueError):module.export(self.output)
        self.assertFalse(self.output.exists())
    def test_existing_output_preserved(self):
        module.export(self.output);raw=(self.output/'file-operator.json').read_bytes()
        with self.assertRaises(ValueError):module.export(self.output)
        self.assertEqual((self.output/'file-operator.json').read_bytes(),raw)
    def test_worker_export_refuses_traversal_and_parent_link(self):
        parent=ROOT/'.build/gateways';name='export-guard-'+secrets.token_hex(6);alias=parent/name
        parent.mkdir(parents=True,exist_ok=True);alias.symlink_to(self.root,target_is_directory=True)
        try:
            for output in [alias/'escaped',parent/'..'/name]:
                result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/export-user-files.py'),'--output',str(output)],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
            self.assertFalse((self.root/'escaped').exists());self.assertFalse((ROOT/'.build'/name).exists())
        finally:alias.unlink()

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Export))
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Actual code-only operator export/mutation and private output-path refusal; no installed/public claim',
            'sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/export-file-operator.py','scripts/export-user-files.py','scripts/file-operator-export-check.py']}}
    (ROOT/'.build/checks/file-operator-export-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() else 1)
