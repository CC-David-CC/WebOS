#!/usr/bin/env python3
"""Read and verify the installed private relay, certificate job and timer."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import hashlib,json,os,pathlib,stat,subprocess,sys
Path=pathlib.Path
receipt=json.loads(Path('/srv/codi-relay/ksu-private-relay-install-result.json').read_text())
assert receipt['status']=='PASS'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),text=True,timeout=45).strip()
operator=Path(receipt['operator']);runtime=Path(receipt['runtime'])
for folder,manifest in [(operator,'relay-operator.json'),(runtime,'runtime.json')]:
 assert digest(folder/manifest)==folder.name
 files=json.loads((folder/manifest).read_text())['files']
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}=={manifest,*files}
 for p in [folder,*folder.rglob('*')]:
  i=p.lstat();assert stat.S_ISDIR(i.st_mode) or stat.S_ISREG(i.st_mode)
  assert i.st_uid==i.st_gid==0 and not i.st_mode&0o022
  if p.is_file():
   assert i.st_nlink==1
   if p.name!=manifest:assert files[str(p.relative_to(folder))]=={'bytes':i.st_size,'sha256':digest(p)}
sys.path.insert(0,str(operator));from relay_service.manager import Manager;from relay_service import certificates
manager=Manager(receipt['configDirectory'])
with manager.locked():
 value=manager.load();manager.installed(value);ready=manager.ready(value);state=manager.status()
 assert not state['pendingTransition'] and state['certificate']['validNow']
 units=certificates.refresh_units(manager,operator,Path('/srv/codi-connected/venvs/517179c/bin/python'))['units']
 for name,body in units.items():
  file=Path('/etc/systemd/system')/name;i=file.lstat();assert stat.S_ISREG(i.st_mode) and i.st_uid==i.st_gid==0 and stat.S_IMODE(i.st_mode)==0o644 and file.read_text()==body
 processes={}
 for name in manager.names(value)[:2]:
  props=dict(line.split('=',1) for line in run(['systemctl','show',name,'-p','MainPID','-p','ActiveState','-p','NoNewPrivileges','-p','CapabilityBoundingSet']).splitlines())
  pid=int(props['MainPID']);assert props['ActiveState']=='active' and props['NoNewPrivileges']=='yes' and props['CapabilityBoundingSet']==''
  info=dict(line.split(':',1) for line in (Path('/proc')/str(pid)/'status').read_text().splitlines())
  uids=set(map(int,info['Uid'].split()));assert len(uids)==1 and 0 not in uids and int(info['CapEff'],16)==0 and info['NoNewPrivs'].strip()=='1'
  processes[name]={'pid':pid,'uid':next(iter(uids)),'namespace':os.readlink('/proc/'+str(pid)+'/ns/net'),'noCapabilities':True,'noNewPrivileges':True}
 assert len({p['namespace'] for p in processes.values()})==1 and len({p['uid'] for p in processes.values()})==2
 pid=next(iter(processes.values()))['pid'];assert processes[next(iter(processes))]['namespace']!=os.readlink('/proc/self/ns/net')
 assert [i['ifname'] for i in json.loads(run(['nsenter','-t',pid,'-n','ip','-j','address','show']))]==['lo']
 probe="import errno,json,socket\ndef connect(h,p):\n with socket.socket() as s:s.settimeout(1);return s.connect_ex((h,p))\na=connect('1.1.1.1',443);b=connect('127.0.0.1',8118);assert a==errno.ENETUNREACH and b==errno.ECONNREFUSED;print(json.dumps({'internetError':a,'hostIssuerError':b}))"
 probes=json.loads(run(['nsenter','-t',pid,'-n','/usr/bin/python3','-B','-c',probe]))
timer=value['instance']+'-certificate-refresh.timer';job=value['instance']+'-certificate-refresh.service'
timer_state=dict(line.split('=',1) for line in run(['systemctl','show',timer,'-p','ActiveState','-p','UnitFileState','-p','LastTriggerUSec','-p','NextElapseUSecMonotonic']).splitlines())
job_state=dict(line.split('=',1) for line in run(['systemctl','show',job,'-p','Result','-p','ExecMainStatus']).splitlines())
assert timer_state['ActiveState']=='active' and timer_state['UnitFileState']=='static' and timer_state['LastTriggerUSec'] and timer_state['NextElapseUSecMonotonic']
assert job_state=={'Result':'success','ExecMainStatus':'0'}
for unit in [*manager.names(value),*units]:
 assert subprocess.run(['systemctl','is-enabled',unit],capture_output=True,text=True).stdout.strip()=='static'
assert all(processes[n]['pid']==p['pid'] for n,p in receipt['processes'].items())
report={'status':'PASS','scope':'Installed immutable private TURN, no-capability worker isolation, real TLS/401 readiness and an actually triggered certificate timer; no public/WAN claim','operatorManifestSHA256':operator.name,'runtimeManifestSHA256':runtime.name,'processes':processes,'namespaceProbes':probes,'certificate':state['certificate'],'timer':timer_state,'certificateJob':job_state,'scheduledCertificateJobActuallyTriggered':True,'relayPidsUnchangedAfterScheduledJob':True,'onlyLoopbackInterface':True,'normalUnitsEnabledForBoot':False,'publicTurnConfigured':'codi_shared_ingress = true' in Path('/home/dflanag3/webhost-sites/sites.toml').read_text(),'installationReceiptSHA256':digest(Path('/srv/codi-relay/ksu-private-relay-install-result.json'))}
print(json.dumps(report))
'''

if __name__ == '__main__':
    process = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'box-webhost', 'sudo', '-n', '/srv/codi-connected/venvs/517179c/bin/python', '-B', '-c', shlex.quote(REMOTE)], capture_output=True, text=True, timeout=90)
    if process.returncode:
        raise SystemExit(process.stderr or process.stdout)
    report = json.loads(process.stdout)
    report['checkerSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT / '.build/checks/webhost-private-relay-health-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
