#!/usr/bin/env python3
"""Install reviewed frontend assets and activate only their managed hidden route."""
import argparse,json,re,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import copy,fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,shutil,socket,ssl,stat,subprocess,sys,tempfile,types
Path=pathlib.Path;ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'));import common;import webctl as ctl
ctl.root_required();inputs=json.load(sys.stdin);pins=inputs['pins'];candidate=inputs['source'].encode();proposed_raw=inputs['manifest'].encode();source=ROOT/'ops/common.py';manifest=ROOT/'sites.toml'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(argv,timeout=60):return subprocess.run(list(map(str,argv)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
def request(path):
 connection=http.client.HTTPSConnection('ksu.codes',timeout=10);connection.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  connection.request('GET',path);response=connection.getresponse();body=response.read(4194305);assert len(body)<=4194304;return response.status,dict(response.getheaders()),body
 finally:connection.close()
def pids():return {role:run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','--value']) for role in ['issuer','steward','guest']}
def reload_generator():
 importlib.invalidate_caches();importlib.reload(common)
 for name in ['caddy','load','dump','validate','unit']:setattr(ctl,name,getattr(common,name))
assert digest(candidate)==pins['candidateGeneratorSHA256'] and digest(proposed_raw)==pins['candidateManifestSHA256']
key=pins['frontendManifestSHA256'];assert len(key)==64 and all(c in '0123456789abcdef' for c in key)
with (ROOT/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);old_source=source.read_bytes();old_manifest=manifest.read_bytes()
 assert digest(old_source)==pins['originalGeneratorSHA256'] and digest(old_manifest)==pins['originalManifestSHA256']
 assert not source.is_symlink() and not manifest.is_symlink() and ctl.current_mode()=='production'
 data=ctl.load();prior={mode:ctl.caddy(data,mode) for mode in ['prepare','production']};assert Path('/etc/caddy/Caddyfile').read_text()==prior['production']
 reviewed=types.ModuleType('reviewed_touch');reviewed.__file__=str(source);exec(compile(candidate,str(source),'exec'),reviewed.__dict__)
 proposed=reviewed.tomllib.loads(proposed_raw.decode());reviewed.validate(proposed);expected=copy.deepcopy(data);next(s for s in expected['sites'] if s['domain']=='ksu.codes')['codi_frontend']=key;assert proposed==expected
 extra='\t\t\t@codi_frontend path /app.js /style.css /terminal.js /assets/terminal-initramfs.cpio.gz /desktop-apps.js /networking.js\n\t\t\thandle @codi_frontend {\n\t\t\t\troot * /srv/codi-connected/frontends/'+key+'\n\t\t\t\tfile_server\n\t\t\t}\n'
 old_paths='/app.js /style.css /terminal.js';four_paths=old_paths+' /assets/terminal-initramfs.cpio.gz';new_paths=four_paths+' /desktop-apps.js /networking.js';previous_paths=next(paths for paths in [new_paths,four_paths,old_paths] if '@codi_frontend path '+paths in old_source.decode())
 for mode in prior:
  assert reviewed.caddy(data,mode)==prior[mode].replace('@codi_frontend path '+previous_paths,'@codi_frontend path '+new_paths);rendered=reviewed.caddy(proposed,mode);previous=next(s for s in data['sites'] if s['domain']=='ksu.codes').get('codi_frontend');baseline=prior[mode].replace(extra.replace(key,previous).replace(new_paths,previous_paths),'') if previous else prior[mode];assert rendered.count(extra)==1 and rendered.replace(extra,'')==baseline
 for site in data['sites']:assert common.unit(site)==reviewed.unit(site)
 fd,name=tempfile.mkstemp(prefix='.codi-touch-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:ctl.write(name,reviewed.caddy(proposed,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(name)
 finally:Path(name).unlink()
 if not inputs['apply']:print(json.dumps({'status':'PASS','scope':'Actual Caddy syntax and six-asset-only routing invariants; no live change'}));raise SystemExit(0)
 checkout=ROOT/'sites/ksu.codes';commit=inputs['commit'];assert len(commit)==40
 assert run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==commit
 assert not run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
 frontend=checkout/'tools/codiserver/frontends'/key
 assert digest((frontend/'frontend.json').read_bytes())==key
 metadata=json.loads((frontend/'frontend.json').read_text());assert metadata=={'version':'codi-frontend-assets/3','files':pins['frontendFiles']} and set(metadata['files'])=={'app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz','desktop-apps.js','networking.js'}
 def exact_tree(folder,root_owned=False):
  assert not folder.is_symlink() and set(str(p.relative_to(folder)) for p in folder.rglob('*'))=={'frontend.json','assets',*metadata['files']}
  if root_owned:assert folder.stat().st_uid==folder.stat().st_gid==0 and stat.S_IMODE(folder.stat().st_mode)==0o755
  for file in folder.rglob('*'):
   info=file.lstat();assert not stat.S_ISLNK(info.st_mode)
   if file.is_dir():
    assert file.name=='assets'
    if root_owned:assert info.st_uid==info.st_gid==0 and stat.S_IMODE(info.st_mode)==0o755
    continue
   assert stat.S_ISREG(info.st_mode) and info.st_nlink==1
   if root_owned:assert info.st_uid==info.st_gid==0 and stat.S_IMODE(info.st_mode)==0o644
   if file.name=='frontend.json':assert digest(file.read_bytes())==key
   else:assert metadata['files'][str(file.relative_to(folder))]=={'bytes':info.st_size,'sha256':digest(file.read_bytes())}
 exact_tree(frontend)
 destination=Path('/srv/codi-connected/frontends')/key;parent=destination.parent
 for directory in [*reversed(parent.parents),parent]:
  if not directory.exists():directory.mkdir(mode=0o755)
  info=directory.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
 if not destination.exists():
  shutil.copytree(frontend,destination)
  for file in [destination,*destination.rglob('*')]:os.chown(file,0,0);file.chmod(0o755 if file.is_dir() else 0o644)
 exact_tree(destination,True)
 native=Path('/etc/codi-connected/ksu/managed.json');native_raw=native.read_bytes();before=pids();assert all(int(pid)>0 for pid in before.values())
 website=Path('/srv/webapps/ksu.codes/current').resolve();assert website.is_relative_to(Path('/srv/webapps/ksu.codes/releases')) and website.stat().st_uid==0 and not website.stat().st_mode&0o022
 desktop={name:digest((website/'public/desktop'/name).read_bytes()) for name in ['release.json','app.js','config.json']}
 assert desktop=={'release.json':'d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9','app.js':'2abb154d558cbc44149cfa46ddcc23c9d4843f822b8a44c5d392cd4bd2f88602','config.json':'5ec30b79a21a07911315ddd9714fba560fc3451004d51942ee53f36c0e6effad'}
 status,headers,index=request('/hidden/');assert status==200 and 'codi_guest_relay=' in headers.get('Set-Cookie','');cookie=headers['Set-Cookie'].split(';',1)[0]
 public_config=json.loads(request('/hidden/config.json')[2]);identity=public_config['identity'];limits=public_config['guestNetwork'];assert identity['mode']=='server'
 receipt=Path('/srv/codi-connected')/('frontend-'+key+'-activation-result.json');assert not receipt.exists()
 source_info=source.stat();manifest_info=manifest.stat();backups={'source':str(ctl.snapshot(source)),'manifest':str(ctl.snapshot(manifest))};changed=False
 try:
  changed=True;ctl.write(source,candidate,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,proposed_raw,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  for name,record in metadata['files'].items():
   status,headers,body=request('/hidden/'+name);assert status==200 and digest(body)==record['sha256'] and headers.get('Cache-Control')=='no-store'
  status,headers,body=request('/hidden/');assert status==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie
  status,headers,body=request('/hidden');assert status==308 and headers['Location']=='/hidden/'
  current=json.loads(request('/hidden/config.json')[2]);assert current['identity']==identity and current['guestNetwork']==limits
  for name,expected_digest in desktop.items():assert digest(request('/desktop/'+name)[2])==expected_digest
  for name in ['frontend.json','issuer.pem','scripts/manage-services.py']:assert request('/hidden/'+name)[0]==404
  smoke=ROOT/'reports/private/codi-touch-frontend-20261023.json';run(['/usr/bin/python3',ROOT/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
  assert native.read_bytes()==native_raw and pids()==before and Path('/srv/webapps/ksu.codes/current').resolve()==website;exact_tree(destination,True)
  report={'status':'PASS','scope':'Frontend and independent-shell guest assets activated only under hidden; existing index/session cookie, native services/state, prototype and all managed websites preserved. Browser touch verification separate.','sourceCommit':commit,'frontendManifestSHA256':key,'frontendFiles':metadata['files'],'installedFrontend':str(destination),'generatorSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest.read_bytes()),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'backups':backups,'beforeGeneratorSHA256':digest(old_source),'beforeManifestSHA256':digest(old_manifest),'nativePidsUnchanged':before,'nativeConfigUnchanged':True,'indexAndGuestCookieUnchanged':True,'bootstrapIndexSHA256':digest(index),'desktopSHA256':desktop,'allSiteSmoke':str(smoke),'siteDomains':sorted(s['domain'] for s in data['sites'] if s['enabled']),'publicTurnConfigured':bool(data.get('codi_shared_ingress')),'routerFirewallAndPortsChanged':False}
  file=receipt;fd=os.open(file,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as output:json.dump(report,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
  print(json.dumps(report))
 except BaseException:
  if changed:
   ctl.write(source,old_source,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,old_manifest,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  raise
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate-dir',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--commit',default='');a=p.parse_args()
 if a.apply and not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('Apply requires the reviewed source commit')
 folder=a.candidate_dir;inputs={'pins':json.loads((folder/'candidate-result.json').read_text()),'source':(folder/'common.touch.py').read_text(),'manifest':(folder/'sites.touch.toml').read_text(),'apply':a.apply,'commit':a.commit}
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(REMOTE)],input=json.dumps(inputs),capture_output=True,text=True,timeout=360)
 if child.returncode:raise SystemExit(child.stderr or child.stdout)
 report=json.loads(child.stdout.strip().splitlines()[-1]);(ROOT/'.build/checks'/('touch-frontend-activation-result.json' if a.apply else 'touch-hosting-validation-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
