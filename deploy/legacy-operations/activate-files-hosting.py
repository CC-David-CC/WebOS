#!/usr/bin/env python3
"""Validate/apply only the reviewed KSU personal-file route through hosting control."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import copy,fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,socket,ssl,stat,subprocess,sys,tempfile,time,types
Path=pathlib.Path;root=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(root/'ops'));import common;import webctl as ctl
ctl.root_required();inputs=json.load(sys.stdin);pins=inputs['pins'];candidate=inputs['source'].encode();manifest_raw=inputs['manifest'].encode()
source=root/'ops/common.py';manifest=root/'sites.toml'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def run(args,timeout=60):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
def request(path,method='GET',body=None,extra=None):
 c=http.client.HTTPSConnection('ksu.codes',timeout=15);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  c.request(method,path,body,headers=extra or {});r=c.getresponse();value=r.read(13*1024*1024);assert len(value)<13*1024*1024;return r.status,dict(r.getheaders()),value
 finally:c.close()
def pids():return {name:run(['systemctl','show',name,'-p','MainPID','--value']) for name in ['codi-ksu-hidden-'+role+'.service' for role in ['issuer','steward','guest']]+['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']}
def reload():
 importlib.invalidate_caches();importlib.reload(common)
 for name in ['load','dump','caddy','unit','validate']:setattr(ctl,name,getattr(common,name))
route='\thandle /hidden/gateway/* {\n\t\turi strip_prefix /hidden\n\t\trequest_body {\n\t\t\tmax_size 12MiB\n\t\t}\n\t\treverse_proxy 127.0.0.1:8140\n\t}\n'
assert sha(candidate)==pins['candidateGeneratorSHA256'] and sha(manifest_raw)==pins['candidateManifestSHA256']
with (root/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 old_source=source.read_bytes();old_manifest=manifest.read_bytes()
 assert sha(old_source)==pins['originalGeneratorSHA256'] and sha(old_manifest)==pins['originalManifestSHA256']
 assert not source.is_symlink() and not manifest.is_symlink() and ctl.current_mode()=='production'
 data=ctl.load();before_generated={mode:ctl.caddy(data,mode) for mode in ['prepare','production']}
 assert Path('/etc/caddy/Caddyfile').read_text()==before_generated['production']
 reviewed=types.ModuleType('reviewed_files');reviewed.__file__=str(source);exec(compile(candidate,str(source),'exec'),reviewed.__dict__)
 proposed=reviewed.tomllib.loads(manifest_raw.decode());reviewed.validate(proposed)
 expected=copy.deepcopy(data);next(s for s in expected['sites'] if s['domain']=='ksu.codes')['codi_files']=True;assert proposed==expected
 for mode,baseline in before_generated.items():
  assert reviewed.caddy(data,mode)==baseline
  rendered=reviewed.caddy(proposed,mode);assert rendered.count(route)==1 and rendered.replace(route,'')==baseline
 for site in data['sites']:assert common.unit(site)==reviewed.unit(site)
 fd,path=tempfile.mkstemp(prefix='.codi-files-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
 try:ctl.write(path,reviewed.caddy(proposed,'production'),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(path)
 finally:Path(path).unlink()
 if not inputs['apply']:print(json.dumps({'status':'PASS','scope':'Actual managed Caddy syntax validation and KSU-only route invariants; no live change','candidateGeneratorSHA256':sha(candidate),'candidateManifestSHA256':sha(manifest_raw)}));raise SystemExit(0)
 checkout=root/'sites/ksu.codes';assert run(['runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==inputs['commit']
 assert not run(['runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
 published=checkout/'tools/codiserver/native-files/hosting/files-route-r1'
 assert (published/'common.files.py').read_bytes()==candidate and (published/'sites.files.toml').read_bytes()==manifest_raw
 config=Path('/etc/codi-connected/ksu/managed.json');config_raw=config.read_bytes();native=json.loads(config_raw)
 assert native['manifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0' and native['version']=='codi-managed-instance/3' and 'userFiles' not in native
 operator=Path('/srv/codi-gateway/operators/8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7')
 assert sha((operator/'file-operator.json').read_bytes())==operator.name
 for name,record in json.loads((operator/'file-operator.json').read_text())['files'].items():
  file=operator/name;info=file.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022 and record=={'bytes':info.st_size,'sha256':sha(file.read_bytes())}
 sys.path.insert(0,str(operator));from file_service.operator import Manager
 worker=Manager('/etc/codi-user-files/ksu');wc=worker.load();worker.health(wc)
 file_pins={str(p):sha(p.read_bytes()) for p in [Path('/etc/codi-user-files/ksu/managed.json'),Path('/etc/codi-user-files/ksu/issuer-policy.json')]}
 sdk=Path(wc['release'])/'gateway_service/client.mjs';sdk_sha=sha(sdk.read_bytes())
 before=pids();assert all(int(value)>0 for value in before.values())
 website=Path('/srv/webapps/ksu.codes/current').resolve();assert website.is_relative_to(Path('/srv/webapps/ksu.codes/releases'))
 prototype={name:sha((website/'public/desktop'/name).read_bytes()) for name in ['release.json','app.js','config.json']}
 assert prototype=={'release.json':'d047681f079d74e44b0ffeeb7a06563dc148375b2adfafa072d3510de0b4d5e9','app.js':'2abb154d558cbc44149cfa46ddcc23c9d4843f822b8a44c5d392cd4bd2f88602','config.json':'5ec30b79a21a07911315ddd9714fba560fc3451004d51942ee53f36c0e6effad'}
 key='179a5b5677686c3b2f131aede94639f0f9f0c6c6882a5e83370d8d9f6fc639e9';assert next(s for s in data['sites'] if s['domain']=='ksu.codes')['codi_frontend']==key
 assets=json.loads((Path('/srv/codi-connected/frontends')/key/'frontend.json').read_text())['files']
 code,headers,index=request('/hidden/');assert code==200;cookie=headers['Set-Cookie'].split(';',1)[0]
 public_config=json.loads(request('/hidden/config.json')[2]);assert 'gateway' not in public_config
 assert request('/hidden/gateway/client.mjs')[0]==404
 si=source.stat();mi=manifest.stat();backups={'source':str(ctl.snapshot(source)),'manifest':str(ctl.snapshot(manifest))};changed=False
 try:
  changed=True;ctl.write(source,candidate,si.st_mode&0o777,si.st_uid,si.st_gid,False);ctl.write(manifest,manifest_raw,mi.st_mode&0o777,mi.st_uid,mi.st_gid,False);reload();ctl.caddy_apply(ctl.load(),'production')
  code,headers,body=request('/hidden/gateway/client.mjs');assert code==200 and sha(body)==sdk_sha and headers['Cache-Control']=='no-store'
  headers={'Origin':'https://ksu.codes','Content-Type':'application/json'}
  assert request('/hidden/gateway/use','POST',b'{}',headers)[0]==401
  assert request('/hidden/gateway/challenge','POST',b'{}',headers)[0]==403
  for path in ['/hidden/gateway/healthz','/hidden/gateway/../permissions.sqlite3','/hidden/gateway/config.json','/gateway/client.mjs']:assert request(path)[0]==404
  assert request('/hidden/api/v1/gateway/challenge','POST',b'{}',headers)[0]==404
  assert json.loads(request('/hidden/config.json')[2])==public_config
  code,headers,body=request('/hidden/');assert code==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie
  code,headers,body=request('/hidden');assert code==308 and headers['Location']=='/hidden/'
  for name,record in assets.items():
   code,headers,body=request('/hidden/'+name);assert code==200 and sha(body)==record['sha256']
  for name,value in prototype.items():assert sha(request('/desktop/'+name)[2])==value
  smoke=root/'reports/private/codi-files-route-20261023.json';run(['/usr/bin/python3',root/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
  assert config.read_bytes()==config_raw and pids()==before and Path('/srv/webapps/ksu.codes/current').resolve()==website
  assert file_pins=={p:sha(Path(p).read_bytes()) for p in file_pins};worker.health(wc)
  result={'status':'PASS','scope':'Only managed HTTPS personal-file worker route installed; issuer authorization/UI remain off; all managed site smoke checks and prototype/native/private-worker preservation pass',
   'sourceCommit':inputs['commit'],'generatorSHA256':sha(source.read_bytes()),'manifestSHA256':sha(manifest.read_bytes()),'activeCaddySHA256':sha(Path('/etc/caddy/Caddyfile').read_bytes()),
   'backups':backups,'nativeAndFilePidsUnchanged':before,'nativeConfigUnchanged':True,'privateWorkerCustodyUnchanged':True,'frontendManifestSHA256':key,
   'desktopSHA256':prototype,'indexAndGuestCookieUnchanged':True,'publicSDK_SHA256':sdk_sha,'unauthorizedFileRequestsDenied':True,'issuerFileHookEnabled':False,
   'siteDomains':sorted(s['domain'] for s in data['sites'] if s['enabled']),'allSiteSmoke':str(smoke),'routerFirewallAndPortsChanged':False}
  receipt=Path('/srv/codi-connected')/('files-route-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as output:json.dump(result,output,indent=2);output.write('\n');output.flush();os.fsync(output.fileno())
  result.update(rootReceipt=str(receipt),rootReceiptSHA256=sha(receipt.read_bytes()));print(json.dumps(result))
 except BaseException:
  if changed:
   ctl.write(source,old_source,si.st_mode&0o777,si.st_uid,si.st_gid,False);ctl.write(manifest,old_manifest,mi.st_mode&0o777,mi.st_uid,mi.st_gid,False);reload();ctl.caddy_apply(ctl.load(),'production')
  raise
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate-dir',type=Path,required=True)
    p.add_argument('--apply',action='store_true')
    p.add_argument('--commit',default='')
    a=p.parse_args()
    if a.apply and not re.fullmatch('[0-9a-f]{40}',a.commit):p.error('Exact source commit required')
    inputs={'pins':json.loads((a.candidate_dir/'candidate-result.json').read_text()),'source':(a.candidate_dir/'common.files.py').read_text(),'manifest':(a.candidate_dir/'sites.files.toml').read_text(),'apply':a.apply,'commit':a.commit}
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(inputs),capture_output=True,text=True,timeout=360)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    result=json.loads(child.stdout.strip().splitlines()[-1]);name='files-hosting-activation-result.json' if a.apply else 'files-hosting-validation-result.json'
    (ROOT/'.build/checks'/name).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
