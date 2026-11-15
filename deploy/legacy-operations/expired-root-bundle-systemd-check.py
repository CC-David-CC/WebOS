#!/usr/bin/env python3
"""Isolated real systemd steward recovery with an interrupted managed renewal.

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
load('origin_service.expired_root_steps','expired_root_steps.py');recovery=load('origin_service.expired_root_recovery','expired_root_recovery.py');managed=load('origin_service.expired_root_managed','expired_root_managed.py')
raw=config.read_bytes();c=json.loads(raw);backend=managed.ManagedExpiredRoot(op,maintenance,config,config_sha256=hashlib.sha256(raw).hexdigest(),release_sha256=c['manifestSHA256'],seconds=600);journal=recovery.RecoveryJournal(journal_dir/'journal.json')
def phase(name):
 if mode=='crash' and name=='after-renew-once':os._exit(77)
result=recovery.execute(backend,journal,resume=mode=='resume',phase=phase);print(json.dumps(result))
'''
def run():
 from urllib.request import Request,urlopen
 token=secrets.token_hex(6);instance='codi-expired-test-'+token;stage=Path('/srv')/instance;release=stage/'release';venv=stage/'venv';python=venv/'bin/python';config=stage/'control/managed.json';state=stage/'state';candidate=stage/'candidate';private=stage/'control/expired-root-recovery';roles=['issuer','steward','guest','issuer-bootstrap'];units=[instance+'-'+role+'.service' for role in roles]
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
  tool('prepare',*args);tool('provision','--seconds','60');tool('start','--roles','issuer','steward')
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
  while time.time()<=old['exp']:time.sleep(.25)
  
  if '--failed' in sys.argv:
   sudo('systemctl','restart',instance+'-steward.service',check=False);deadline=time.monotonic()+20
   while True:
    status=sudo('systemctl','show',instance+'-steward.service','-p','ActiveState','--value').stdout.strip()
    if status=='failed':break
    if time.monotonic()>deadline:raise RuntimeError('Fixture steward did not reach failed state')
    time.sleep(.2)
  else:tool('stop','--roles','steward')
  sudo('install','-d','-m','0700',private);sudo('install','-d','-m','0755',candidate)
  bundle=ROOT/'.build/recovery-operators/expired-root-r1';bundle_hash=hashlib.sha256((bundle/'recovery-operator.json').read_bytes()).hexdigest();sudo('cp','-a',str(bundle)+'/.',candidate);sudo('chown','-R','root:root',candidate);assert digest(candidate/'recovery-operator.json')==bundle_hash;report['bundleSHA256']=bundle_hash;report['candidateSHA256']={}
  for name in ['expired_root_steps.py','expired_root_recovery.py','expired_root_managed.py','run.py']:
   expected=hashlib.sha256((bundle/name).read_bytes()).hexdigest();assert digest(candidate/name)==expected;report['candidateSHA256'][name]=expected
  lock=stage/'control/controller.lock';sudo('install','-m','0600','/dev/null',lock)
  common=['--config',config,'--config-sha256',digest(config),'--release-sha256',digest(release/'connected-release.json'),'--bundle-sha256',bundle_hash,'--base-revision','1','--seconds','600','--controller-lock',lock,'--controller-owner-uid','0','--controller-owner-gid','0']
  inspected=json.loads(sudo(python,'-I','-B',candidate/'run.py','inspect',*common,timeout=120).stdout);assert inspected['nextStep']=='renew-once' and inspected['baseRevision']==1 and inspected['liveChanged'] is False
  wrong=list(common);wrong[wrong.index('--config-sha256')+1]='0'*64;refused=sudo(python,'-I','-B',candidate/'run.py','start',*wrong,check=False,timeout=120);assert refused.returncode!=0 and sudo('test','-e',private/'journal.json',check=False).returncode!=0
  report['checks'].append('packaged runner inspects safely and refuses a wrong configuration pin')
  driver=stage/'driver.py';temp=ROOT/'.build/checks'/('expired-systemd-driver-'+token+'.py');temp.write_text(DRIVER)
  try:
   sudo('install','-m','0644',temp,driver);report['driverSHA256']=hashlib.sha256(DRIVER.encode()).hexdigest();assert digest(driver)==report['driverSHA256']
  finally:temp.unlink()
  if '--direct' in sys.argv:
   resumed=json.loads(sudo(python,'-I','-B',candidate/'run.py','start',*common,timeout=120).stdout);report['checks'].append('packaged direct start performs one journaled renewal')
  else:
   interrupted=sudo(python,'-I','-B',driver,release,candidate,config,private,'crash',check=False,timeout=120);assert interrupted.returncode==77,(interrupted.returncode,interrupted.stderr)
   assert sudo('test','-f',private/'journal.json',check=False).returncode==0 and digest(state/'steward/ledger/publisher.sqlite3')==ledger_before
   report['checks'].append('actual root renewal committed with write-ahead journal before process interruption')
   resumed=json.loads(sudo(python,'-I','-B',candidate/'run.py','resume',*common,timeout=120).stdout)
  assert resumed=={'status':'recovered','rootRevision':2};assert sudo('test','-e',private/'journal.json',check=False).returncode!=0
  status=sudo('systemctl','show',instance+'-steward.service','-p','ActiveState','-p','MainPID').stdout;assert 'ActiveState=active' in status and 'MainPID=0' not in status
  with urlopen(request,timeout=5) as response:current=json.load(response)
  seed=jose.inspect(current['discovery']['seed'],'codi-seed/1',32768)[1];assert seed['revision']==2 and time.time()<seed['exp']
  assert key_before==digest(state/'operator/root/root.pem') and issuer_before==digest(state/'issuer/state/issuer.pem') and accounts_before==digest(state/'issuer/state/accounts.sqlite3')
  report['checks'].append('actual systemd steward starts and issuer publishes the renewed signed seed')
  report['checks'].append('root and issuer keys and account database remain byte-identical')
  report.update(status='PASS',rootBefore=1,rootAfter=2,actualSystemd=True,directStart='--direct' in sys.argv,interruptedExit=None if '--direct' in sys.argv else 77)
 except Exception:report['error']=traceback.format_exc()
 finally:
  if created:
   try:
    sudo('systemctl','stop',*units,check=False)
    for unit in units:sudo('rm','-f',Path('/etc/systemd/system')/unit)
    sudo('systemctl','daemon-reload');assert stage.parent==Path('/srv') and stage.name==instance and instance.startswith('codi-expired-test-');sudo('rm','-rf','--',stage)
    report['cleanup']={'unitsRemoved':all(not (Path('/etc/systemd/system')/u).exists() for u in units),'fixtureRemoved':not stage.exists()}
    if not all(report['cleanup'].values()):report['status']='FAIL'
   except Exception:report.update(status='FAIL',cleanupError=traceback.format_exc())
 out=ROOT/('.build/checks/expired-root-bundle-systemd-r3-direct-result.json' if '--direct' in sys.argv else '.build/checks/expired-root-bundle-systemd-r3-resume-result.json');assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report['status']=='PASS'
if __name__=='__main__':sys.exit(not run())
