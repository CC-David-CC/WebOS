#!/usr/bin/env python3
"""Actual xterm/nano key-bar and phone regressions on an exact native candidate."""
import argparse,copy,hashlib,importlib.util,json,time,urllib.request
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
def module(name,file):
 s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(release,public):
 expected=hashlib.sha256((release/'connected-release.json').read_bytes()).hexdigest();vm=None
 if public:origin='https://ksu.codes';spki=None
 else:
  vm=module('touch_key_vm',ROOT/'scripts/upgrade-signin-native-vm.py');before=vm.runtime();assert before['manifestSHA256']==expected;installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));origin=installed['publicOrigin'];spki=installed['fixtureSPKI']
 if public:
  with urllib.request.urlopen(origin+'/hidden/index.html',timeout=20) as r:assert r.read()==(release/'index.html').read_bytes()
 suite=module('touch_key_xterm',ROOT/'scripts/xterm-browser-check.py');original=suite.call
 def call(path,data=None,method=None):
  if path=='/session':
   data=copy.deepcopy(data);args=data['capabilities']['alwaysMatch']['goog:chromeOptions']['args'];assert not any('ignore-certificate' in a for a in args)
   if spki:args.append('--ignore-certificate-errors-spki-list='+spki)
  return original(path,data,method)
 suite.call=call;result=suite.browser(SimpleNamespace(origin=origin,base='/hidden'))
 if vm:assert before==vm.runtime()
 assert len(result['checks'])==38
 return result|{'scope':__doc__,'nativeManifestSHA256':expected,'publicURL':origin+'/hidden/','publicSiteUsed':public,'defaultPublicTLS':public,'fixtureSPKIOnly':not public,'suiteSourceSHA256':hashlib.sha256((ROOT/'scripts/xterm-browser-check.py').read_bytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--release-dir',type=Path,required=True);p.add_argument('--public',action='store_true');a=p.parse_args();result={'status':'FAIL'}
 try:result.update(run(a.release_dir.resolve(),a.public))
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/('terminal-touch-'+('public' if a.public else 'vm')+'-result.json')
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
