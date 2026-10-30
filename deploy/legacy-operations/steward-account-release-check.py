#!/usr/bin/env python3
"""Verify a sealed steward-only candidate and fail closed on local mutations."""
import hashlib,importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.build/releases/connected-browser-files-r1';CANDIDATE=ROOT/'.build/releases/steward-account-features-r1';BASE_PIN='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46';PIN='b355c1b60f2f43574704334e12ed0edc72995c7d5155e8fbb82fb6889b5df68e';CHANGED={'steward/leases.py','steward/protocol.py'}
spec=importlib.util.spec_from_file_location('release_contract',BASE/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);checks=[]
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
def refused(name,path):
 try:contract.verify(path)
 except (ValueError,OSError):checks.append(name);return
 raise AssertionError(name)
check('base manifest remains pinned',contract.verify(BASE)['manifestSHA256']==BASE_PIN)
check('candidate manifest remains pinned',contract.verify(CANDIDATE)['manifestSHA256']==PIN)
a=json.loads((BASE/'connected-release.json').read_bytes());b=json.loads((CANDIDATE/'connected-release.json').read_bytes());check('only the two reviewed steward files differ',{n for n in a['files'] if a['files'][n]!=b['files'][n]}==CHANGED and a.keys()==b.keys() and a['files'].keys()==b['files'].keys())
check('public release bytes remain identical',(BASE/'release.json').read_bytes()==(CANDIDATE/'release.json').read_bytes())
with tempfile.TemporaryDirectory(prefix='codi-steward-release-check-') as tmp:
 p=Path(tmp)/'candidate';shutil.copytree(CANDIDATE,p)
 target=p/'steward/protocol.py';original=target.read_bytes();target.write_bytes(original+b'\n# altered\n');refused('tampered steward source rejected',p);target.write_bytes(original)
 extra=p/'unexpected';extra.write_text('untracked');refused('unexpected file rejected',p);extra.unlink()
 target.unlink();target.symlink_to(BASE/'steward/protocol.py');refused('symlinked native source rejected',p)
print(json.dumps({'status':'PASS','checks':checks,'candidateSHA256':PIN,'scope':'Local release-inventory and tamper checks; no installed transition or state preservation.'},indent=2))
