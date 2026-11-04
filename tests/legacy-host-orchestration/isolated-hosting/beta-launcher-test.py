"""Local launcher input checks only; never invokes host operations."""
import hashlib,importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1];path=root/'ops/beta_launcher.py';spec=importlib.util.spec_from_file_location('launcher',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Launcher(unittest.TestCase):
 def test_bundled_sources_match_all_declared_pins(self):
  for name,expected in m.PINS.items():self.assertEqual(hashlib.sha256((root/'ops'/name).read_bytes()).hexdigest(),expected,name)
 def test_nofollow_source_and_bounded_read(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'file';p.write_bytes(b'expected');self.assertEqual(m.read(p),b'expected');p.unlink();p.symlink_to('/dev/null')
   with self.assertRaises(OSError):m.read(p)
   p.unlink();p.write_bytes(b'abcdef')
   with self.assertRaises(ValueError):m.read(p,3)
 def test_untrusted_module_bytes_are_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'module.py';p.write_text('raise RuntimeError("must not execute")')
   with patch.object(m,'PKG',Path(t)):
    with self.assertRaisesRegex(ValueError,'pin changed'):m.module('fixture','module.py','0'*64)
 @unittest.skipUnless(os.geteuid()==0,'root-owned temporary fixture required')
 def test_worker_verifier_full_inventory_and_tamper(self):
  with tempfile.TemporaryDirectory(prefix='beta-worker-check-',dir='/var/lib') as t:
   p=Path(t);(p/'gateway_service').mkdir();file=p/'gateway_service'/'chunk_sync.py';file.write_bytes(b'original')
   raw=json.dumps({'version':'codi-private-file-service/1','files':{'gateway_service/chunk_sync.py':{'bytes':8,'sha256':hashlib.sha256(b'original').hexdigest()}}}).encode();(p/'files-service.json').write_bytes(raw);pin=hashlib.sha256(raw).hexdigest()
   m.verify_beta_worker(p,pin)
   file.write_bytes(b'tampered')
   with self.assertRaises(ValueError):m.verify_beta_worker(p,pin)
   file.write_bytes(b'original');(p/'extra').write_bytes(b'x')
   with self.assertRaises(ValueError):m.verify_beta_worker(p,pin)
   (p/'extra').unlink();(p/'gateway_service'/'files-service.json').write_bytes(b'x')
   with self.assertRaises(ValueError):m.verify_beta_worker(p,pin)
 @unittest.skipUnless(os.geteuid()==0,'root-owned fixture required')
 def test_static_verifier_accepts_valid_tree_and_rejects_drift(self):
  with tempfile.TemporaryDirectory(prefix='beta-static-check-',dir='/var/lib') as temp:
   parent=Path(temp);payload=b'asset';files={'assets/one.js':{'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}}
   release=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest();root=parent/release;(root/'assets/desktop').mkdir(parents=True);(root/'assets/one.js').write_bytes(payload)
   raw=json.dumps({'id':release,'files':files}).encode();worker=b'worker';(root/'assets/desktop/cache-manifest.json').write_bytes(raw);(root/'assets/desktop/offline-worker.js').write_bytes(worker)
   original=m.sha
   def fixture_sha(data):
    if data==raw:return '18140be41c4f6cd3a1fcdbee39998e00c363ed677223eeffc8cc97c450ba4720'
    if data==worker:return 'e49a8667db0e20b8fca90ee3e19eec17b70b964846b916d734391dda93c3f69c'
    return original(data)
   def fixture_path(value):return parent if str(value)=='/srv/codi-connected/simplified' else Path(value)
   with patch.object(m,'Path',fixture_path),patch.object(m,'RELEASE',release),patch.object(m,'sha',fixture_sha):
    m.verify_static();fifo=root/'assets/fifo';os.mkfifo(fifo)
    with self.assertRaisesRegex(ValueError,'Unsafe static release'):m.verify_static()
    fifo.unlink();(root/'assets/one.js').write_bytes(b'other')
    with self.assertRaisesRegex(ValueError,'asset changed'):m.verify_static()
 def test_rebased_launcher_forbids_mutation(self):
  for action in ('apply','recover'):
   r=subprocess.run([sys.executable,'-I','-B',str(path),action],capture_output=True,text=True,timeout=5)
   self.assertNotEqual(r.returncode,0);self.assertIn('read-only plan only',r.stderr)
 def test_local_process_refuses_host_action(self):
  r=subprocess.run([sys.executable,'-I','-B',str(path),'plan'],capture_output=True,text=True,timeout=5)
  self.assertNotEqual(r.returncode,0);self.assertIn('Root on box-webhost required',r.stderr)
if __name__=='__main__':unittest.main(verbosity=2)
