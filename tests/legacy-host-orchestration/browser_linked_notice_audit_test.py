"""Check the notice audit identifies missing headings and supplemental labels."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit_linked',ROOT/'apps/system/browser/tools/audit_linked_rust_notices.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class AuditTest(unittest.TestCase):
    def test_missing_and_grouped_supplement(self):
        entry=lambda n:{'version':'1','license':'MIT','manifest':'third_party/rust/'+n+'/Cargo.toml'}
        inv={'packages':{'alpha':[entry('alpha')],'beta':[entry('beta')],'gamma':[entry('gamma')]}}
        summary={'uniquePackageSymbols':{'alpha':1,'beta':1},'ambiguousPackageSymbols':{'gamma':1}}
        text=('===== alpha 1; declared license: MIT =====\n--- LICENSE ---\ntext\n'
              '===== beta 1; declared license: MIT =====\nNo separate license file in this vendored package; see declared license and source.\n'
              '===== another 1, beta 1; https://raw.githubusercontent.com/example/LICENSE =====\nlicense\n')
        rows={r['name']:r for r in m.audit(inv,summary,text)['rows']}
        self.assertTrue(rows['alpha']['vendoredNotice'])
        self.assertTrue(rows['beta']['supplementPresent'])
        self.assertFalse(rows['gamma']['heading'])
        self.assertFalse(m.audit(inv,summary,text.replace('https://raw.githubusercontent.com/','https://example.org/'))['rows'][1]['supplementPresent'])

if __name__=='__main__':unittest.main()
