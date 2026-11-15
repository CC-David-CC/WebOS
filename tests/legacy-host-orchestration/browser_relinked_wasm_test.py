import hashlib,importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('relinked_wasm',ROOT/'apps/system/browser/tools/verify_relinked_wasm.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sized(b):
 if len(b)>=128:raise ValueError('fixture too large')
 return bytes([len(b)])+b
def module(name,build,code=b'\x00'):
 sec=lambda k,b:bytes([k])+sized(b)
 name_section=sized(b'name')+b'\x00'+sized(sized(name))+b'\x01'+sized(b'\x00')
 return b'\0asm\x01\0\0\0'+sec(10,code)+sec(0,name_section)+sec(0,sized(b'build_id')+build)
class ComparisonTest(unittest.TestCase):
 def test_ignores_only_module_name_and_build_id(self):
  with tempfile.TemporaryDirectory() as t:
   a,b=Path(t)/'a',Path(t)/'b';a.write_bytes(module(b'a',b'1'));b.write_bytes(module(b'longer',b'2'));old=(m.ORIGINAL,m.RELINK);m.ORIGINAL=hashlib.sha256(a.read_bytes()).hexdigest();m.RELINK=hashlib.sha256(b.read_bytes()).hexdigest()
   try:
    self.assertEqual(m.verify(a,b)['sections'],3)
    b.write_bytes(module(b'longer',b'2',b'\x01'));m.RELINK=hashlib.sha256(b.read_bytes()).hexdigest()
    with self.assertRaisesRegex(ValueError,'Non-metadata section differs'):m.verify(a,b)
   finally:m.ORIGINAL,m.RELINK=old
if __name__=='__main__':unittest.main()
