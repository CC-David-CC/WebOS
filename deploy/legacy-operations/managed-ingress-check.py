#!/usr/bin/env python3
"""Disposable shared HTTP/TLS ingress, redirects, source IP and SNI/ACME routing."""
import csv,hashlib,http.client,io,json,os,secrets,shutil,socket,ssl,subprocess,tempfile,threading,time,sys
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));from ingress_service.configuration import haproxy as render_proxy,service as render_service
checks=ROOT/'.build/checks';run=Path(tempfile.mkdtemp(prefix='shared-ingress-',dir=checks));run.chmod(0o700)
ports=[24080,24443,25080,25443,26079]
for port in ports:
 with socket.socket() as probe:probe.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);probe.bind(('127.0.0.1',port))
hosts=['site'+str(index)+'.example.invalid' for index in range(9)];turn_host='turn.ksu.codes';instance='codi-shared-ingress-test-'+secrets.token_hex(3);stats=Path('/run')/instance/'stats.sock';children=[];stub=None;worker=None;result={'status':'FAIL','scope':'Loopback-only shared ingress with disposable local CA; no live/public/WAN or real TURN allocation claim','fixtureDirectory':str(run)}
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
 probe="import socket,sys\nwith socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:\n s.settimeout(3);s.connect(sys.argv[1]);s.sendall(b'show stat'+bytes([10]));s.shutdown(socket.SHUT_WR);raw=b''\n while True:\n  chunk=s.recv(65536)\n  if not chunk:break\n  raw+=chunk\n sys.stdout.buffer.write(raw)"
 raw=subprocess.check_output(['sudo','-n','python3','-B','-c',probe,str(stats)])
 rows=csv.DictReader(io.StringIO(raw.decode().lstrip('# ')));return {row['pxname']:int(row['stot']) for row in rows if row['svname']=='BACKEND'}
