#!/usr/bin/env python3
"""Disposable shared HTTP/TLS ingress, redirects, source IP and SNI/ACME routing."""
import csv,hashlib,http.client,io,json,os,secrets,shutil,socket,ssl,subprocess,tempfile,threading,time
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;checks=ROOT/'.build/checks';run=Path(tempfile.mkdtemp(prefix='shared-ingress-',dir=checks));run.chmod(0o700)
ports=[24080,24443,25080,25443,26079]
for port in ports:
 with socket.socket() as probe:probe.bind(('127.0.0.1',port))
hosts=['site'+str(index)+'.example.invalid' for index in range(8)];turn_host='turn.example.invalid';stats=Path('/run/user')/str(os.getuid())/('codi-ingress-'+secrets.token_hex(6)+'.sock');children=[];stub=None;worker=None;result={'status':'FAIL','scope':'Loopback-only shared ingress with disposable local CA; no live/public/WAN or real TURN allocation claim','fixtureDirectory':str(run)}
def start(name,args):
 with (run/(name+'.log')).open('wb') as log:child=subprocess.Popen([str(x) for x in args],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'XDG_CONFIG_HOME':str(run/'config'),'XDG_DATA_HOME':str(run/'data')})
 children.append(child);return child
def request(host,path='/',alpn=None,port=24443,source='127.0.0.3'):
 context=ssl.create_default_context(cafile=str(run/'test-ca.crt'))
 if alpn:context.set_alpn_protocols(alpn)
 raw=socket.socket();raw.settimeout(5);raw.bind((source,0));raw.connect(('127.0.0.1',port));connection=http.client.HTTPSConnection(host,timeout=5);connection.sock=context.wrap_socket(raw,server_hostname=host)
 try:
  connection.request('GET',path);response=connection.getresponse();body=response.read();return response.status,body.decode(),response.headers
 finally:connection.close()
def counters():
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
  client.settimeout(3);client.connect(str(stats));client.sendall(b'show stat\n');client.shutdown(socket.SHUT_WR);raw=b''
  while True:
   chunk=client.recv(65536)
   if not chunk:break
   raw+=chunk
 rows=csv.DictReader(io.StringIO(raw.decode().lstrip('# ')));return {row['pxname']:int(row['stot']) for row in rows if row['svname']=='BACKEND'}
