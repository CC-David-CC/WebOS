#!/usr/bin/env python3
"""Exercise the actual loopback HTTP helper against a disposable server."""
import http.server,importlib.util,json,pathlib,threading
path=pathlib.Path(__file__).resolve().parents[1]/'research/main-opfs-release/main-one-shot.py';spec=importlib.util.spec_from_file_location('one_shot_health_test',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  assert self.headers['Host']=='ksu.codes';body=json.dumps({'path':self.path}).encode();self.send_response(200);self.end_headers();self.wfile.write(body)
 def log_message(self,*args):pass
server=http.server.HTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever);thread.start()
try:
 for path in ('/config.json','/healthz'):
  status,raw=m.get_http(server.server_port,path);assert status==200 and json.loads(raw)=={'path':path}
 print('PASS actual one-shot HTTP helper: loopback, host and response')
finally:server.shutdown();thread.join();server.server_close()
