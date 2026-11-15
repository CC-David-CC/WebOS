#!/usr/bin/env python3
"""Verify native15/schema5 with unified public assets and registered-only guest Internet."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
BASELINE=ROOT/'.build/releases/connected-signin-r7'
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
assert config['version']=='codi-managed-instance/5' and config['manifestSHA256']==input_value['expectedManifestSHA256']
assert sha(release/'connected-release.json')==config['manifestSHA256']
assert config['turn']['iceTransportPolicy']=='all'
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
assert '--ice-preferences' in Path('/proc/'+str(pids['issuer'])+'/cmdline').read_bytes().decode()
assert '--user-files' in Path('/proc/'+str(pids['issuer'])+'/cmdline').read_bytes().decode()
assert '--guest-network-policy-sha256' in Path('/proc/'+str(pids['issuer'])+'/cmdline').read_bytes().decode()
assert '--network-control' in Path('/proc/'+str(pids['guest'])+'/cmdline').read_bytes().decode()
binding=config['guestNetwork'];assert sha(binding['configFile'])==binding['configSHA256'] and sha(binding['frontendFile'])==binding['frontendSHA256']
assert sha(Path(binding['operatorRelease'])/'guest-operator.json')==binding['operatorManifestSHA256']
guest_status=json.loads(run([config['python'],'-I','-B',Path(binding['operatorRelease'])/'scripts/manage-guest-network.py','status','--config-dir',str(Path(binding['configFile']).parent)]))
assert guest_status['active'] and guest_status['kernelMatches'] and not guest_status['guardFault'] and not guest_status['bootEnabled']

assert run(['systemctl','show','codi-ksu-hidden-issuer-bootstrap.service','-p','MainPID','--value'])=='0'
assert Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()==['1000','1001'] and Path('/proc/sys/net/ipv4/ip_forward').read_text().strip()=='0'
hosting=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(hosting/'ops'));import common
manifest=common.load();assert common.caddy(manifest,'production')==Path('/etc/caddy/Caddyfile').read_text()
site=next(s for s in manifest['sites'] if s['domain']=='ksu.codes');assert site['codi_files'] is True
assert 'codi_frontend' not in site
key=None;public=json.loads((release/'release.json').read_text())['files'];names=['app.js','style.css','terminal.js','assets/terminal-initramfs.cpio.gz','desktop-apps.js','networking.js','assets/desktop/cache-manifest.json','assets/desktop/offline-worker.js']
metadata={'files':{name:public[name] for name in names}}
activation=json.loads(Path('/srv/codi-connected/frontend-97b80a77ce3f377aecdea64928730d35c947ce13c3c6e8a968123fa218778381-activation-result.json').read_text())
assert json.loads(Path(config['guestNetwork']['configFile']).read_text())['policy']=={'version':'codi-guest-egress-policy/2','anonymousInternet':'deny','ownPublicIPv4':['104.180.210.33'],'dnsIPv4':['1.1.1.1','9.9.9.9']}
website=Path('/srv/webapps/ksu.codes/current').resolve()
for name,expected in activation['desktopSHA256'].items():assert sha(website/'public/desktop'/name)==expected
prototype_records=json.loads((website/'public/desktop/release.json').read_text())['files']
for name,record in prototype_records.items():
 p=website/'public/desktop'/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts and record=={'bytes':p.stat().st_size,'sha256':sha(p)}
smoke=hosting/'reports/private/codi-native15-signin-health-20261024.json'
run(['/usr/bin/python3',hosting/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],120)
print(json.dumps({'status':'PASS','scope':'Pinned native15/schema5/unified public assets and strict sign-in, active guest guard, private Files kernel/DAC boundaries, generated hosting and all-site HTTPS smoke; no personal file contents read',
 'nativeManifestSHA256':config['manifestSHA256'],'nativeConfigVersion':config['version'],'nativeConfigSHA256':sha('/etc/codi-connected/ksu/managed.json'),'nativePIDs':pids,'guestPolicy':guest_status,
 'frontendManifestSHA256':key,'frontendFiles':metadata['files'],'prototypeSHA256':activation['desktopSHA256'],'prototypeDeclaredFilesVerified':len(prototype_records),'privateWorker':private,
 'hostingSHA256':{name:sha(path) for name,path in [('generator',hosting/'ops/common.py'),('manifest',hosting/'sites.toml'),('activeCaddy','/etc/caddy/Caddyfile')]},
 'siteDomains':sorted(s['domain'] for s in manifest['sites'] if s['enabled']),'allSiteSmoke':str(smoke),'servicesRestarted':False,'personalFileContentsRead':False}))
'''

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--release-dir',type=Path,default=BASELINE);parser.add_argument('--manifest-sha256',default='ec6a637c197684921a3ac18ee87a1d1d6380a0a5984ece1cdb40884db627bbed');parser.add_argument('--output',default='webhost-signin-health-result.json');parser.add_argument('--files-release-dir',type=Path,default=ROOT/'.build/gateways/user-files-r4');parser.add_argument('--files-manifest-sha256',default='aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d');args=parser.parse_args()
    baseline_raw=(args.release_dir/'connected-release.json').read_bytes()
    assert hashlib.sha256(baseline_raw).hexdigest()==args.manifest_sha256
    baseline=json.loads(baseline_raw)['files']
    files_raw=(args.files_release_dir/'files-service.json').read_bytes()
    assert hashlib.sha256(files_raw).hexdigest()==args.files_manifest_sha256
    files_baseline=json.loads(files_raw)['files']
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps({'workerCode':worker.REMOTE.replace('aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d',args.files_manifest_sha256),'expectedManifestSHA256':args.manifest_sha256}),capture_output=True,text=True,timeout=180)
    if child.returncode:raise SystemExit(child.stderr or child.stdout)
    report=json.loads(child.stdout)
    url='https://ksu.codes/hidden/'
    for name,record in report['frontendFiles'].items():
        with urllib.request.urlopen(url+name,timeout=20) as response:
            assert response.status==200 and response.headers['Cache-Control']=='no-store' and hashlib.sha256(response.read()).hexdigest()==record['sha256']
    with urllib.request.urlopen(url+'gateway/client.mjs',timeout=15) as response:
        assert response.status==200 and hashlib.sha256(response.read()).hexdigest()==files_baseline['gateway_service/client.mjs']['sha256']
    with urllib.request.urlopen(url+'config.json',timeout=15) as response:
        config=json.load(response);assert config['rtc']['iceTransportPolicy']=='relay' and config['rtc']['preference']=={'version':'codi-session-ice/1','allowed':['relay','all'],'preferred':'all'}
        assert config['gateway']=={'version':'codi-user-files/1','basePath':'/hidden/gateway','fileBytes':8388608}
    for path,expected in [('gateway/use',401),('api/v1/gateway/challenge',400)]:
        request=urllib.request.Request(url+path,method='POST',data=b'{}',headers={'Content-Type':'application/json','Origin':'https://ksu.codes'})
        try:
            with urllib.request.urlopen(request,timeout=15) as response:status=response.status
        except urllib.error.HTTPError as error:status=error.code
        assert status==expected,(path,status)
    with urllib.request.urlopen(url+'api/v1/desktop-status',timeout=15) as response:
        status=json.load(response);assert status['version']=='codi-desktop-status/1' and response.headers['Cache-Control']=='no-store'
    with urllib.request.urlopen(url+'assets/desktop/offline-worker.js',timeout=15) as response:
        assert response.headers['Service-Worker-Allowed']=='/hidden/' and hashlib.sha256(response.read()).hexdigest()==baseline['assets/desktop/offline-worker.js']['sha256']
    with urllib.request.urlopen(url+'guest-access/client.mjs',timeout=15) as response:
        assert hashlib.sha256(response.read()).hexdigest()==baseline['guest_service/client.mjs']['sha256']
    report.update(defaultPublicTLSVerified=True,unauthorizedFileAccessDenied=True,liveDesktopStatusVerified=True,workerScopeRestrictedToHidden=True)
    report['publicAssetsCheckedAgainstFrozenLiveManifest']=True
    report['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['scripts/webhost-signin-health.py','scripts/webhost-files-health.py']}
    (ROOT/'.build/checks'/args.output).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
