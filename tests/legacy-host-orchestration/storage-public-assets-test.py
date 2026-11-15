"""Packaging boundary tests for the product mirror and its worker imports."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'public_storage', ROOT / 'active-system/origin_service/public_storage.py')
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


class StorageAssetsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source, self.public = self.root / 'source', self.root / 'public'
        self.source.mkdir()
        self.public.mkdir()
        for name in assets.BROWSER_STORAGE_ASSETS:
            target = self.source / 'storage/browser' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(name)

    def test_closed_bundle_with_notice_never_copies_private_or_research_files(self):
        private = self.source / 'storage/browser/private-state.json'
        private.write_text('must not be served')
        (self.source / 'storage/browser/README.md').write_text('not a runtime asset')
        assets.stage_browser_storage(self.source, self.public)
        actual = {p.relative_to(self.public / 'storage/browser').as_posix()
                  for p in self.public.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(assets.BROWSER_STORAGE_ASSETS))
        for name in actual:
            path = self.public / 'storage/browser' / name
            self.assertEqual(path.read_text(), name)
            self.assertEqual(path.stat().st_mode & 0o777, 0o644)

    def test_incomplete_bundle_fails_before_any_output(self):
        (self.source / 'storage/browser/opfs/worker.mjs').unlink()
        with self.assertRaises(ValueError):
            assets.stage_browser_storage(self.source, self.public)
        self.assertEqual(list(self.public.iterdir()), [])

    def test_source_symlink_and_destination_symlink_are_refused(self):
        worker = self.source / 'storage/browser/opfs/worker.mjs'
        worker.unlink()
        worker.symlink_to(self.source / 'storage/browser/mirror.mjs')
        with self.assertRaises(ValueError):
            assets.stage_browser_storage(self.source, self.public)
        worker.unlink()
        worker.write_text('worker')
        (self.public / 'storage').symlink_to(self.source / 'storage')
        with self.assertRaises(ValueError):
            assets.stage_browser_storage(self.source, self.public)
        self.assertEqual(worker.read_text(), 'worker')

    def test_previous_release_hard_links_are_not_mutated(self):
        output = self.public / 'storage/browser'
        output.mkdir(parents=True)
        old = self.root / 'previous-mirror.mjs'
        old.write_text('old mirror')
        os.link(old, output / 'mirror.mjs')
        assets.stage_browser_storage(self.source, self.public)
        self.assertEqual(old.read_text(), 'old mirror')
        self.assertEqual((output / 'mirror.mjs').read_text(), 'mirror.mjs')
        self.assertNotEqual(old.stat().st_ino, (output / 'mirror.mjs').stat().st_ino)

    def test_unexpected_existing_public_state_is_refused(self):
        output = self.public / 'storage/browser'
        output.mkdir(parents=True)
        (output / 'private.json').write_text('private')
        with self.assertRaises(ValueError):
            assets.stage_browser_storage(self.source, self.public)
        self.assertFalse((output / 'mirror.mjs').exists())

    def test_general_stage_requires_independent_destination_before_copying(self):
        assets.require_independent_stage(self.public)
        old = self.root / 'previous-app.js'
        old.write_text('previous app')
        linked = self.public / 'app.js'
        os.link(old, linked)
        with self.assertRaises(ValueError):
            assets.require_independent_stage(self.public)
        self.assertEqual(old.read_text(), 'previous app')
        linked.unlink()
        linked.write_text('independent app')
        assets.require_independent_stage(self.public)
        linked.unlink()
        linked.symlink_to(old)
        with self.assertRaises(ValueError):
            assets.require_independent_stage(self.public)


if __name__ == '__main__':
    unittest.main()
