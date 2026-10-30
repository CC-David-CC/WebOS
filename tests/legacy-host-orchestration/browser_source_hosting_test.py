"""Check the opt-in source route preserves the current managed website."""
import copy
import importlib.util
from pathlib import Path
import sys
import tomllib
import types
import unittest

ROOT=Path(__file__).resolve().parents[1]
STAGED=ROOT/'.build/browser-hosting-candidate'
sys.path.insert(0,str(STAGED))
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
source=load('source_hosting',ROOT/'active-system/scripts/prepare-browser-source-hosting.py')


class SourceHostingTest(unittest.TestCase):
    def test_route_is_explicit_and_ksu_only(self):
        if not (STAGED/'common.py').exists():self.skipTest('Captured live hosting generator unavailable')
        base=load('source_hosting_base',STAGED/'common.py')
        candidate=types.ModuleType('source_hosting_candidate');candidate.__file__=str(STAGED/'common.py')
        exec(compile(source.derive((STAGED/'common.py').read_text()),candidate.__file__,'exec'),candidate.__dict__)
        data=tomllib.loads((STAGED/'sites-login-relay.toml').read_text())
        for mode in ('prepare','production'):self.assertEqual(base.caddy(data,mode),candidate.caddy(data,mode))
        site=next(x for x in data['sites'] if x['domain']=='ksu.codes');site['codi_browser_sources']=True
        candidate.validate(data);config=candidate.caddy(data,'production')
        self.assertIn('handle_path /browser-sources/*',config)
        self.assertIn('root * /srv/codi-browser/source-staging/engine-6736dce5',config)
        for name in source.NAMES:self.assertIn('/'+name,config)
        self.assertIn('respond 404',config)
        copydata=copy.deepcopy(data);other=next(x for x in copydata['sites'] if x['domain']!='ksu.codes')
        other['codi_browser_sources']=True
        with self.assertRaises(ValueError):candidate.validate(copydata)
        self.assertTrue(next(x for x in tomllib.loads(candidate.dump(data))['sites'] if x['domain']=='ksu.codes')['codi_browser_sources'])


if __name__=='__main__':unittest.main()
