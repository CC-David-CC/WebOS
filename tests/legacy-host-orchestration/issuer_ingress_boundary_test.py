"""Exercise the issuer's proxy-UID boundary in a disposable network namespace.

Run with: sudo unshare -n python3 tests/issuer_ingress_boundary_test.py
The test never changes the host network namespace or existing firewall tables.
"""
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'active-system'))
from network_policy.kernel import render_issuer_ingress, render_issuer_ingress_update


class IngressBoundaryTests(unittest.TestCase):
    def test_rejects_ambiguous_configuration(self):
        for uid in (0, -1, True, '997'):
            with self.subTest(uid=uid), self.assertRaises(ValueError):
                render_issuer_ingress(uid, 8118)
        for port in (0, 65536, True, '8118'):
            with self.subTest(port=port), self.assertRaises(ValueError):
                render_issuer_ingress(997, port)
        with self.assertRaises(ValueError):
            render_issuer_ingress(997, 8118, table='x;flush ruleset')

    @unittest.skipUnless(os.environ.get('CODI_TEST_PRIVATE_NETNS') == '1',
                         'Requires a disposable network namespace')
    def test_real_local_connections(self):
        self.assertEqual(os.geteuid(), 0)
        self.assertNotEqual(os.stat('/proc/self/ns/net').st_ino, os.stat('/proc/1/ns/net').st_ino,
                            'Refusing to change the initial network namespace')
        subprocess.run(['ip', 'link', 'set', 'lo', 'up'], check=True)
        self.assertNotIn('codi_issuer_ingress', subprocess.check_output(['nft', 'list', 'tables'], text=True))
        server = socket.socket()
        server.bind(('127.0.0.1', 0))
        server.listen()
        port = server.getsockname()[1]
        server.settimeout(.2)
        stop = threading.Event()
        def accept():
            while not stop.is_set():
                try:
                    conn, _ = server.accept()
                    with conn:
                        conn.sendall(b'ok')
                except TimeoutError:
                    continue
        thread = threading.Thread(target=accept, daemon=True)
        thread.start()
        script = ('import socket,sys; '
                  's=socket.create_connection(("127.0.0.1",int(sys.argv[1])),timeout=2); '
                  'assert s.recv(2)==b"ok"')
        def probe(uid):
            return subprocess.run(['setpriv', '--reuid', str(uid), '--regid', str(uid),
                                   '--clear-groups', sys.executable, '-c', script, str(port)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        try:
            self.assertEqual(probe(12345), 0)
            self.assertEqual(probe(12346), 0)
            rules = render_issuer_ingress_update(12345, port)
            for _ in range(2):
                subprocess.run(['nft', '-f', '-'], input=rules, text=True, check=True)
                self.assertNotEqual(probe(12346), 0, 'reapplying keeps boundary active')
            self.assertEqual(probe(12345), 0, 'designated proxy can reach issuer')
            self.assertNotEqual(probe(12346), 0, 'other local user is rejected')
            self.assertNotEqual(probe(0), 0, 'root process is rejected too')
            subprocess.run(['nft', 'delete', 'table', 'inet', 'codi_issuer_ingress'], check=True)
            self.assertEqual(probe(12346), 0, 'removing only the test table restores access')
        finally:
            stop.set()
            thread.join(timeout=2)
            server.close()


if __name__ == '__main__':
    unittest.main()
