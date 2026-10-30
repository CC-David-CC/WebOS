#!/usr/bin/env python3
"""Actual immutable-release launchers: private persistence, restart and exclusion."""
import argparse,hashlib,importlib.util,json,os,secrets,shutil,signal,socket,subprocess,sys,tempfile,time,urllib.error,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'codiserver-server-v0.3.0'))
from codiauth import jose
from codiauth.service import PROOF_TYPE
from cryptography.hazmat.primitives.asymmetric import ec
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release-dir',type=Path);args=parser.parse_args();RELEASE=args.release_dir.absolute() if args.release_dir else ROOT
release_record=None
if args.release_dir:
 spec=importlib.util.spec_from_file_location('connected_export',ROOT/'scripts/export-connected.py');exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter);release_record=exporter.verify(RELEASE)
checks=ROOT/'.build/checks';checks.mkdir(parents=True,exist_ok=True)
run=Path(tempfile.mkdtemp(prefix='runtime-launcher-',dir=checks));run.chmod(0o700)
runtime_parent=Path('/run/user')/str(os.geteuid())
if not shutil.which('bwrap') or not runtime_parent.is_dir():raise SystemExit('This fixture requires bubblewrap and a private /run/user/UID directory')
fixture=tempfile.TemporaryDirectory(prefix='codi-runtime-launcher-',dir=runtime_parent);folder=Path(fixture.name)
processes=[];results=[]
report={'status':'FAIL','scope':'Actual read-only release native launchers, HTTP crypto and SQLite restart; no public service change','fixtureDirectory':str(run),'release':release_record}
origin='https://preview.invalid';base='/hidden';password=secrets.token_urlsafe(32);username='test_'+secrets.token_hex(6)
def port():
 with socket.socket() as probe:probe.bind(('127.0.0.1',0));return probe.getsockname()[1]
def sandbox(command):return ['bwrap','--die-with-parent','--ro-bind','/','/','--bind',str(folder),str(folder),'--proc','/proc','--dev','/dev','--',*[str(x) for x in command]]
def command(combined,runtime,http_port):
 launch=[sys.executable,'-B',RELEASE/'scripts'/('serve-connected-discovery.py' if combined else 'serve-connected.py'),'--runtime-dir',runtime,'--port',str(http_port),'--origin',origin,'--base-path',base]
 if combined:launch+=['--steward-port',str(port()),'--endpoint','wss://preview.invalid/hidden/rendezvous']
 return sandbox(launch)
def start(combined,runtime,http_port,label):
 launch=command(combined,runtime,http_port);info=run/(label+'.sandbox.json')
 with info.open('wb') as metadata,(run/(label+'.log')).open('wb') as output:
  child=subprocess.Popen([launch[0],'--info-fd',str(metadata.fileno()),*launch[1:]],pass_fds=(metadata.fileno(),),cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=output,stderr=subprocess.STDOUT)
 child.sandbox_info=info;child.sandbox_command=launch[launch.index('--')+1:]
 processes.append(child);return child
def terminate(child):
 if child.poll() is not None:return
 # SIGTERM to bwrap itself activates --die-with-parent's SIGKILL. Signal the
 # exact command it reported instead, then let bwrap reap that clean exit.
 pid=json.loads(child.sandbox_info.read_text())['child-pid']
 try:pidfd=os.pidfd_open(pid)
 except ProcessLookupError:pidfd=None
 if pidfd is not None:
  try:
   raw=Path('/proc',str(pid),'cmdline').read_bytes()
   if raw:
    assert raw.removesuffix(b'\0').split(b'\0')==[os.fsencode(x) for x in child.sandbox_command],'Sandbox command identity changed'
    signal.pidfd_send_signal(pidfd,signal.SIGTERM)
  except (FileNotFoundError,ProcessLookupError):pass
  finally:os.close(pidfd)
 try:child.wait(6)
 except subprocess.TimeoutExpired:child.kill();child.wait();raise AssertionError('Launcher did not shut down cleanly')
def stop(child,runtime):
 terminate(child)
 assert child.returncode==0,child.returncode
 record=runtime/'state/steward-process.json'
 if record.exists():assert not Path('/proc',str(json.loads(record.read_text())['pid'])).exists(),'Orphan steward'
 assert not list(runtime.glob('public-*')),'Staged public directory survived clean exit'
def http(http_port,route,data=None,token=None):
 headers={'Host':'preview.invalid','Origin':origin,'Content-Type':'application/json'}
 if token:headers['Authorization']='Codi '+token
 request=urllib.request.Request('http://127.0.0.1:'+str(http_port)+route,data=None if data is None else json.dumps(data).encode(),headers=headers)
 try:
  with urllib.request.urlopen(request,timeout=3) as response:return response.status,json.load(response)
 except urllib.error.HTTPError as error:return error.code,None
