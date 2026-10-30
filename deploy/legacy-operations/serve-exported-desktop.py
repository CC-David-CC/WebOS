#!/usr/bin/env python3
"""Loopback-only release/prefix check server; never serves the worktree."""
import argparse,json
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
CSP="default-src 'none'; script-src 'self' 'wasm-unsafe-eval'; connect-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--prefix',default='/desktop/');p.add_argument('--port',type=int,default=8122);a=p.parse_args()
 root=Path(a.root).resolve();manifest=json.loads((root/'release.json').read_text());allowed=set(manifest['files'])|{'release.json'}
 if not a.prefix.startswith('/') or not a.prefix.endswith('/') or any(part in ('.','..') for part in a.prefix.split('/')):p.error('Absolute prefix with trailing slash required')
 class Handler(SimpleHTTPRequestHandler):
  def do_GET(self):
   if urlsplit(self.path).path==a.prefix.rstrip('/'):
    self.send_response(308);self.send_header('Location',a.prefix);self.end_headers();return
   super().do_GET()
  def send_head(self):
   path=unquote(urlsplit(self.path).path)
   if not path.startswith(a.prefix):self.send_error(404);return None
   relative=path[len(a.prefix):] or 'index.html'
   if relative not in allowed or any(part in ('.','..','') for part in relative.split('/')):self.send_error(404);return None
   target=root
   for part in relative.split('/'):
    target=target/part
    if target.is_symlink():self.send_error(404);return None
   self.release_relative=relative
   return super().send_head()
  def translate_path(self,path):return str(root/getattr(self,'release_relative','index.html'))
  def end_headers(self):
   self.send_header('Content-Security-Policy',CSP);self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');super().end_headers()
  def log_message(self,*args):pass
 with ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=str(root))) as server:
  print('Export check: http://127.0.0.1:'+str(a.port)+a.prefix,flush=True)
  try:server.serve_forever()
  except KeyboardInterrupt:pass
if __name__=='__main__':main()
