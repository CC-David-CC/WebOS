#!/usr/bin/env python3
"""Guarded one-rule hosting fix: canonicalize /hidden to /hidden/."""
import argparse,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,socket,ssl,subprocess,sys,tempfile,types
Path=pathlib.Path;ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'));import common;import webctl as ctl
ctl.root_required();apply=json.load(sys.stdin)['apply'];source=ROOT/'ops/common.py';manifest=ROOT/'sites.toml'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(argv,timeout=60):return subprocess.run(list(map(str,argv)),check=True,capture_output=True,text=True,timeout=timeout).stdout
def request(path,method='GET'):
 connection=http.client.HTTPSConnection('ksu.codes',timeout=10);connection.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  connection.request(method,path);response=connection.getresponse();body=response.read(524289);assert len(body)<=524288;return response.status,dict(response.getheaders()),body
 finally:connection.close()
def pids():return {role:run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','--value']).strip() for role in ['issuer','steward','guest']}
def reload_generator():
 importlib.invalidate_caches();importlib.reload(common)
 for name in ['caddy','load','dump','validate','unit']:setattr(ctl,name,getattr(common,name))
with (ROOT/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);old=source.read_bytes();manifest_raw=manifest.read_bytes()
 assert digest(old)=='58c7c2ffdd8ab490c022889bfe66b4b7c02f32158f67d46bc082f1a996b0b414' and digest(manifest_raw)=='1e6183699af82d0a019e112f550b70744928b3fb59d3151fe1e80a3b7cad836c'
 assert not source.is_symlink() and ctl.current_mode()=='production'
 needle=r"'\t\tredir /hidden/ 308'";replacement=r"'\t\tredir * /hidden/ 308'";assert old.decode().count(needle)==1
 candidate=old.decode().replace(needle,replacement).encode();reviewed=types.ModuleType('reviewed_hidden_redirect');reviewed.__file__=str(source);exec(compile(candidate,str(source),'exec'),reviewed.__dict__)
 data=ctl.load();prior={mode:ctl.caddy(data,mode) for mode in ['prepare','production']};assert Path('/etc/caddy/Caddyfile').read_text()==prior['production']
 for mode in prior:
  assert reviewed.caddy(data,mode)==prior[mode].replace('\t\tredir /hidden/ 308','\t\tredir * /hidden/ 308')
 for site in data['sites']:assert common.unit(site)==reviewed.unit(site)
 fd,name=tempfile.mkstemp(prefix='.codi-hidden-redirect-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:
  ctl.write(name,reviewed.caddy(data,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(name)
  adapted=json.loads(run(['/usr/bin/caddy','adapt','--config',name,'--adapter','caddyfile']))
  found=[]
  def visit(value):
   if isinstance(value,dict):
    if value.get('match')==[{'path':['/hidden']}]:found.append(value)
    for item in value.values():visit(item)
   elif isinstance(value,list):
    for item in value:visit(item)
  visit(adapted);assert len(found)==1
  inner=found[0]['handle'][0]['routes'];assert len(inner)==1 and not inner[0].get('match')
  handler=inner[0]['handle'][0];assert handler['handler']=='static_response' and handler['status_code']==308 and handler['headers']['Location']==['/hidden/']
 finally:Path(name).unlink()
 if not apply:print(json.dumps({'status':'PASS','scope':'Actual Caddy validation/adaptation proves an unconditional 308 inside exact /hidden handler; no live change'}));raise SystemExit(0)
 native=Path('/etc/codi-connected/ksu/managed.json');native_raw=native.read_bytes();before=pids();assert all(int(pid)>0 for pid in before.values())
 website=Path('/srv/webapps/ksu.codes/current').resolve();desktop={name:digest((website/'public/desktop'/name).read_bytes()) for name in ['release.json','app.js','config.json']};hidden=request('/hidden/config.json')[2]
 info=source.stat();backup=ctl.snapshot(source);changed=False
 try:
  changed=True;ctl.write(source,candidate,info.st_mode&0o777,info.st_uid,info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  entries={}
  for method in ['GET','HEAD']:
   status,headers,body=request('/hidden',method);assert status==308 and headers['Location']=='/hidden/';entries[method]={'status':status,'location':headers['Location']}
  status,headers,body=request('/hidden/');assert status==200 and b'CodiServer' in body and b'app.js' in body
  assert request('/hidden/config.json')[2]==hidden
  for name,expected in desktop.items():assert digest(request('/desktop/'+name)[2])==expected
  smoke=ROOT/'reports/private/codi-hidden-redirect-20261023.json';run(['/usr/bin/python3',ROOT/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
  assert pids()==before and native.read_bytes()==native_raw and manifest.read_bytes()==manifest_raw and Path('/srv/webapps/ksu.codes/current').resolve()==website
  report={'status':'PASS','scope':'Managed one-rule canonical-path fix; default-trusted HTTPS GET/HEAD, unchanged existing preview/prototype and eight-site smoke','entries':entries,'generatorSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest_raw),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'sourceBackup':str(backup),'nativePidsUnchanged':before,'nativeConfigUnchanged':True,'desktopSHA256':desktop,'eightSiteSmoke':str(smoke),'publicTurnConfigured':False,'routerFirewallAndPortsChanged':False}
  target=Path('/srv/codi-connected/hidden-redirect-fix-result.json');fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as output:json.dump(report,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
  print(json.dumps(report))
 except BaseException:
  if changed:ctl.write(source,old,info.st_mode&0o777,info.st_uid,info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  raise
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');a=p.parse_args()
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'apply':a.apply}),capture_output=True,text=True,timeout=300)
 if child.returncode:raise SystemExit(child.stderr or child.stdout)
 report=json.loads(child.stdout.strip().splitlines()[-1]);(ROOT/'.build/checks'/('hidden-redirect-fix-result.json' if a.apply else 'hidden-redirect-validation-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
