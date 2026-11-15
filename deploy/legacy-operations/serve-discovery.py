#!/usr/bin/env python3
"""Disposable loopback desktop + independently scoped RAM public steward.

No accounts, persistence, root/issuer key files, public listeners or router ports.
Run with .build/auth-venv/bin/python scripts/serve-discovery.py.
"""
import argparse,asyncio,json,secrets,sys,threading,time
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from serve import PublicHandler
from steward.server import StewardServer
from steward.protocol import jose
from cryptography.hazmat.primitives.asymmetric import ec

async def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8100);p.add_argument('--steward-port',type=int,default=8101)
 p.add_argument('--origin',help='Explicit external origin when testing behind a reverse proxy')
 p.add_argument('--endpoint',help='Explicit signed external steward endpoint; backend remains loopback')
 a=p.parse_args()
 if not 1<=a.steward_port<=65535 or not 0<=a.port<=65535:raise ValueError('Invalid loopback ports')
 if a.origin:
  u=urlsplit(a.origin)
  if not u.hostname or u.username or u.password or u.path or u.query or u.fragment or (u.scheme!='https' and not (u.scheme=='http' and u.hostname in ('127.0.0.1','localhost','::1'))):raise ValueError('External origin must be HTTPS authority or loopback HTTP')
 root=ec.generate_private_key(ec.SECP256R1());service=ec.generate_private_key(ec.SECP256R1());realm=secrets.token_urlsafe(32);scope=secrets.token_urlsafe(32);now=int(time.time())
 endpoint=a.endpoint or f'ws://127.0.0.1:{a.steward_port}/rendezvous';public=jose.public_jwk(service)
 grant={'key_id':jose.thumbprint(public),'public_key':public,'endpoints':[endpoint],'scopes':[scope],'limits':{'lease_seconds':120,'sample_size':4,'signal_bytes':32768},'exp':now+600,'failure_domain':'one-loopback-host'}
 seed=jose.sign({'version':'codi-seed/1','realm':realm,'revision':1,'iat':now,'exp':now+600,'stewards':[grant]},root,'codi-seed/1')
 config=json.loads((ROOT/'config.json').read_text())
 if config['identity']['mode']!='local-development':raise ValueError('This disposable demo requires explicit local-development identity policy')
 class Handler(PublicHandler):
  def send_config(self,head=False):
   current={**config,'discovery':{**config['discovery'],'descriptor':server.descriptor(renew_if_expiring=True)}}
   body=json.dumps(current).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers()
   if not head:self.wfile.write(body)
  def send_bootstrap(self,head=False):
   try:body=json.dumps(server.bundle(renew_if_expiring=True)).encode()
   except ValueError:self.send_error(503,'Discovery delegation expired');return
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers()
   if not head:self.wfile.write(body)
  def do_GET(self):
   if self.path=='/discovery.json':self.send_bootstrap();return
   if self.path=='/config.json':
    try:self.send_config()
    except ValueError:self.send_error(503,'Discovery delegation expired')
    return
   super().do_GET()
  def do_HEAD(self):
   if self.path=='/discovery.json':self.send_bootstrap(True);return
   if self.path=='/config.json':
    try:self.send_config(True)
    except ValueError:self.send_error(503,'Discovery delegation expired')
    return
   super().do_HEAD()
  def log_message(self,*args):pass
 http=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);origin=a.origin or f'http://127.0.0.1:{http.server_port}'
 server=StewardServer(seed=seed,root_key=jose.public_jwk(root),realm=realm,endpoint=endpoint,service_key=service,identity_policy=config['identity'],origins=[origin])
 config['discovery']={'pin':{'realm':realm,'rootKey':jose.public_jwk(root),'endpoints':[endpoint],'allowLoopback':endpoint.startswith('ws://')},'seed':seed,'descriptor':server.descriptor(),'scope':scope,'sourcePath':'/discovery.json'}
 serving=False
 try:
  await server.start(a.steward_port);threading.Thread(target=http.serve_forever,daemon=True).start();serving=True
  print(f'Disposable discovery desktop: {origin}/',flush=True)
  print('Open two Chrome sessions. Chat → Join discovery in both → Discover peers → Invite selected → Accept peer.',flush=True)
  print('Local / not server validated. Public scope only. Descriptors and control admissions renew within a ten-minute delegation. Ctrl-C discards service keys and leases.',flush=True)
  await asyncio.Event().wait()
 finally:
  await server.close()
  if serving:await asyncio.to_thread(http.shutdown)
  http.server_close()

if __name__=='__main__':
 try:asyncio.run(main())
 except KeyboardInterrupt:pass
