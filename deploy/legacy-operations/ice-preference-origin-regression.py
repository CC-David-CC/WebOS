#!/usr/bin/env python3
"""Run the existing account lifecycle suite with the native14 issuer class."""
import hashlib,json,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT))
import origin_service.lifecycle as lifecycle
from origin_service.ice_preference import PreferenceService
original=lifecycle.Service
try:
 lifecycle.Service=PreferenceService
 try:runpy.run_path(str(ROOT/'scripts/origin-lifecycle-check.py'),run_name='__main__')
 except SystemExit as result:
  if result.code not in (None,0):raise
finally:lifecycle.Service=original
value=json.loads((ROOT/'.build/checks/origin-lifecycle-result.json').read_text())
assert value['status']=='PASS' and value['tests']==90
value['scope']='Existing 90 real crypto/SQLite/account lifecycle regressions executed with native14 PreferenceService; no browser or public rollout claim'
value['sha256'].update({name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['origin_service/ice_preference.py','scripts/ice-preference-origin-regression.py']})
(ROOT/'.build/checks/ice-preference-origin-regression-result.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'status':value['status'],'tests':value['tests'],'native14IssuerClassSelected':True}))
