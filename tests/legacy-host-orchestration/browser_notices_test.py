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
        liberation=ROOT/'.build/browser-notice-inputs/liberation-license.txt'
        compiled=ROOT/'.build/browser-notice-inputs/compiled-component-notices.txt'
        rust=ROOT/'.build/browser-notice-inputs/rust-component-notices-corrected.txt'
        stdlib=ROOT/'.build/browser-notice-inputs/rust-stdlib-copyright.html'
        pulse=ROOT/'.build/browser-notice-inputs/cubeb-pulse-license.txt'
        rlbox=ROOT/'.build/browser-notice-inputs/rlbox-license.txt'
        graphics=ROOT/'.build/browser-notice-inputs/graphics-component-notices.txt'
        freetype=ROOT/'.build/browser-notice-inputs/freetype-FTL.txt'
        upstream=ROOT/'.build/browser-notice-inputs/rust-upstream-licenses.txt'
        enum_map=ROOT/'.build/browser-notice-inputs/enum-map-notices.txt'
        if not all(p.is_file() for p in (firefox,ems,wisp,liberation,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map)):self.skipTest('Pinned engine build inputs not available')
        with tempfile.TemporaryDirectory(prefix='codi-browser-notices-test-') as t:
            out=Path(t)/'notices';records=module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map,out)
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
            self.assertIn('SIL OPEN FONT LICENSE Version 1.1',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/abseil-cpp/LICENSE',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/content_analysis_sdk/LICENSE',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/seahash/Cargo.toml.orig',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/app_units/Cargo.toml.orig',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/core_maths/Cargo.toml.orig',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/debug_tree/Cargo.toml.orig',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/void/Cargo.toml',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('Target-built vendored Rust crate notices',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('third_party/rust/remove_dir_all/LICENCE-MIT',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('Copyright notices for The Rust Standard Library',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('cubeb-pulse-rs LICENSE',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('Copyright (c) 2019 UCSD PLSysSec',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('gfx/angle/checkout/LICENSE',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('The FreeType Project LICENSE',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('Pinned upstream Rust license files',(out/'emscripten-licenses.txt').read_text())
            self.assertIn('enum-map 2.7.3 vendored SPDX copyright lines',(out/'emscripten-licenses.txt').read_text())
            index=(out/'index.html').read_text()
            self.assertIn('copyright © 2026 The FreeType Project',index)
            for name,digest in module.SOURCES.items():self.assertIn(name,index);self.assertIn(digest,index)
            with self.assertRaises(ValueError):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map,out)
            bad=Path(t)/'wrong-license.txt';bad.write_text('wrong')
            with self.assertRaisesRegex(ValueError,'font license'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',bad,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'component notices'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,bad,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'Rust component notices'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,bad,stdlib,pulse,rlbox,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'standard library'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,bad,pulse,rlbox,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'Pulse Rust license'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,bad,rlbox,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'RLBox license'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,bad,graphics,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'graphics component notices'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,bad,freetype,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'FreeType license'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,graphics,bad,upstream,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'upstream Rust notices'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,bad,enum_map,Path(t)/'other')
            with self.assertRaisesRegex(ValueError,'enum-map notices'):module.prepare(firefox,ems,wisp,ROOT/'apps/system/browser/docs/LICENSE',liberation,compiled,rust,stdlib,pulse,rlbox,graphics,freetype,upstream,bad,Path(t)/'other')


if __name__=='__main__':unittest.main()
