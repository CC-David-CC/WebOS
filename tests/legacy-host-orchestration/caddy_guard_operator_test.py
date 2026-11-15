"""Keep the reviewed live-migration pins bound to the rendered guard."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/'active-system/scripts'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class CaddyGuardOperatorTest(unittest.TestCase):
    def test_operator_pins_exact_rendered_files_and_start_order(self):
        render=load('guard_renderer',ROOT/'render-caddy-proxy-guard.py')
        operator=load('guard_operator',ROOT/'activate-caddy-proxy-guard.py')
        rules,unit,dropin=render.render(operator.UID)
        for name,content in [('caddy-proxy-guard.nft',rules),
                             ('codi-caddy-proxy-guard.service',unit),
                             ('40-codi-caddy-proxy-guard.conf',dropin)]:
            self.assertEqual(hashlib.sha256(content.encode()).hexdigest(),operator.FILES[name][1])
        self.assertIn('meta skuid != 966',rules)
        self.assertIn('Before=caddy.service',unit)
        self.assertIn('Requires=codi-caddy-proxy-guard.service',dropin)
        self.assertIn('After=codi-caddy-proxy-guard.service',dropin)


if __name__=='__main__':unittest.main()
