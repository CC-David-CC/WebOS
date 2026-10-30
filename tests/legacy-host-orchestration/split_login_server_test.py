"""Real HTTP checks for the issuer's isolated login listener."""
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'active-system'))
from network_policy.login_server import split_login_server
from origin_service.http_server import BoundedServer, QuietHandler


class SplitLoginServerTest(unittest.TestCase):
    def test_real_listener_scope_reload_and_teardown(self):
        def app(env, start):
            body = b'upstream'
            start('200 OK', [('Content-Length', str(len(body)))])
            return [body]
        def free_port():
            with socket.socket() as s:
                s.bind(('127.0.0.1', 0))
                return s.getsockname()[1]
        def request(port, path, ip='8.8.8.8'):
            req=Request(f'http://127.0.0.1:{port}{path}', data=b'{}',
                        headers={'X-Codi-Client-IP': ip}, method='POST')
            try:
                with urlopen(req, timeout=3) as response:
                    return response.status
            except HTTPError as error:
                return error.code
        with tempfile.TemporaryDirectory() as tmp:
            policy=Path(tmp)/'access.json'
            value={'version':'codi-network-access/1',
                   'incomingLogin':{'blockedCidrs':['203.0.113.0/24'],'blockedCountries':[]},
                   'outgoing':{'blockedCidrs':[],'blockedCountries':[]}}
            policy.write_text(json.dumps(value))
            login_port=free_port()
            with split_login_server(app, policy, port=login_port,
                                    server_class=BoundedServer, handler_class=QuietHandler) as ordinary:
                with make_server('127.0.0.1', 0, ordinary, server_class=BoundedServer,
                                 handler_class=QuietHandler) as main:
                    thread=threading.Thread(target=main.serve_forever, daemon=True)
                    thread.start()
                    try:
                        self.assertEqual(request(main.server_port, '/config.json'), 200)
                        self.assertEqual(request(main.server_port, '/api/v1/auth'), 404)
                        self.assertEqual(request(login_port, '/config.json'), 404)
                        self.assertEqual(request(login_port, '/api/v1/auth'), 200)
                        self.assertEqual(request(login_port, '/api/v1/auth', '203.0.113.8'), 403)
                        value['incomingLogin']['blockedCidrs'].append('8.8.8.8')
                        new=policy.with_suffix('.new');new.write_text(json.dumps(value));new.replace(policy)
                        self.assertEqual(request(login_port, '/api/v1/auth'), 403)
                    finally:
                        main.shutdown();thread.join()
            with self.assertRaises(OSError):
                socket.create_connection(('127.0.0.1', login_port), timeout=1)


if __name__ == '__main__':
    unittest.main()
