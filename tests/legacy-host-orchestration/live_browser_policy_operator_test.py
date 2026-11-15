"""Exercise the operator against disposable policy copies, never live files."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'active-system'),str(ROOT/'apps/system/browser')]
from network_policy.policy import AccessPolicy,countries,networks
from relay.policy import DestinationPolicy,hostname

spec=importlib.util.spec_from_file_location('live_policy_operator',ROOT/'active-system/scripts/manage-live-browser-policy.py')
operator=importlib.util.module_from_spec(spec);spec.loader.exec_module(operator)
IMPORTS=(AccessPolicy,countries,networks,DestinationPolicy,hostname)

class PolicyOperatorTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();p=Path(self.temp.name)
        self.access=p/'access.json';self.domains=p/'domains.json'
        shutil.copyfile(ROOT/'active-system/network_policy/default.json',self.access)
        shutil.copyfile(ROOT/'apps/system/browser/relay/policy.json',self.domains)
        self.old_protect=operator.protect
        # Production enforces root-owned files. These are isolated user-owned
        # fixture copies, and must still be regular non-symlink files.
        operator.protect=lambda path: self.assertTrue(path.is_file() and not path.is_symlink())
    def tearDown(self):operator.protect=self.old_protect;self.temp.cleanup()

    def test_independent_access_lists_and_invalid_input(self):
        add=lambda direction,kind,value:operator.update_access(self.access,'add',direction,kind,value,IMPORTS)
        self.assertTrue(add('incomingLogin','blockedCidrs','203.0.113.4'))
        self.assertTrue(add('outgoing','blockedCountries','CA'))
        self.assertFalse(add('outgoing','blockedCountries','CA'))
        state=json.loads(self.access.read_text())
        self.assertEqual(state['incomingLogin']['blockedCidrs'],['203.0.113.4'])
        self.assertEqual(state['outgoing']['blockedCountries'],['CA'])
        self.assertEqual(state['incomingLogin']['blockedCountries'],[])
        before=self.access.read_bytes()
        with self.assertRaises(ValueError):add('outgoing','blockedCidrs','not-an-ip')
        self.assertEqual(before,self.access.read_bytes())
        self.assertTrue(operator.update_access(self.access,'remove','outgoing','blockedCountries','CA',IMPORTS))

    def test_domain_lists_and_whitelist_switch(self):
        add=lambda kind,value:operator.update_domains(self.domains,'add',kind,value,IMPORTS)
        self.assertTrue(add('blacklist','EXAMPLE.COM.'))
        self.assertFalse(add('blacklist','example.com'))
        self.assertTrue(add('whitelist','supplier.example'))
        self.assertTrue(operator.update_domains(self.domains,'set','whitelistEnabled','on',IMPORTS))
        policy=DestinationPolicy.load(self.domains)
        self.assertTrue(policy.whitelist_enabled)
        self.assertEqual(policy.check_hostname('supplier.example',443),'supplier.example')
        with self.assertRaises(ValueError):policy.check_hostname('example.com',443)
        before=self.domains.read_bytes()
        with self.assertRaises(ValueError):add('whitelist','127.0.0.1')
        self.assertEqual(before,self.domains.read_bytes())
        self.assertTrue(operator.update_domains(self.domains,'set','whitelistEnabled','off',IMPORTS))
        self.assertTrue(operator.update_domains(self.domains,'remove','blacklist','example.com',IMPORTS))

if __name__=='__main__':unittest.main()