try:
 caddy=run/'Caddyfile';caddy.write_text('''{
 admin off
 persist_config off
 local_certs
 skip_install_trust
 http_port 25080
 https_port 25443
 default_bind 127.0.0.1
 servers {
  protocols h1 h2
  listener_wrappers {
   proxy_protocol {
    timeout 1s
    allow 127.0.0.1/32
    fallback_policy reject
   }
   tls
  }
 }
}
'''+''.join(host+' {\n respond "WEB:'+host+':{http.request.remote.host}"\n}\n' for host in [*hosts,turn_host])+':25080 {\n respond "Not found" 404\n}\n')
 haproxy=run/'haproxy.cfg';haproxy.write_text('''global
 maxconn 128
 stats socket STATS mode 600 level admin
defaults
 mode tcp
 timeout connect 3s
 timeout client 30s
 timeout server 30s
frontend web_http
 bind 127.0.0.1:24080
 default_backend web_plain
frontend shared_tls
 bind 127.0.0.1:24443
 tcp-request inspect-delay 3s
 tcp-request content accept if { req.ssl_hello_type 1 }
 acl turn_name req.ssl_sni -i turn.example.invalid
 use_backend web_tls if { req.ssl_alpn acme-tls/1 }
 use_backend turn_tls if turn_name
 default_backend web_tls
backend web_plain
 server web 127.0.0.1:25080 send-proxy-v2
backend web_tls
 server web 127.0.0.1:25443 send-proxy-v2
backend turn_tls
 server turn 127.0.0.1:26079
'''.replace('STATS',str(stats)))
 caddy_binary=ROOT.parent/'.build/tools/caddy';haproxy_binary=ROOT/'.build/tools/haproxy-root/usr/sbin/haproxy'
 subprocess.run([str(haproxy_binary),'-c','-f',str(haproxy)],check=True,capture_output=True,text=True)
 start('caddy',[caddy_binary,'run','--config',caddy,'--adapter','caddyfile'])
 deadline=time.monotonic()+20;root_cert=run/'data/caddy/pki/authorities/local/root.crt'
 while not root_cert.exists():
  if time.monotonic()>deadline:raise ValueError('Disposable Caddy CA not ready')
  time.sleep(.1)
 shutil.copyfile(root_cert,run/'test-ca.crt')
 leaf=None
 while leaf is None:
  leaf=next((file for file in (run/'data').rglob('*.crt') if file.name==turn_host+'.crt'),None)
  if leaf is None:
   if time.monotonic()>deadline:raise ValueError('Disposable TURN hostname certificate not ready')
   time.sleep(.1)
 class TurnStub(BaseHTTPRequestHandler):
  def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b'TURN backend reached')
  def log_message(self,*args):pass
 stub=ThreadingHTTPServer(('127.0.0.1',26079),TurnStub);stub.daemon_threads=True;context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(leaf,leaf.with_suffix('.key'));stub.socket=context.wrap_socket(stub.socket,server_side=True);worker=threading.Thread(target=stub.serve_forever,daemon=True);worker.start()
 start('haproxy',[haproxy_binary,'-db','-f',haproxy])
 while not stats.exists():
  if time.monotonic()>deadline:raise ValueError('HAProxy control socket not ready')
  time.sleep(.1)
 redirects={};https_hosts=[]
 for host in hosts:
  connection=http.client.HTTPConnection('127.0.0.1',24080,timeout=5);connection.request('GET','/sample?x=1',headers={'Host':host});response=connection.getresponse();response.read();location=response.getheader('Location');assert response.status==308 and location=='https://'+host+'/sample?x=1',(host,response.status,location);connection.close();redirects[host]=location
  for alpn in [None,['http/1.1']]:
   status,body,headers=request(host,alpn=alpn);assert status==200 and body=='WEB:'+host+':127.0.0.3',(host,status,body)
  https_hosts.append(host)
 before=counters();status,body,_=request(turn_host);after=counters();assert status==200 and body=='TURN backend reached' and after['turn_tls']==before['turn_tls']+1 and after['web_tls']==before['web_tls']
 before=counters()
 context=ssl.create_default_context(cafile=str(run/'test-ca.crt'));context.set_alpn_protocols(['acme-tls/1'])
 try:
  with socket.create_connection(('127.0.0.1',24443),5) as raw:
   with context.wrap_socket(raw,server_hostname=turn_host):pass
 except ssl.SSLError:pass
 after=counters();assert after['web_tls']==before['web_tls']+1 and after['turn_tls']==before['turn_tls']
 context=ssl.create_default_context(cafile=str(run/'test-ca.crt'));context.set_alpn_protocols(['h2'])
 with socket.create_connection(('127.0.0.1',24443),5) as raw:
  with context.wrap_socket(raw,server_hostname=hosts[0]) as tls:assert tls.selected_alpn_protocol()=='h2'
 # Existing operator loopback checks can still reach Caddy without PROXY headers.
 status,body,_=request(hosts[0],port=25443,source='127.0.0.1');assert status==200 and body=='WEB:'+hosts[0]+':127.0.0.1'
 result.update(status='PASS',websiteHosts=https_hosts,redirects=redirects,noInternalPortsInRedirects=True,httpsWithoutAlpnPreserved=True,http1AndHttp2Preserved=True,sourceIpPreservedWithProxyV2=True,dedicatedTurnSniRouted=True,acmeAlpnForTurnSniRoutedToCaddy=True,operatorDirectLoopbackTlsPreserved=True)
except BaseException as error:result['error']=str(error)
finally:
 if stub is not None:stub.shutdown();stub.server_close();worker.join(5)
 for child in reversed(children):
  child.terminate();child.wait(10)
 stats.unlink(missing_ok=True);shutil.rmtree(run/'data',ignore_errors=True);shutil.rmtree(run/'config',ignore_errors=True)
 result['allChildrenReaped']=all(child.poll() is not None for child in children);result['disposableCaKeysRemoved']=not (run/'data').exists();result['sha256']={'scripts/shared-ingress-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 if not result['allChildrenReaped'] or not result['disposableCaKeysRemoved'] or worker is not None and worker.is_alive():result['status']='FAIL'
 (checks/'shared-ingress-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if result['status']!='PASS':raise SystemExit(1)
