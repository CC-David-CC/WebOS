#!/usr/bin/env python3
"""Reproducible recovery source bundle; does not qualify host execution."""
import hashlib, importlib.util, json, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',HERE/'build-beta-successor.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
with tempfile.TemporaryDirectory(prefix='beta-successor-build-') as t:
 root=Path(t); a=root/'a'; c=root/'c'
 b.build(a);b.build(c)
 assert (a/'inventory.json').read_bytes()==(c/'inventory.json').read_bytes()
 manifest=json.loads((a/'inventory.json').read_bytes())
 assert len(manifest)==28
 for p,h in manifest.items():assert hashlib.sha256((a/p).read_bytes()).hexdigest()==h
 for action in ('plan','apply'):
  p=subprocess.run([sys.executable,'-B',str(a/'ops/beta_files_recover.py'),action],capture_output=True,text=True)
  assert p.returncode==2 and 'invalid choice' in p.stderr
 try:b.build(a)
 except FileExistsError:pass
 else:raise AssertionError('existing bundle accepted')
 # Test source pin failure with a private disposable copy of the small source tree.
 ops=root/'source'/'ops';shutil.copytree(b.OPS,ops)
 source=ops/'beta_launcher.py';source.write_bytes(source.read_bytes()+b'\n')
 b.OPS=ops
 try:b.build(root/'tampered')
 except ValueError as e:assert 'Pinned input mismatch' in str(e)
 else:raise AssertionError('tampered input accepted')
 assert not (root/'tampered').exists()
print('PASS reproducible inventory, recover-only CLI, no-overwrite and tamper refusal')
