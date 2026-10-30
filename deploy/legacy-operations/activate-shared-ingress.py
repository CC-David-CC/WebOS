#!/usr/bin/env python3
"""Validate/activate shared ingress with guarded rollback and durable recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import copy,datetime,fcntl,hashlib,http.client,importlib,json,os,pathlib,pwd,secrets,shutil,socket,ssl,stat,struct,subprocess,sys,tempfile,time,types
Path=pathlib.Path;inputs=json.load(sys.stdin);root=Path('/home/dflanag3/webhost-sites');sys.path.insert(0,str(root/'ops'));import common;import webctl as ctl
assert os.geteuid()==0
class RollbackExercise(Exception):pass
source=root/'ops/common.py';manifest=root/'sites.toml';unit=Path('/etc/systemd/system/codi-shared-ingress.service');dropin=Path('/etc/systemd/system/caddy.service.d/30-codi-ingress.conf');config=Path('/etc/codi-ingress/haproxy.cfg');state=Path('/var/lib/codi-ingress');journal=state/'maintenance.json';latest=state/'last-transition.json';receipt=Path('/srv/codi-ingress/ksu-shared-ingress-activation-result.json')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,check=True,timeout=90):
 p=subprocess.run(list(map(str,args)),check=check,capture_output=True,text=True,timeout=timeout);return p.stdout.strip()
def protected(directory,mode=0o755):
 for p in [*reversed(directory.parents),directory]:
  if not p.exists():p.mkdir(mode=mode if p==directory else 0o755)
  i=p.lstat();assert stat.S_ISDIR(i.st_mode) and i.st_uid==0 and not i.st_mode&0o022
def atomic(p,raw,mode=0o600):
 protected(p.parent,0o700 if p.parent==state else 0o755);fd,name=tempfile.mkstemp(prefix='.'+p.name+'-',dir=p.parent)
 try:
  os.fchmod(fd,mode)
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(name,p);fd=os.open(p.parent,os.O_DIRECTORY);os.fsync(fd);os.close(fd)
 finally:Path(name).unlink(missing_ok=True)
def save(p,value):atomic(p,(json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def private_json(p):
 i=p.lstat();assert stat.S_ISREG(i.st_mode) and i.st_uid==i.st_gid==0 and stat.S_IMODE(i.st_mode)==0o600 and i.st_nlink==1;return json.loads(p.read_text())
def reload_generator():
 importlib.invalidate_caches();importlib.reload(common)
 for n in ['caddy','load','dump','validate','unit']:setattr(ctl,n,getattr(common,n))
def archive(t,outcome):
 t={**t,'outcome':outcome};save(journal,t);history=state/'history';protected(history,0o700);os.replace(journal,history/(t['id']+'-'+outcome+'.json'))
def restore(t):
 # An unrelated edit must not be overwritten during automatic recovery.
 for p,n in [(source,'common.ingress.py'),(manifest,'sites.ingress.toml')]:assert digest(p.read_bytes()) in (digest(t['before'][str(p)]['text'].encode()),digest(t['files'][n].encode()))
 assert digest(Path('/etc/codi-connected/ksu/managed.json').read_bytes())==t['nativeConfigSHA256']
 run(['systemctl','stop',unit.name],False)
 for p,n in [(unit,'codi-shared-ingress.service'),(dropin,'30-codi-ingress.conf'),(config,'haproxy.cfg')]:
  if p.exists():assert p.read_text()==t['files'][n];p.unlink()
 run(['systemctl','daemon-reload'])
 for p in [source,manifest]:
  previous=t['before'][str(p)];ctl.write(p,previous['text'].encode(),previous['mode'],previous['uid'],previous['gid'],False)
 reload_generator()
 if digest(Path('/etc/caddy/Caddyfile').read_bytes())!=t['beforeCaddySHA256']:ctl.caddy_apply(ctl.load(),'production')
 assert digest(Path('/etc/caddy/Caddyfile').read_bytes())==t['beforeCaddySHA256']
 run(['systemctl','reset-failed',unit.name],False)
def https(path):
 c=http.client.HTTPSConnection('ksu.codes',timeout=15);c.sock=ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname='ksu.codes')
 try:c.request('GET',path);r=c.getresponse();raw=r.read(524289);assert len(raw)<=524288;return r.status,dict(r.headers),raw
 finally:c.close()
def pid(name):return run(['systemctl','show',name,'-p','MainPID','--value'])
with (root/'.controller.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if inputs['action'] in ['recover','rollback']:
  if inputs['action']=='recover':
   if not journal.exists():print(json.dumps({'status':'PASS','action':'no-pending-transition'}));raise SystemExit(0)
   t=private_json(journal)
  else:
   assert not journal.exists();t=private_json(latest);assert digest(source.read_bytes())==digest(t['files']['common.ingress.py'].encode()) and digest(manifest.read_bytes())==digest(t['files']['sites.ingress.toml'].encode());save(journal,{**t,'phase':'prepared'})
  assert t['version']=='codi-shared-ingress-transition/1' and t['phase'] in ['prepared','committed']
  if t['phase']=='committed' and inputs['action']=='recover':
   for p,n in [(source,'common.ingress.py'),(manifest,'sites.ingress.toml'),(unit,'codi-shared-ingress.service'),(dropin,'30-codi-ingress.conf'),(config,'haproxy.cfg')]:assert p.read_text()==t['files'][n]
   assert Path('/etc/caddy/Caddyfile').read_text()==t['files']['Caddyfile.production'];assert run(['systemctl','is-active',unit.name])=='active'
   save(receipt,t['report']);save(latest,t);archive(t,'committed-recovered');result={'status':'PASS','action':'committed-state-preserved','activation':t['report']}
  else:
   restore(t);archive(t,'rolled-back');result={'status':'PASS','action':'prior-hosting-restored','sourceSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest.read_bytes())};save(Path('/srv/codi-ingress/ksu-shared-ingress-rollback-result.json'),result)
  print(json.dumps(result));raise SystemExit(0)
 assert not journal.exists() and not unit.exists() and not dropin.exists() and not config.exists()
 props=run(['systemctl','show',unit.name,'-p','ActiveState','-p','FragmentPath','-p','DropInPaths'],False)
 assert 'ActiveState=active' not in props and not any(line.split('=',1)[1] for line in props.splitlines() if line.startswith(('FragmentPath=','DropInPaths=')))
 files=inputs['files'];pins=inputs['pins'];assert pins['status']=='PASS'
 assert set(files)==set(pins['candidateFilesSHA256'])=={'common.ingress.py','sites.ingress.toml','Caddyfile.production','Caddyfile.prepare','haproxy.cfg','codi-shared-ingress.service','30-codi-ingress.conf'}
 for name,raw in files.items():assert digest(raw.encode())==pins['candidateFilesSHA256'][name]
 assert digest(source.read_bytes())==pins['originalGeneratorSHA256'] and digest(manifest.read_bytes())==pins['originalManifestSHA256']
 assert not source.is_symlink() and not manifest.is_symlink() and ctl.current_mode()=='production'
 data=ctl.load();assert not data.get('codi_shared_ingress');assert common.caddy(data,'production')==Path('/etc/caddy/Caddyfile').read_text()
 domains=sorted(s['domain'] for s in data['sites'] if s['enabled']);assert domains==pins['siteDomains']
 candidate=types.ModuleType('reviewed_ingress');candidate.__file__=str(source);exec(compile(files['common.ingress.py'],str(source),'exec'),candidate.__dict__)
 proposed=candidate.tomllib.loads(files['sites.ingress.toml']);expected=copy.deepcopy(data);expected['codi_shared_ingress']=True;candidate.validate(proposed);assert proposed==expected
 for mode in ['prepare','production']:
  assert candidate.caddy(data,mode)==common.caddy(data,mode) and candidate.caddy(proposed,mode)==files['Caddyfile.'+mode]
 for site in data['sites']:assert candidate.unit(site)==common.unit(site)
 # Byte-for-byte site policy/route preservation after removing only the
 # reviewed listener additions and catchall port change.
 extras='\thttp_port 8080\n\thttps_port 8443\n\tdefault_bind 127.0.0.1\n'
 wrappers='\t\tlistener_wrappers {\n\t\t\tproxy_protocol {\n\t\t\t\ttimeout 1s\n\t\t\t\tallow 127.0.0.1/32\n\t\t\t\tfallback_policy reject\n\t\t\t}\n\t\t\ttls\n\t\t}\n'
 rendered=files['Caddyfile.production'];assert rendered.count(extras)==rendered.count(wrappers)==1 and rendered.replace(extras,'').replace(wrappers,'').replace(':8080 {',':80 {')==common.caddy(data,'production')
 assert files['Caddyfile.prepare']==common.caddy(data,'prepare')
 checkout=root/'sites/ksu.codes';commit=inputs['commit'];assert run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==commit and not run(['/usr/sbin/runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
 runtime_source=checkout/'tools/codiserver/ingress-runtime';raw=(runtime_source/'runtime.json').read_bytes();key=digest(raw);assert key==pins['runtimeManifestSHA256']=='7bbd7877cd64bdb10cd170d4a0d0bdf1e11e6b186a329b7564735951090f59f8'
 meta=json.loads(raw);assert meta['upstreamRelease']=='2.8.31' and meta['files']==pins['runtimeFiles'] and set(p.name for p in runtime_source.iterdir())=={'runtime.json','haproxy','LICENSE-haproxy'}
 for name,record in meta['files'].items():
  p=runtime_source/name;i=p.lstat();assert stat.S_ISREG(i.st_mode) and i.st_nlink==1 and record=={'bytes':i.st_size,'sha256':digest(p.read_bytes())}
 runtime=Path('/srv/codi-ingress/runtimes')/key
 stage=Path(tempfile.mkdtemp(prefix='codi-shared-ingress-preflight-'))
 try:
  shutil.copyfile(runtime_source/'haproxy',stage/'haproxy');(stage/'haproxy').chmod(0o755);assert digest((stage/'haproxy').read_bytes())==meta['files']['haproxy']['sha256']
  assert run([stage/'haproxy','-v']).startswith('HAProxy version 2.8.31-');assert 'not found' not in run(['ldd',stage/'haproxy'])
  (stage/'haproxy.cfg').write_text(files['haproxy.cfg']);run([stage/'haproxy','-c','-f',stage/'haproxy.cfg'])
  (stage/unit.name).write_text(files[unit.name].replace(str(runtime/'haproxy'),str(stage/'haproxy')));run(['systemd-analyze','verify',stage/unit.name])
  fd,name=tempfile.mkstemp(prefix='.codi-shared-ingress-',suffix='.Caddyfile',dir='/etc/caddy');os.close(fd)
  try:ctl.write(name,rendered.encode(),0o640,0,pwd.getpwnam('caddy').pw_gid,False);ctl.caddy_validate(name)
  finally:Path(name).unlink()
 finally:shutil.rmtree(stage)
 for port in [8080,8443]:
  with socket.socket() as s:s.bind(('127.0.0.1',port))
 native=Path('/etc/codi-connected/ksu/managed.json');native_raw=native.read_bytes()
 names=[s['service'] for s in data['sites'] if s['enabled']]+['caddy.service',*['codi-ksu-hidden-'+r+'.service' for r in ['issuer','steward','guest']], 'codi-relay-ksu-hidden.service','codi-relay-ksu-hidden-proxy.service']
 pids={n:pid(n) for n in names};assert all(int(p)>0 for p in pids.values())
 before={str(p):{'text':p.read_text(),'mode':stat.S_IMODE(p.stat().st_mode),'uid':p.stat().st_uid,'gid':p.stat().st_gid} for p in [source,manifest]}
 status,headers,index=https('/hidden/');assert status==200;cookie=headers['Set-Cookie'].split(';',1)[0]
 desktop={n:digest(https('/desktop/'+n)[2]) for n in ['release.json','app.js','config.json']};frontend={n:digest(https('/hidden/'+n)[2]) for n in ['app.js','style.css','terminal.js']}
 relay_operator=Path('/srv/codi-relay/operators/53ad5058662dbb0113caf43b900bcb77cbfdf0923e62477f899abe006d56c52b');sys.path.insert(0,str(relay_operator));from relay_service.manager import Manager
 relay=Manager('/etc/codi-relay/ksu')
 with relay.locked():value=relay.load();relay.installed(value);ready=relay.ready(value)
 if inputs['action']=='validate':print(json.dumps({'status':'PASS','scope':'Actual Caddy/HAProxy syntax, systemd unit verification, nine-site route invariants, protected private relay readiness and free internal ports; no live change','sourceCommit':commit,'runtimeManifestSHA256':key,'siteDomains':domains,'candidateFilesSHA256':pins['candidateFilesSHA256']}));raise SystemExit(0)
 assert inputs['action'] in ['apply','exercise-rollback','stage-recovery-test'] and not receipt.exists()
 protected(runtime.parent)
 if not runtime.exists():
  shutil.copytree(runtime_source,runtime)
  for p in [runtime,*runtime.iterdir()]:os.chown(p,0,0);p.chmod(0o755 if p.is_dir() or p.name=='haproxy' else 0o644)
 assert set(p.name for p in runtime.iterdir())=={'runtime.json','haproxy','LICENSE-haproxy'}
 for p in [runtime,*runtime.iterdir()]:
  i=p.lstat();assert i.st_uid==i.st_gid==0 and not i.st_mode&0o022
  if p.is_file():assert digest(p.read_bytes())==(key if p.name=='runtime.json' else meta['files'][p.name]['sha256'])
 transition={'version':'codi-shared-ingress-transition/1','id':datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'),'phase':'prepared','before':before,'beforeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'files':files,'nativeConfigSHA256':digest(native_raw),'sourceCommit':commit}
 save(journal,transition)
 try:
  atomic(config,files['haproxy.cfg'].encode(),0o644);atomic(unit,files[unit.name].encode(),0o644);atomic(dropin,files[dropin.name].encode(),0o644)
  run(['systemd-analyze','verify',unit]);run(['systemctl','daemon-reload'])
  assert run(['systemctl','show','caddy.service','-p','Before','--value']).find(unit.name)>=0
  assert unit.name in run(['systemctl','show','caddy.service','-p','Wants','--value']).split()
  assert pid(unit.name)=='0' and all(pid(n)==p for n,p in pids.items())
  if inputs['action']=='exercise-rollback':raise RollbackExercise('Deliberate pre-listener rollback exercise')
  if inputs['action']=='stage-recovery-test':
   # Deliberately exit after durable preparation, bypassing automatic rollback.
   # The next explicit --recover must restore these staged files. Public
   # listeners and all website/native processes have not changed.
   print(json.dumps({'status':'PASS','scope':'Durable prepared journal and real unit/dependency staged; no listener or hosting-input change. Explicit recover required now.','pendingRecoveryRequired':True,'journal':str(journal),'priorPids':pids,'beforeCaddySHA256':transition['beforeCaddySHA256']}),flush=True);os._exit(0)
  for p,n in [(source,'common.ingress.py'),(manifest,'sites.ingress.toml')]:
   old=before[str(p)];ctl.write(p,files[n].encode(),old['mode'],old['uid'],old['gid'],False)
  reload_generator();ctl.caddy_apply(ctl.load(),'production');run(['systemctl','start',unit.name])
  # Readiness through the public listeners; default trust and the protected
  # TURN challenge pin are both required before committing the transition.
  end=time.monotonic()+15
  while True:
   try:status,headers,body=https('/hidden/');assert status==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie;break
   except (OSError,AssertionError):
    if time.monotonic()>end:raise
    time.sleep(.2)
  with ssl.create_default_context().wrap_socket(socket.create_connection(('127.0.0.1',443),5),server_hostname='turn.ksu.codes') as tls:
   assert digest(tls.getpeercert(binary_form=True))==ready['pinnedTLSLeaf'];transaction=secrets.token_bytes(12)
   tls.sendall(struct.pack('!HHI12s',3,8,0x2112A442,transaction)+struct.pack('!HHI',0x19,4,17<<24))
   def receive(size):
    raw=b''
    while len(raw)<size:
     chunk=tls.recv(size-len(raw));assert chunk;raw+=chunk
    return raw
   kind,length,magic,echo=struct.unpack('!HHI12s',receive(20));assert kind==0x113 and length<=4096 and magic==0x2112A442 and echo==transaction
   body=receive(length);offset=0;code=None
   while offset+4<=len(body):
    attr,size=struct.unpack('!HH',body[offset:offset+4]);item=body[offset+4:offset+4+size];assert len(item)==size
    if attr==9 and size>=4:code=(item[2]&7)*100+item[3]
    offset+=4+((size+3)//4)*4
   assert code==401
  assert desktop=={n:digest(https('/desktop/'+n)[2]) for n in desktop} and frontend=={n:digest(https('/hidden/'+n)[2]) for n in frontend}
  assert all(pid(n)==p for n,p in pids.items()) and native.read_bytes()==native_raw
  status,headers,body=https('/hidden');assert status==308 and headers['Location']=='/hidden/'
  worker=int(pid(unit.name));info=dict(line.split(':',1) for line in (Path('/proc')/str(worker)/'status').read_text().splitlines());uids=set(map(int,info['Uid'].split()));assert len(uids)==1 and 0 not in uids and int(info['CapEff'],16)==1024 and info['NoNewPrivs'].strip()=='1'
  smoke=root/'reports/private/codi-shared-ingress-20261023.json';run(['/usr/bin/python3',root/'ops/production-smoke.py','--address','127.0.0.1','--scope','server-loopback','--output',smoke],timeout=120);smokes=json.loads(smoke.read_text());assert sorted(smokes['sites'])==domains and all(s['result']=='PASS' for s in smokes['sites'].values())
  report={'status':'PASS','scope':'Managed shared80/443 website/TURN TLS ingress with prior site policies/assets/native services preserved; public browser/independent WAN verification separate','sourceCommit':commit,'runtimeManifestSHA256':key,'runtimeBinarySHA256':meta['files']['haproxy']['sha256'],'ingressPid':worker,'ingressUID':next(iter(uids)),'ingressCapability':'CAP_NET_BIND_SERVICE','siteDomains':domains,'allSiteSmoke':str(smoke),'generatorSHA256':digest(source.read_bytes()),'manifestSHA256':digest(manifest.read_bytes()),'activeCaddySHA256':digest(Path('/etc/caddy/Caddyfile').read_bytes()),'existingPidsUnchanged':pids,'desktopSHA256':desktop,'frontendSHA256':frontend,'indexAndGuestCookieUnchanged':True,'nativeConfigUnchanged':True,'defaultTrustedTurnTLS':True,'publicUnauthenticatedAllocation401':True,'publicTurnListenerConfigured':True,'issuerTurnPolicyConfigured':False,'normalNativeUnitsEnabledForBoot':False,'ingressFollowsExistingCaddyStart':True,'routerFirewallAndPublicPortsChanged':False,'candidateFilesSHA256':pins['candidateFilesSHA256'],'rollbackCommand':'activate-shared-ingress.py --rollback','recoveryCommand':'activate-shared-ingress.py --recover'}
  transition.update(phase='committed',report=report);save(journal,transition);save(receipt,report);save(latest,transition);archive(transition,'committed');print(json.dumps(report))
 except BaseException as error:
  pending=private_json(journal)
  if pending['phase']=='prepared':restore(pending);archive(pending,'failed-rolled-back')
  if inputs['action']=='exercise-rollback' and isinstance(error,RollbackExercise):
   assert all(pid(n)==p for n,p in pids.items()) and native.read_bytes()==native_raw
   assert digest(Path('/etc/caddy/Caddyfile').read_bytes())==transition['beforeCaddySHA256'] and not any(p.exists() for p in [unit,dropin,config,journal])
   status,headers,body=https('/hidden/');assert status==200 and body==index and headers['Set-Cookie'].split(';',1)[0]==cookie
   report={'status':'PASS','scope':'Actual prepared-journal rollback after installing/verifying the ingress unit and Caddy boot dependency; public listeners never changed','existingPidsUnchanged':pids,'unitAndDependencyRemoved':True,'hostingAndNativeInputsUnchanged':True,'indexAndGuestCookieUnchanged':True,'publicTurnListenerConfigured':False};save(Path('/srv/codi-ingress/ksu-shared-ingress-rollback-exercise-result.json'),report);print(json.dumps(report));raise SystemExit(0)
  raise
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-dir', type=Path)
    parser.add_argument('--commit', default='')
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('--apply', action='store_true')
    actions.add_argument('--recover', action='store_true')
    actions.add_argument('--rollback', action='store_true')
    actions.add_argument('--exercise-rollback', action='store_true')
    actions.add_argument('--stage-recovery-test', action='store_true')
    args = parser.parse_args()
    action = 'recover' if args.recover else 'rollback' if args.rollback else 'exercise-rollback' if args.exercise_rollback else 'stage-recovery-test' if args.stage_recovery_test else 'apply' if args.apply else 'validate'
    payload = {'action': action, 'commit': args.commit}
    if action in ['validate', 'apply', 'exercise-rollback', 'stage-recovery-test']:
        if not args.candidate_dir or not re.fullmatch('[0-9a-f]{40}', args.commit):
            parser.error('Candidate directory and full reviewed source commit required')
        pins = json.loads((args.candidate_dir / 'candidate-result.json').read_text())
        payload.update(pins=pins, files={name: (args.candidate_dir / name).read_text() for name in pins['candidateFilesSHA256']})
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'box-webhost', 'sudo', '-n', '/srv/codi-connected/venvs/517179c/bin/python', '-B', '-c', shlex.quote(REMOTE)], input=json.dumps(payload), text=True, capture_output=True, timeout=360)
    if child.returncode:
        raise SystemExit(child.stderr or child.stdout)
    report = json.loads(child.stdout.strip().splitlines()[-1])
    report['controllerSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT / '.build/checks' / ('shared-ingress-' + action + '-result.json')).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
