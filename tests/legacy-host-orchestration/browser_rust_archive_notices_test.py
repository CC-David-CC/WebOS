import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rust_archive_notices',ROOT/'apps/system/browser/tools/verify_rust_archive_notices.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CoverageTest(unittest.TestCase):
 def test_requires_pinned_input_and_each_vendored_heading(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);inv=p/'inventory';rust=p/'rust';combined=p/'combined'
   inv.write_text(json.dumps({'version':'codi-gecko-rust-archive-inputs/1','packages':{'a':[{'manifest':'third_party/rust/a/Cargo.toml','version':'1.0'}]}}));rust.write_text('===== a 1.0; declared license: MIT =====\n');combined.write_bytes(b'prefix\n'+rust.read_bytes()+b'\nsuffix')
   old=(m.INVENTORY_SHA,m.RUST_SHA,m.COMBINED_SHA);m.INVENTORY_SHA=hashlib.sha256(inv.read_bytes()).hexdigest();m.RUST_SHA=hashlib.sha256(rust.read_bytes()).hexdigest();m.COMBINED_SHA=hashlib.sha256(combined.read_bytes()).hexdigest()
   try:
    self.assertEqual(m.verify(inv,rust,combined)['vendoredManifestsCovered'],1)
    inv.write_text(inv.read_text().replace('1.0','2.0'));m.INVENTORY_SHA=hashlib.sha256(inv.read_bytes()).hexdigest()
    with self.assertRaisesRegex(ValueError,'headings missing'):m.verify(inv,rust,combined)
    combined.write_bytes(b'changed')
    with self.assertRaisesRegex(ValueError,'combined notices hash'):m.verify(inv,rust,combined)
   finally:m.INVENTORY_SHA,m.RUST_SHA,m.COMBINED_SHA=old
if __name__=='__main__':unittest.main()
