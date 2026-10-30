"""Verify the notice set comes from the exact pinned engine dependencies."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('browser_notices',ROOT/'apps/system/browser/tools/prepare_notices.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class NoticesTest(unittest.TestCase):
    def test_real_build_notices_preserve_licenses_and_link_exact_sources(self):
        folder=ROOT/'.build/browser-source-provision'
        firefox=folder/'firefox-license.generated.html';ems=folder/'emscripten-6.0.1-patched-source.tar.zst';wisp=folder/'wisp-js-0.4.1-source.tar.zst'
        if not all(p.is_file() for p in (firefox,ems,wisp)):self.skipTest('Pinned engine build inputs not available')
        with tempfile.TemporaryDirectory(prefix='codi-browser-notices-test-') as t:
            out=Path(t)/'notices';records=module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',out)
            manifest=json.loads((out/'notice-manifest.json').read_text())
            self.assertEqual(manifest['files'],records)
            self.assertEqual(manifest['sourceArchives'],module.SOURCES)
            page=(out/'firefox-licenses.html').read_text()
            self.assertIn('Mozilla Public License 2.0',page)
            self.assertIn('GNU Lesser General Public License',page)
            self.assertNotIn('href="about:license#',page)
            self.assertNotIn('href="chrome://global/skin/',page)
            self.assertIn('GNU AFFERO GENERAL PUBLIC LICENSE',(out/'wisp-license.txt').read_text())
            self.assertIn('emscripten/system/lib/libc/musl/COPYRIGHT',(out/'emscripten-licenses.txt').read_text())
            index=(out/'index.html').read_text()
            for name,digest in module.SOURCES.items():self.assertIn(name,index);self.assertIn(digest,index)
            with self.assertRaises(ValueError):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',out)


if __name__=='__main__':unittest.main()
