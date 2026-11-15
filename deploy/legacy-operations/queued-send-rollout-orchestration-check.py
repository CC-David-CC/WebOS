#!/usr/bin/env python3
"""Run rollout orchestration against temporary fake host state."""
import hashlib,importlib.util,json,shutil,socket,tempfile,types
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'.build/rollout/queued-send-steward-r1/publish-device-test.py';spec=importlib.util.spec_from_file_location('publisher',src);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);checks=[];commit='a'*40
with tempfile.TemporaryDirectory(prefix='codi-rollout-orchestration-') as tmp:
 root=Path(tmp);host=root/'host';host.mkdir();(host/'.controller.lock').write_text('');repo=root/'repo';packet=repo/'tools/codiserver/queued-send-steward-r1';packet.mkdir(parents=True);shutil.copyfile(src,packet/'publish-device-test.py');shutil.copyfile(src.parent/'renewal-template.service',packet/'renewal-template.service');(packet/'release').mkdir();before=root/'before';dest=root/'after';before.mkdir();dest.mkdir();control=root/'managed.json';unit=root/'timer';unit.write_bytes((packet/'renewal-template.service').read_bytes());state={'origin':'https://ksu.codes','basePath':'','manifestSHA256':p.OLD};control.write_text(json.dumps(state));helper=types.SimpleNamespace(HOST=host,REPO=repo,CONTROL=control,PYTHON='python',protected=lambda _:None,hosting_pins=lambda:p.PINS,capture=lambda _: {'ok':True},preserved=lambda *_:None,install=lambda *_:None)
 def run(args,*_):return commit if 'rev-parse' in args else ''
 helper.run=run
 def native(action,*args):
  assert action=='upgrade';state['manifestSHA256']=p.NEW;control.write_text(json.dumps(state));return {'status':'upgraded'}
 helper.native=native
 p.BEFORE=before;p.DEST=dest;p.TIMER_UNIT=unit;p.HELPER=root/'helper';p.HELPER.mkdir();(p.HELPER/'x').write_text('helper');p.HELPER=p.HELPER/'x';p.__file__=str(packet/'publish-device-test.py');p.module=lambda *_:helper;p.check=lambda *_:{'nativeStewardChanged':True};p.sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest();helper_hash=p.sha(p.HELPER);p.HELPER.parent.rename(root/helper_hash);p.HELPER=root/helper_hash/'x'
 fail={'enabled':True}
 def update(m,c,template):
  if fail['enabled']:raise OSError('injected failure after native upgrade')
  desired=p.render_timer(template,p.sha(control),p.NEW);unit.write_bytes(desired);return {'sha256':p.sha(unit)}
 p.update_timer=update
 with patch.object(p.os,'geteuid',return_value=0),patch.object(p.socket,'gethostname',return_value='box-webhost'):
  # Protected executable path is content-addressed, as on the host.
  installed=root/p.sha(src);installed.mkdir();shutil.copyfile(src,installed/'publisher.py');p.__file__=str(installed/'publisher.py')
  try:p.main('activate',commit)
  except OSError:pass
  else:raise AssertionError('fault did not interrupt activation')
  assert state['manifestSHA256']==p.NEW and unit.read_bytes()==(packet/'renewal-template.service').read_bytes();checks.append('timer failure leaves candidate and original timer detectable')
  fail['enabled']=False;result=p.main('recover-timer',commit);assert result['renewalTimer']['status']=='repaired';checks.append('recovery completes timer after interrupted activation')
  assert p.main('recover-timer',commit)['renewalTimer']['status']=='already-current';checks.append('recovery is idempotent')
  assert p.main('verify',commit)['afterManifestSHA256']==p.NEW;checks.append('verification accepts repaired candidate state')
print(json.dumps({'status':'PASS','checks':checks,'scope':'Actual publisher main with fake helper, timer writes and temporary files; no systemd or live changes.'},indent=2))
