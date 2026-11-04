#!/usr/bin/env python3
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
here=Path(__file__).resolve().parent;enabled=Path(sys.argv[1])
with tempfile.TemporaryDirectory(prefix='main-package-test-') as d:
 root=Path(d);cmd=[sys.executable,'-B',str(here/'build-protected-package.py'),str(enabled)]
 for name in ('a','b'):subprocess.run([*cmd,str(root/name)],check=True,capture_output=True)
 assert (root/'a/manifest.json').read_bytes()==(root/'b/manifest.json').read_bytes()
 assert len(json.loads((root/'a/manifest.json').read_bytes()))==7
 assert subprocess.run([*cmd,str(root/'a')],capture_output=True).returncode
 bad=root/'bad';shutil.copytree(enabled,bad);p=bad/'main-launcher.py';p.write_bytes(p.read_bytes()+b'\n')
 assert subprocess.run([sys.executable,'-B',str(here/'build-protected-package.py'),str(bad),str(root/'rejected')],capture_output=True).returncode and not (root/'rejected').exists()
print('PASS deterministic seven-file package, no-overwrite and launcher drift rejection')
