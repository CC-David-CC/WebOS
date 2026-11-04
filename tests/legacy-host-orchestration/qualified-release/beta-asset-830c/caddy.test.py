#!/usr/bin/env python3
"""Actual generated beta routes through disposable loopback Caddy only."""
import copy,hashlib,importlib.util,json,os,subprocess,sys,tempfile,threading,time,tomllib,urllib.error,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
here=Path(__file__).resolve().parent;ops=here.parents[1]/'beta-isolated-hosting/ops';sys.path.insert(0,str(ops))
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
build=load('builder',here/'build-generator.py');old=Path(sys.argv[1]);new=Path(sys.argv[2]);base=Path(sys.argv[3]);caddy=Path(sys.argv[4]);port=int(os.environ.get('CODI_ASSET_PORT','19891'));admin=int(os.environ.get('CODI_ASSET_ADMIN','19892'));sha=lambda b:hashlib.sha256(b).hexdigest()
class Backend(BaseHTTPRequestHandler):
 def do_GET(self):
  b=('fixture:'+self.path).encode();self.send_response(200);self.end_headers();self.wfile.write(b)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Backend);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 with tempfile.TemporaryDirectory(prefix='830c-caddy-') as d:
  tmp=Path(d);build.build(old,new,tmp/'generator');gen=load('asset_common',tmp/'generator/common.py');manifest=json.loads((new/'manifest.json').read_bytes());oldmanifest=json.loads((old/'manifest.json').read_bytes());routes=gen.OPFS_NEW_PUBLIC_FILES
  data=tomllib.loads((ops/'sites_live.toml').read_text());data['codi_beta_maintenance']=False;data['codi_beta_opfs']=build.OLD
  # Preserve the two old content-addressed overlays in their exact tested form.
  overlays=(Path('/tmp/codi-beta-overlay-fixture'),Path('/tmp/codi-beta-overlay-final-fixture'))
  for record,source in zip(data['codi_beta_retained_overlays'],overlays,strict=True):
   package,_,_=record.split(':');assert sha((source/'manifest.json').read_bytes())==package
  cfg=tmp/'Caddyfile'
  def render(selector,gate=False):
   x=copy.deepcopy(data);x['codi_beta_maintenance']=gate
   if gate:x.pop('codi_beta_opfs')
   else:x['codi_beta_opfs']=selector
   s=gen.caddy(x,'production');a=s.index('beta.ksu.codes {');b=s.index('\n}\n',a)+3;block=s[a:b].replace('beta.ksu.codes {','http://127.0.0.1:'+str(port)+' {',1).replace('\timport site_defaults\n','')
   block=block.replace('/srv/data/codi-beta-opfs/'+build.OLD,str(old)).replace('/srv/data/codi-beta-opfs/'+build.NEW,str(new)).replace('/srv/codi-connected/simplified/'+data['codi_beta_simplified'],str(base))
   for record,source in zip(data['codi_beta_retained_overlays'],overlays,strict=True):block=block.replace('/srv/codi-connected/beta-overlays/'+record.split(':')[0],str(source))
   for p in (28118,28132,28140):block=block.replace('127.0.0.1:'+str(p),'127.0.0.1:'+str(server.server_port))
   cfg.write_text('{\n admin 127.0.0.1:'+str(admin)+'\n}\n'+block+'\n')
  def get(path,method='GET'):
   try:
    with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+path,method=method),timeout=5) as r:return r.status,r.read()
   except urllib.error.HTTPError as e:return e.code,e.read()
  def reload():subprocess.run([str(caddy),'reload','--address','127.0.0.1:'+str(admin),'--config',str(cfg),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  render(build.OLD);proc=subprocess.Popen([str(caddy),'run','--config',str(cfg),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for _ in range(100):
    if proc.poll() is not None:raise RuntimeError(proc.stderr.read().decode())
    try:get('/');break
    except OSError:time.sleep(.05)
   added=[p for p in routes if p[1:] not in oldmanifest['files']]
   for path in added:assert get(path)[0]==404,('new asset exposed before transition',path)
   render(build.NEW);reload()
   for path,want in routes.items():
    status,body=get(path);assert status==200 and sha(body)==want,path
    assert get(path,'HEAD')==(200,b''),path
   for path,target in (('/app.js?simplified=1','shell/app.js'),('/desktop-apps.js?simplified=1','shell/desktop-apps.js')):
    status,body=get(path);assert status==200 and sha(body)==manifest['files'][target]['sha256'],path
   for name in ('app','desktop-apps'):
    for suffix in ('','?not=simplified','?simplified=1&extra=1'):
     status,body=get('/'+name+'.js'+suffix);assert status==200 and body==(base/(name+'.js')).read_bytes(),name+suffix
   for record in data['codi_beta_retained_overlays']:
    package,desktop,mirror=record.split(':')
    for path,want in (('/assets/desktop/desktop-apps.'+desktop+'.js',desktop),('/storage/browser/mirror.'+mirror+'.mjs',mirror)):
     status,body=get(path);assert status==200 and sha(body)==want,path
   for path in ('/api/v1/auth','/config.json','/gateway/use'):assert get(path)==(200,('fixture:'+path).encode())
   assert get(next(iter(routes)),'POST')[0]==405
   for path in ('/storage/browser/releases/3daf09a753455be1dc07ce183097b6535a999d2cc2124f9d0e6df25c7180be3a/unknown.mjs','/assets/desktop/apps/files/b7e943c563ea83ad91988e595e1afcada8f31d71eda01e9915d104f32774d7b7/unknown.js','/shell/app.js'):assert get(path)[0]==404,path
   render(build.NEW,True);reload()
   for path in list(routes)+['/app.js?simplified=1','/desktop-apps.js?simplified=1','/api/v1/auth','/config.json','/gateway/use']:assert get(path)[0]==503,('gate leaked',path)
   print('PASS exact generated old/new/gate real Caddy routes, GET/HEAD, retained overlays and backend paths')
  finally:proc.terminate();proc.wait(timeout=10)
finally:server.shutdown();server.server_close();thread.join(2)
