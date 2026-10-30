#!/usr/bin/env python3
"""Exercise the exact staging program in a disposable local root-owned tree."""
import base64,hashlib,importlib.util,json,secrets,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('expired_stager',ROOT/'scripts/stage-live-root-bundle.py');stage=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage)
def sudo(*args,input=None):return subprocess.run(['sudo','-n',*[str(a) for a in args]],input=input,text=True,capture_output=True,timeout=30)
class Stage(unittest.TestCase):
 def setUp(self):
  self.base=Path('/srv')/('codi-stage-test-'+secrets.token_hex(6));self.assertEqual(sudo('install','-d','-m','0755',self.base).returncode,0)
  for path,mode in [(self.base/'service','0755'),(self.base/'control','0755'),(self.base/'hosting','0755')]:self.assertEqual(sudo('install','-d','-m',mode,path).returncode,0)
  self.config=json.dumps({'manifestSHA256':stage.RELEASE,'origin':'https://ksu.codes','basePath':''}).encode();self.assertEqual(sudo('/usr/bin/python3','-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(bytes.fromhex(sys.argv[2]))',self.base/'control/managed.json',self.config.hex()).returncode,0)
  self.assertEqual(sudo('install','-m','0644','/dev/null',self.base/'hosting/lock').returncode,0)
  bundle=ROOT/'.build/recovery-operators/live-root-r1';self.payload={'pin':stage.PIN,'config':hashlib.sha256(self.config).hexdigest(),'release':stage.RELEASE,'files':{n:base64.b64encode((bundle/n).read_bytes()).decode() for n in stage.NAMES}}
  self.code=stage.REMOTE.replace('/home/dflanag3/webhost-sites/.controller.lock',str(self.base/'hosting/lock')).replace('/etc/codi-connected/ksu/managed.json',str(self.base/'control/managed.json')).replace('/srv/codi-connected',str(self.base/'service'))
 def tearDown(self):
  self.assertTrue(self.base.parent==Path('/srv') and self.base.name.startswith('codi-stage-test-'));result=sudo('rm','-rf','--',self.base);self.assertEqual(result.returncode,0,result.stderr)
 def call(self,value=None):return sudo('/usr/bin/python3','-I','-B','-c',self.code,input=json.dumps(value or self.payload))
 def test_stage_idempotence_and_refuse_changed_inputs(self):
  first=self.call();self.assertEqual(first.returncode,0,first.stderr);self.assertEqual(json.loads(first.stdout)['status'],'PASS');second=self.call();self.assertEqual(second.returncode,0,second.stderr)
  changed=json.loads(json.dumps(self.payload));changed['files']['run.py']=base64.b64encode(b'changed').decode();self.assertNotEqual(self.call(changed).returncode,0)
  target=self.base/'service/recovery-operators'/stage.PIN/'run.py';self.assertEqual(sudo('/usr/bin/python3','-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("changed")',target).returncode,0);self.assertNotEqual(self.call().returncode,0)
 def test_existing_journal_is_never_overwritten(self):
  first=self.call();self.assertEqual(first.returncode,0,first.stderr);journal=self.base/'control/live-root-renewal/journal.json';self.assertEqual(sudo('/usr/bin/python3','-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_text("preserve")',journal).returncode,0);self.assertNotEqual(self.call().returncode,0);result=sudo('cat',journal);self.assertEqual(result.stdout,'preserve')
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Stage));sys.exit(not result.wasSuccessful())
