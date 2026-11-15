#!/usr/bin/env python3
"""Kill the scoped file-code transition at two real installed VM commit boundaries."""
import hashlib,importlib.util,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
if __name__=='__main__':
 spec=importlib.util.spec_from_file_location('document_recovery_vm',ROOT/'scripts/upgrade-signin-native-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm);checks=[];result={'status':'FAIL'}
 try:
  native='a3a5c3dd20dde6bdd0b8af77c79a8e28c25a8de2f60172fbb7a44500b70e4558';helper='/srv/codi-network-fixture/document-code-r1.py';config='/etc/codi-native-fixture/managed.json';assert vm.runtime()['manifestSHA256']==native
  query="import hashlib,json;from pathlib import Path;c=json.loads(Path('"+config+"').read_text());p=Path(c['userFiles']['configFile']);print(json.dumps({'config':hashlib.sha256(p.read_bytes()).hexdigest(),'worker':json.loads(p.read_text())['manifestSHA256']}))"
  before=json.loads(vm.remote('python3 -I -B -c '+shlex.quote(query)));assert before['worker']=='fd17711bbb04f7af4cd7c79237f90604cc2b680621d0d26f1d193128c1cd0b9e'
  old_path=vm.remote("python3 -I -B -c "+shlex.quote("from pathlib import Path;import json;print(next(str(p.parent) for p in Path('/srv/codi-network-fixture').glob('*/files-service.json') if json.loads(p.read_text())['files']['gateway_service/client.mjs']['sha256']=='c9271be6f17437fe3ab252714c642aa9e6e40010ee506e7dd69b6ed20d5bfdec'))")).strip()
  old_pin=vm.remote('sha256sum '+shlex.quote(old_path+'/files-service.json')).split()[0]
  for point in ['files-configured','pins-configured']:
   code="import importlib.util,os;from pathlib import Path;s=importlib.util.spec_from_file_location('fault_upgrade',"+repr(helper)+");m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.execute(Path("+repr(config)+"),"+repr(native)+",Path("+repr(old_path)+"),"+repr(old_pin)+",phase=lambda n:os._exit(73) if n=="+repr(point)+" else None)"
   killed=subprocess.run([*vm.vm.ssh_args(),'/srv/codi-network-fixture/venv/bin/python -I -B -c '+shlex.quote(code)],capture_output=True,text=True,timeout=90);assert killed.returncode==73,killed.stderr
   recovered=json.loads(vm.remote(shlex.join(['/srv/codi-network-fixture/venv/bin/python','-I','-B',helper,'recover','--config',config,'--native-manifest-sha256',native])));assert recovered['status']=='code-recovered'
   after=json.loads(vm.remote('python3 -I -B -c '+shlex.quote(query)));assert after==before;checks.append('actual process death after '+point+' restores exact code pins without data restore')
  result.update(status='PASS',checks=checks,liveWebhostChanged=False,accountOrFileDataRestored=False)
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/document-code-recovery-result.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
