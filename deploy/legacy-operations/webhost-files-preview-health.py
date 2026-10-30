#!/usr/bin/env python3
"""Verify the actual native11/R15 personal-files preview and private boundary."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('private_worker_health',ROOT/'scripts/webhost-files-health.py')
worker=importlib.util.module_from_spec(spec);spec.loader.exec_module(worker)
REMOTE=r'''
import contextlib,hashlib,io,json,pathlib,subprocess,sys
Path=pathlib.Path;input_value=json.load(sys.stdin);scope={};buffer=io.StringIO()
with contextlib.redirect_stdout(buffer):exec(compile(input_value['workerCode'],'private-worker-health','exec'),scope)
private=json.loads(buffer.getvalue());assert private['status']=='PASS'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(args,timeout=60):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=timeout).stdout.strip()
config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text());release=Path(config['release'])
assert config['version']=='codi-managed-instance/4' and config['manifestSHA256']=='99f938cd7f895831191957e342824b7d44506df19d32edfa2157b48bc9385ec0'
assert sha(release/'connected-release.json')==config['manifestSHA256']
for name,record in json.loads((release/'connected-release.json').read_text())['files'].items():
 p=release/name;info=p.lstat();assert not p.is_symlink() and info.st_uid==0 and not info.st_mode&0o022 and record=={'bytes':info.st_size,'sha256':sha(p)}
assert sha(config['userFiles']['configFile'])==config['userFiles']['configSHA256']
assert sha(Path(config['userFiles']['operatorRelease'])/'file-operator.json')==config['userFiles']['operatorManifestSHA256']
assert config['userFiles']['operatorManifestSHA256']=='8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7'
pids={}
for role in ['issuer','steward','guest']:
 name='codi-ksu-hidden-'+role+'.service';pid=run(['systemctl','show',name,'-p','MainPID','--value'])
 assert int(pid)>0 and run(['systemctl','is-active',name])=='active' and run(['systemctl','show',name,'-p','UnitFileState','--value'])=='disabled'
 assert (str(release)+'/').encode() in Path('/proc/'+pid+'/cmdline').read_bytes()
 status=dict(line.split(':',1) for line in Path('/proc/'+pid+'/status').read_text().splitlines())
 assert int(status['Uid'].split()[0])>0 and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
 pids[role]=int(pid)
assert '--user-files' in Path('/proc/'+str(pids['issuer'])+'/cmdline').read_bytes().decode()
assert run(['systemctl','show','codi-ksu-hidden-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
assert Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001'] and Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
hosting=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(hosting/'ops'));import common
manifest=common.load();assert common.caddy(manifest,'production')==Path('/etc/caddy/Caddyfile').read_text()
site=next(s for s in manifest['sites'] if s['domain']=='ksu.codes');assert site['codi_files'] is True
key='6d81a52bf9d7be264ebba58340ccc4302b8208c2594a4f3b2138224eaa938787';assert site['codi_frontend']==key
frontend=Path('/srv/codi-connected/frontends')/key;assert sha(frontend/'frontend.json')==key
metadata=json.loads((frontend/'frontend.json').read_text())
for name,record in metadata['files'].items():assert record=={'bytes':(frontend/name).stat().st_size,'sha256':sha(frontend/name)}
activation=json.loads((Path('/srv/codi-connected')/('frontend-'+key+'-activation-result.json')).read_text())
website=Path('/srv/webapps/ksu.codes/current').resolve()
for name,expected in activation['desktopSHA256'].items():assert sha(website/'public/desktop'/name)==expected
prototype_records=json.loads((website/'public/desktop/release.json').read_text())['files']
for name,record in prototype_records.items():
 p=website/'public/desktop'/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts and record=={'bytes':p.stat().st_size,'sha256':sha(p)}
smoke=hosting/'reports/private/codi-files-enabled-20261023.json'
run(['/usr/bin/python3',hosting/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
print(json.dumps({'status':'PASS','scope':'Actual native11/R15 file hook/routing/immutable assets, private worker kernel/DAC boundaries, generated hosting and all-site HTTPS smoke; no real account sign-in or file contents read',
 'nativeManifestSHA256':config['manifestSHA256'],'nativeConfigVersion':config['version'],'nativePIDs':pids,
 'frontendManifestSHA256':key,'frontendFiles':metadata['files'],'prototypeSHA256':activation['desktopSHA256'],'prototypeDeclaredFilesVerified':len(prototype_records),'privateWorker':private,
 'hostingSHA256':{name:sha(path) for name,path in [('generator',hosting/'ops/common.py'),('manifest',hosting/'sites.toml'),('activeCaddy','/etc/caddy/Caddyfile')]},
 'siteDomains':sorted(s['domain'] for s in manifest['sites'] if s['enabled']),'allSiteSmoke':str(smoke),'servicesRestarted':False,'personalFileContentsRead':False}))
'''

if __name__=='__main__':
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'workerCode':worker.REMOTE}),capture_output=True,text=True,timeout=180)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    report=json.loads(child.stdout)
    url='https://ksu.codes/hidden/'
    for name,record in report['frontendFiles'].items():
        with urllib.request.urlopen(url+name,timeout=20) as response:
            assert response.status==200 and response.headers['Cache-Control']=='no-store' and hashlib.sha256(response.read()).hexdigest()==record['sha256']
    with urllib.request.urlopen(url+'gateway/client.mjs',timeout=15) as response:
        assert response.status==200 and hashlib.sha256(response.read()).hexdigest()==hashlib.sha256((ROOT/'gateway_service/client.mjs').read_bytes()).hexdigest()
    with urllib.request.urlopen(url+'config.json',timeout=15) as response:
        config=json.load(response);assert config['gateway']=={'version':'codi-user-files/1','basePath':'/hidden/gateway','fileBytes':8388608}
    for path,expected in [('gateway/use',401),('api/v1/gateway/challenge',400)]:
        request=urllib.request.Request(url+path,method='POST',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://ksu.codes'})
        try:
            with urllib.request.urlopen(request,timeout=15) as response:status=response.status
        except urllib.error.HTTPError as error:status=error.code
        assert status==expected,(path,status)
    report.update(defaultPublicTLSVerified=True,unauthorizedFileAccessDenied=True)
    report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/webhost-files-preview-health.py','scripts/webhost-files-health.py']}
    (ROOT/'.build/checks/webhost-files-preview-health-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
