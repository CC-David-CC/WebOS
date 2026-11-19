"""Explicit proxy origin validation before account state initialization."""
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_development as server


class OriginTests(unittest.TestCase):
    def test_https_and_loopback_origins(self):
        for value in ['https://ksu.codes', 'https://ksu.codes:8443', 'http://127.0.0.1:18140', 'http://localhost:1234', 'http://[::1]:1234']:
            self.assertEqual(server.validate_origin(value), value)

    def test_refuses_credentials_paths_unsafe_schemes_and_bad_ports(self):
        for value in ['http://ksu.codes', 'https://user:password@ksu.codes', 'https://ksu.codes/', 'https://ksu.codes/a', 'https://ksu.codes?x=1', 'https://ksu.codes#x', 'https://ksu.codes:99999', 'file:///tmp/site', 'https://ksu.codes\n']:
            with self.subTest(origin=value):
                with self.assertRaises(ValueError):
                    server.validate_origin(value)


class ProxyOriginTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_loopback_http_uses_explicit_https_identity_and_checks_headers(self):
        from aiohttp.test_utils import TestClient, TestServer
        from cryptography.hazmat.primitives.asymmetric import ec
        from webos_accounts import jose
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            public = base / 'public'; public.mkdir(); (public / 'index.html').write_text('<!doctype html><title>Test</title>')
            (public / 'wordcraft').mkdir(); (public / 'wordcraft/index.html').write_text('<!doctype html><title>Print fixture</title>')
            (public / 'asset.js').write_text('// fixture')
            state = base / 'private'
            app = await server.create_application(public, state, 'https://ksu.codes')
            client = TestClient(TestServer(app)); await client.start_server()
            try:
                response = await client.get('/', headers={'Host': 'ksu.codes'})
                desktop = response.headers['Content-Security-Policy']
                self.assertIn('https://noaa-gfs-bdp-pds.s3.amazonaws.com', desktop)
                self.assertIn("frame-src 'self';", desktop)
                self.assertIn("object-src 'none'", desktop)
                response = await client.get('/asset.js', headers={'Host': 'ksu.codes'})
                ordinary = response.headers['Content-Security-Policy']
                self.assertIn("connect-src 'self';", ordinary)
                self.assertNotIn('noaa.gov', ordinary)
                self.assertIn("frame-src 'self';", ordinary)
                self.assertIn("object-src 'none'", ordinary)
                response = await client.get('/wordcraft/index.html', headers={'Host': 'ksu.codes'})
                self.assertEqual(response.headers['Content-Security-Policy'], ordinary.replace("frame-src 'self';", "frame-src 'self' blob:;"))
                response = await client.get('/config.json', headers={'Host': 'ksu.codes'})
                self.assertEqual(response.status, 200)
                configuration = await response.json()
                self.assertEqual(configuration['identity']['issuer'], 'https://ksu.codes')
                self.assertNotIn('agentOperations', configuration)
                self.assertEqual(configuration['gateway']['concurrentTransfers'], 8)
                self.assertEqual(configuration['gateway']['sharedConcurrentTransfers'], 16)
                response = await client.get('/config.json', headers={'Host': 'other.example'})
                self.assertEqual(response.status, 403)
                payload = {'key': jose.public_jwk(ec.generate_private_key(ec.SECP256R1()).public_key()), 'path': '/api/v1/auth'}
                response = await client.post('/api/v1/challenge', json=payload, headers={'Host': 'ksu.codes', 'Origin': 'https://ksu.codes'})
                self.assertEqual(response.status, 200)
                response = await client.post('/api/v1/challenge', json=payload, headers={'Host': 'ksu.codes', 'Origin': 'https://other.example'})
                self.assertEqual(response.status, 403)
            finally:
                await client.close()
            with self.assertRaises(ValueError):
                await server.create_application(public, state, 'https://other.example')

    async def test_agent_operations_refuse_proxy_origin_before_state_initialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            state = base / 'private'
            with self.assertRaisesRegex(ValueError, 'direct loopback'):
                await server.create_application(base / 'public', state, 'https://ksu.codes', agent_operations=True)
            self.assertFalse(state.exists())


if __name__ == '__main__':
    unittest.main()
