#!/usr/bin/env python3
"""Check candidate rollout pins reject changed artifacts without touching services."""
import importlib.util,json,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];packet=ROOT/'.build/rollout/queued-send-steward-r1';base=ROOT/'.build/releases/channel-short-provider-live-r1';candidate=ROOT/'.build/releases/queued-send-steward-candidate-r1'
spec=importlib.util.spec_from_file_location('publisher',packet/'publish-device-test.py');publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
checks=[]
def reject(fn):
 try:fn()
 except (AssertionError,ValueError):return
 raise AssertionError('mutation was accepted')
result=publisher.check(base,candidate);assert result['nativeFilesUnchanged']==56 and result['nativeStewardChanged'];checks.append('verified candidate allows only pinned steward native change')
template=(packet/'renewal-template.service').read_bytes();rendered=publisher.render_timer(template,'a'*64,publisher.NEW);assert b'a'*64 in rendered and publisher.NEW.encode() in rendered;checks.append('timer retains template and changes only pinned targets')
reject(lambda:publisher.render_timer(template+b'\n','a'*64,publisher.NEW));checks.append('modified timer template refused')
reject(lambda:publisher.render_timer(template,'a'*64,'b'*64));checks.append('unexpected release refused')
with tempfile.TemporaryDirectory(prefix='codi-rollout-check-',dir=ROOT/'.build') as tmp:
 copy=Path(tmp)/'release';shutil.copytree(candidate,copy);target=copy/'steward/server.py';target.write_bytes(target.read_bytes()+b'\n');reject(lambda:publisher.check(base,copy));checks.append('altered steward file refused')
with tempfile.TemporaryDirectory(prefix='codi-timer-recover-',dir=ROOT/'.build') as tmp:
 from types import SimpleNamespace
 folder=Path(tmp);unit=folder/'unit';control=folder/'control';control.write_text('candidate control');publisher.TIMER_UNIT=unit
 helper=SimpleNamespace(CONTROL=control)
 def fake_update(m,config,source):
  assert unit.read_bytes()==source
  desired=publisher.render_timer(source,publisher.sha(control),publisher.NEW);unit.write_bytes(desired)
  return {'sha256':publisher.sha(unit)}
 publisher.update_timer=fake_update
 unit.write_bytes(template);assert publisher.recover_timer(helper,{'manifestSHA256':publisher.NEW},template)['status']=='repaired';checks.append('interrupted timer update repairs known old template')
 assert publisher.recover_timer(helper,{'manifestSHA256':publisher.NEW},template)['status']=='already-current';checks.append('timer recovery is idempotent')
 unit.write_text('unknown');reject(lambda:publisher.recover_timer(helper,{'manifestSHA256':publisher.NEW},template));checks.append('timer recovery rejects unknown unit')
 reject(lambda:publisher.recover_timer(helper,{'manifestSHA256':publisher.OLD},template));checks.append('timer recovery rejects old release')
print(json.dumps({'status':'PASS','checks':checks,'liveChanged':False},indent=2))
