#!/usr/bin/env python3
"""Check candidate generator against a captured managed-hosting baseline."""
import copy
import importlib.util
from pathlib import Path
import sys
import tomllib

ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'.build/browser-hosting-candidate'
sys.path.insert(0,str(folder))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
base=module('base',folder/'common-base.py');candidate=module('candidate',folder/'common.py')
data=tomllib.loads((folder/'sites.toml').read_text())
for mode in ('prepare','production'):assert base.caddy(data,mode)==candidate.caddy(data,mode)
site=next(item for item in data['sites'] if item['domain']=='ksu.codes')
site.update(codi_browser_relay=True,codi_large_files=True,codi_login_filter=True)
candidate.validate(data);render=candidate.caddy(data,'production')
for value in ['unix//run/codi-browser/relay.sock','X-Codi-Client-IP {http.request.remote.host}','max_size 192MiB','/assets/desktop/apps/browser/*/src/engine-worker.js']:
    assert value in render,value
roundtrip=tomllib.loads(candidate.dump(data));candidate.validate(roundtrip)
assert next(item for item in roundtrip['sites'] if item['domain']=='ksu.codes')['codi_browser_relay'] is True
for target in data['sites']:
    if target['domain']=='ksu.codes':continue
    invalid=copy.deepcopy(data);next(item for item in invalid['sites'] if item['domain']==target['domain'])['codi_browser_relay']=True
    try:candidate.validate(invalid)
    except ValueError:pass
    else:raise AssertionError('Other site accepted relay flag: '+target['domain'])
print('PASS managed baseline is unchanged without opt-ins; KSU flags render and round-trip')
