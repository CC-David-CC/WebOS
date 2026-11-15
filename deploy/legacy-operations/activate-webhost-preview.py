#!/usr/bin/env python3
"""Validate/apply the reviewed KSU preview under the existing hosting controller."""
import argparse,hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import copy,fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,socket,ssl,subprocess,sys,tempfile,types
Path=pathlib.Path;ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'));import common;import webctl as ctl
ctl.root_required();inputs=json.load(sys.stdin);pins=inputs['pins'];candidate=inputs['source'].encode();proposed_raw=inputs['manifest'].encode();source=ROOT/'ops/common.py';manifest=ROOT/'sites.toml'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.run([str(x) for x in args],check=True,capture_output=True,text=True,timeout=timeout)
def local_json(port,path='/config.json'):
 connection=http.client.HTTPConnection('127.0.0.1',port,timeout=5)
 try:
  connection.request('GET',path,headers={'Host':'ksu.codes'});response=connection.getresponse();body=response.read(65537);assert response.status==200 and len(body)<=65536;return json.loads(body)
 finally:connection.close()
def https(path):
 connection=http.client.HTTPSConnection('ksu.codes',timeout=10);connection.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  connection.request('GET',path);response=connection.getresponse();body=response.read(524289);assert len(body)<=524288;return response.status,body
 finally:connection.close()
def reload_generator():
 importlib.invalidate_caches();importlib.reload(common)
 for name in ['caddy','load','dump','validate','unit']:setattr(ctl,name,getattr(common,name))
