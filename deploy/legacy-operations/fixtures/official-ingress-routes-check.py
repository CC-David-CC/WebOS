#!/usr/bin/env python3
"""Check the official ingress candidate is narrow and handles mount prefixes."""
import importlib.util
from pathlib import Path
root=Path(__file__).resolve().parents[2];s=importlib.util.spec_from_file_location('routes',root/'scripts/official-ingress-routes.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for prefix in ('','/hidden','/nested/site'):
 text=m.routes(prefix,8145);assert text.count('handle ')==6 and text.count('reverse_proxy 127.0.0.1:8145')==6 and text.count('uri strip_prefix')==(6 if prefix else 0)
 assert '/internal/' not in text and '*' not in text and 'handle '+prefix+'/official-ingest/use {' in text
for prefix,port in [('/../bad',8145),('/bad/',8145),('//bad',8145),('',80),('',65536)]:
 try:m.routes(prefix,port);raise AssertionError('invalid route accepted')
 except ValueError:pass
print('PASS: exact route list, private health excluded, mount prefixes and invalid inputs')
