#!/usr/bin/env python3
"""Activate reviewed immutable speech assets under hidden, preserving all roles."""
import argparse,json,re,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import copy,fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,shutil,socket,ssl,stat,subprocess,sys,tempfile,types
Path=pathlib.Path;ROOT=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(ROOT/'ops'));import common;import webctl as ctl
ctl.root_required();inputs=json.load(sys.stdin);pins=inputs['pins'];candidate=inputs['source'].encode();proposed_raw=inputs['manifest'].encode();source=ROOT/'ops/common.py';manifest=ROOT/'sites.toml'
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(argv,timeout=60):return subprocess.run(list(map(str,argv)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
def connection():
 result=http.client.HTTPSConnection('ksu.codes',timeout=30);result.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes');return result
def request(path):
 client=connection()
 try:
  client.request('GET',path);response=client.getresponse();raw=response.read(524289);assert len(raw)<=524288;return response.status,dict(response.getheaders()),raw
 finally:client.close()
def asset(path,record):
 client=connection()
 try:
  client.request('GET',path);response=client.getresponse();assert response.status==200 and response.getheader('Cache-Control')=='no-store';h=hashlib.sha256();total=0
  while True:
   chunk=response.read(65536)
   if not chunk:break
   h.update(chunk);total+=len(chunk);assert total<=record['bytes']
  assert {'bytes':total,'sha256':h.hexdigest()}==record
 finally:client.close()
def pids():return {role:run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','--value']) for role in ['issuer','steward','guest']}
def reload_generator():
 importlib.invalidate_caches();importlib.reload(common)
 for name in ['caddy','load','dump','validate','unit']:setattr(ctl,name,getattr(common,name))
def route(key):return '\t\t\thandle_path /assets/speech/* {\n\t\t\t\troot * /srv/codi-connected/speech/'+key+'\n\t\t\t\tfile_server\n\t\t\t}\n'
assert digest(candidate)==pins['candidateGeneratorSHA256'] and digest(proposed_raw)==pins['candidateManifestSHA256']
key=pins['speechManifestSHA256'];assert len(key)==64 and all(c in '0123456789abcdef' for c in key)
with (ROOT/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);old_source=source.read_bytes();old_manifest=manifest.read_bytes();assert digest(old_source)==pins['originalGeneratorSHA256'] and digest(old_manifest)==pins['originalManifestSHA256'] and ctl.current_mode()=='production'
 data=ctl.load();prior={mode:ctl.caddy(data,mode) for mode in ['prepare','production']};assert Path('/etc/caddy/Caddyfile').read_text()==prior['production']
 reviewed=types.ModuleType('reviewed_speech');reviewed.__file__=str(source);exec(compile(candidate,str(source),'exec'),reviewed.__dict__);proposed=reviewed.tomllib.loads(proposed_raw.decode());reviewed.validate(proposed)
 expected=copy.deepcopy(data);ksu=next(s for s in expected['sites'] if s['domain']=='ksu.codes');previous=ksu.get('codi_speech');ksu['codi_speech']=key;assert proposed==expected
 for mode in prior:
  assert reviewed.caddy(data,mode)==prior[mode];rendered=reviewed.caddy(proposed,mode);assert rendered.count(route(key))==1 and rendered.replace(route(key),'')==(prior[mode].replace(route(previous),'') if previous else prior[mode])
 for site in data['sites']:assert common.unit(site)==reviewed.unit(site)
 fd,name=tempfile.mkstemp(prefix='.codi-speech-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:ctl.write(name,reviewed.caddy(proposed,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(name)
 finally:Path(name).unlink()
 if not inputs['apply']:print(json.dumps({'status':'PASS','scope':'Actual Caddy syntax and one hidden-only static speech route; no live change'}));raise SystemExit(0)
 commit=inputs['commit'];checkout=ROOT/'sites/ksu.codes';assert len(commit)==40
 assert run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==commit and not run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
 speech=checkout/'tools/codiserver/speech'/key;records=pins['speechFiles'];allowed=set(inputs['allowedFiles']);assert set(records)==allowed and len(allowed)==22
 assert digest((speech/'speech.json').read_bytes())==key and json.loads((speech/'speech.json').read_text())=={'version':'codi-speech-assets/1','files':records}
 def exact_tree(folder,root_owned=False):
  assert not folder.is_symlink();found=set()
  for file in [folder,*folder.rglob('*')]:
   info=file.lstat();assert stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)
   if root_owned:assert info.st_uid==info.st_gid==0 and stat.S_IMODE(info.st_mode)==(0o755 if file.is_dir() else 0o644)
   if file.is_dir():continue
   assert info.st_nlink==1;name=str(file.relative_to(folder));assert name=='speech.json' or name in allowed
   if name=='speech.json':assert digest(file.read_bytes())==key
   else:assert records[name]=={'bytes':info.st_size,'sha256':digest(file.read_bytes())};found.add(name)
  assert found==allowed
 exact_tree(speech)
 destination=Path('/srv/codi-connected/speech')/key
 for directory in [*reversed(destination.parent.parents),destination.parent]:
  if not directory.exists():directory.mkdir(mode=0o755)
  info=directory.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
 if not destination.exists():
  shutil.copytree(speech,destination)
  for file in [destination,*destination.rglob('*')]:os.chown(file,0,0);file.chmod(0o755 if file.is_dir() else 0o644)
 exact_tree(destination,True)
 config=Path('/etc/codi-connected/ksu/managed.json');before_config=config.read_bytes();before=pids();assert all(int(pid)>0 for pid in before.values())
 status,headers,index=request('/hidden/');assert status==200;cookie=headers['Set-Cookie'].split(';',1)[0]
 desktop={name:digest(request('/desktop/'+name)[2]) for name in ['release.json','app.js','config.json']};frontend={name:digest(request('/hidden/'+name)[2]) for name in ['app.js','style.css','terminal.js']}
 receipt=Path('/srv/codi-connected')/('speech-'+key+'-activation-result.json');assert not receipt.exists();source_info=source.stat();manifest_info=manifest.stat();backups={'source':str(ctl.snapshot(source)),'manifest':str(ctl.snapshot(manifest))};changed=False
 try:
  changed=True;ctl.write(source,candidate,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,proposed_raw,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  for name,record in records.items():asset('/hidden/assets/speech/'+name,record)
  status,headers,body=request('/hidden/');assert status==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie
  for name,pin in frontend.items():assert digest(request('/hidden/'+name)[2])==pin
  for name,pin in desktop.items():assert digest(request('/desktop/'+name)[2])==pin
  assert request('/hidden/assets/speech/turn.secret')[0]==404 and request('/hidden/assets/speech/../issuer.pem')[0]==404
  smoke=ROOT/'reports/private/codi-speech-assets-20261023.json';run(['/usr/bin/python3',ROOT/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
  assert config.read_bytes()==before_config and pids()==before;exact_tree(destination,True)
  report={'status':'PASS','scope':'One static speech-assets route under hidden; native roles/config/cookie, frontend/prototype bytes and eight sites preserved. No microphone/audio is uploaded by this static route.','sourceCommit':commit,'speechManifestSHA256':key,'speechFiles':records,'installedSpeech':str(destination),'generatorSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest.read_bytes()),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'backups':backups,'nativePidsUnchanged':before,'nativeConfigUnchanged':True,'indexAndGuestCookieUnchanged':True,'desktopSHA256':desktop,'frontendSHA256':frontend,'eightSiteSmoke':str(smoke)}
  fd=os.open(receipt,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
  with os.fdopen(fd,'w') as out:json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
  print(json.dumps(report))
 except BaseException:
  if changed:ctl.write(source,old_source,source_info.st_mode&0o777,source_info.st_uid,source_info.st_gid,False);ctl.write(manifest,old_manifest,manifest_info.st_mode&0o777,manifest_info.st_uid,manifest_info.st_gid,False);reload_generator();ctl.caddy_apply(ctl.load(),'production')
  raise
'''
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate-dir',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--commit',default='');a=p.parse_args()
 if a.apply and not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('Apply requires the reviewed Git commit')
 import importlib.util
 spec=importlib.util.spec_from_file_location('speech_export',ROOT/'scripts/export-speech.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
 folder=a.candidate_dir;inputs={'pins':json.loads((folder/'candidate-result.json').read_text()),'source':(folder/'common.speech.py').read_text(),'manifest':(folder/'sites.speech.toml').read_text(),'apply':a.apply,'commit':a.commit,'allowedFiles':sorted(exporter.FILES)}
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(REMOTE)],input=json.dumps(inputs),capture_output=True,text=True,timeout=360)
 if child.returncode:raise SystemExit(child.stderr or child.stdout)
 report=json.loads(child.stdout.strip().splitlines()[-1]);(ROOT/'.build/checks'/('speech-activation-result.json' if a.apply else 'speech-hosting-validation-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='speechFiles'},indent=2))
