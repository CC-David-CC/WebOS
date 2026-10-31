#!/usr/bin/env python3
"""Check the restricted, source-pinned Browser systemd service template."""
import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('browser_service_render',ROOT/'active-system/scripts/render-browser-service.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Render(unittest.TestCase):
    def test_caddy_starts_relay_without_blocking_the_rest_of_the_site(self):
        text=module.caddy_dependency()
        self.assertIn('Wants=codi-browser-relay.service',text)
        self.assertIn('After=codi-browser-relay.service',text)
        self.assertNotIn('Requires=',text)

    def test_expected_isolation_and_exact_pins(self):
        values=dict(runtime='a'*64,venv='b'*64,issuer='c'*64,policy='d'*64,proxy_uid=997,proxy_gid=984)
        text=module.render(**values)
        self.assertNotIn('--source-root',text)
        self.assertIn('--source-root /srv/codi-browser/source-staging/engine-6736dce5',module.render(**values,sources=True))
        self.assertNotIn('--report-database',text)
        self.assertNotIn('--audit-database',text)
        self.assertNotIn('LoadCredential=',text)
        enabled=module.render(**values,reports=True)
        self.assertIn('StateDirectoryMode=0700',enabled)
        self.assertIn('--report-admins /etc/codi-browser/report-admins.json',enabled)
        audited=module.render(**values,reports=True,audit=True)
        self.assertIn('StateDirectory=codi-browser-reports codi-browser-audit',audited)
        self.assertIn('LoadCredential=audit-signing-key:/etc/codi-browser/private/audit-signing-key',audited)
        self.assertIn('--audit-key /run/credentials/codi-browser-relay.service/audit-signing-key',audited)
        for required in ('User=codi-browser','Group=caddy','RuntimeDirectoryMode=0750','--require-root-runtime','--proxy-uid 997','--proxy-gid 984','ProtectSystem=strict','PrivateTmp=yes','NoNewPrivileges=yes','MemoryMax=512M','CapabilityBoundingSet='):
            self.assertIn(required,text)
        for field in ('runtime','venv','issuer','policy'):
            with self.subTest(field=field),self.assertRaises(ValueError):module.render(**{**values,field:'abc\nExecStart=/bin/sh'})
        for field in ('proxy_uid','proxy_gid'):
            with self.subTest(field=field),self.assertRaises(ValueError):module.render(**{**values,field:0})

if __name__=='__main__':unittest.main(verbosity=2)