try:
 caddy=run/'Caddyfile';caddy.write_text('''{
 admin unix/ADMIN_SOCKET
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
 caddy.write_text(caddy.read_text().replace('ADMIN_SOCKET',str(run/'admin.sock')))
 haproxy=run/'haproxy.cfg';haproxy.write_text(render_proxy(http_bind='127.0.0.1:24080',tls_bind='127.0.0.1:24443',http_backend=25080,tls_backend=25443,turn_backend=26079,stats=str(stats)))
 caddy_binary=ROOT.parent/'.build/tools/caddy';haproxy_binary=ROOT/'.build/tools/haproxy-2.8.31-build-r1/runtime/haproxy'
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
 # Install the rendered production sandbox with disposable fixture paths.
 # Caddy/firewall dependencies are absent on this development machine, so
 # only those two dependency lines are omitted; production retains both.
 protected=Path('/srv')/instance
 unit=Path('/run/systemd/system')/(instance+'.service')
 unit_body=render_service(protected/'haproxy',protected/'haproxy.cfg',instance=instance).replace('Requires=caddy.service webhost-firewall.service\nAfter=caddy.service webhost-firewall.service\n','')
 payload={'directory':str(protected),'unit':str(unit),'binary':str(haproxy_binary),'config':haproxy.read_text(),'body':unit_body,'binarySHA256':hashlib.sha256(haproxy_binary.read_bytes()).hexdigest()}
 install="""import hashlib,json,os,pathlib,shutil,subprocess,sys
v=json.load(sys.stdin);p=pathlib.Path(v['directory']);u=pathlib.Path(v['unit']);assert not p.exists() and not u.exists();p.mkdir(mode=0o755)
shutil.copyfile(v['binary'],p/'haproxy');(p/'haproxy').chmod(0o755);assert hashlib.sha256((p/'haproxy').read_bytes()).hexdigest()==v['binarySHA256']
(p/'haproxy.cfg').write_text(v['config']);(p/'haproxy.cfg').chmod(0o644);u.write_text(v['body']);u.chmod(0o644)
checked=subprocess.run(['systemd-analyze','verify',str(u)],text=True,capture_output=True);assert checked.returncode==0,checked.stderr;subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','start',u.name],check=True)
"""
 installed=subprocess.run(['sudo','-n','python3','-B','-c',install],input=json.dumps(payload),text=True,capture_output=True);assert installed.returncode==0,installed.stderr
 probe="""import json,os,pathlib,subprocess,sys
u=sys.argv[1];pid=int(subprocess.check_output(['systemctl','show',u,'-p','MainPID','--value'],text=True));v=dict(line.split(':',1) for line in pathlib.Path('/proc',str(pid),'status').read_text().splitlines());uids=set(map(int,v['Uid'].split()));assert len(uids)==1 and 0 not in uids and int(v['CapEff'],16)==1024 and v['NoNewPrivs'].strip()=='1';print(json.dumps({'pid':pid,'uid':next(iter(uids)),'capabilities':v['CapEff'].strip(),'noNewPrivileges':True}))
"""
 sandbox=json.loads(subprocess.check_output(['sudo','-n','python3','-B','-c',probe,unit.name],text=True))
 # The stats socket is private to its dynamic user. Read it as root.

 while subprocess.run(['sudo','-n','test','-S',str(stats)],capture_output=True).returncode:
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
 # Exercise the controller's exact restore function against actual Caddy
 # reloads and the real fixture unit, with only filesystem paths/dependencies
 # replaced by disposable fixture resources. No hosting service is touched.
 recovery_probe=r'''
import ast,hashlib,json,os,pathlib,subprocess,sys,types
v=json.load(sys.stdin);P=pathlib.Path;protected=P(v['directory']);active=P(v['active']);source=protected/'common.py';manifest=protected/'sites.toml';native=protected/'native.json';dropin=protected/'caddy-fixture.conf';config=protected/'haproxy.cfg';unit=P(v['unit']);old=v['old'];new=v['new']
def digest(raw):return hashlib.sha256(raw).hexdigest()
def command(args,check=True,timeout=90):return subprocess.run(list(map(str,args)),check=check,capture_output=True,text=True,timeout=timeout).stdout.strip()
def reload_caddy(text):
 active.write_text(text);command([v['caddyBinary'],'reload','--config',active,'--adapter','caddyfile','--address','unix/'+v['admin']])
def remap(value):
 return native if str(value)=='/etc/codi-connected/ksu/managed.json' else active if str(value)=='/etc/caddy/Caddyfile' else P(value)
def write(p,raw,mode,uid,gid,_):p.write_bytes(raw);os.chmod(p,mode);os.chown(p,uid,gid)
ctl=types.SimpleNamespace(write=write,load=lambda:None,caddy_apply=lambda data,mode:reload_caddy(source.read_text()))
ns={'Path':remap,'source':source,'manifest':manifest,'unit':unit,'dropin':dropin,'config':config,'digest':digest,'run':command,'ctl':ctl,'reload_generator':lambda:None}
controller=ast.parse(v['controller']);fn=next(node for node in controller.body if isinstance(node,ast.FunctionDef) and node.name=='restore');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<exact-controller-restore>','exec'),ns)
command(['systemctl','stop',unit.name]);reload_caddy(old);native.write_text('disposable fixture metadata, no authority keys')
checks=[]
for running in [False,True]:
 source.write_text(new);manifest.write_text('proposed');config.write_text(v['config']);unit.write_text(v['unitBody']);dropin.write_text('disposable fixture dependency')
 for p in [source,manifest,config,unit,dropin]:p.chmod(0o644)
 command(['systemctl','daemon-reload']);reload_caddy(new)
 if running:command(['systemctl','start',unit.name])
 t={'before':{str(source):{'text':old,'mode':0o644,'uid':0,'gid':0},str(manifest):{'text':'prior','mode':0o644,'uid':0,'gid':0}},'files':{'common.ingress.py':new,'sites.ingress.toml':'proposed','codi-shared-ingress.service':v['unitBody'],'30-codi-ingress.conf':'disposable fixture dependency','haproxy.cfg':v['config']},'nativeConfigSHA256':digest(native.read_bytes()),'beforeCaddySHA256':digest(old.encode())}
 ns['restore'](t)
 assert active.read_text()==old and source.read_text()==old and manifest.read_text()=='prior' and not unit.exists() and not dropin.exists() and not config.exists()
 # Actual TLS/HTTP website response proves that rollback reopened the original
 # frontend ports, rather than merely restoring the config text.
 import http.client,socket,ssl
 ctx=ssl.create_default_context(cafile=v['ca']);c=http.client.HTTPSConnection(v['host'],timeout=5);c.sock=ctx.wrap_socket(socket.create_connection(('127.0.0.1',24443),5),server_hostname=v['host']);c.request('GET','/');r=c.getresponse();assert r.status==200 and r.read().decode()=='WEB:'+v['host']+':127.0.0.1';c.close()
 checks.append({'afterCutoverIngressRunning':running,'oldListenerActuallyRestored':True,'stagedUnitAndDependencyRemoved':True})
source.write_text('unrelated concurrent edit')
try:ns['restore'](t)
except AssertionError:assert source.read_text()=='unrelated concurrent edit'
else:raise AssertionError('Unrelated edit overwritten')
print(json.dumps({'checks':checks,'unrelatedHostingEditRefused':True,'exactControllerRestoreFunctionExecuted':True,'fullActivationRecoveryEnvelopeTested':False}))
'''
 spec=__import__('importlib.util',fromlist=['util']).spec_from_file_location('activation',ROOT/'scripts/activate-shared-ingress.py');activation=__import__('importlib.util',fromlist=['util']).module_from_spec(spec);spec.loader.exec_module(activation)
 new=caddy.read_text();old=new.replace('http_port 25080','http_port 24080').replace('https_port 25443','https_port 24443').replace(':25080 {',':24080 {')
 wrapper='  listener_wrappers {\n   proxy_protocol {\n    timeout 1s\n    allow 127.0.0.1/32\n    fallback_policy reject\n   }\n   tls\n  }\n';assert old.count(wrapper)==1;old=old.replace(wrapper,'')
 recovery_payload={'directory':str(protected),'active':str(caddy),'unit':str(unit),'unitBody':unit_body,'config':haproxy.read_text(),'old':old,'new':new,'caddyBinary':str(caddy_binary),'admin':str(run/'admin.sock'),'controller':activation.REMOTE,'ca':str(run/'test-ca.crt'),'host':hosts[0]}
 recovered=subprocess.run(['sudo','-n','python3','-B','-c',recovery_probe],input=json.dumps(recovery_payload),text=True,capture_output=True);assert recovered.returncode==0,recovered.stderr
 rollback=json.loads(recovered.stdout)
 result.update(status='PASS',managedUnitSandbox=sandbox,rollback=rollback,productionBootDependenciesTested=False,haproxyRelease='2.8.31',haproxyBinarySHA256=hashlib.sha256(haproxy_binary.read_bytes()).hexdigest(),websiteHosts=https_hosts,redirects=redirects,noInternalPortsInRedirects=True,httpsWithoutAlpnPreserved=True,http1AndHttp2Preserved=True,sourceIpPreservedWithProxyV2=True,dedicatedTurnSniRouted=True,acmeAlpnForTurnSniRoutedToCaddy=True,operatorDirectLoopbackTlsPreserved=True)
except BaseException as error:result['error']=str(error)
finally:
 if stub is not None:stub.shutdown();stub.server_close();worker.join(5)
 for child in reversed(children):
  child.terminate();child.wait(10)
 cleanup="""import pathlib,shutil,subprocess,sys
name=sys.argv[1];u=pathlib.Path('/run/systemd/system')/(name+'.service');p=pathlib.Path('/srv')/name
subprocess.run(['systemctl','stop',u.name],check=False,capture_output=True)
assert subprocess.check_output(['systemctl','show',u.name,'-p','MainPID','--value'],text=True).strip()=='0'
u.unlink(missing_ok=True);shutil.rmtree(p,ignore_errors=True);subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','reset-failed',u.name],capture_output=True)
"""
 subprocess.run(['sudo','-n','python3','-B','-c',cleanup,instance],check=True,capture_output=True)
 result['installedFixtureUnitRemoved']=not Path('/run/systemd/system',instance+'.service').exists()
 result['protectedFixtureRuntimeRemoved']=subprocess.run(['sudo','-n','test','!','-e','/srv/'+instance],capture_output=True).returncode==0
 shutil.rmtree(run/'data',ignore_errors=True);shutil.rmtree(run/'config',ignore_errors=True)
 result['allChildrenReaped']=all(child.poll() is not None for child in children);result['disposableCaKeysRemoved']=not (run/'data').exists();result['sha256']={'scripts/managed-ingress-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'ingress_service/configuration.py':hashlib.sha256((ROOT/'ingress_service/configuration.py').read_bytes()).hexdigest(),'scripts/activate-shared-ingress.py':hashlib.sha256((ROOT/'scripts/activate-shared-ingress.py').read_bytes()).hexdigest()}
 if not result['allChildrenReaped'] or not result['disposableCaKeysRemoved'] or worker is not None and worker.is_alive():result['status']='FAIL'
 (checks/'managed-ingress-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if result['status']!='PASS':raise SystemExit(1)
