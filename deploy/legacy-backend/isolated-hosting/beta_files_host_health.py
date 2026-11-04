"""Concrete v2 Files signed-health binding for the protected host launcher.

No CLI. All three module arguments must already have been loaded and hash-pinned
by that launcher; this code does not install or activate anything.
"""
import hashlib,json,os
from pathlib import Path
ORIGIN='https://beta.ksu.codes'
POLICY_SHA='71a7f2d380051ecde367bfc2517a77e2570d3797621e3e8f1cb4a141f8cd6dca'
WORKER='dd8cbea7de0a411eca100bdc3811eec1fc6bf3d7e8b6a7c0236fe509ceb9dbd1'
NATIVE='853c12e581c9f89fc3d78507f43941dd16cd0b4b894b28cdb8317e8a58340f21'
UNITS={'codi-beta-issuer.service':'d3ed82ddf87ff643288baac0a7476b35ed701a016b3d297ccb4a10cfaec224e4','codi-beta-frontend.service':'4b909882dfd879235e10bf3cbb004bd3e61db1786cfd99e122b7abbd39be5f78','codi-beta-gateway.service':'f7fe40291ed89df101e511673b201b5606ba526333b1f55743fdec8ed069b47e'}
POLICY=Path('/etc/codi-user-files/beta/issuer-policy.json')
CREDENTIAL=Path('/var/lib/webhost-ops/beta-files-probe/probe.json')

def create(*,lock,launcher,preflight,signed_health,jose):
 """Return read-only v2 health callable; lock must be held on each call.

Launcher verifies its own bundle/code, protected interpreter and JOSE module;
this binding additionally rechecks current artifacts, unit custody, identity,
credential ancestors and main health before and after the signed read.
 """
 def custody():
  lock.check()
  if os.geteuid()!=0:raise ValueError('root protected launcher required')
  launcher.protected(CREDENTIAL);preflight.protected_ancestors(CREDENTIAL.parent)
  launcher.protected(POLICY);raw=launcher.read(POLICY,32768)
  if hashlib.sha256(raw).hexdigest()!=POLICY_SHA:raise ValueError('issuer policy pin changed')
  preflight.tree('/srv/data/codi-beta-native/'+NATIVE,'connected-release.json',NATIVE)
  launcher.verify_beta_worker(Path('/srv/codi-gateway/releases')/WORKER,WORKER)
  for name,pin in UNITS.items():
   path=Path('/etc/systemd/system')/name;launcher.protected(path)
   if hashlib.sha256(launcher.read(path)).hexdigest()!=pin:raise ValueError('beta unit pin changed: '+name)
   state=launcher.unit_state(name);role=name.removeprefix('codi-beta-').removesuffix('.service');user='codi-beta-'+role
   if state.get('ActiveState')!='active' or state.get('MainPID') in (None,'0') or state.get('FragmentPath')!=str(path) or state.get('DropInPaths') or state.get('NeedDaemonReload')!='no' or state.get('User')!=user or state.get('Group')!=user:raise ValueError('beta service unavailable: '+name)
  launcher.main_ready();lock.check()
 def run():
  custody();raw=launcher.read(POLICY,32768);value=json.loads(raw);identity=value.get('identity',value)
  for port in (28118,28132):
   status,body=launcher.get(port,'/config.json');config=json.loads(body)
   if status!=200 or config.get('identity')!=identity or config.get('fileStorage')!={'version':'codi-browser-file-content/1','backend':'opfs','databaseVersion':2}:raise ValueError('beta v2 service identity or config mismatch')
  pin=hashlib.sha256(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  health=signed_health.SignedHealth(check_lock=lock.check,check_custody=custody,origin=ORIGIN,issuer_port=28118,gateway_port=28140,policy=identity,policy_sha256=pin,credential_path=CREDENTIAL,jose=jose)
  return health()
 return run
