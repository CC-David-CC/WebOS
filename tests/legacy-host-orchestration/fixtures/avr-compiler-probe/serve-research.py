#!/usr/bin/env python3
"""Serve a local AVR research fixture with the desktop's restricted CSP."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
  self.send_header('X-Content-Type-Options','nosniff');super().end_headers()
 def log_message(self,*args):pass
p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--port',type=int,default=18290);a=p.parse_args();root=a.directory.resolve(strict=True)
if not root.is_dir():raise SystemExit('Directory required')
with ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(root))) as server:server.serve_forever()
