#!/usr/bin/env python3
"""Disposable real systemd and service-user lifecycle, no live units touched."""
import importlib.util,json,os,pwd,secrets,shutil,socket,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if os.geteuid()!=0:raise SystemExit('Run this disposable fixture as root')
code=secrets.token_hex(5);name='codi-fixture-'+code;unit=name+'.service';stage=Path('/srv')/name;unitfile=Path('/run/systemd/system')/unit;dropins=Path(str(unitfile)+'.d');created=False;installed=False;checks=[];probe=None
def run(*args):
 result=subprocess.run(args,capture_output=True,text=True)
 if result.returncode:raise RuntimeError(f"{args[0]} failed: {result.stderr[-2000:]}")
 return result
try:
 try:pwd.getpwnam(name);raise RuntimeError('Fixture account collision')
 except KeyError:pass
 assert not stage.exists() and not unitfile.exists()
 run('useradd','--system','--user-group','--home-dir','/nonexistent','--no-create-home','--shell','/usr/sbin/nologin',name);created=True;account=pwd.getpwnam(name)
 stage.mkdir(mode=0o755);shutil.copytree(ROOT/'.build/official-services/systemd-fixture-r3',stage/'package');shutil.copytree(ROOT/'.build/notice-test-venv',stage/'venv',symlinks=True)
 for directory in [stage/'package',*(p for p in (stage/'package').rglob('*') if p.is_dir())]:directory.chmod(0o755)
 parent=stage/'data';parent.mkdir(mode=0o700);os.chown(parent,account.pw_uid,account.pw_gid)
 python=stage/'venv/bin/python';package=stage/'package';state=parent/'state'
 run('runuser','-u',name,'--',str(python),str(package/'scripts/official-admin.py'),'--state',str(state),'init')
 fixture=json.loads((ROOT/'.build/checks/official-browser-offer-export-r1.json').read_text())['offerFixture'];offer=fixture['offer'];payload=stage/'fixture.json';payload.write_text(json.dumps(fixture));payload.chmod(0o644)
 seed=stage/'seed.py';seed.write_text("""import json,sys
from pathlib import Path
sys.path[:0]=[sys.argv[1],sys.argv[1]+'/codiserver-server-v0.3.0']
from steward.official_registry import OfficialChannelRegistry
f=json.loads(Path(sys.argv[3]).read_text());o=f['offer'];s=OfficialChannelRegistry(Path(sys.argv[2]));s._db.execute('INSERT INTO official_channels VALUES(?,?,?,?,?,?,?)',(o['channel'],f['genesisHash'],f['policyWire'],'fixture','',1,0))
for n in o['nodes']:s.stage_node(o['channel'],n['cid'],n['wire'])
s.append_staged_history(o['channel'],expected_head=o['expectedHead'],history=o['history'],height=o['height'],head=o['head']);s.close()
""");seed.chmod(0o644)
 run('runuser','-u',name,'--',str(python),str(seed),str(package),str(state/'official.sqlite'),str(payload))
 sys.path.insert(0,str(package/'codiserver-server-v0.3.0'));from cryptography.hazmat.primitives.asymmetric import ec
 from codiauth import jose
 key=ec.generate_private_key(ec.SECP256R1());policy={'mode':'server','issuer':'http://127.0.0.1:8091','authorityKeys':[{'kid':'fixture','jwk':jose.public_jwk(key)}]};policyfile=stage/'policy.json';policyfile.write_text(json.dumps({'identity':policy}));policyfile.chmod(0o644)
 with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
 # Compare same-account connectivity outside and inside the service sandbox.
 route=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);route.connect(('1.1.1.1',53));host=route.getsockname()[0];route.close()
 probe=socket.socket();probe.bind((host,0));probe.listen(8);probe_port=probe.getsockname()[1]
 probe_code="import socket,sys\ns=socket.socket();s.settimeout(2)\ntry:s.connect((sys.argv[1],int(sys.argv[2])));result='allowed'\nexcept OSError:result='blocked'\nopen(sys.argv[3],'w').write(result)\n"
 prober=stage/'probe.py';prober.write_text(probe_code);prober.chmod(0o644);control=parent/'probe-control'
 run('runuser','-u',name,'--',str(python),str(prober),host,str(probe_port),str(control));assert control.read_text()=='allowed';control.unlink()
 spec=importlib.util.spec_from_file_location('unit',ROOT/'scripts/render-official-service-unit.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 text=module.render(python=str(python),package=str(package),state=str(state),policy=str(policyfile),port=port,discovery=True).replace('User=codi-official','User='+name).replace('Group=codi-official','Group='+name);text=text.replace('ExecStart=',f'ExecStartPre={python} {prober} {host} {probe_port} {state}/probe-result\nExecStart=',1);unitfile.write_text(text);unitfile.chmod(0o644);installed=True
 run('systemd-analyze','verify',str(unitfile));run('systemctl','daemon-reload');run('systemctl','start',unit)
 def pid():return int(run('systemctl','show',unit,'-p','MainPID','--value').stdout.strip())
 def ready():
  end=time.monotonic()+25
  while time.monotonic()<end:
   try:
    req=urllib.request.Request('http://127.0.0.1:'+str(port)+'/official-directory?after=&limit=1',headers={'Host':'127.0.0.1:8091'})
    with urllib.request.urlopen(req,timeout=1) as response:return response.status==200
   except Exception:time.sleep(.2)
  raise RuntimeError('Official runtime did not become ready')
 def saved_head():
  req=urllib.request.Request('http://127.0.0.1:'+str(port)+'/official-head?channel='+offer['channel'],headers={'Host':'127.0.0.1:8091'})
  with urllib.request.urlopen(req,timeout=3) as response:return json.load(response)['head']
 assert ready();assert (state/'probe-result').read_text()=='blocked','systemd IP sandbox did not block non-loopback host';checks.append('service sandbox blocks non-loopback connection that same user can otherwise reach');assert saved_head()==offer['head'];sys.path.insert(0,str(ROOT));from origin_service.official_backend_custody import verify_listener
 import hashlib
 pins={'systemctl':lambda *args:run('systemctl',*args).stdout,'unit':unit,'unit_path':unitfile,'unit_sha256':hashlib.sha256(unitfile.read_bytes()).hexdigest(),'uid':account.pw_uid,'argv':[str(python),'-I','-B',str(package/'scripts/run-official-runtime.py'),'--database',str(state/'official.sqlite'),'--ledger',str(state/'access.sqlite'),'--issuer-discovery',str(policyfile),'--port',str(port)],'port':port}
 assert verify_listener(**pins)==pid()
 from origin_service.official_management import check_backend
 public=stage/'public';public.mkdir();(public/'origin-discovery.json').write_text(json.dumps({'identity':policy}))
 class HealthOp:
  def read_owned(self,path,*args):return Path(path).read_bytes()
 assert check_backend(HealthOp(),{'stateRoot':str(stage),'origin':policy['issuer']},port);checks.append('same packaged systemd service passes issuer identity health and listener custody')
 from origin_service import official_management,maintenance,deployment
 from unittest.mock import patch
 class SwitchOp(HealthOp):
  def atomic(self,path,data,mode=0o600):Path(path).write_bytes(data)
  def unit(self,c,role):return role+'.service'
  def render(self,c,role):return ('enabled='+str(c.get('officialChannels',False))).encode()
  def installed(self,c):pass
  def stop(self,c,roles):pass
  def ready(self,c,roles):pass
  def systemctl(self,*args):
   if args[0]=='show' and args[1]==unit:return run('systemctl',*args).stdout
   return ''
 op=SwitchOp();switchdir=stage/'switch';switchdir.mkdir();configpath=switchdir/'managed.json';config={'maintenance':1,'unitDir':str(switchdir),'stateRoot':str(stage),'origin':policy['issuer']};configpath.write_text(json.dumps(config));backend_pins={k:pins[k] for k in ('unit','unit_path','unit_sha256','uid','argv')}
 with patch.object(maintenance,'guard'),patch.object(maintenance,'guard_epoch'),patch.object(maintenance,'sync_directory'),patch.object(deployment,'syntax'),patch.object(deployment,'active',return_value=[]):
  result=official_management.configure(op,config,configpath,True,backend_port=port,backend_custody=backend_pins);assert result['enabled'] and json.loads(configpath.read_text())['officialChannels']
  result=official_management.configure(op,json.loads(configpath.read_text()),configpath,False);assert not result['enabled'] and 'officialChannels' not in json.loads(configpath.read_text())
 checks.append('real backend custody and health gate journaled enable and disable; issuer effects mocked')
 def stale_status(*args):return run('systemctl',*args).stdout.replace('NeedDaemonReload=no','NeedDaemonReload=yes')
 try:verify_listener(**(pins|{'systemctl':stale_status}));raise AssertionError('stale loaded unit accepted')
 except ValueError:pass
 dropins.mkdir();(dropins/'fixture.conf').write_text('[Service]\nEnvironment=CODI_FIXTURE=1\n');run('systemctl','daemon-reload')
 try:verify_listener(**pins);raise AssertionError('unit drop-in accepted')
 except ValueError:pass
 shutil.rmtree(dropins);run('systemctl','daemon-reload');assert verify_listener(**pins)==pid();checks.append('stale unit and actual systemd drop-in rejected')
 for wrong in ({'uid':account.pw_uid+1},{'port':port+1 if port<65535 else port-1},{'unit_sha256':'0'*64}):
  try:verify_listener(**(pins|wrong));raise AssertionError('incorrect custody pin accepted')
  except ValueError:pass
 checks.append('pinned unit, process identity and actual listener match; wrong pins refused');
 first=pid();policy['authorityKeys']=[{'kid':'replacement','jwk':jose.public_jwk(ec.generate_private_key(ec.SECP256R1()))}];replacement=stage/'replacement.json';replacement.write_text(json.dumps({'identity':policy}));replacement.chmod(0o644);replacement.replace(policyfile);(public/'origin-discovery.json').write_text(json.dumps({'identity':policy}));end=time.monotonic()+30
 while time.monotonic()<end:
  if pid()>0 and pid()!=first:
   try:
    if check_backend(HealthOp(),{'stateRoot':str(stage),'origin':policy['issuer']},port):break
   except Exception:pass
  time.sleep(.25)
 else:raise RuntimeError('Systemd did not restart on discovery update')
 assert saved_head()==offer['head'];checks.append('systemd reloads changed issuer identity and retains saved history')
 checks.append('signed browser-produced history is served before crash');first=pid();assert first>0 and Path('/proc',str(first),'status').read_text().split('Uid:')[1].split()[0]==str(account.pw_uid);checks.append('service runs as dedicated unprivileged account and serves loopback')
 run('systemctl','kill','--signal=SIGKILL',unit);end=time.monotonic()+30
 while time.monotonic()<end:
  current=pid()
  if current>0 and current!=first:
   try:
    if ready():break
   except Exception:pass
  time.sleep(.25)
 else:raise RuntimeError('Service did not restart')
 assert saved_head()==offer['head'];checks.append('systemd restart serves the same verified saved head')
 assert (state/'official.sqlite').is_file() and (state/'access.sqlite').is_file();run('systemctl','stop',unit);checks.append('clean stop retains database files')
 print(json.dumps({'status':'PASS','checks':checks,'scope':'Disposable local systemd account, package and state; no live webhost, public ingress or power-loss test.'}))
finally:
 if installed:
  subprocess.run(['systemctl','stop',unit],capture_output=True);unitfile.unlink(missing_ok=True);shutil.rmtree(dropins,ignore_errors=True);subprocess.run(['systemctl','daemon-reload'],capture_output=True);subprocess.run(['systemctl','reset-failed',unit],capture_output=True)
 if probe:probe.close()
 if stage.exists():shutil.rmtree(stage)
 if created:subprocess.run(['userdel',name],check=True,capture_output=True)