assert digest(candidate)==pins['candidateGeneratorSHA256'] and digest(proposed_raw)==pins['candidateManifestSHA256']
with (ROOT/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old_source=source.read_bytes();old_manifest=manifest.read_bytes();assert digest(old_source)==pins['originalGeneratorSHA256'] and digest(old_manifest)==pins['originalManifestSHA256']
 assert not source.is_symlink() and not manifest.is_symlink() and ctl.current_mode()=='production'
 data=ctl.load();prior={mode:ctl.caddy(data,mode) for mode in ['prepare','production']};assert Path('/etc/caddy/Caddyfile').read_text()==prior['production']
 reviewed=types.ModuleType('reviewed_preview');reviewed.__file__=str(source);exec(compile(candidate,str(source),'exec'),reviewed.__dict__)
 proposed=reviewed.load.__globals__['tomllib'].loads(proposed_raw.decode());reviewed.validate(proposed)
 expected=copy.deepcopy(data);next(site for site in expected['sites'] if site['domain']=='ksu.codes')['codi_preview']=True;assert proposed==expected
 for mode in prior:
  assert reviewed.caddy(data,mode)==prior[mode]
  rendered=reviewed.caddy(proposed,mode);assert rendered.count('handle_path /hidden/*')==1
 for site in data['sites']:assert common.unit(site)==reviewed.unit(site)
 fd,temporary=tempfile.mkstemp(prefix='.codi-preview-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:
  ctl.write(temporary,reviewed.caddy(proposed,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False)
  ctl.caddy_validate(temporary)
 finally:Path(temporary).unlink()
 if not inputs['apply']:
  print(json.dumps({'status':'PASS','scope':'Actual webhost Caddy validation and source/manifest/scope checks; no activation','candidateGeneratorSHA256':digest(candidate),'candidateManifestSHA256':digest(proposed_raw),'publicPreviewEnabled':False}));raise SystemExit(0)
 config_path=Path('/etc/codi-connected/ksu/managed.json');config_raw=config_path.read_bytes();config=json.loads(config_raw)
 assert config['release']=='/srv/codi-connected/releases/f2fbd4d' and config['manifestSHA256']=='e6bd7e6df07544c58ce57efe3672f18df793dd5fbea381d05d89f2953f0baace'
 assert config['origin']=='https://ksu.codes' and config['basePath']=='/hidden' and config['ports']=={'issuer':8118,'steward':8119,'guest':8132}
 assert not (config_path.parent/'maintenance.json').exists()
 issuer=local_json(8118);assert issuer['identity']['mode']=='server' and issuer['identity']['authorityClass']=='development' and issuer['identity']['apiBase']=='/hidden/api/v1'
 assert run(['systemctl','show','codi-ksu-hidden-guest.service','-p','MainPID','--value']).stdout.strip()=='0'
 import grp
 assert grp.getgrnam('codi-guest').gr_gid==1001
 ping_path=Path('/proc/sys/net/ipv4/ping_group_range');ping_before=ping_path.read_text();forward=Path('/proc/sys/net/ipv4/ip_forward').read_text();assert ping_before.split()==['1000','1000'] and forward.strip()=='0'
 policy=Path('/etc/sysctl.d/90-codi-guest-preview.conf');assert not policy.exists() and not policy.is_symlink()
 website=Path('/srv/webapps/ksu.codes/current').resolve();assert str(website)=='/srv/webapps/ksu.codes/releases/20261021T125622370238Z-279f978f'
 desktop={name:digest((website/'public/desktop'/name).read_bytes()) for name in ['release.json','app.js','config.json']}
 source_info=source.stat();manifest_info=manifest.stat();backups={'source':str(ctl.snapshot(source)),'manifest':str(ctl.snapshot(manifest))};held=None;changed=False
 try:
  ctl.write(policy,'# Bounded CodiServer preview: administrator and isolated guest group only.\nnet.ipv4.ping_group_range = 1000 1001\n',0o644,0,0,False)
  run(['sysctl','-q','-w','net.ipv4.ping_group_range=1000 1001'])
  run([config['python'],'-B',Path(config['release'])/'scripts/manage-services.py','start','--config',config_path,'--roles','guest'],180)
  held=open('/run/codi-service-operators/codi-ksu-hidden.lock','r+b');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);assert config_path.read_bytes()==config_raw
  guest=local_json(8132);assert guest['identity']==issuer['identity'] and guest['guestNetwork']['egress']=='relay-host'
  limits=guest['guestNetwork']['previewPolicy'];assert limits['version']=='bounded-preview/1' and limits['tcpPorts']==[80,443] and limits['sessionBytes']==67108864 and limits['serviceBytes']==268435456
  changed=True;ctl.write(source,candidate,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,proposed_raw,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  status,body=https('/hidden/config.json');assert status==200;public=json.loads(body);assert public['identity']==issuer['identity'] and public['guestNetwork']['previewPolicy']==limits
  status,body=https('/hidden/');assert status==200 and b'<html' in body.lower()
  for name,expected_digest in desktop.items():
   status,body=https('/desktop/'+name);assert status==200 and digest(body)==expected_digest
  for name in ['issuer.pem','accounts.sqlite3','scripts/manage-services.py','origin_service/release.py']:assert https('/hidden/'+name)[0]==404
  smoke=run(['/usr/bin/python3',ROOT/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',ROOT/'reports/private/codi-hidden-activation-20261023.json'],120)
  assert Path('/srv/webapps/ksu.codes/current').resolve()==website and Path('/proc/sys/net/ipv4/ip_forward').read_text()==forward
  report={'status':'PASS','scope':'Managed hidden preview activation and trusted server-loopback HTTPS; external browser/WAN verification remains separate','publicPreviewEnabled':True,'nativeRelease':config['release'],'nativeManifestSHA256':config['manifestSHA256'],'generatorSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest.read_bytes()),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'backups':backups,'desktopSHA256':desktop,'currentWebsiteUnchanged':str(website),'guestPreviewPolicy':limits,'pingGroupRange':ping_path.read_text().split(),'forwardingUnchanged':True,'normalUnitsRemainDisabledForBoot':True,'eightSiteSmoke':smoke.stdout.strip().splitlines()}
  for role in ['issuer','steward','guest']:assert subprocess.run(['systemctl','is-enabled','codi-ksu-hidden-'+role+'.service'],capture_output=True,text=True).stdout.strip()=='disabled'
  file=Path('/srv/codi-connected/hidden-preview-activation-result.json');fd=os.open(file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as out:json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
  print(json.dumps(report))
 except BaseException:
  try:
   if changed:
    ctl.write(source,old_source,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,old_manifest,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  finally:
   try:run(['systemctl','stop','codi-ksu-hidden-guest.service'])
   finally:
    run(['sysctl','-q','-w','net.ipv4.ping_group_range='+' '.join(ping_before.split())]);policy.unlink(missing_ok=True)
  raise
 finally:
  if held is not None:held.close()
'''
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--candidate-dir',type=Path,required=True);parser.add_argument('--apply',action='store_true');a=parser.parse_args();folder=a.candidate_dir;pins=json.loads((folder/'candidate-result.json').read_text());payload={'pins':pins,'source':(folder/'common.preview.py').read_text(),'manifest':(folder/'sites.preview.toml').read_text(),'apply':a.apply}
 process=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(REMOTE)],input=json.dumps(payload),capture_output=True,text=True,timeout=600)
 if process.returncode:raise SystemExit(process.stderr or process.stdout)
 # Caddy's validator may emit a human-readable success line before the receipt.
 report=json.loads(process.stdout.strip().splitlines()[-1]);name='preview-webhost-activation-result.json' if a.apply else 'preview-webhost-proxy-validation-result.json';(ROOT/'.build/checks'/name).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
