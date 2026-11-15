"""Real checkout composition checks; browser/backend acceptance is a separate gate."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('assembly_inspection', ROOT / 'scripts/inspect_assembly.py')
inspection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspection)


class SourceAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = inspection.inspect(ROOT)

    def test_git_links_and_checkouts_are_consistent(self):
        self.assertEqual(self.report['errors'], [])

    def test_component_paths_and_identities_are_unique(self):
        components = self.report['components']
        self.assertEqual(len(components), len({r['path'] for r in components}))
        self.assertEqual(len(components), len({r['id'] for r in components}))

    def test_required_core_sources_are_present(self):
        self.assertEqual(self.report['missing_core_sources'], [],
                         'The core source assembly is incomplete; this is not a browser functionality test.')


if __name__ == '__main__':
    unittest.main()
