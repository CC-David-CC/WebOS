#!/usr/bin/env python3
"""Exercise the installed xterm release's real verified cache, offline and rebuild."""
import argparse,hashlib,importlib.util,json,time,urllib.request
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-xterm-r1'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--public',action='store_true');p.add_argument('--release-dir',type=Path,default=RELEASE);p.add_argument('--catalog-path');p.add_argument('--output');p.add_argument('--base-path',default='/hidden');a=p.parse_args();RELEASE=a.release_dir.resolve();result={'status':'FAIL','public':a.public}
 try:
  catalog=RELEASE/a.catalog_path if a.catalog_path else next(RELEASE.glob('assets/desktop/apps-v2-*.json'));m=module('xterm_cache_suite',ROOT/'scripts/device-cache-browser-check.py');m.ROOT=RELEASE
  if a.public:
   origin='https://ksu.codes';args=[]
   with urllib.request.urlopen(origin+a.base_path+'/index.html',timeout=20) as response:assert response.read()==(RELEASE/'index.html').read_bytes()
  else:
   vm=module('xterm_cache_vm',ROOT/'scripts/upgrade-signin-native-vm.py');installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'));origin=installed['publicOrigin'];args=['--ignore-certificate-errors-spki-list='+installed['fixtureSPKI']]
  result.update(m.browser(SimpleNamespace(origin=origin,base=a.base_path,chromeArgs=args,catalogPath=str(catalog.relative_to(RELEASE)))),defaultPublicTLS=a.public,releaseSHA256=hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks'/(a.output or ('xterm-cache-public-result.json' if a.public else 'xterm-cache-native-vm-result.json'))
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
