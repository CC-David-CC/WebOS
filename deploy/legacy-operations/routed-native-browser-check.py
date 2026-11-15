#!/usr/bin/env python3
"""Run actual browser suites against the installed native16 fixture, not a proxy.

Test-only module imports resolve to the same versioned graph as the real host.
The certificate exception is the isolated fixture's exact SPKI, never public TLS.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import time
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent.parent
EXPECTED='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200'
RELEASE=ROOT/'.build/releases/connected-routed-r8'
SUITES={'group':'routed-group-browser-check.py','history':'routed-history-browser-check.py','xterm':'xterm-browser-check.py','lifecycle':'public-app-lifecycle-stress-check.py','four':'routed-four-room-browser-check.py'}
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def run(kind):
 vm=module('routed_native_vm',ROOT/'scripts/upgrade-signin-native-vm.py')
 runtime=vm.runtime();assert runtime['manifestSHA256']==EXPECTED
 installed=json.loads(vm.remote('cat /srv/codi-network-fixture/installed-result.json'))
 graph=json.loads((RELEASE/'assets/desktop/network-release.json').read_text())
 suite=module('installed_routed_'+kind,ROOT/'scripts'/SUITES[kind]);original=suite.call
 state=SimpleNamespace(origin=installed['publicOrigin'],base='/hidden',http_chat=False,strictAnonymous=True)
 observation={'requests':0,'posts':0,'postBodiesObserved':0,'unavailablePostBodies':0}
 def observe(sid):
  for row in original('/session/'+sid+'/log',{'type':'performance'}):
   message=json.loads(row['message'])['message']
   if message['method']!='Network.requestWillBeSent':continue
   request=message['params']['request'];observation['requests']+=1
   if request['method']!='POST':continue
   observation['posts']+=1;body=request.get('postData')
   if body is None and request.get('hasPostData'):
    try:body=original('/session/'+sid+'/goog/cdp/execute',{'cmd':'Network.getRequestPostData','params':{'requestId':message['params']['requestId']}})['postData']
    except RuntimeError:observation['unavailablePostBodies']+=1
   if body is not None:
    observation['postBodiesObserved']+=1
    if 'ROUTED_HISTORY' in body or 'ROUTED_MARKER_' in body:state.http_chat=True
 def call(path,data=None,method=None):
  if path=='/session' and data:
   data=copy.deepcopy(data);options=data['capabilities']['alwaysMatch'];options['goog:chromeOptions']['args'].append('--ignore-certificate-errors-spki-list='+installed['fixtureSPKI'])
   options.setdefault('goog:loggingPrefs',{})['performance']='ALL'
  if data and isinstance(data.get('script'),str):
   data=copy.deepcopy(data)
   data['script']=data['script'].replace('./network/','./'+graph['directory']+'/')
  if method=='DELETE' and path.startswith('/session/'):observe(path.split('/')[2])
  result=original(path,data,method)
  if path=='/session':
   original('/session/'+result['sessionId']+'/goog/cdp/execute',{'cmd':'Network.enable','params':{'maxPostDataSize':1048576}})
  elif path.endswith('/execute/async') or path.endswith('/execute/sync'):observe(path.split('/')[2])
  return result
 suite.call=call
 result=suite.browser(state)
 assert not state.http_chat,'Chat marker sent in HTTP POST'
 assert runtime==vm.runtime(),'Installed runtime changed during browser execution'
 return result|{'scope':__doc__,'suite':kind,'installedRuntime':runtime,'networkDirectory':graph['directory'],'fixtureSPKIOnly':True,'publicSiteChanged':False,'HTTPObservation':observation,'sourceSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'suiteSourceSHA256':hashlib.sha256((ROOT/'scripts'/SUITES[kind]).read_bytes()).hexdigest()}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('suite',choices=SUITES);parser.add_argument('--release-dir',type=Path,default=RELEASE);parser.add_argument('--output',type=Path);args=parser.parse_args()
 RELEASE=args.release_dir.resolve();EXPECTED=hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest()
 result={'status':'FAIL','suite':args.suite}
 try:result.update(run(args.suite))
 finally:
  path=args.output or ROOT/'.build/checks'/('routed-native-'+args.suite+'-result.json')
  if path.exists():path.rename(path.with_name(path.stem+'-before-'+str(time.time_ns())+'.json'))
  path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