def ready(child,http_port):
 deadline=time.monotonic()+15
 while True:
  if child.poll() is not None:raise AssertionError('Launcher exited before readiness; inspect fixture log')
  try:
   status,config=http(http_port,'/config.json')
   if status==200:return config
  except (OSError,urllib.error.URLError):pass
  if time.monotonic()>deadline:raise AssertionError('Readiness timed out')
  time.sleep(.05)
def signed(http_port,route,key,data,session=None):
 path=base+route;status,challenge=http(http_port,'/api/v1/challenge',{'key':jose.public_jwk(key),'path':path});assert status==200
 now=int(time.time());request=jose.dumps(data)
 proof=jose.sign({'v':1,'nonce':challenge['nonce'],'iss':session['identity']['sid'] if session else 'runtime-check','aud':origin,'method':'POST','path':path,'iat':now,'exp':now+60,'request_sha256':jose.digest(request)},key,PROOF_TYPE)
 return http(http_port,route,{'request':request,'proof':proof},session['session_token'] if session else None)
try:
 # A command running in this exact sandbox must receive EROFS for release writes.
 target=run/'write-probe'
 probe=subprocess.run(sandbox([sys.executable,'-B','-c',"import errno,pathlib,sys\ntry:pathlib.Path(sys.argv[1]).write_text('unexpected')\nexcept OSError as e:sys.exit(0 if e.errno==errno.EROFS else 2)\nsys.exit(1)",target]),capture_output=True,timeout=5)
 assert probe.returncode==0 and not target.exists(),'Read-only mount was not enforced'
 for combined in [False,True]:
  label='combined' if combined else 'standalone';runtime=folder/label;runtime.mkdir(mode=0o700);http_port=port()
  child=start(combined,runtime,http_port,label+'-first');config=ready(child,http_port)
  assert config['identity']['apiBase']==base+'/api/v1' and config['identity']['authorityClass']=='development'
  key=ec.generate_private_key(ec.SECP256R1());status,session=signed(http_port,'/api/v1/auth',key,{'username':username,'password':password});assert status==200
  assert session['identity']['kind']=='registered'
  issuer_digest=hashlib.sha256((runtime/'state/issuer.pem').read_bytes()).hexdigest()
  for name in ['issuer.pem','accounts.sqlite3']:assert (runtime/'state'/name).stat().st_mode&0o777==0o600
  # A second launch must fail before opening its different HTTP listener.
  other_port=port();second=subprocess.run(command(combined,runtime,other_port),capture_output=True,timeout=10)
  assert second.returncode!=0 and b'already in use' in second.stderr
  with socket.socket() as connection:assert connection.connect_ex(('127.0.0.1',other_port))!=0
  for route in ['/state/issuer.pem','/state/accounts.sqlite3','/.runtime.lock','/steward-private/provision.json']:
   assert http(http_port,route)[0]==404,'Private runtime path exposed'
  stop(child,runtime)
  child=start(combined,runtime,http_port,label+'-restart');config2=ready(child,http_port)
  assert config2['identity']['authorityKeys']==config['identity']['authorityKeys']
  assert hashlib.sha256((runtime/'state/issuer.pem').read_bytes()).hexdigest()==issuer_digest
  assert signed(http_port,'/api/v1/renew',key,{},session)[0]==401,'RAM session survived issuer restart'
  new_key=ec.generate_private_key(ec.SECP256R1());status,new_session=signed(http_port,'/api/v1/auth',new_key,{'username':username,'password':password});assert status==200
  assert new_session['identity']['sub']==session['identity']['sub'] and new_session['identity']['sid']!=session['identity']['sid']
  if combined:
   assert config2['discovery']['pin']['realm']!=config['discovery']['pin']['realm'],'Disposable discovery was mislabeled persistent'
  stop(child,runtime)
  results.append({'launcher':label,'readOnlyReleaseEnforced':True,'registeredSubjectAndIssuerKeyPersisted':True,'oldRamSessionRefused':True,'concurrentLauncherRefusedBeforeBind':True,'privateHttpPathsRefused':True,'gracefulCleanup':True,'discoveryStillDisposable':combined})
 report.update(status='PASS',cases=results)
except BaseException as error:report['error']=str(error);raise
finally:
 for child in processes:
  if child.poll() is None:
   try:terminate(child)
   except (AssertionError,OSError,ValueError):child.kill();child.wait()
 report['childrenReaped']=all(child.poll() is not None for child in processes)
 fixture.cleanup();report['disposableRuntimeRemoved']=not folder.exists()
 report['sha256']={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['origin_service/runtime.py','scripts/serve-connected.py','scripts/serve-connected-discovery.py','scripts/runtime-launcher-check.py']}
 (checks/('runtime-launcher-release-result.json' if args.release_dir else 'runtime-launcher-result.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
