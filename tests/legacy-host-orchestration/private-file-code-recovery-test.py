#!/usr/bin/env python3
"""Fault tests of the real transition function with isolated stand-in services.

Run as root only on a test host; no real systemd or account files are touched.
The stand-ins prove transaction control flow, not native-operator integration.
"""
import base64,contextlib,hashlib,importlib.util,json,os,sys,tempfile,types,unittest
from pathlib import Path

SOURCE=Path(os.environ.get('CODI_HELPER_SOURCE',Path(__file__).resolve().parent.parent/'active-system/scripts/upgrade-private-file-code.py'))
spec=importlib.util.spec_from_file_location('upgrade_under_test',SOURCE);u=importlib.util.module_from_spec(spec);spec.loader.exec_module(u)

def raw(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
class FakeManager:
 def __init__(self,folder):self.config_path=folder/'gateway.json'
 def locked(self):return contextlib.nullcontext()
 def load(self):return json.loads(self.config_path.read_text())
 def validate(self,c):assert c['manifestSHA256'] in ('old','new')
 def check_units(self,c):pass
 def states(self,c):return {'one':{'ActiveState':'active'}}
 def baseline(self,c):return {'stable':'same'}
 def names(self,c):return ['fake.service']
 def inactive(self,c):pass
 def units(self,c):return {'fake.service':c['release'].encode()}
 def start(self):pass
class FakeFile:
 Manager=FakeManager
 @staticmethod
 def systemctl(*a):pass
 @staticmethod
 def read(p,mode):return p.read_bytes()
 @staticmethod
 def atomic(p,data,mode=0o600):p.write_bytes(data)
class FakeOp:
 def __init__(self):self.failure=None
 def locked(self,config):return contextlib.nullcontext()
 def read_owned(self,*args):return True
 def load(self,c):return json.loads(c.read_text())
 def stop(self,*args):pass
 def installed(self,*args):pass
 def unit(self,*args):return 'issuer'
 def systemctl(self,*args):pass
 def ready(self,*args):pass
 def atomic(self,p,data):
  is_commit=p.name=='private-file-code.json' and json.loads(data)['phase']=='committed'
  if is_commit and self.failure=='before-marker':raise OSError('before rename')
  p.write_bytes(data)
  if is_commit and self.failure=='after-marker':raise OSError('after rename before directory fsync')
class Recovery(unittest.TestCase):
 def setUp(self):
  assert os.geteuid()==0
  self.temp=tempfile.TemporaryDirectory(prefix='codi-recovery-test-',dir='/var/lib');self.addCleanup(self.temp.cleanup);root=Path(self.temp.name)
  release=root/'release';release.mkdir();(release/'scripts').mkdir();(release/'scripts/manage-services.py').write_text('test stub')
  data=(release/'scripts/manage-services.py').read_bytes();manifest={'files':{'scripts/manage-services.py':{'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}}};manifest_raw=raw(manifest);(release/'connected-release.json').write_bytes(manifest_raw);self.pin=hashlib.sha256(manifest_raw).hexdigest()
  self.units=root/'units';self.units.mkdir();(self.units/'fake.service').write_bytes(b'/old')
  self.gw=root/'gateway.json';self.before_file={'release':'/old','manifestSHA256':'old','unitDir':str(self.units)};self.gw.write_bytes(raw(self.before_file));self.config=root/'native.json'
  self.before={'release':str(release),'manifestSHA256':self.pin,'userFiles':{'operatorRelease':str(root/'operator'),'configFile':str(self.gw),'configSHA256':u.digest(self.gw.read_bytes())}};self.config.write_text(json.dumps(self.before))
  self.op=FakeOp();self.orig_load=u.load;u.load=lambda name,path: self.op if name=='private_file_native_operator' else FakeFile;self.addCleanup(setattr,u,'load',self.orig_load)
  origin=types.ModuleType('origin_service');origin.maintenance=types.SimpleNamespace(require_clean=lambda *a:None,guard=lambda *a:None,sync_directory=lambda p:None)
  previous=sys.modules.get('origin_service');sys.modules['origin_service']=origin
  self.addCleanup(lambda:sys.modules.pop('origin_service',None) if previous is None else sys.modules.__setitem__('origin_service',previous))
 def test_failure_points_and_retry(self):
  for fault in ('prepared','files-configured','pins-configured','ready','before-marker','after-marker','committed'):
   with self.subTest(fault=fault):
    self.setUp()
    def phase(name):
     if name==fault:raise RuntimeError('interruption '+name)
    if fault in ('before-marker','after-marker'):self.op.failure=fault
    with self.assertRaises((RuntimeError,OSError)):u.execute(self.config,self.pin,Path('/new'),'new',phase=phase)
    journal=self.config.parent/'private-file-code.json';self.assertTrue(journal.exists());j=json.loads(journal.read_text());expected='new' if j['phase']=='committed' else 'old'
    if fault in ('ready','before-marker','after-marker','committed'):
     self.assertEqual(json.loads(self.gw.read_text())['manifestSHA256'],'new','must not silently roll back after an ambiguous failure')
     self.assertEqual(json.loads(self.config.read_text())['userFiles']['configSHA256'],u.digest(self.gw.read_bytes()))
    self.op.failure=None
    # A second failure during recovery must not change its recorded direction.
    def recover_fault(name):
     if name=='pins-configured':raise RuntimeError('second interruption')
    with self.assertRaises(RuntimeError):u.execute(self.config,self.pin,recover=True,phase=recover_fault)
    self.assertEqual(json.loads(journal.read_text())['phase'],j['phase'])
    result=u.execute(self.config,self.pin,recover=True);self.assertEqual(result['workerManifestSHA256'],expected);self.assertEqual(json.loads(self.gw.read_text())['manifestSHA256'],expected);self.assertFalse(journal.exists())
if __name__=='__main__':unittest.main()
