#!/usr/bin/env python3
"""Guarded issuer-only ICE policy operation using the installed native controller.

Default is read-only. Native14's signed preference profile keeps legacy clients
on relay while modern clients may request all candidates. This never installs code, rotates
keys, restores private data, edits hosting, enables boot or opens router ports.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import hashlib,http.client,json,os,pathlib,ssl,socket,subprocess,sys,time
P=pathlib.Path;inputs=json.load(sys.stdin);assert os.geteuid()==0
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr[-2000:])
 return r.stdout.strip()
path=P('/etc/codi-connected/ksu/managed.json');before=json.loads(path.read_text());native=P(before['release']);python=before['python']
assert sha(path)==inputs['configSHA256'] and before['version']=='codi-managed-instance/5'
assert before['instance']=='codi-ksu-hidden' and before['origin']=='https://ksu.codes' and before['basePath']=='/hidden'
assert before['release']=='/srv/codi-connected/releases/native14-8810761ee7e47e15'
assert before['manifestSHA256']=='8810761ee7e47e15b055ccda8ed83cd15c017f839770b980dbfaa0d7ab62e0ce' and sha(native/'connected-release.json')==before['manifestSHA256']
for name,record in json.loads((native/'connected-release.json').read_text())['files'].items():
 p=native/name;s=p.lstat();assert not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022 and record=={'bytes':s.st_size,'sha256':sha(p)}
assert before.get('turn') and before.get('userFiles') and before.get('guestNetwork')
assert not (path.parent/'maintenance.json').exists() and not (path.parent/'native-rollout.json').exists()
hosting=P('/home/dflanag3/webhost-sites');pins={str(p):sha(p) for p in [hosting/'ops/common.py',hosting/'sites.toml',P('/etc/caddy/Caddyfile')]}
assert pins=={str(hosting/'ops/common.py'):'718934ce2d95a9ebea7e96b386027b1c0523a7390c310e74c8eba009cd8a10a4',str(hosting/'sites.toml'):'da1383b2b4f7fa25911c204c212981d54b05355f53e07ff8284242971b387bd9','/etc/caddy/Caddyfile':'09763673ee7b6bcc6ade992a931e3c409aebd0daafeeb5ba46181178d81a5a7f'}
def public(suffix):
 c=http.client.HTTPSConnection('ksu.codes',timeout=15);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),10),server_hostname='ksu.codes')
 try:
  c.request('GET','/hidden/'+suffix);r=c.getresponse();assert r.status==200;return json.loads(r.read(262144))
 finally:c.close()
def rtc(policy):return {'iceServers':[],'credentialMode':'session-turn/1','turnUrls':['turns:turn.ksu.codes:443?transport=tcp'],'iceTransportPolicy':'relay','preference':{'version':'codi-session-ice/1','allowed':['relay','all'] if policy=='all' else ['relay'],'preferred':policy}}
assert before['turn']['urls']==['turns:turn.ksu.codes:443?transport=tcp']
original=public('config.json');assert original['rtc']==rtc(before['turn']['iceTransportPolicy'])
units=['codi-ksu-hidden-'+r+'.service' for r in ['issuer','steward','guest']]+['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service','codi-net-ksu-hidden-guard.service','codi-net-ksu-hidden-anonymous.service','codi-net-ksu-hidden-registered.service']
def pids():return {unit:int(run(['systemctl','show',unit,'-p','MainPID','--value'])) for unit in units}
prior=pids();assert all(prior.values())
assert '--ice-preferences' in P('/proc/'+str(prior['codi-ksu-hidden-issuer.service'])+'/cmdline').read_bytes().decode()
private=[P('/var/lib/codi-connected/guest-cookie-codi-ksu-hidden/secret'),P(before['stateRoot'])/'issuer/state/issuer.pem',P(before['stateRoot'])/'issuer/state/accounts.sqlite3']
held={str(p):sha(p) for p in private}
def notice(phase):return json.loads(run([python,'-I','-B',native/'scripts/desktop-maintenance.py','--directory',P(before['stateRoot'])/'public',phase,'--in-seconds','60' if phase=='scheduled' else '0','--duration','600','--message','Network maintenance: the sign-in service will restart shortly. Please save your work. Linux may stay open, but you may need to sign in again afterward.']))
report={'status':'PASS','action':inputs['action'],'scope':'Exact installed native14/R18, current config/hosting and identity checks; only the issuer preference policy may change; legacy relay preserved','beforeConfigSHA256':sha(path),'beforeTransportPolicy':before['turn']['iceTransportPolicy'],'requestedTransportPolicy':inputs['transport'],'beforePIDs':prior,'hostingSHA256':pins,'runtimeSourceCommit':inputs['commit'],'privateDataRestored':False,'routerFirewallPortsAndBootChanged':False}
if inputs['action']=='plan':print(json.dumps(report));raise SystemExit(0)
checkout=hosting/'sites/ksu.codes';assert run(['runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==inputs['commit']
assert not run(['runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
source=checkout/'tools/codiserver/native14-live/scripts/configure-direct-ice.py';assert sha(source)==inputs['helperSHA256']
if inputs['action']=='announce':
 current=public('api/v1/desktop-status')['maintenance'];assert current is None or current['phase']=='cancelled'
 report['notice']=notice('scheduled');print(json.dumps(report));raise SystemExit(0)
current=public('api/v1/desktop-status')['maintenance'];assert current and current['id']==inputs['noticeId'] and current['phase']=='scheduled' and current['deadline']<=int(time.time())<current['expiresAt']
notice('active')
turn=before['turn'];command=[python,'-I','-B',native/'scripts/manage-services.py','configure-turn','--config',path,'--turn-secret-file',turn['secretFile'],'--turn-transport-policy',inputs['transport']]
for url in turn['urls']:command+=['--turn-url',url]
change=json.loads(run(command));assert change['status'] in ('turn-configured','turn-already-current'),change
after=json.loads(path.read_text());expected={**before,'turn':{**turn,'iceTransportPolicy':inputs['transport']}};assert after==expected
current_pids=pids();assert all(current_pids.values()) and all(current_pids[k]==v for k,v in prior.items() if k!='codi-ksu-hidden-issuer.service')
assert all(sha(p)==value for p,value in held.items()) and all(sha(p)==value for p,value in pins.items())
now=public('config.json');assert now['identity']==original['identity'] and now['gateway']==original['gateway'] and now['guestNetwork']==original['guestNetwork']
assert now['rtc']==rtc(inputs['transport'])
assert not (path.parent/'maintenance.json').exists()
for role in ['issuer','steward','guest']:assert run(['systemctl','show','codi-ksu-hidden-'+role+'.service','-p','UnitFileState','--value'])=='disabled'
cleared=notice('cancelled');assert not cleared['servicesRestarted'] and not cleared['workSaved']
report.update(configurationResult=change,afterConfigSHA256=sha(path),afterTransportPolicy=now['rtc']['preference']['preferred'],legacyTransportPolicy=now['rtc']['iceTransportPolicy'],afterPIDs=current_pids,issuerOnlyRestarted=True,keysAccountsCookieAndOtherProcessesPreserved=True,noticeCleared=True)
receipt=P('/srv/codi-connected')/('direct-ice-policy-'+str(time.time_ns())+'-result.json')
fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w') as stream:json.dump(report,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
report.update(rootReceipt=str(receipt),rootReceiptSHA256=sha(receipt));print(json.dumps(report))
'''

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    action=p.add_mutually_exclusive_group();action.add_argument('--announce',action='store_true');action.add_argument('--apply',action='store_true')
    p.add_argument('--config-sha256',required=True);p.add_argument('--commit');p.add_argument('--notice-id');p.add_argument('--transport',choices=['all','relay'],default='all')
    a=p.parse_args()
    if not re.fullmatch('[0-9a-f]{64}',a.config_sha256):p.error('Exact config SHA256 required')
    if (a.apply or a.announce) and not re.fullmatch('[0-9a-f]{40}',a.commit or ''):p.error('Exact Git-first helper commit required')
    if a.apply and not re.fullmatch('[0-9a-f]{32}',a.notice_id or ''):p.error('Exact elapsed maintenance notice ID required')
    inputs={'action':'apply' if a.apply else 'announce' if a.announce else 'plan','configSHA256':a.config_sha256,'transport':a.transport,'commit':a.commit,'noticeId':a.notice_id,'helperSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    child=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(REMOTE)],input=json.dumps(inputs),capture_output=True,text=True,timeout=240)
    if child.returncode:raise RuntimeError(child.stderr[-5000:] or child.stdout[-5000:])
    report=json.loads(child.stdout);report['sha256']={'scripts/configure-direct-ice.py':inputs['helperSHA256']}
    output=ROOT/'.build/checks'/('direct-ice-policy-'+inputs['action']+'-result.json')
    if output.exists():output.rename(output.with_name(output.stem+'-before-'+str(__import__('time').time_ns())+'.json'))
    output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
