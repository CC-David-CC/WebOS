#!/usr/bin/env python3
"""Read actual native process credentials and the latest eight-site smoke receipt."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import json,pathlib,pwd,subprocess
Path=pathlib.Path
config=json.loads(Path('/etc/codi-connected/ksu/managed.json').read_text());processes={}
def show(role,*fields):
 command=['systemctl','show','codi-ksu-hidden-'+role+'.service']
 for field in fields:command+=['-p',field]
 return dict(line.split('=',1) for line in subprocess.run(command,check=True,capture_output=True,text=True).stdout.splitlines())
for role in ['issuer','steward']:
 unit=show(role,'MainPID','ActiveState','FragmentPath','NoNewPrivileges','ProtectSystem','CapabilityBoundingSet');pid=int(unit['MainPID']);assert pid>0 and unit['ActiveState']=='active'
 assert unit['FragmentPath']=='/etc/systemd/system/codi-ksu-hidden-'+role+'.service' and unit['NoNewPrivileges']=='yes' and unit['ProtectSystem']=='strict' and unit['CapabilityBoundingSet']==''
 status=dict(line.split(':',1) for line in (Path('/proc')/str(pid)/'status').read_text().splitlines());account=pwd.getpwnam('codi-'+role)
 assert set(map(int,status['Uid'].split()))=={account.pw_uid} and set(map(int,status['Gid'].split()))=={account.pw_gid} and set(map(int,status['Groups'].split()))<={account.pw_gid}
 assert account.pw_uid>0 and int(status['CapEff'],16)==0 and status['NoNewPrivs'].strip()=='1'
 processes[role]={'pid':pid,'uid':account.pw_uid,'gid':account.pw_gid,'groups':list(map(int,status['Groups'].split())),'capabilities':status['CapEff'].strip(),'noNewPrivileges':status['NoNewPrivs'].strip()}
for role in ['guest','issuer-bootstrap']:
 unit=show(role,'MainPID','ActiveState');assert unit=={'MainPID':'0','ActiveState':'inactive'}
smoke=json.loads(Path('/home/dflanag3/webhost-sites/reports/private/codi-native-preview-20261022.json').read_text());sites={name:value['result'] for name,value in smoke['sites'].items()};assert len(sites)==8 and set(sites.values())=={'PASS'}
assert config['release']=='/srv/codi-connected/releases/f2fbd4d' and config['manifestSHA256']=='e6bd7e6df07544c58ce57efe3672f18df793dd5fbea381d05d89f2953f0baace'
result={'status':'PASS','scope':'Actual post-upgrade private process credentials and eight-site HTTPS health; no independent WAN claim','processes':processes,'siteResults':sites,'smokeObservedUTC':smoke['time'],'configVersion':config['version'],'onlineRoleRelease':config['release'],'manifestSHA256':config['manifestSHA256'],'currentWebsite':str(Path('/srv/webapps/ksu.codes/current').resolve()),'guestAndBootstrapInactive':True,'pingGroupRange':Path('/proc/sys/net/ipv4/ping_group_range').read_text().split()}
assert result['currentWebsite']=='/srv/webapps/ksu.codes/releases/20261021T125622370238Z-279f978f' and result['pingGroupRange']==['1000','1000']
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':
 process=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-'],input=REMOTE,text=True,capture_output=True,timeout=45)
 if process.returncode:raise SystemExit(process.stderr or process.stdout)
 report=json.loads(process.stdout);(ROOT/'.build/checks/preview-webhost-health-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
