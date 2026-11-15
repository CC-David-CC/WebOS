#!/usr/bin/env python3
"""Run the real xterm suite against the installed, sealed strict native15 artifact."""
import copy,hashlib,importlib.util,json,shutil,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
EXPECTED='391724a55907489e2e975575057893bff3dcd3a632db43db18df8e06892280cb'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if __name__=='__main__':
 result={'status':'FAIL','liveWebhostChanged':False,'fixtureCertificatePinUsed':True}
 try:
  vm=module('xterm_vm_runtime',ROOT/'scripts/upgrade-signin-native-vm.py');vm.vm.status();runtime=vm.runtime();assert runtime['manifestSHA256']==EXPECTED
  installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));suite=module('xterm_installed_browser',ROOT/'scripts/xterm-browser-check.py');original=suite.call
  def fixture_call(path,data=None,method=None):
   if path=='/session' and data:
    data=copy.deepcopy(data);data['capabilities']['alwaysMatch']['goog:chromeOptions']['args'].append('--ignore-certificate-errors-spki-list='+installed['fixtureSPKI'])
   return original(path,data,method)
  suite.call=fixture_call;image=ROOT/'.build/checks/xterm-nano.png'
  if image.exists():shutil.copyfile(image,image.with_name('xterm-nano-local.png'))
  result.update(suite.browser(SimpleNamespace(origin=installed['publicOrigin'],base='/hidden')),runtime=runtime,scope=__doc__)
  if image.exists():shutil.copyfile(image,image.with_name('xterm-nano-native-vm.png'))
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/xterm-native-vm-browser-result.json'
  if out.exists():out.rename(out.with_name('xterm-native-vm-browser-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
