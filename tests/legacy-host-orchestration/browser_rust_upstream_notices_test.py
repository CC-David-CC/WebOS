"""Verify pinned upstream notice collection rejects changed or unsafe inputs."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rust_upstream_notices',ROOT/'apps/system/browser/tools/collect_rust_upstream_licenses.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class Response:
    def __init__(self,value):self.value=value
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,limit):return self.value[:limit]

class UpstreamNoticesTest(unittest.TestCase):
    def test_exact_revision_and_digest_are_required(self):
        contents=b'Example license and copyright\n'
        item={'repository':'https://github.com/example/project','revision':'1'*40,'packages':['sample 1.0'],'files':[{'path':'license/MIT','sha256':hashlib.sha256(contents).hexdigest()}]}
        manifest={'version':'codi-rust-upstream-notices/1','sources':[item]}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'manifest.json';path.write_text(json.dumps(manifest))
            with patch.object(module,'urlopen',return_value=Response(contents)) as fetch:
                output=module.collect(path);self.assertIn(contents.rstrip(),output)
                self.assertIn('/'+('1'*40)+'/license/MIT',fetch.call_args.args[0].full_url)
            with patch.object(module,'urlopen',return_value=Response(b'changed')):
                with self.assertRaisesRegex(ValueError,'changed'):module.collect(path)
            item['files'][0]['path']='../secret';path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'Invalid license path'):module.collect(path)

if __name__=='__main__':unittest.main()
