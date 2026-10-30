"""Test the production-derived file-worker export boundary."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('large_file_worker',ROOT/'active-system/scripts/build-large-file-worker.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class WorkerBuildTest(unittest.TestCase):
    def test_pinned_baseline_and_deterministic_candidate(self):
        source=ROOT/'.build/gateway-candidate/base'
        if not source.is_dir():self.skipTest('Captured production worker unavailable')
        with tempfile.TemporaryDirectory(prefix='codi-large-worker-test-') as t:
            folder=Path(t);baseline=folder/'base';shutil.copytree(source,baseline)
            first=module.build(baseline,folder/'one');second=module.build(baseline,folder/'two')
            self.assertEqual(first,second)
            self.assertEqual(first['manifestSHA256'],'53588b25c06c7b88e038bcca4cca13b8de9bcabc35b952d463c1d7ff3727b5c0')
            self.assertTrue(first['requirementsPreserved'])
            self.assertFalse(first['installed'])
            (baseline/'gateway_service/auth.py').write_text('changed')
            with self.assertRaises(ValueError):module.build(baseline,folder/'three')


if __name__=='__main__':unittest.main()
