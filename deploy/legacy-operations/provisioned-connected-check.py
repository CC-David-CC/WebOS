#!/usr/bin/env python3
"""Actual provision/init/renew/restart/fail-closed checks over native HTTP."""
import hashlib,json,os,secrets,socket,subprocess,sys,tempfile,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from steward.root_authority import RootAuthority,atomic_private
from steward.protocol import jose
checks=ROOT/'.build/checks';run=Path(tempfile.mkdtemp(prefix='provisioned-connected-',dir=checks));run.chmod(0o700)
fixture=tempfile.TemporaryDirectory(prefix='codi-provisioned-');folder=Path(fixture.name);runtime=folder/'runtime';authority=folder/'operator-root'
origin='https://preview.invalid';endpoint='wss://preview.invalid/hidden/rendezvous';processes=[]
report={'status':'FAIL','scope':'Actual local operator CLI, supervised native workers and HTTP metadata; no public/WAN proof','fixtureDirectory':str(run)}
def free_port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
http_port,steward_port=free_port(),free_port()
def operator(command,seconds=None):
 arguments=[sys.executable,'-B',str(ROOT/'scripts/provision-connected.py'),command,'--runtime-dir',str(runtime),'--root-dir',str(authority)]
 if seconds:arguments+=['--seconds',str(seconds)]
 if command=='init':arguments+=['--origin',origin,'--endpoint',endpoint,'--base-path','/hidden']
 return subprocess.run(arguments,cwd=ROOT,capture_output=True,timeout=15)
def command():return [sys.executable,'-B',str(ROOT/'scripts/serve-connected-discovery.py'),'--runtime-dir',str(runtime),'--provisioned-steward','--origin',origin,'--endpoint',endpoint,'--base-path','/hidden','--port',str(http_port),'--steward-port',str(steward_port)]
def config():
 with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(http_port)+'/config.json',headers={'Host':'preview.invalid'}),timeout=3) as response:return json.load(response)
def start(label):
 with (run/(label+'.log')).open('wb') as log:process=subprocess.Popen(command(),cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 processes.append(process);deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  if process.poll() is not None:raise AssertionError('Native launcher failed; inspect '+label+'.log')
  try:return process,config()
  except (OSError,urllib.error.URLError):time.sleep(.05)
 raise AssertionError('Native readiness timeout')
def stop(process):
 process.terminate();process.wait(6);assert process.returncode==0
 record=json.loads((runtime/'state/steward-process.json').read_text());assert not Path('/proc',str(record['pid'])).exists()
def rejected():
 child=subprocess.run(command(),cwd=ROOT,capture_output=True,timeout=15);assert child.returncode!=0
 with socket.socket() as probe:assert probe.connect_ex(('127.0.0.1',http_port))!=0
try:
 initialized=operator('init',600);assert initialized.returncode==0,initialized.stderr.decode()
 private=runtime/'steward-private/provisioned';provision_path=private/'provision.json';initial=json.loads(provision_path.read_text())
 root_bytes=(authority/'root.pem').read_bytes();root_db_before=(authority/'authority.sqlite3').read_bytes()
 assert all(root_bytes not in p.read_bytes() for p in runtime.rglob('*') if p.is_file())
 process,first=start('first');assert first['discovery']['seed']==initial['seed'] and first['identity']['mode']=='server'
 stop(process);process,second=start('restart')
 assert first['discovery']==second['discovery'] and first['identity']==second['identity'],'Restart changed identity, realm, scope or cached publication'
 assert (authority/'authority.sqlite3').read_bytes()==root_db_before,'Online service changed operator state'
 renewed=operator('renew',900);assert renewed.returncode==0,renewed.stderr.decode();new=json.loads(provision_path.read_text());assert new['seed']!=initial['seed']
 deadline=time.monotonic()+45
 while time.monotonic()<deadline:
  current=config()
  if current['discovery']['seed']==new['seed']:break
  assert process.poll() is None;time.sleep(.1)
 else:raise AssertionError('Running worker did not publish new signed root policy')
 assert current['discovery']['pin']==first['discovery']['pin'] and current['discovery']['scope']==first['discovery']['scope'] and current['identity']==first['identity']
 assert jose.inspect(new['seed'],'codi-seed/1')[1]['revision']==2
 assert jose.inspect(current['discovery']['descriptor'],'codi-steward/1')[1]['revision']>jose.inspect(first['discovery']['descriptor'],'codi-steward/1')[1]['revision']
 stop(process)
 # Native restart retains the new root revision and same publication floor.
 process,third=start('renewed-restart');assert third['discovery']==current['discovery'];stop(process)
 # Partially restored operator state must not overwrite a newer live provision.
 latest_db=(authority/'authority.sqlite3').read_bytes();(authority/'authority.sqlite3').write_bytes(root_db_before)
 rejected_export=operator('export');assert rejected_export.returncode!=0 and provision_path.read_bytes()==jose.dumps(new).encode()
 (authority/'authority.sqlite3').write_bytes(latest_db)
 provision_path.unlink();reexported=operator('export');assert reexported.returncode==0 and json.loads(provision_path.read_text())==new
 # Correctly signed provision does not authorize a different identity policy.
 changed={**new,'identity_policy':{**new['identity_policy'],'authorityKeys':[]}};atomic_private(provision_path,jose.dumps(changed).encode());rejected();atomic_private(provision_path,jose.dumps(new).encode())
 ledger=private/'ledger/publisher.sqlite3';saved=ledger.with_name('retained.sqlite3');ledger.rename(saved);rejected();assert not ledger.exists();saved.rename(ledger)
 before=provision_path.read_bytes();again=operator('init',600);assert again.returncode!=0 and provision_path.read_bytes()==before
 root=RootAuthority(authority)
 with root.operator():
  busy=operator('renew',1200);assert busy.returncode!=0 and provision_path.read_bytes()==before
 assert (authority/'root.pem').read_bytes()==root_bytes
 report.update(status='PASS',stableRestart=True,explicitSignedLiveRenewal=True,newRootRevision=2,issuerAndScopeUnchanged=True,operatorRootNotInRuntime=True,onlineServiceDoesNotWriteRootState=True,rootRollbackRefused=True,committedExportRecovery=True,wrongIdentityPolicyRefused=True,missingLedgerNotReinitialized=True,repeatInitRefused=True,concurrentOperatorRefused=True)
except BaseException as error:report['error']=str(error);raise
finally:
 for process in processes:
  if process.poll() is None:
   process.terminate()
   try:process.wait(6)
   except subprocess.TimeoutExpired:process.kill();process.wait()
 report['childrenReaped']=all(p.poll() is not None for p in processes)
 fixture.cleanup();report['disposableRuntimeRemoved']=not folder.exists()
 report['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['scripts/provision-connected.py','scripts/serve-connected-discovery.py','steward/root_authority.py','scripts/provisioned-connected-check.py']}
 (checks/'provisioned-connected-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
