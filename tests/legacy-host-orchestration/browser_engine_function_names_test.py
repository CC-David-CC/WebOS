"""Verify the bounded WASM name scan on a small synthetic module."""
import hashlib,importlib.util,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('engine_names',ROOT/'apps/system/browser/tools/inspect_engine_function_names.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def leb(n):
 out=bytearray()
 while True:
  b=n&127;n>>=7;out.append(b|(128 if n else 0))
  if not n:return bytes(out)
def sized(raw):return leb(len(raw))+raw
class ScannerTest(unittest.TestCase):
 def test_pinned_name_section_counts_and_rejects_changed_file(self):
  entries=[b'function app_units::Au',b'seahash::hash',b'unrelated']
  body=leb(len(entries))+b''.join(leb(i)+sized(name) for i,name in enumerate(entries))
  name_section=sized(b'name')+b'\x01'+sized(body)
  data=b'\0asm\x01\0\0\0'+b'\x00'+sized(name_section)
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'engine.wasm';p.write_bytes(data);old=module.ENGINES;module.ENGINES=frozenset([hashlib.sha256(data).hexdigest()])
   try:
    result=module.inspect(p);self.assertEqual(result['namedFunctions'],3);self.assertEqual(result['matches']['app_units::'],1);self.assertEqual(result['matches']['seahash::'],1)
    p.write_bytes(data+b'\x00');self.assertRaisesRegex(ValueError,'pinned shipped engine',module.inspect,p)
   finally:module.ENGINES=old
if __name__=='__main__':unittest.main()
