import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rust_linkmap',ROOT/'apps/system/browser/tools/inventory_rust_linkmap.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class LinkMapTest(unittest.TestCase):
 def test_deduplicates_members_and_checks_both_pins(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);mp=root/'map';inv=root/'inventory';mp.write_bytes(b'x libgkrust.a(md5-0123456789abcdef.a.o):(a)\ny libgkrust.a(md5-0123456789abcdef.a.o):(b)\n')
   inv.write_text(json.dumps({'version':'codi-gecko-rust-archive-inputs/1','crateBuilds':[{'crate':'md5','buildHash':'0123456789abcdef','package':'md-5','members':1}],'otherMembers':[]}))
   old=(m.MAP_SHA,m.INVENTORY_SHA);m.MAP_SHA=hashlib.sha256(mp.read_bytes()).hexdigest();m.INVENTORY_SHA=hashlib.sha256(inv.read_bytes()).hexdigest()
   try:
    d=m.analyze(mp,inv);self.assertEqual(d['mapEntries'],2);self.assertEqual(d['distinctArchiveMembers'],1);self.assertEqual(d['crateBuilds'][0]['package'],'md-5')
    mp.write_bytes(mp.read_bytes()+b'changed')
    with self.assertRaisesRegex(ValueError,'map hash'):m.analyze(mp,inv)
   finally:m.MAP_SHA,m.INVENTORY_SHA=old
if __name__=='__main__':unittest.main()
