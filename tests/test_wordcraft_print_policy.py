"""The print exception cannot broaden desktop/app/object/script permissions."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('viewer_operator', ROOT / 'deploy/viewer_static_operator.py')
operator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(operator)

class WordCraftPrintPolicy(unittest.TestCase):
    def test_only_wordcraft_html_gets_blob_frames(self):
        base = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; frame-src 'self'; object-src 'none'; base-uri 'none'"
        original = 'ksu.codes {\n\theader >Content-Security-Policy "' + base + '"\n\thandle {\n\t\troot * /unchanged/public\n\t}\n}'
        result = operator.with_wordcraft_print_policy(original)
        self.assertIn('@wordcraft_print path /wordcraft/index.html', result)
        self.assertIn('@other_viewer not path /wordcraft/index.html', result)
        self.assertIn('header @other_viewer >Content-Security-Policy "' + base + '"', result)
        self.assertIn('header @wordcraft_print >Content-Security-Policy "' + base.replace("frame-src 'self';", "frame-src 'self' blob:;") + '"', result)
        self.assertEqual(result.count("object-src 'none'"), 2)
        self.assertIn('root * /unchanged/public', result)
        self.assertNotIn('unsafe-inline', result)
        with self.assertRaises(AssertionError): operator.with_wordcraft_print_policy(result)

    def test_unknown_policy_is_not_replaced(self):
        for policy in ["frame-src *; object-src 'none';", "frame-src 'self'; object-src *;"]:
            with self.assertRaises(AssertionError): operator.with_wordcraft_print_policy('ksu.codes {\n\theader >Content-Security-Policy "' + policy + '"\n}')

if __name__ == '__main__': unittest.main()
