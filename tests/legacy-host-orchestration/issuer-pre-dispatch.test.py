"""The retry marker is emitted only when the WSGI app was not dispatched."""
import socket
import sys
import threading
import unittest
from pathlib import Path
from wsgiref.simple_server import make_server
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'active-system'))
from origin_service.http_server import BoundedServer, QuietHandler

class AdmissionTest(unittest.TestCase):
    def test_overload_response_is_before_dispatch(self):
        invoked=[]
        def app(environ,start_response):
            invoked.append(environ['PATH_INFO']);start_response('200 OK',[('Content-Length','0')]);return [b'']
        server=make_server('127.0.0.1',0,app,server_class=BoundedServer,handler_class=QuietHandler)
        # Saturate the exact server admission gate before a real HTTP request.
        for _ in range(8): self.assertTrue(server.slots.acquire(blocking=False))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with socket.create_connection(server.server_address,timeout=5) as s:
                s.settimeout(5);s.sendall(b'POST /api/v1/auth HTTP/1.1\r\nHost: localhost\r\nContent-Length: 2\r\n\r\n{}');response=s.recv(4096)
            self.assertIn(b'503 Service Unavailable',response)
            self.assertIn(b'X-Codi-Admission: pre-dispatch',response)
            self.assertEqual(invoked,[], 'pre-dispatch failure must not invoke account code')
        finally:
            for _ in range(8):server.slots.release()
            server.shutdown();server.server_close();thread.join(timeout=5)
if __name__=='__main__':unittest.main()
