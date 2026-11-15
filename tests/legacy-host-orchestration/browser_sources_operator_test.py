"""Verify the source-route activation operator matches reviewed artifacts."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.modules.setdefault('common',types.ModuleType('common'))
sys.modules.setdefault('webctl',types.ModuleType('webctl'))
spec=importlib.util.spec_from_file_location('browser_sources_operator',ROOT/'active-system/scripts/activate-browser-sources.py')
operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)


class SourceOperatorPins(unittest.TestCase):
    def test_exact_reviewed_inputs(self):
        folder=ROOT/'.build/browser-hosting-candidate';notices=ROOT/'.build/browser-source-provision/notices-r1'
        paths={'newSource':folder/'common-sources.py','newManifest':folder/'sites-sources.toml',
               'newCaddy':folder/'Caddyfile-sources','notices':notices/'notice-manifest.json'}
        if not all(path.is_file() for path in paths.values()):self.skipTest('Staged notice and hosting candidates unavailable')
        for name,path in paths.items():
            with self.subTest(name=name):self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),operator.PINS[name])


if __name__=='__main__':unittest.main()
