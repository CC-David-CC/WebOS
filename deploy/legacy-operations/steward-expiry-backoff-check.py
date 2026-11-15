#!/usr/bin/env python3
"""Kill a verified disposable worker just before its signed delegation expires."""
import argparse,base64,hashlib,json,os,re,signal,stat,time,urllib.request
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--instance',required=True);p.add_argument('--issuer-port',type=int,default=8118);a=p.parse_args()
if not 1<=a.issuer_port<=65535:p.error('Valid loopback issuer port required')
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',a.instance):p.error('Instance label required')
runtime=ROOT/'.build/connected-instances'/a.instance/'state/steward-process.json'
result={'status':'FAIL','scope':'Actual local native process expiry during supervisor backoff; no browser/WAN claim'}
try:
 info=runtime.lstat();assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600
 worker=json.loads(runtime.read_text());assert worker['status']=='running' and worker['restarts']==0
 provision=json.loads((Path(worker['privateRun'])/'provision.json').read_text());seed=json.loads(base64.urlsafe_b64decode(provision['seed'].split('.')[1]+'==='));expiry=seed['exp']
 assert 0<expiry-.4-time.time()<45,'Start against a fresh short-lived fixture'
 until=time.monotonic()+45
 while time.time()<expiry-.4:
  assert time.monotonic()<until,'Clock moved beyond the test budget';time.sleep(.01)
 actual=[part.decode() for part in Path('/proc/'+str(worker['pid'])+'/cmdline').read_bytes().removesuffix(b'\0').split(b'\0')]
 assert actual==worker['command'] and str(ROOT/'scripts/serve-steward.py') in actual
 killed_at=time.time();os.kill(worker['pid'],signal.SIGKILL)
 until=time.monotonic()+10
 while time.monotonic()<until:
  final=json.loads(runtime.read_text())
  if final['status']=='delegation-expired':break
  time.sleep(.02)
 assert final['status']=='delegation-expired',final
 origin=urlsplit(provision['origins'][0]);probe=urllib.request.Request('http://127.0.0.1:'+str(a.issuer_port)+'/config.json',headers={'Host':origin.netloc})
 with urllib.request.urlopen(probe,timeout=5) as response:assert json.load(response)['identity']['mode']=='server'
 result.update({'expiry':expiry,'killedAt':killed_at,'checkedAt':time.time(),'issuerStillServer':True,'workerNotRelaunched':final['pid']==worker['pid'],'finalStatus':final['status'],'restartBudgetCharged':final['restarts']})
 assert final['pid']==worker['pid'],'Supervisor launched another worker after expiry during backoff'
 result['status']='PASS'
except Exception as error:result['error']=str(error);raise
finally:
 result['sha256']={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('scripts/serve-connected-discovery.py','scripts/steward-expiry-backoff-check.py')}
 (ROOT/'.build/checks/steward-expiry-backoff-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
