#!/usr/bin/env python3
"""Serve a disposable CAD host fixture; apply the production policy to frames.

The parent harness deliberately has test-only in-memory account storage. This
server does not provide signed accounts or deploy/modify any hosting route.
"""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

POLICY=("default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
        "media-src 'self' blob:; connect-src 'self' wss://ksu.codes; "
        "font-src 'self' data:; frame-src 'self' blob:; worker-src 'self' blob:; "
        "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'self'")

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split('?',1)[0].startswith('/node_modules/jsketcher-build/'):
            self.send_header('Content-Security-Policy',POLICY)
        self.send_header('Cache-Control','no-store')
        super().end_headers()

    def log_message(self,*args):
        pass

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--port',type=int,default=19843)
    args=p.parse_args()
    root=args.directory.resolve(strict=True)
    if not (root/'index.html').is_file():
        p.error('Disposable fixture index.html required')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(Handler,directory=str(root)))
    print(f'Isolated CAD host ready at http://127.0.0.1:{args.port}/',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
