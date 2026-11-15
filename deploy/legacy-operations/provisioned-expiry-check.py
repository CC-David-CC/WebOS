#!/usr/bin/env python3
"""Real elapsed root expiry and explicit renewal preserve the independent issuer."""
import hashlib,json,secrets,socket,subprocess,sys,tempfile,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
from steward.protocol import jose
from cryptography.hazmat.primitives.asymmetric import ec
from codiauth.service import PROOF_TYPE
checks=ROOT/'.build/checks';run=Path(tempfile.mkdtemp(prefix='provisioned-expiry-',dir=checks));run.chmod(0o700)
fixture=tempfile.TemporaryDirectory(prefix='codi-provisioned-expiry-');folder=Path(fixture.name);runtime=folder/'runtime';authority=folder/'operator';process=None
origin='https://preview.invalid';endpoint='wss://preview.invalid/hidden/rendezvous'
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
http_port,steward_port=port(),port()
def operator(action,seconds):
 command=[sys.executable,'-B',str(ROOT/'scripts/provision-connected.py'),action,'--runtime-dir',str(runtime),'--root-dir',str(authority),'--seconds',str(seconds)]
 if action=='init':command+=['--origin',origin,'--endpoint',endpoint,'--base-path','/hidden']
 child=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=15);assert child.returncode==0,'Operator command failed'
def http(route,data=None,token=None):
 headers={'Host':'preview.invalid','Origin':origin,'Content-Type':'application/json'}
 if token:headers['Authorization']='Codi '+token
 request=urllib.request.Request('http://127.0.0.1:'+str(http_port)+route,data=None if data is None else json.dumps(data).encode(),headers=headers)
 with urllib.request.urlopen(request,timeout=3) as response:return json.load(response)
def signed(route,key,data,session=None):
 path='/hidden'+route;challenge=http('/api/v1/challenge',{'key':jose.public_jwk(key),'path':path});now=int(time.time());request=jose.dumps(data)
 proof=jose.sign({'v':1,'nonce':challenge['nonce'],'iss':session['identity']['sid'] if session else 'expiry-fixture','aud':origin,'method':'POST','path':path,'iat':now,'exp':now+60,'request_sha256':jose.digest(request)},key,PROOF_TYPE)
 return http(route,{'request':request,'proof':proof},session['session_token'] if session else None)
report={'status':'FAIL','scope':'Actual native elapsed expiry, issuer session and explicit signed restoration; no browser/WAN/public claim','fixtureDirectory':str(run)}
try:
 operator('init',30)
 command=[sys.executable,'-B',str(ROOT/'scripts/serve-connected-discovery.py'),'--runtime-dir',str(runtime),'--provisioned-steward','--origin',origin,'--endpoint',endpoint,'--base-path','/hidden','--port',str(http_port),'--steward-port',str(steward_port)]
 with (run/'service.log').open('wb') as log:process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 end=time.monotonic()+15
 while True:
  assert process.poll() is None
  try:first=http('/config.json');break
  except (OSError,urllib.error.URLError):
   assert time.monotonic()<end;time.sleep(.05)
 pid_file=runtime/'state/steward-process.json';before=json.loads(pid_file.read_text());seed=jose.inspect(first['discovery']['seed'],'codi-seed/1')[1];root_db=(authority/'authority.sqlite3').read_bytes()
 key=ec.generate_private_key(ec.SECP256R1());session=signed('/api/v1/anonymous',key,{})
 end=time.monotonic()+45
 while True:
  current=json.loads(pid_file.read_text())
  if current['status']=='delegation-expired':break
  assert process.poll() is None and time.monotonic()<end;time.sleep(.1)
 assert int(time.time())>=seed['exp'] and current['pid']==before['pid'] and current['restarts']==0
 assert not Path('/proc',str(before['pid'])).exists() and http('/config.json')['identity']['mode']=='server'
 assert (authority/'authority.sqlite3').read_bytes()==root_db,'Runtime extended its own root permission'
 expired_renew=signed('/api/v1/renew',key,{},session);assert expired_renew['identity']['sid']==session['identity']['sid']
 operator('renew',600)
 end=time.monotonic()+20
 while True:
  worker=json.loads(pid_file.read_text());config=http('/config.json')
  if worker['status']=='running' and worker['pid']!=before['pid'] and jose.inspect(config['discovery']['seed'],'codi-seed/1')[1]['revision']==2:break
  assert process.poll() is None and time.monotonic()<end;time.sleep(.1)
 assert worker['privateRun']==before['privateRun'] and worker['command']==before['command'] and worker['restarts']==1
 assert config['identity']==first['identity'] and config['discovery']['pin']==first['discovery']['pin']
 restored=signed('/api/v1/renew',key,{},session);assert restored['identity']['sid']==session['identity']['sid'] and restored['identity']['key']==session['identity']['key']
 report.update(status='PASS',elapsedExpiryEnforced=True,expiredWorkerReaped=True,noImplicitRootRenewal=True,issuerRenewedDuringExpiry=True,explicitSignedRestore=True,sameRealmRootAndServiceKey=True,sameIssuerSessionAfterRestore=True,restartBudgetCharged=worker['restarts'])
except BaseException as error:report['error']=str(error);raise
finally:
 if process is not None and process.poll() is None:
  process.terminate()
  try:process.wait(6)
  except subprocess.TimeoutExpired:process.kill();process.wait()
 report['parentReaped']=process is None or process.poll() is not None
 record=runtime/'state/steward-process.json'
 if record.exists():report['workerReaped']=not Path('/proc',str(json.loads(record.read_text())['pid'])).exists()
 fixture.cleanup();report['disposableRuntimeRemoved']=not folder.exists()
 report['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['scripts/serve-connected-discovery.py','scripts/provision-connected.py','steward/root_authority.py','scripts/provisioned-expiry-check.py']}
 (checks/'provisioned-expiry-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
