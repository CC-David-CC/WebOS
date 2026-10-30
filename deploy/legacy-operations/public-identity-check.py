#!/usr/bin/env python3
"""Public Chrome identity check with exact disposable-account cleanup on webhost."""
import hashlib,json,secrets,shlex,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
REMOTE=r'''
import json,pathlib,re,subprocess,sys
name=sys.argv[1];assert re.fullmatch('publiccheck_[0-9a-f]{12}',name)
config=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_text());root=pathlib.Path(config['release'])
assert config['origin']=='https://ksu.codes' and config['basePath']=='/hidden'
code="""import json,sys
sys.path.insert(0,sys.argv[1]);from origin_service.lifecycle import set_disabled
try:
 result=set_disabled(sys.argv[2],sys.argv[3],True);assert result['disabled'];print(json.dumps({'disabled':True,'subject':result['subject']}))
except ValueError as error:
 if str(error)!='Unknown account; no account created':raise
 print(json.dumps({'disabled':False,'accountNotCreated':True}))
"""
result=subprocess.run(['/usr/sbin/runuser','-u','codi-issuer','--',config['python'],'-B','-c',code,str(root),'/var/lib/codi-connected/ksu/issuer/state',name],cwd=root,check=True,capture_output=True,text=True);print(result.stdout)
'''
if __name__=='__main__':
 name='publiccheck_'+secrets.token_hex(6);report={'status':'FAIL','scope':'Default-trusted public HTTPS origin in real Chrome on development network; no independent WAN/NAT or production identity claim','url':'https://ksu.codes/hidden/'}
 try:
  process=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/identity-check.py'),'--url',report['url'],'--public-tls','--probe-account-name',name],cwd=ROOT,capture_output=True,text=True,timeout=300)
  if process.returncode:raise ValueError((process.stderr or process.stdout)[-3000:])
  identity=json.loads((ROOT/'.build/checks/identity-result.json').read_text());assert identity['probeAccount']==name and identity['defaultCertificateTrust'];report['identity']=identity;report['status']='PASS'
 except BaseException as error:report['error']=str(error)
 finally:
  cleanup=subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','box-webhost','sudo','-n','/usr/bin/python3','-B','-c',shlex.quote(REMOTE),name],capture_output=True,text=True,timeout=45)
  if cleanup.returncode:report['status']='FAIL';report['cleanupError']=cleanup.stderr[-2000:]
  else:
   report['cleanup']=json.loads(cleanup.stdout)
   if report['status']=='PASS' and not report['cleanup']['disabled']:report['status']='FAIL';report['cleanupError']='Created probe account was not disabled'
  report['driverSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();(ROOT/'.build/checks/preview-public-identity-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 raise SystemExit(0 if report['status']=='PASS' else 1)
