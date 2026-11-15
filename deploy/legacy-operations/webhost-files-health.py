#!/usr/bin/env python3
"""Read the installed private file boundary; verify public route is still absent."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r"""
import hashlib,json,os,pathlib,sqlite3,stat,subprocess,sys,uuid
Path=pathlib.Path;key='8fdbbdda508425df7a9f52848b801c7aed44e9db84de643eea27d8fc2bc4f0e7';root=Path('/srv/codi-gateway/operators')/key
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'file-operator.json')==key
for name,record in json.loads((root/'file-operator.json').read_text())['files'].items():
 p=root/name;assert not p.is_symlink() and p.stat().st_uid==0 and not p.stat().st_mode&0o022
 assert record=={'bytes':p.stat().st_size,'sha256':sha(p)}
sys.path.insert(0,str(root));from file_service.operator import Manager
m=Manager('/etc/codi-user-files/ksu');c=m.load();m.health(c)
assert c['manifestSHA256']=='aa2409356d1868ce48579e9dcfb015582dff08b97c1ab30d5c13c586f7e7a05d'
states=m.states(c);values={}
for name in m.names(c):
 assert states[name]['ActiveState']=='active' and states[name]['UnitFileState']=='static'
 if name.endswith('.socket'):continue
 pid=int(states[name]['MainPID']);s=dict(line.split(':',1) for line in Path('/proc',str(pid),'status').read_text().splitlines())
 assert int(s['CapEff'],16)==0 and s['NoNewPrivs'].strip()=='1'
 values[name]={'pid':pid,'uid':int(s['Uid'].split()[0]),'netns':os.readlink('/proc/'+str(pid)+'/ns/net')}
assert len({v['uid'] for v in values.values()})==2 and 0 not in {v['uid'] for v in values.values()}
assert len({v['netns'] for v in values.values()})==1 and next(iter(values.values()))['netns']!=os.readlink('/proc/self/ns/net')
worker=values[m.names(c)[0]]['pid']
probe='''import errno,json,socket
def check(host,port):
 with socket.socket() as s:s.settimeout(1);return s.connect_ex((host,port))
v={'Internet':check('1.1.1.1',443),'LAN':check('10.0.7.84',443),'hostIssuer':check('127.0.0.1',8118)}
assert v['Internet']==v['LAN']==errno.ENETUNREACH and v['hostIssuer']==errno.ECONNREFUSED
print(json.dumps(v))
'''
network=json.loads(subprocess.run(['nsenter','-t',str(worker),'-n','/usr/bin/python3','-I','-B','-c',probe],check=True,capture_output=True,text=True).stdout)
interfaces=json.loads(subprocess.run(['nsenter','-t',str(worker),'-n','ip','-j','address','show'],check=True,capture_output=True,text=True).stdout)
assert [item['ifname'] for item in interfaces]==['lo']
database=Path(c['stateRoot'])/'permissions.sqlite3'
with sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True) as db:
 assert db.execute('PRAGMA quick_check(1)').fetchall()==[('ok',)]
 rows=db.execute('SELECT subject,home_id,state FROM users').fetchall();permissions=db.execute('SELECT count(*) FROM permissions').fetchone()[0]
 for sub,home,state in rows:assert sub=='user:'+str(uuid.UUID(hex=home)) and state=='ready'
 assert len(list((Path(c['dataRoot'])/'users').iterdir()))==len(rows)
 for name in ['gateway_auth_metadata','gateway_transfer_metadata']:assert db.execute('SELECT version FROM '+name).fetchall()==[(1,)]
for role in ['codi-issuer','codi-steward','codi-guest','caddy']:
 assert subprocess.run(['runuser','-u',role,'--','test','-r',str(database)],capture_output=True).returncode==1
assert subprocess.run(['runuser','-u','codi-gateway','--','test','-r','/var/lib/codi-connected/ksu/issuer/state/accounts.sqlite3'],capture_output=True).returncode==1
print(json.dumps({'status':'PASS','scope':'Read-only actual private file worker, kernel/DAC boundaries and retained registry; no registered public file API test',
 'workerManifestSHA256':c['manifestSHA256'],'operatorManifestSHA256':key,'processes':values,'kernelNetworkProbe':network,'onlyLoopbackInterface':True,'staticUnits':True,
 'retainedRegisteredFolders':len(rows),'permissionRows':permissions,'anonymousFolders':0,'privateDatabasesSeparated':True,'personalFileContentsRead':False,'serviceRestarted':False}))
"""

if __name__=='__main__':
    process=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-'],input=REMOTE,capture_output=True,text=True,timeout=45)
    if process.returncode:raise SystemExit(process.stderr or process.stdout)
    result=json.loads(process.stdout)
    for path,method in [('/hidden/gateway/client.mjs','GET'),('/hidden/api/v1/gateway/challenge','POST')]:
        request=urllib.request.Request('https://ksu.codes'+path,method=method,data=b'{}' if method=='POST' else None,headers={'Origin':'https://ksu.codes','Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=15) as response:status=response.status
        except urllib.error.HTTPError as error:status=error.code
        assert status==404,(path,status)
    result.update(publicGatewayRoutesAbsent=True,defaultPublicTLSVerified=True)
    result['sha256']={'scripts/webhost-files-health.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT/'.build/checks/webhost-files-health-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
