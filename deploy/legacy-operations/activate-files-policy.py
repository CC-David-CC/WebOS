#!/usr/bin/env python3
"""Explicit native11 account-file enablement after matched frontend/route installation."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,http.client,json,os,pathlib,socket,ssl,subprocess,time
Path=pathlib.Path
assert os.geteuid()==0
config_path=Path('/etc/codi-connected/ksu/managed.json');before_raw=config_path.read_bytes();before=json.loads(before_raw)
release=Path('/srv/codi-connected/releases/native11-99f938cd7f895831');expected='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(args,timeout=120):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
assert before['release']==str(release) and before['manifestSHA256']==expected and sha(release/'connected-release.json')==expected
assert before['version']=='codi-managed-instance/3' and 'userFiles' not in before
assert before['origin']=='https://ksu.codes' and before['basePath']=='/hidden'
for name,record in json.loads((release/'connected-release.json').read_text())['files'].items():
 p=release/name;info=p.lstat();assert not p.is_symlink() and info.st_uid==0 and not info.st_mode&0o022 and record=={'bytes':info.st_size,'sha256':sha(p)}
hosting=Path('/home/dflanag3/webhost-sites');import sys;sys.path.insert(0,str(hosting/'ops'));import common
manifest=common.load();assert common.caddy(manifest,'production')==Path('/etc/caddy/Caddyfile').read_text()
ksu=next(s for s in manifest['sites'] if s['domain']=='ksu.codes')
assert ksu['codi_files'] is True and ksu['codi_frontend']=='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787'
hosting_pins={str(p):sha(p) for p in [hosting/'ops/common.py',hosting/'sites.toml',Path('/etc/caddy/Caddyfile')]}
file_pins={str(p):sha(p) for p in [Path('/etc/codi-user-files/ksu/managed.json'),Path('/etc/codi-user-files/ksu/issuer-policy.json')]}
names=['codi-ksu-hidden-'+r+'.service' for r in ['issuer','steward','guest']]+['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']
def pids():return {n:run(['systemctl','show',n,'-p','MainPID','--value']) for n in names}
def request(path):
 c=http.client.HTTPSConnection('ksu.codes',timeout=15);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  c.request('GET',path);r=c.getresponse();return r.status,dict(r.getheaders()),r.read(4*1024*1024)
 finally:c.close()
before_pids=pids();assert all(int(v)>0 for v in before_pids.values())
code,headers,index=request('/hidden/');assert code==200;cookie=headers['Set-Cookie'].split(';',1)[0]
public_before=json.loads(request('/hidden/config.json')[2]);assert 'gateway' not in public_before
sdk_sha=sha('/srv/codi-gateway/releases/aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d/gateway_service/client.mjs')
assert hashlib.sha256(request('/hidden/gateway/client.mjs')[2]).hexdigest()==sdk_sha
python=Path(before['python']);operator=release/'scripts/manage-services.py';argv=[python,'-I','-B',operator,'configure-user-files','--config',config_path]
try:
 result=json.loads(run(argv+['--gateway-config','/etc/codi-user-files/ksu/managed.json','--file-operator','/srv/codi-gateway/operators/8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7']))
 after=json.loads(config_path.read_text());assert after['version']=='codi-managed-instance/4' and 'userFiles' in after
 stable=lambda x:{k:v for k,v in x.items() if k not in ('version','userFiles')}
 assert stable(before)==stable(after)
 after_pids=pids();assert int(after_pids[names[0]])>0 and after_pids[names[0]]!=before_pids[names[0]]
 assert {n:p for n,p in before_pids.items() if n!=names[0]}=={n:p for n,p in after_pids.items() if n!=names[0]}
 public_after=json.loads(request('/hidden/config.json')[2]);assert public_after.pop('gateway')=={'version':'codi-user-files/1','basePath':'/hidden/gateway','fileBytes':8388608};assert public_after==public_before
 code,headers,body=request('/hidden/');assert code==200 and body==index and cookie==headers['Set-Cookie'].split(';',1)[0]
 assert hosting_pins=={p:sha(p) for p in hosting_pins} and file_pins=={p:sha(p) for p in file_pins}
 for role in ['issuer','steward','guest']:assert run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','UnitFileState','--value'])=='disabled'
 report={'status':'PASS','scope':'Explicit journaled file authorization enabled after HTTPS route and matching R15; only issuer restarted, no account or file contents inspected, public Files tests separate',
 'nativeManifestSHA256':expected,'frontendManifestSHA256':ksu['codi_frontend'],'nativeConfigVersion':after['version'],'configurationResult':result,
 'beforePids':before_pids,'afterPids':after_pids,'otherRolesAndPrivateWorkerPidsUnchanged':True,'indexAndGuestCookieUnchanged':True,
 'hostingSHA256':hosting_pins,'privateWorkerCustodyUnchanged':True,'dataRestored':False,'routerFirewallAndPortsChanged':False}
 receipt=Path('/srv/codi-connected')/('files-enable-'+str(time.time_ns())+'-result.json');fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 report.update(rootReceipt=str(receipt),rootReceiptSHA256=sha(receipt));print(json.dumps(report))
except BaseException:
 current=json.loads(config_path.read_text())
 if current.get('userFiles') and not (config_path.parent/'maintenance.json').exists():run(argv+['--disable'])
 raise
'''

if __name__=='__main__':
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],capture_output=True,text=True,timeout=210)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    report=json.loads(child.stdout);report['sha256']={'scripts/activate-files-policy.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'.build/checks/files-policy-activation-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
