#!/usr/bin/env python3
"""Real issuer/gateway proof for compact authenticated file versions."""
import base64
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('gateway_http_fixture', ROOT / 'scripts/gateway-http-check.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class Version(fixture.HTTP):
    async def test_capabilities_are_public_bounded_and_not_cached(self):
        async with self.client.get(self.gateway_url+'/gateway/capabilities',headers={'Host':self.origin.removeprefix('http://')}) as response:
            self.assertEqual(response.status,200)
            self.assertEqual(await response.json(),{'version':'codi-file-capabilities/1','fileVersion':True})
            self.assertEqual(response.headers['Cache-Control'],'no-store')
        async with self.client.get(self.gateway_url+'/gateway/capabilities',headers={'Host':'other.invalid'}) as response:
            self.assertEqual(response.status,403)

    async def test_version_is_private_authorized_and_tracks_replacement(self):
        alice, ak = await self.enter()
        bob, bk = await self.enter('bob')
        payload = b'private content ' * 2048
        status, created, _ = await self.rpc(alice, ak, 'create', 'note', data=base64.b64encode(payload).decode())
        self.assertEqual(status, 200)
        status, version, headers = await self.rpc(alice, ak, 'version', 'note')
        self.assertEqual(status, 200)
        self.assertEqual(version, {'bytes': len(payload), 'sha256': created['sha256']})
        self.assertLess(len(json.dumps(version)), 150)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual((await self.rpc(bob, bk, 'version', 'note'))[0], 404)
        self.assertEqual((await self.rpc(alice, ak, 'version', '../note'))[0], 403)
        self.assertEqual((await self.rpc(alice, ak, 'version', 'note', subject=bob['identity']['sub']))[0], 403)
        status, changed, _ = await self.rpc(alice, ak, 'replace', 'note', data='bmV3', previousSHA256=created['sha256'])
        self.assertEqual(status, 200)
        self.assertEqual((await self.rpc(alice, ak, 'version', 'note'))[1], {'bytes': 3, 'sha256': changed['sha256']})
        self.store.set_permission(alice['identity']['sub'], 'read', False)
        self.assertEqual((await self.rpc(alice, ak, 'version', 'note'))[0], 403)
        anonymous, key = await self.enter(None)
        raw = fixture.jose.dumps({'resource': 'my-files', 'operation': 'version', 'path': 'note'})
        self.assertEqual((await self.authorize(anonymous, key, raw))[0], 403)


if __name__ == '__main__':
    suite = unittest.TestSuite([Version('test_version_is_private_authorized_and_tracks_replacement'), Version('test_capabilities_are_public_bounded_and_not_cached')])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
