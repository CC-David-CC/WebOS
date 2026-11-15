#!/usr/bin/env python3
"""Exercise root operator command in an owned temporary directory only."""
import importlib.util,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('gate_operator',ROOT/'scripts/operator-anonymous-introductions.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert os.geteuid()==0
with tempfile.TemporaryDirectory(prefix='codi-operator-gate-') as temp:
 m.POLICY=Path(temp)/'anonymous-introductions'
 for state in ['enabled','disabled','enabled']:
  sys.argv=['operator',state];m.main();assert m.POLICY.read_text()==state+'\n' and m.POLICY.stat().st_uid==0 and (m.POLICY.stat().st_mode&0o777)==0o644
 m.POLICY.unlink();m.POLICY.symlink_to(Path(temp)/'elsewhere')
 try:sys.argv=['operator','disabled'];m.main();raise AssertionError('symlink accepted')
 except SystemExit:pass
print(json.dumps({'status':'PASS','scope':'Owned temporary directory, root operator only; no live state changed'}))
