import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rust_archive',ROOT/'apps/system/browser/tools/inventory_rust_archive.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ArchiveInventory(unittest.TestCase):
 def test_matches_alias_by_hash_and_counts_archive_members(self):
  rows,other=m.associate(['md5-0123456789abcdef.one.rcgu.o','md5-0123456789abcdef.two.rcgu.o','native.o'],['md-5-0123456789abcdef'])
  self.assertEqual(rows,[{'crate':'md5','buildHash':'0123456789abcdef','package':'md-5','members':2}]);self.assertEqual(other,['native.o'])
 def test_refuses_missing_and_ambiguous_hashes(self):
  for names in ([],['first-0123456789abcdef','second-0123456789abcdef']):
   with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):m.associate(['md5-0123456789abcdef.x.o'],names)
if __name__=='__main__':unittest.main()
