#!/usr/bin/env python3
"""Real generated beta Caddy block: exact candidate routes and gate, loopback only."""
import copy,hashlib,json,os,shutil,subprocess,sys,tempfile,threading,time,tomllib,urllib.error,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'ops'));import common
CADDY=os.environ.get('CODI_CADDY','/tmp/codi-microduck-hosting-evidence/caddy');CAND=Path(os.environ.get('CODI_OPFS_CANDIDATE','/tmp/codi-beta-opfs-transition-candidate'));BASE=Path(os.environ.get('CODI_BETA_BASELINE','/tmp/codi-beta-opfs-review-fixture/codi-beta-opfs-test-baseline-2'));PORT=19994;ADMIN=19995
sha=lambda b:hashlib.sha256(b).hexdigest();raw=(CAND/'manifest.json').read_bytes();assert sha(raw)=='3ad04c48e60caa559e7b4c56ff624b50a23c093f0dacbc339ca8df147fd009bc';manifest=json.loads(raw);table=json.loads((root/'OPFS-ROUTE-TABLE.json').read_text());assert len(table['routes'])==84
assert {x['path']:x['sha256'] for x in table['routes'] if x['target'].startswith(('assets/','storage/'))}==common.OPFS_PUBLIC_FILES
for item in table['routes']:
 b=(CAND/item['target']).read_bytes();assert sha(b)==item['sha256']==manifest['files'][item['target']]['sha256']
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  b=('fixture-backend:'+self.path).encode();self.send_response(200);self.end_headers();self.wfile.write(b)
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),H);th=threading.Thread(target=server.serve_forever,daemon=True);th.start();backend=server.server_port
try:
 with tempfile.TemporaryDirectory(prefix='opfs-exact-routes-') as tmp:
  t=Path(tmp);oldrecords=tomllib.loads((root/'ops/sites_live.toml').read_text())['codi_beta_retained_overlays']
  for i,record in enumerate(oldrecords):
   package,desktop,mirror=record.split(':');d=t/package;(d/'assets/desktop').mkdir(parents=True);(d/'storage/browser').mkdir(parents=True)
   desktop_src=BASE/'guarded-loader.js' if i==1 else Path('/tmp/codi-old-loader-0b9e.js');mirror_src=BASE/'storage/browser'/('mirror.'+mirror+'.mjs') if i==1 else Path('/tmp/codi-old-mirror-2044.mjs')
   assert sha(desktop_src.read_bytes())==desktop and sha(mirror_src.read_bytes())==mirror
   shutil.copyfile(desktop_src,d/'assets/desktop'/('desktop-apps.'+desktop+'.js'));shutil.copyfile(mirror_src,d/'storage/browser'/('mirror.'+mirror+'.mjs'))
  data=tomllib.loads((root/'ops/sites_live.toml').read_text());data['codi_beta_opfs']=table['candidate'];cfg=t/'Caddyfile'
  def render(maintenance):
   x=copy.deepcopy(data);x['codi_beta_maintenance']=maintenance;s=common.caddy(x,'production');a=s.index('beta.ksu.codes {');b=s.index('\n}\n',a)+3;block=s[a:b].replace('beta.ksu.codes {','http://127.0.0.1:'+str(PORT)+' {',1).replace('\timport site_defaults\n','').replace(table['root'],str(CAND)).replace('/srv/codi-connected/simplified/'+data['codi_beta_simplified'],str(BASE))
   for record in oldrecords:
    package=record.split(':')[0];block=block.replace('/srv/codi-connected/beta-overlays/'+package,str(t/package))
   for port in (28118,28132,28140):block=block.replace('127.0.0.1:'+str(port),'127.0.0.1:'+str(backend))
   cfg.write_text('{\n admin 127.0.0.1:'+str(ADMIN)+'\n}\n'+block+'\n')
  render(False);proc=subprocess.Popen([CADDY,'run','--config',str(cfg),'--adapter','caddyfile'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  def get(path,method='GET'):
   try:
    with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}'+path,method=method),timeout=5) as r:return r.status,r.read(),r.headers
   except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
  try:
   for _ in range(100):
    if proc.poll() is not None:raise RuntimeError(proc.stderr.read().decode())
    try:get('/');break
    except OSError:time.sleep(.05)
   for item in table['routes']:
    path=item['path']+('?simplified=1' if item['query']=='simplified=1 exactly' else '')
    code,body,headers=get(path);assert code==200 and sha(body)==item['sha256'],path
    status,body,_=get(path,'HEAD');assert status==200 and not body,path
   for name in ('app','desktop-apps'):
    for suffix in ('','?not=simplified','?simplified=1&extra=1'):
     status,body,_=get('/'+name+'.js'+suffix);assert status==200 and body==(BASE/(name+'.js')).read_bytes(),name+suffix
   for record in oldrecords:
    package,desktop,mirror=record.split(':')
    for path,expected in (('/assets/desktop/desktop-apps.'+desktop+'.js',desktop),('/storage/browser/mirror.'+mirror+'.mjs',mirror)):
     status,body,_=get(path);assert status==200 and sha(body)==expected,path
   for path in ('/storage/browser/releases/0ea94092ebb6cd6120433c49cd4fe1284842e334b6313dc9945ed3d6cf87011a/unknown.mjs','/assets/desktop/apps/files/12ee27eeb5c462e43ff9b2d5f59d83f4c5687812406c1e41d8414bd5a6122244/unknown.js','/shell/app.js'):
    assert get(path)[0]==404,path
   for path in ('/api/v1/auth','/config.json','/gateway/use'):
    status,body,_=get(path);assert status==200 and body==('fixture-backend:'+path).encode(),path
   assert get('/browser-sources')[0]==404
   assert get(table['routes'][0]['path'],'POST')[0]==405
   status,_,headers=get('/assets/desktop/offline-worker.js');assert headers.get('Service-Worker-Allowed')=='/'
   render(True);subprocess.run([CADDY,'reload','--address',f'127.0.0.1:{ADMIN}','--config',str(cfg),'--adapter','caddyfile'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   for item in table['routes']:
    path=item['path']+('?simplified=1' if item['query']=='simplified=1 exactly' else '')
    assert get(path)[0]==503,('gate leaked',path)
   for path in ('/api/v1/auth','/config.json','/gateway/use'):assert get(path)[0]==503,path
   for record in oldrecords:
    _,desktop,mirror=record.split(':')
    for path in ('/assets/desktop/desktop-apps.'+desktop+'.js','/storage/browser/mirror.'+mirror+'.mjs'):assert get(path)[0]==503,path
   print('PASS generated Caddy exact 84 GET/HEAD routes, both old asset pairs, bare/query distinction, service routing, unknown denial and maintenance gate')
  finally:proc.terminate();proc.wait(timeout=10)
finally:server.shutdown();server.server_close();th.join(2)
