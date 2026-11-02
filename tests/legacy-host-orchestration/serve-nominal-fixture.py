#!/usr/bin/env python3
"""Serve only the unwired nominal-worker fixture on loopback."""
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES={'/nominal-worker.mjs':ROOT/'apps/system/gcode-preview/experimental/nominal-worker.mjs','/nominal-probe.mjs':ROOT/'apps/system/gcode-preview/experimental/nominal-probe.mjs','/nominal-panel.mjs':ROOT/'apps/system/gcode-preview/experimental/nominal-panel.mjs','/nominal-renderer.mjs':ROOT/'apps/system/gcode-preview/experimental/nominal-renderer.mjs','/comments.mjs':ROOT/'apps/system/gcode-preview/comments.mjs'}
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  # Preserve the module's parent-relative import without exposing directories.
  path=self.path.replace('/experimental/nominal-worker.mjs','/nominal-worker.mjs').replace('/experimental/nominal-probe.mjs','/nominal-probe.mjs').replace('/experimental/nominal-panel.mjs','/nominal-panel.mjs').replace('/experimental/nominal-renderer.mjs','/nominal-renderer.mjs')
  if path=='/':body=b'<!doctype html><title>Isolated nominal worker test</title>';content='text/html'
  elif path in FILES:body=FILES[path].read_bytes();content='text/javascript'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',content);self.send_header('Cache-Control','no-store');self.send_header('Access-Control-Allow-Origin','*');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
HTTPServer(('127.0.0.1',19476),Handler).serve_forever()
