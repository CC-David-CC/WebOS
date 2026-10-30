#!/usr/bin/env python3
"""Isolated real systemd live steward renewal after an interrupted operator.

Only uniquely named local /srv fixture, ports and unit files are touched. No
webhost, existing authority, router, firewall, user data or boot enablement.
"""
import hashlib,json,secrets,socket,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

DRIVER=r'''
import hashlib,importlib.util,json,os,sys
from pathlib import Path
release=Path(sys.argv[1]);candidate=Path(sys.argv[2]);config=Path(sys.argv[3]);journal_dir=Path(sys.argv[4]);mode=sys.argv[5]
sys.path.insert(0,str(release))
spec=importlib.util.spec_from_file_location('fixture_installed_operator',release/'scripts/manage-services.py');op=importlib.util.module_from_spec(spec);sys.modules[spec.name]=op;spec.loader.exec_module(op)
from origin_service import maintenance
def load(name,file):
 s=importlib.util.spec_from_file_location(name,candidate/file);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
for name in ['expired_root_steps','expired_root_recovery','expired_root_managed','live_root_renewal','live_root_journal','live_root_managed']:load('origin_service.'+name,name+'.py')
from origin_service.live_root_journal import LiveRenewalJournal,execute
from origin_service.live_root_managed import ManagedLiveRenewal
raw=config.read_bytes();c=json.loads(raw);backend=ManagedLiveRenewal(op,maintenance,config,config_sha256=hashlib.sha256(raw).hexdigest(),release_sha256=c['manifestSHA256'],seconds=1200,renewal_window=600);journal=LiveRenewalJournal(journal_dir/'root-journal.json')
def phase(name):
 if mode=='crash' and name=='after-renew-once':os._exit(77)
result=execute(backend,journal,resume=mode=='resume',phase=phase);print(json.dumps(result))
'''

