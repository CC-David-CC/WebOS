#!/usr/bin/env python3
"""Read-only live baseline: preserve R14/native10 while local files work advances.

Does not run tests against actual accounts or read personal-file contents.
This is not an all-site HTTP smoke or a gateway deployment receipt.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,json,pathlib,subprocess,sys
Path=pathlib.Path
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text())
release='/srv/codi-connected/releases/native10-7705a87e09c44e22'
assert config['release']==release and config['manifestSHA256']=='7705a87e09c44e22be792f91133a24dbd52f4af9e418d6df66978440570c5625'
assert sha(Path(release)/'connected-release.json')==config['manifestSHA256']
pids={}
for role,expected in [('issuer',227448),('steward',227450),('guest',227451)]:
    raw=subprocess.run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','MainPID','-p','ActiveState'],check=True,capture_output=True,text=True).stdout
    value=dict(line.split('=',1) for line in raw.splitlines())
    assert value['ActiveState']=='active' and int(value['MainPID'])==expected
    assert (release+'/').encode() in Path('/proc/'+value['MainPID']+'/cmdline').read_bytes()
    pids[role]=expected
sys.path.insert(0,'/home/dflanag3/webhost-sites/ops');import common
hosting=common.load(Path('/home/dflanag3/webhost-sites/sites.toml'))
assert common.caddy(hosting,'production')==Path('/etc/caddy/Caddyfile').read_text()
site=next(s for s in hosting['sites'] if s['domain']=='ksu.codes')
key='179a5b5677686c3b2f131aede94639f0f9f0c6c6882a5e83370d8d9f6fc639e9'
assert site['codi_frontend']==key
frontend=Path('/srv/codi-connected/frontends')/key
assert sha(frontend/'frontend.json')==key
for name,record in json.loads((frontend/'frontend.json').read_text())['files'].items():
    assert record=={'bytes':(frontend/name).stat().st_size,'sha256':sha(frontend/name)}
activation=json.loads((Path('/srv/codi-connected')/('frontend-'+key+'-activation-result.json')).read_text())
website=Path('/srv/webapps/ksu.codes/current').resolve()
for name,expected in activation['desktopSHA256'].items():assert sha(website/'public/desktop'/name)==expected
print(json.dumps({'status':'PASS','scope':'Read-only actual R14/native10 process/frontend/prototype preservation and generated hosting equality; no all-site HTTP or live file API claim',
 'onlineRoleRelease':release,'nativePIDs':pids,'frontendManifestSHA256':key,'prototypeBytesPreserved':True,
 'hostingSHA256':{name:sha(path) for name,path in [('generator','/home/dflanag3/webhost-sites/ops/common.py'),('manifest','/home/dflanag3/webhost-sites/sites.toml'),('activeCaddy','/etc/caddy/Caddyfile')]},
 'enabledSites':sorted(s['domain'] for s in hosting['sites'] if s['enabled']),
 'personalFilesRead':False,'accountsModified':False,'servicesRestarted':False}))
'''

if __name__=='__main__':
    completed=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-'],input=REMOTE,capture_output=True,text=True,timeout=45)
    if completed.returncode:raise SystemExit(completed.stderr or completed.stdout)
    result=json.loads(completed.stdout);assert result['status']=='PASS'
    result['sha256']={'scripts/gateway-live-preservation-check.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'.build/checks/gateway-live-preservation-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
