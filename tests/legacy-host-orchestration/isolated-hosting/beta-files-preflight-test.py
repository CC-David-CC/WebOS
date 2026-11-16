#!/usr/bin/env python3
"""Read-only preflight artifact and refusal tests on disposable files."""
import hashlib,importlib.util,json,os,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('preflight',root/'ops/beta_files_preflight.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:m.inspect_host();raise AssertionError('non-webhost preflight accepted')
except ValueError as e:assert 'box-webhost' in str(e)
with tempfile.TemporaryDirectory(prefix='opfs-trust-fixture-',dir='/home/dflanag3') as tmp:
 p=Path(tmp);p.chmod(0o775);m.protected_ancestors(p,os.getuid())
 p.chmod(0o777)
 try:m.protected_ancestors(p,os.getuid());raise AssertionError('world-writable path accepted')
 except ValueError:pass
 p.chmod(0o775);subprocess.run(['/usr/bin/setfacl','-m','u:nobody:rwx',str(p)],check=True)
 try:m.protected_ancestors(p,os.getuid());raise AssertionError('untrusted ACL writer accepted')
 except ValueError:pass
 subprocess.run(['/usr/bin/setfacl','-b',str(p)],check=True)
with tempfile.TemporaryDirectory(prefix='opfs-preflight-') as tmp:
 p=Path(tmp);(p/'data').write_bytes(b'fixture');manifest=json.dumps({'files':{'data':{'bytes':7,'sha256':hashlib.sha256(b'fixture').hexdigest()}}}).encode();(p/'manifest.json').write_bytes(manifest);(p/'data').chmod(0o644);(p/'manifest.json').chmod(0o644);pin=hashlib.sha256(manifest).hexdigest()
 # Content/inventory test only: /tmp ancestry is intentionally not trusted.
 try:m.protected_ancestors(p,os.getuid());raise AssertionError('unprotected /tmp accepted')
 except ValueError:pass
 m.protected_ancestors=lambda path,uid:None
 assert m.tree(p,'manifest.json',pin,os.getuid())['files']==1
 (p/'extra').write_text('unexpected');(p/'extra').chmod(0o644)
 try:m.tree(p,'manifest.json',pin,os.getuid());raise AssertionError('extra accepted')
 except ValueError:pass
 (p/'extra').unlink();(p/'data').write_bytes(b'tampered')
 try:m.tree(p,'manifest.json',pin,os.getuid());raise AssertionError('tamper accepted')
 except ValueError:pass
 (p/'data').unlink();(p/'data').symlink_to(p/'manifest.json')
 try:m.tree(p,'manifest.json',pin,os.getuid());raise AssertionError('symlink accepted')
 except ValueError:pass
print('PASS read-only preflight host boundary, trusted admin ancestry, untrusted ACL/world-writer and artifact refusal')
