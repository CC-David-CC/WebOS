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


class OrganizedLayoutTests(unittest.TestCase):
    def test_apps_include_files_and_wordcraft(self):
        for component in ('files', 'wordcraft', 'calculator'):
            self.assertTrue(inspection.organized_path(component, 'apps/' + component))
            self.assertFalse(inspection.organized_path(component, component))
            self.assertFalse(inspection.organized_path(component, 'platform/' + component))

    def test_shared_projects_have_distinct_owners(self):
        for component, role in [('craft-libs', 'libraries'), ('egui', 'libraries'),
                                ('craft-fonts', 'assets'), ('craft-i18n', 'assets'),
                                ('craft-common-actions', 'tooling'), ('engine-ffmpeg', 'engines')]:
            self.assertTrue(inspection.organized_path(component, role + '/' + component))
            self.assertFalse(inspection.organized_path(component, 'apps/' + component))

    def test_paths_cannot_escape_organized_roots(self):
        for path in ('/apps/wordcraft', 'apps/../wordcraft', '../apps/wordcraft',
                     'apps/wordcraft/private', 'wordcraft'):
            self.assertFalse(inspection.organized_path('wordcraft', path))


if __name__ == '__main__':
    unittest.main()
