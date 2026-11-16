"""Exercise actual candidate webctl CLI dispatch in a disposable directory."""
import hashlib,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OPS=ROOT/'research/beta-isolated-hosting/ops';sys.path.insert(0,str(OPS))
P=Path(__file__).with_name('webctl-main-guard.py');OLD=OPS/'webctl_floor_candidate.py'
assert hashlib.sha256(OLD.read_bytes()).hexdigest()=='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='fb27bc0ccb9be273765e489890a5fea056f578d08d729b92d00815de873ae783'
source=P.read_text();source=source.replace("\nMAIN_RESTRICTION_JOURNAL = STATE/'main-restriction-journal.json'",'').replace("        # Main recovery owns its distinct journal; never mutate hosting while it is pending.\n        try: MAIN_RESTRICTION_JOURNAL.lstat()\n        except FileNotFoundError: pass\n        else: raise RuntimeError('Legacy hosting writes frozen by pending main restriction')\n",'')
assert hashlib.sha256(source.encode()).hexdigest()=='84c09e08e64dadc02fe396b529f1a380ee2ab724eca877f108be0490c92caa6e'
sc=importlib.util.spec_from_file_location('scaffold',OPS/'scaffold_live.py');scaffold=importlib.util.module_from_spec(sc);sys.modules['scaffold']=scaffold;sc.loader.exec_module(scaffold)
spec=importlib.util.spec_from_file_location('guarded_cli',P);ctl=importlib.util.module_from_spec(spec);spec.loader.exec_module(ctl)
class Tests(unittest.TestCase):
 def test_all_supported_writes_refused_without_loading_or_changes(self):
  with tempfile.TemporaryDirectory() as tmp:
   t=Path(tmp);ctl.ROOT=t;ctl.BETA_FILES_JOURNAL=t/'beta-journal';ctl.MAIN_RESTRICTION_JOURNAL=t/'main-restriction-journal.json';ctl.BETA_FILES_FLOOR=t/'beta-floor';ctl.root_required=lambda:None;ctl.load=lambda:(_ for _ in ()).throw(AssertionError('loaded mutable state before guard'))
   (t/'.controller.lock').touch();ctl.MAIN_RESTRICTION_JOURNAL.write_text('malformed still fences');before={p.name:p.read_bytes() for p in t.iterdir()}
   commands=[['prepare'],['render'],['validate'],['private'],['deploy','ksu.codes'],['up','ksu.codes'],['down','ksu.codes'],['restart','ksu.codes'],['rollback','ksu.codes'],['workers','ksu.codes','2'],['activate'],['add','x.example','--theme','x','--description','x','--port','9000'],['caddy-rollback','/tmp/ignored']]
   for args in commands:
    with self.subTest(args=args):
     old=sys.argv;sys.argv=['webctl.py',*args]
     try:
      with self.assertRaisesRegex(RuntimeError,'pending main restriction'):ctl.main()
     finally:sys.argv=old
   self.assertEqual(before,{p.name:p.read_bytes() for p in t.iterdir()})
   ctl.MAIN_RESTRICTION_JOURNAL.unlink();ctl.MAIN_RESTRICTION_JOURNAL.symlink_to(t/'missing')
   old=sys.argv;sys.argv=['webctl.py','render']
   try:
    with self.assertRaisesRegex(RuntimeError,'pending main restriction'):ctl.main()
   finally:sys.argv=old
 def test_read_only_status_remains_available(self):
  ctl.load=lambda:{'sites':[]};ctl.current_mode=lambda:'production';old=sys.argv;sys.argv=['webctl.py','status']
  try:ctl.main()
  finally:sys.argv=old
if __name__=='__main__':unittest.main(verbosity=2)
