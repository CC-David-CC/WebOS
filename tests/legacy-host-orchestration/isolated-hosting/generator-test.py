"""Local-only generated routing isolation checks; no host activation."""
import copy,importlib.util,sys,tempfile,subprocess,tomllib,unittest,threading,socket,ssl,urllib.request,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'))
spec=importlib.util.spec_from_file_location('hosting',root/'ops/common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Beta(unittest.TestCase):
 def setUp(self):self.base=tomllib.loads((root/'sites.toml').read_text());self.base_render=m.caddy(self.base,'production');self.value=copy.deepcopy(self.base);self.value['codi_beta_simplified']='a'*64
 def test_baseline_unchanged_and_beta_has_only_dedicated_backends(self):
  output=m.caddy(self.value,'production');start=output.index('beta.ksu.codes {');end=output.index('\n}\n',start)+4;beta=output[start:end]
  self.assertEqual(output[:start]+output[end:],self.base_render)
  for port in (28118,28132,28140):self.assertIn('127.0.0.1:'+str(port),beta)
  for port in (8117,8118,8132,8140):self.assertNotIn('127.0.0.1:'+str(port),beta)
  self.assertIn('wss://beta.ksu.codes',beta);self.assertNotIn('wss://ksu.codes',beta);self.assertIn('respond "Not found" 404',beta)
 def test_manifest_roundtrip_and_invalid_values_refused(self):
  value=tomllib.loads(m.dump(self.value));self.assertEqual(value,self.value)
  for invalid in ('a'*63,'../etc',True,'F'*64):
   copy_=copy.deepcopy(self.value);copy_['codi_beta_simplified']=invalid
   with self.assertRaises(ValueError):m.validate(copy_)
  copy_=copy.deepcopy(self.value);copy_['codi_shared_ingress']=False
  with self.assertRaises(ValueError):m.validate(copy_)
  copy_=copy.deepcopy(self.value);copy_['sites'][0]['domain']='beta.ksu.codes'
  with self.assertRaises(ValueError):m.validate(copy_)
 def test_generated_beta_routes_to_isolated_stub_services(self):
  servers=[];threads=[];proc=None
  class H(BaseHTTPRequestHandler):
   def do_GET(self):
    body=(self.server.tag+' '+self.path).encode();self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
   def log_message(self,*args):pass
  try:
   for tag in ('issuer','guest','gateway'):
    server=ThreadingHTTPServer(('127.0.0.1',0),H);server.tag=tag;servers.append(server);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
   with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
   rendered=m.caddy(self.value,'production');start=rendered.index('beta.ksu.codes {');end=rendered.index('\n}\n',start)+3;block=rendered[start:end]
   block=block.replace('beta.ksu.codes {','http://127.0.0.1:'+str(port)+' {',1).replace('\timport site_defaults\n','')
   for old,server in zip((28118,28132,28140),servers):block=block.replace('127.0.0.1:'+str(old),'127.0.0.1:'+str(server.server_port))
   with tempfile.TemporaryDirectory(prefix='codi-beta-routes-') as d:
    static=Path(d)/'static';static.mkdir();(static/'index.html').write_text('beta fixture');(static/'assets/desktop').mkdir(parents=True);(static/'assets/desktop/offline-worker.js').write_text('// fixture');block=block.replace('/srv/codi-connected/simplified/'+'a'*64,str(static));cfg=Path(d)/'Caddyfile';cfg.write_text('{\n admin off\n}\n'+block+'\n')
    proc=subprocess.Popen(['/tmp/codi-microduck-hosting-evidence/caddy','run','--config',str(cfg),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(100):
     try:
      with socket.create_connection(('127.0.0.1',port),timeout=.1):break
     except OSError:time.sleep(.02)
    else:self.fail('local Caddy failed to start')
    def get(path):
     try:
      with urllib.request.urlopen('http://127.0.0.1:'+str(port)+path,timeout=3) as r:return r.status,r.read().decode()
     except urllib.error.HTTPError as e:return e.code,e.read().decode()
    self.assertEqual(get('/'),(200,'beta fixture'));
    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/assets/desktop/offline-worker.js',timeout=3) as worker:self.assertEqual(worker.headers.get('Service-Worker-Allowed'),'/')
    self.assertEqual(get('/api/v1/auth'),(200,'issuer /api/v1/auth'));self.assertEqual(get('/gateway/use'),(200,'gateway /gateway/use'));self.assertEqual(get('/config.json'),(200,'guest /config.json'));self.assertEqual(get('/codi-guest-cookie'),(200,'guest /'));self.assertEqual(get('/guest-network')[0],503);self.assertEqual(get('/unknown')[0],404)
  finally:
   if proc is not None:
    proc.terminate()
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:proc.kill();proc.wait()
   for server in servers:server.shutdown();server.server_close()
   for thread in threads:thread.join(2)
 def test_beta_hostname_https_with_disposable_certificate(self):
  proc=None
  with tempfile.TemporaryDirectory(prefix='codi-beta-tls-') as d:
   root_=Path(d);cert=root_/'cert.pem';key=root_/'key.pem'
   subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=beta.ksu.codes','-addext','subjectAltName=DNS:beta.ksu.codes'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   static=root_/'static';static.mkdir();(static/'index.html').write_text('beta tls fixture')
   with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
   rendered=m.caddy(self.value,'production');start=rendered.index('beta.ksu.codes {');end=rendered.index('\n}\n',start)+3;block=rendered[start:end]
   block=block.replace('beta.ksu.codes {','https://beta.ksu.codes:'+str(port)+' {\n\tbind 127.0.0.1\n\ttls '+str(cert)+' '+str(key),1).replace('\timport site_defaults\n','').replace('/srv/codi-connected/simplified/'+'a'*64,str(static))
   cfg=root_/'Caddyfile';cfg.write_text('{\n admin off\n auto_https disable_redirects\n}\n'+block+'\n')
   try:
    proc=subprocess.Popen(['/tmp/codi-microduck-hosting-evidence/caddy','run','--config',str(cfg),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    for _ in range(100):
     try:
      with socket.create_connection(('127.0.0.1',port),timeout=.1):break
     except OSError:time.sleep(.02)
    else:self.fail('local TLS Caddy failed to start: '+proc.stderr.read().decode())
    ctx=ssl.create_default_context(cafile=str(cert))
    with socket.create_connection(('127.0.0.1',port),timeout=3) as raw:
     with ctx.wrap_socket(raw,server_hostname='beta.ksu.codes') as conn:
      conn.sendall(b'GET / HTTP/1.1\r\nHost: beta.ksu.codes\r\nConnection: close\r\n\r\n');chunks=[]
      while True:
       data=conn.recv(65536)
       if not data:break
       chunks.append(data)
    response=b''.join(chunks);self.assertIn(b'HTTP/1.1 200',response);self.assertIn(b'beta tls fixture',response)
   finally:
    if proc is not None:
     proc.terminate()
     try:proc.wait(timeout=5)
     except subprocess.TimeoutExpired:proc.kill();proc.wait()
     if proc.stderr:proc.stderr.close()
 def test_caddy_config_validates(self):
  with tempfile.TemporaryDirectory(prefix='codi-beta-caddy-') as d:
   logs=Path(d)/'logs';logs.mkdir();p=Path(d)/'Caddyfile';p.write_text(m.caddy(self.value,'production').replace('/var/log/caddy/',str(logs)+'/').replace('import /etc/caddy/private/hardware-users','disposable $2a$14$Vsf9aNUClfIcH1B53DOtBeXH1dC/g55j5jA0XWRGuTb.2zsRuVONS'))
   r=subprocess.run(['/tmp/codi-microduck-hosting-evidence/caddy','validate','--config',str(p),'--adapter','caddyfile'],capture_output=True,text=True,timeout=20)
   self.assertEqual(r.returncode,0,r.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
