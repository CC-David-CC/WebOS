"""The complete connected preview stage must refuse hardlinked destinations."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'active-system'))
SPEC = importlib.util.spec_from_file_location('serve_connected_for_stage_test', ROOT / 'active-system/scripts/serve-connected.py')
serve = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(serve)


class CompleteStageHardlinkTest(unittest.TestCase):
    def test_existing_release_inode_is_never_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, previous, staged, bundle = (base / name for name in ('source', 'previous', 'staged', 'bundle'))
            for directory in (source, previous, staged, bundle):
                directory.mkdir()
            for name in serve.FILES:
                (source / name).write_text('new ' + name)
            (source / 'assets').mkdir()
            (source / 'network').mkdir()
            for name in ('crypto.mjs', 'identity.mjs', 'strict-json.mjs'):
                (source / 'network' / name).write_text('new network')
            for name in serve.RUNTIME:
                path = source / 'runtime/v86' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('runtime')
            (bundle / 'apps.json').write_text('{}')
            old = previous / 'app.js'
            old.write_text('original release')
            os.link(old, staged / 'app.js')
            # The shared helper is irrelevant: the entire output must be checked
            # before stage() writes even its first root asset.
            with patch.object(serve, 'ROOT', source), patch.object(serve, 'stage_browser_storage'):
                with self.assertRaises((ValueError, OSError)):
                    serve.stage(staged, bundled=bundle)
            self.assertEqual(old.read_text(), 'original release')
            self.assertFalse((staged / 'index.html').exists(), 'stage wrote other files before refusing')


if __name__ == '__main__':
    unittest.main()
