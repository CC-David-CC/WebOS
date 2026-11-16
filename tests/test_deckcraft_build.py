"""Exercise build-command preservation guards without invoking compilers."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class DeckcraftBuildGuards(unittest.TestCase):
    def setUp(self):
        self.fixture = Path(tempfile.mkdtemp(prefix='webos-deckcraft-build-'))

    def invoke(self, output, target=None):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/build_deckcraft.py'),
                               '--output', str(output), '--target-dir', str(target or self.fixture / 'target'),
                               '--cargo', '/nonexistent-test-tool'], text=True, capture_output=True)

    def test_output_collision_preserves_existing_material(self):
        output = self.fixture / 'existing'; output.mkdir()
        marker = output / 'preserve'; marker.write_bytes(b'unchanged')
        result = self.invoke(output)
        self.assertEqual(result.returncode, 2)
        self.assertIn('collision', result.stderr)
        self.assertEqual(marker.read_bytes(), b'unchanged')
        self.assertFalse(output.with_name('existing.build').exists())

    def test_target_inside_source_is_rejected_before_compilation(self):
        target = ROOT / 'never-create-this-cargo-target'
        self.assertFalse(target.exists())
        result = self.invoke(self.fixture / 'new-site', target)
        self.assertEqual(result.returncode, 2)
        self.assertIn('outside the source assembly', result.stderr)
        self.assertFalse(target.exists())
        self.assertFalse((self.fixture / 'new-site').exists())

    def test_parent_traversal_cannot_bypass_source_or_collision_checks(self):
        result = self.invoke(self.fixture / 'unused' / '..' / 'escaped')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Parent traversal', result.stderr)
        self.assertFalse((self.fixture / 'escaped').exists())


if __name__ == '__main__':
    unittest.main()
