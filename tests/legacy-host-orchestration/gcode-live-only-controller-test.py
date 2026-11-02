import contextlib,hashlib,importlib.util,io,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
MODULE=Path(__file__).resolve().parents[1]/'tools/gcode-live-only-controller.py'
spec=importlib.util.spec_from_file_location('candidate_operator',MODULE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def digest(data):return hashlib.sha256(data).hexdigest()
class CandidateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);m.ROOT=self.root/'hosting';m.ROOT.mkdir();(m.ROOT/'ops').mkdir();(m.ROOT/'.controller.lock').touch();m.MANIFEST=m.ROOT/'sites.toml';m.COMMON_PATH=m.ROOT/'ops/common.py';m.CADDY=self.root/'Caddyfile';m.BACKUP=self.root/'backup';m.BACKUP.mkdir();m.RELEASES=self.root/'releases';m.RELEASES.mkdir();m.OLD='old';m.NEW='new'
  self.old={'sites':[{'domain':'ksu.codes','codi_simplified':m.OLD,'codi_simplified_mode':'active'}]};self.new={'sites':[{'domain':'ksu.codes','codi_simplified':m.NEW,'codi_simplified_mode':'active'}]}
  self.dump=lambda d:json.dumps(d,sort_keys=True);self.caddy=lambda d,mode:'rendered:'+self.dump(d)
  oldmanifest=self.dump(self.old).encode();oldcaddy=self.caddy(self.old,'production').encode();newmanifest=self.dump(self.new).encode();newcaddy=self.caddy(self.new,'production').encode();m.PINS={'old':(digest(oldmanifest),digest(oldcaddy)),'new':(digest(newmanifest),digest(newcaddy))};m.MANIFEST.write_bytes(oldmanifest);m.CADDY.write_bytes(oldcaddy);m.COMMON_PATH.write_bytes(b'common');m.COMMON=digest(b'common')
  backup=m.BACKUP;(backup/'sites.toml').write_bytes(oldmanifest);(backup/'Caddyfile').write_bytes(oldcaddy);(backup/'common.py').write_bytes(b'common');(m.BACKUP/'release-diff.json').write_bytes(b'diff');m.DIFF_PIN=digest(b'diff')
  for release in (m.OLD,m.NEW):(m.RELEASES/release/'assets/desktop').mkdir(parents=True);(m.RELEASES/release/'index.html').write_bytes(b'index')
  root=m.RELEASES/m.NEW;(root/'file').write_bytes(b'content');manifest=json.dumps({'id':m.NEW,'files':{'file':{'bytes':7,'sha256':digest(b'content')}}}).encode();(root/'assets/desktop/cache-manifest.json').write_bytes(manifest);(root/'assets/desktop/offline-worker.js').write_bytes(b'worker');m.CACHE_PIN=digest(manifest);m.WORKER_PIN=digest(b'worker');old=m.RELEASES/m.OLD;(old/'file').write_bytes(b'oldfile');oldmanifest=json.dumps({'id':m.OLD,'files':{'file':{'bytes':7,'sha256':digest(b'oldfile')}}}).encode();(old/'assets/desktop/cache-manifest.json').write_bytes(oldmanifest);(old/'assets/desktop/offline-worker.js').write_bytes(b'oldworker');m.OLD_CACHE_PIN=digest(oldmanifest);m.OLD_WORKER_PIN=digest(b'oldworker')
  self.fail=False
  def apply(data,mode):
   m.CADDY.write_text(self.caddy(data,mode))
   if self.fail:self.fail=False;raise RuntimeError('injected reload failure')
  self.ctl=types.SimpleNamespace(current_mode=lambda:'production',load=lambda:json.loads(m.MANIFEST.read_text()),caddy=self.caddy,validate=lambda d:None,dump=self.dump,snapshot=lambda p:'fixture-backup',write=lambda p,v,*args:p.write_bytes(v.encode() if isinstance(v,str) else v),caddy_apply=apply)
 def run_action(self,action):
  with patch.object(m.os,'geteuid',return_value=0),patch.dict(sys.modules,{'webctl':self.ctl}),patch.object(sys,'argv',['tool',action]),contextlib.redirect_stdout(io.StringIO()):m.main()
 def test_verify_is_read_only_and_full_cycle(self):
  before=m.MANIFEST.read_bytes();self.run_action('verify');self.assertEqual(m.MANIFEST.read_bytes(),before);self.run_action('activate');self.assertEqual(json.loads(m.MANIFEST.read_text()),self.new);self.run_action('rollback');self.assertEqual(m.MANIFEST.read_bytes(),before)
 def test_reload_failure_restores_baseline(self):
  before=(m.MANIFEST.read_bytes(),m.CADDY.read_bytes());self.fail=True
  with self.assertRaisesRegex(RuntimeError,'injected'):self.run_action('activate')
  self.assertEqual((m.MANIFEST.read_bytes(),m.CADDY.read_bytes()),before)
 def test_rejects_changed_configuration_or_candidate_without_writes(self):
  m.CADDY.write_bytes(b'tampered');before=m.MANIFEST.read_bytes()
  with self.assertRaisesRegex(RuntimeError,'pins changed'):self.run_action('activate')
  self.assertEqual(m.MANIFEST.read_bytes(),before)
  m.CADDY.write_text(self.caddy(self.old,'production'));(m.RELEASES/m.NEW/'file').write_bytes(b'altered')
  with self.assertRaisesRegex(RuntimeError,'Candidate file changed'):self.run_action('activate')
  self.assertEqual(m.MANIFEST.read_bytes(),before)
 def test_rejects_corrupt_rollback_before_mutation(self):
  before=m.MANIFEST.read_bytes();(m.RELEASES/m.OLD/'file').write_bytes(b'damaged')
  with self.assertRaisesRegex(RuntimeError,'Rollback file changed'):self.run_action('activate')
  self.assertEqual(m.MANIFEST.read_bytes(),before)
if __name__=='__main__':unittest.main()
