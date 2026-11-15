#!/usr/bin/env python3
"""Check the uninstalled steward publisher's exact-release verifier."""
import importlib.util,json,shutil,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True;ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_publisher',ROOT/'scripts/publish-steward-account.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=ROOT/'.build/releases/connected-browser-files-r1';b=ROOT/'.build/releases/steward-account-features-r1';checks=[]
def rejected(name,old,new):
 try:m.verify_release(old,new)
 except (AssertionError,ValueError,OSError):checks.append(name);return
 raise AssertionError(name)
assert m.verify_release(a,b)['manifestSHA256']==m.NEW;checks.append('exact candidate accepted')
with tempfile.TemporaryDirectory(prefix='codi-steward-publisher-check-') as t:
 p=Path(t)/'candidate';shutil.copytree(b,p);target=p/'steward/protocol.py';raw=target.read_bytes();target.write_bytes(raw+b'\n# mutation\n');rejected('native file mutation refused',a,p);target.write_bytes(raw)
 extra=p/'extra';extra.write_text('unexpected');rejected('extra file refused',a,p);extra.unlink()
 target.unlink();target.symlink_to(a/'steward/protocol.py');rejected('symlink refused',a,p)
rejected('incorrect release ordering refused',b,a)
print(json.dumps({'status':'PASS','checks':checks,'scope':'Uninstalled publisher exact-release verification; no installed transition or recovery.'},indent=2))