def run():
 from urllib.request import Request,urlopen
 token=secrets.token_hex(6);instance='codi-live-test-'+token;stage=Path('/srv')/instance;release=stage/'release';venv=stage/'venv';python=venv/'bin/python';config=stage/'control/managed.json';state=stage/'state';candidate=stage/'candidate';private=stage/'control/recovery-private';roles=['issuer','steward','guest','issuer-bootstrap'];units=[instance+'-'+role+'.service' for role in roles]
 def command(args,*,check=True,timeout=120):
  result=subprocess.run([str(x) for x in args],capture_output=True,text=True,check=False,timeout=timeout)
  if check and result.returncode:raise RuntimeError('Fixture command failed: '+result.stderr[-6000:])
  return result
 def sudo(*args,**kw):return command(['sudo','-n',*args],**kw)
 def tool(action,*args):return json.loads(sudo(python,'-I','-B',release/'scripts/manage-services.py',action,'--config',config,*args).stdout)
 def port():
  with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
 def digest(path):return sudo('/usr/bin/sha256sum',path).stdout.split()[0]
 report={'status':'FAIL','scope':__doc__,'checks':[],'productionChanged':False};created=False
 try:
  source=ROOT/'.build/releases/connected-browser-files-r1';assert hashlib.sha256((source/'connected-release.json').read_bytes()).hexdigest()=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46';ports={name:port() for name in ['issuer','steward','guest']};assert len(set(ports.values()))==3
  sudo('mkdir','-m','0755',stage);created=True;sudo('cp','-a',source,release);sudo('cp','-a',ROOT/'.venv',venv);sudo('chown','-R','root:root',stage);sudo('chmod','-R','go-w',stage)
  origin='https://127.0.0.1:8446';args=['--release',release,'--python',python,'--state-root',state,'--unit-dir','/etc/systemd/system','--instance',instance,'--origin',origin,'--base-path','',*[item for role in ports for item in ['--'+role+'-port',str(ports[role])]]]
  tool('prepare',*args);tool('provision','--seconds','600');tool('start','--roles','issuer','steward')
  request=Request('http://127.0.0.1:'+str(ports['issuer'])+'/config.json',headers={'Host':'127.0.0.1:8446'});deadline=time.monotonic()+15
  while True:
   with urlopen(request,timeout=3) as response:public=json.load(response)
   if public.get('discovery'):break
   if time.monotonic()>deadline:raise RuntimeError('Fixture discovery did not initialize')
   time.sleep(.1)
  from steward.protocol import jose
  old=jose.inspect(public['discovery']['seed'],'codi-seed/1',32768)[1];assert old['revision']==1
  tool('stop','--roles','issuer','steward');sudo('install','-d','-m','0700',stage/'backups');tool('backup','--output',stage/'backups/initial');tool('start','--roles','issuer','steward')
  key_before=digest(state/'operator/root/root.pem');issuer_before=digest(state/'issuer/state/issuer.pem');accounts_before=digest(state/'issuer/state/accounts.sqlite3');ledger_before=digest(state/'steward/ledger/publisher.sqlite3')
  sudo('install','-d','-m','0700',private);sudo('install','-d','-m','0755',candidate)
  report['candidateSHA256']={}
  for name in ['expired_root_steps.py','expired_root_recovery.py','expired_root_managed.py','live_root_renewal.py','live_root_journal.py','live_root_managed.py']:
   source_file=ROOT/'origin_service'/name;expected=hashlib.sha256(source_file.read_bytes()).hexdigest();sudo('install','-m','0644',source_file,candidate/name);assert digest(candidate/name)==expected;report['candidateSHA256'][name]=expected
  driver=stage/'driver.py';temp=ROOT/'.build/checks'/('expired-systemd-driver-'+token+'.py');temp.write_text(DRIVER)
  try:
   sudo('install','-m','0644',temp,driver);report['driverSHA256']=hashlib.sha256(DRIVER.encode()).hexdigest();assert digest(driver)==report['driverSHA256']
  finally:temp.unlink()
  interrupted=sudo(python,'-I','-B',driver,release,candidate,config,private,'crash',check=False,timeout=120);assert interrupted.returncode==77,(interrupted.returncode,interrupted.stderr)
  assert sudo('test','-f',private/'root-journal.json',check=False).returncode==0
  report['checks'].append('actual root renewal committed with write-ahead journal before process interruption')
  resumed=json.loads(sudo(python,'-I','-B',driver,release,candidate,config,private,'resume',timeout=120).stdout);assert resumed=={'status':'renewed','rootRevision':2};assert sudo('test','-e',private/'root-journal.json',check=False).returncode!=0
  status=sudo('systemctl','show',instance+'-steward.service','-p','ActiveState','-p','MainPID').stdout;assert 'ActiveState=active' in status and 'MainPID=0' not in status
  with urlopen(request,timeout=5) as response:current=json.load(response)
  seed=jose.inspect(current['discovery']['seed'],'codi-seed/1',32768)[1];assert seed['revision']==2 and time.time()<seed['exp']
  assert key_before==digest(state/'operator/root/root.pem') and issuer_before==digest(state/'issuer/state/issuer.pem') and accounts_before==digest(state/'issuer/state/accounts.sqlite3')
  report['checks'].append('actual running systemd steward publishes the renewed signed seed')
  report['checks'].append('root and issuer keys and account database remain byte-identical')
  report.update(status='PASS',rootBefore=1,rootAfter=2,actualSystemd=True,interruptedExit=77)
 except Exception:report['error']=traceback.format_exc()
 finally:
  if created:
   try:
    sudo('systemctl','stop',*units,check=False)
    for unit in units:sudo('rm','-f',Path('/etc/systemd/system')/unit)
    sudo('systemctl','daemon-reload');assert stage.parent==Path('/srv') and stage.name==instance and instance.startswith('codi-live-test-');sudo('rm','-rf','--',stage)
    report['cleanup']={'unitsRemoved':all(not (Path('/etc/systemd/system')/u).exists() for u in units),'fixtureRemoved':not stage.exists()}
    if not all(report['cleanup'].values()):report['status']='FAIL'
   except Exception:report.update(status='FAIL',cleanupError=traceback.format_exc())
 out=ROOT/'.build/checks/live-root-systemd-r1-result.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report['status']=='PASS'
if __name__=='__main__':sys.exit(not run())
