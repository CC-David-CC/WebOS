"""Verify exact staged inputs match the live-transition operator's pins."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.modules.setdefault('common',types.ModuleType('common'))
sys.modules.setdefault('webctl',types.ModuleType('webctl'))
spec=importlib.util.spec_from_file_location('browser_backend_operator',ROOT/'active-system/scripts/activate-browser-backend.py')
operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)


class BackendPins(unittest.TestCase):
    def test_reviewed_candidate_pins(self):
        folder=ROOT/'.build/browser-hosting-candidate'
        paths={'candidateSource':folder/'common.py','candidateManifest':folder/'sites-login-relay.toml',
               'candidateCaddy':folder/'Caddyfile-login-relay',
               'candidateRelease':ROOT/'.build/browser-native-candidate/profile28-r3/connected-release.json'}
        if not all(path.is_file() for path in paths.values()):self.skipTest('Staged candidate artifacts not present')
        for name,path in paths.items():
            with self.subTest(name=name):self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),operator.PINS[name])
        config=(folder/'Caddyfile-login-relay').read_text()
        self.assertIn('handle /api/v1/auth {',config)
        self.assertIn('reverse_proxy 127.0.0.1:8117',config)
        self.assertIn('unix//run/codi-browser/relay.sock',config)


if __name__=='__main__':unittest.main()
