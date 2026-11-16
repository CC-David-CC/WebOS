#!/usr/bin/env python3
"""Loopback-only public static baseline/candidate switch for cache testing."""
import os,pathlib,http.server
BASE=pathlib.Path(os.environ['CODI_MAIN_BASELINE']).resolve();NEXT=pathlib.Path(os.environ['CODI_MAIN_CANDIDATE']).resolve();PORT=int(os.environ.get('CODI_CACHE_PORT','19961'));selected=BASE
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE),**kwargs)
 def do_POST(self):
  global selected
  if self.path!='/__candidate':self.send_error(404);return
  selected=NEXT;self.send_response(204);self.end_headers()
 def do_GET(self):
  if self.path=='/__fixture':
   body=b'<!doctype html><title>Isolated cache test</title>';self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
  super().do_GET()
 def end_headers(self):
  if self.path.split('?')[0]=='/assets/desktop/offline-worker.js':self.send_header('Service-Worker-Allowed','/')
  super().end_headers()
 def translate_path(self,path):self.directory=str(selected);return super().translate_path(path)
 def log_message(self,*args):pass
http.server.ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
