#!/usr/bin/env python3
"""Run the seven-app repeat-close/stale-work suite on the exact public R8 release."""
import hashlib,importlib.util,json,shlex,subprocess,time,urllib.request
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent.parent
RELEASE=ROOT/'.build/releases/connected-routed-r8'
EXPECTED='6fbca9e61a02008c32b917e2db5cb8805271b2f6300d97338ea976532cd97200'
def runtime():
 code='''import hashlib,json,subprocess
from pathlib import Path
p=Path('/etc/codi-connected/ksu/managed.json');c=json.loads(p.read_text());assert c['manifestSHA256']==EXPECTED
assert hashlib.sha256((Path(c['release'])/'connected-release.json').read_bytes()).hexdigest()==EXPECTED
units=['codi-ksu-hidden-'+r+'.service' for r in ['issuer','steward','guest']]+['codi-files-ksu-hidden.service','codi-files-ksu-hidden-proxy.service']
print(json.dumps({'manifestSHA256':c['manifestSHA256'],'configSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'PIDs':{n:int(subprocess.check_output(['systemctl','show',n,'-p','MainPID','--value'],text=True)) for n in units}}))
'''.replace('EXPECTED',repr(EXPECTED))
 return json.loads(subprocess.check_output(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','python3','-I','-B','-c',shlex.quote(code)],text=True,timeout=20))
def run():
 assert hashlib.sha256((RELEASE/'connected-release.json').read_bytes()).hexdigest()==EXPECTED
 for name in ['index.html','assets/desktop/network-release.json']:
  with urllib.request.urlopen('https://ksu.codes/hidden/'+name,timeout=20) as r:assert r.read()==(RELEASE/name).read_bytes()
 before=runtime();assert all(before['PIDs'].values())
 spec=importlib.util.spec_from_file_location('public_r8_app_stress',ROOT/'scripts/public-app-lifecycle-stress-check.py');suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
 original=suite.call
 def call(path,data=None,method=None):
  if path=='/session':
   options=data['capabilities']['alwaysMatch']['goog:chromeOptions'];assert not any('ignore-certificate' in a for a in options['args'])
   options['args'].append('--no-proxy-server')
  return original(path,data,method)
 suite.call=call
 result=suite.browser(SimpleNamespace(origin='https://ksu.codes',base='/hidden'))
 assert runtime()==before
 assert len(result['checks'])==13 and result['ordinaryOpensAndCloses']==182 and result['cyclesPerApp']==26
 assert all(s['resources']==result['samples'][0]['resources'] and s['budget']==result['samples'][0]['budget'] for s in result['samples'])
 return result|{'scope':__doc__,'publicURL':'https://ksu.codes/hidden/','defaultPublicTLS':True,'certificateExceptionUsed':False,'nativeManifestSHA256':EXPECTED,'beforeAndAfterRuntime':before,'suiteSourceSHA256':hashlib.sha256((ROOT/'scripts/public-app-lifecycle-stress-check.py').read_bytes()).hexdigest(),'probeSHA256':hashlib.sha256((ROOT/'scripts/fixtures/app-lifecycle-probe.js').read_bytes()).hexdigest()}
if __name__=='__main__':
 result={'status':'FAIL'}
 try:result.update(run())
 finally:
  result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/routed-public-lifecycle-result.json'
  if out.exists():out.rename(out.with_name(out.stem+'-before-'+str(time.time_ns())+'.json'))
  out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
