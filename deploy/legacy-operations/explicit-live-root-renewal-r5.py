#!/usr/bin/env python3
"""One explicit 24-hour development renewal, Root4 -> Root5, on unchanged code.

Not a timer or an unattended signer. Runs the already installed protected
operator; never provisions, restores data or retries a signing operation.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import urllib.request

REMOTE = r'''
import fcntl,hashlib,importlib.util,json,os,pathlib,socket,sys,time
P=pathlib.Path;assert os.geteuid()==0 and socket.gethostname()=='box-webhost'
helper=P('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py')
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(helper)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
s=importlib.util.spec_from_file_location('renewal_preservation',helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.protected(helper)
with (m.HOST/'.controller.lock').open('rb') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);m.protected(m.CONTROL);c=json.loads(m.CONTROL.read_bytes())
 assert c['manifestSHA256']=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46' and c['basePath']=='' and c['origin']=='https://ksu.codes'
 release=P(c['release']);assert str(release)=='/srv/codi-connected/releases/native25-36868e655bc12c61'
 config_pin=sha(m.CONTROL);assert config_pin=='19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092'
 assert m.hosting_pins()=={'common.py':'9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a','sites.toml':'35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776','Caddy':'5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb'}
 m.NATIVE_DIR=release
 op=m.module('renewal_installed_operator',release/'scripts/manage-services.py')
 def pids():return {role:op.systemctl('show',op.unit(c,role),'-p','MainPID','--value').strip() for role in op.ROLES}
 with op.locked(m.CONTROL):
  op.load(m.CONTROL);op.ready(c,op.ROLES);before=m.capture(c);original_pids=pids()
  assert before['authorityBinding']['rootRevision']==4 and all(int(v)>0 for v in original_pids.values())
  fence=P('/etc/codi-connected/ksu/recovery-fence.json');assert json.loads(fence.read_bytes())['rootFloor']==4
  for role in op.ROLES:assert op.systemctl('show',op.unit(c,role),'-p','UnitFileState','--value').strip()=='disabled'
  root=P(c['stateRoot']);from steward.protocol import jose
  prior=json.loads((root/'steward/provision.json').read_bytes());old_seed=jose.inspect(prior['seed'],'codi-seed/1',32768)[1]
  assert old_seed['revision']==4 and time.time()<old_seed['exp']
  if __PLAN__:
   print(json.dumps({'status':'PLAN','readOnly':True,'rootBefore':4,'rootAfter':5,'seconds':86400,'release':str(release),'manifestSHA256':c['manifestSHA256'],'configSHA256':config_pin,'pids':original_pids,'priorExpiresAt':old_seed['exp'],'keysRealmAccountsFilesAndPrototypePreservedByPostconditions':True,'noRestartOrCodeHostingChange':True}));sys.exit(0)
  receipt=P('/srv/codi-connected')/('explicit-root5-renewal-'+str(time.time_ns())+'-result.json')
  pre={'status':'prepared','before':before,'originalPIDs':original_pids,'sourceSHA256':'__SOURCE_SHA__','priorExpiresAt':old_seed['exp']}
  op.atomic(receipt,json.dumps(pre,indent=2).encode()+b'\n')
 # The installed operator takes its own instance lock and durably reserves the
 # new independent recovery fence before advancing the root epoch.
 operation=json.loads(m.run([c['python'],'-I','-B',release/'scripts/manage-services.py','renew','--config',m.CONTROL,'--seconds','86400'],120))
 assert operation['revision']==5 and operation['status']=='renew' and operation['liveLedgerUnchangedByOperator']
 with op.locked(m.CONTROL):
  op.load(m.CONTROL);op.ready(c,op.ROLES)
  deadline=time.monotonic()+45
  while True:
   public=op.issuer_config(c).get('discovery',{})
   if public.get('seed'):
    seed=jose.inspect(public['seed'],'codi-seed/1',32768)[1]
    if seed['revision']==5:break
   if time.monotonic()>=deadline:raise RuntimeError('Root5 is committed; inspect publication, do not sign again')
   time.sleep(.25)
  from steward.provision import verified_seed
  seed=verified_seed(public['seed'],prior['root_key'],prior['realm'],int(time.time()))
  assert seed['exp']-seed['iat']==86400 and seed['exp']>old_seed['exp'] and seed['revision']==5
  after=m.capture(c)
  for k in ['keys','cookie','fileConfig','filesPIDs','website','prototypeManifest','blog','accounts','users','permissions','documents']:assert before[k]==after[k],k
  for k in ['issuerKeyId','rootKeyId','realm','serviceKeyId']:assert before['authorityBinding'][k]==after['authorityBinding'][k],k
  assert after['authorityBinding']['rootRevision']==5 and after['authorityBinding']['publisherRevision']>=before['authorityBinding']['publisherRevision']
  assert json.loads(fence.read_bytes())['rootFloor']==5 and pids()==original_pids and sha(m.CONTROL)==config_pin and m.hosting_pins()=={'common.py':'9f7fef18df198f783b71d13da1950272edc8518f8726700ab01e18ff299acd4a','sites.toml':'35bd536bf8933f70a52efbb5ff4bbafbae737568b0fac16b60aba565187fd776','Caddy':'5e76e178c0a54dd43c7a240781d57ae4fcbc9f2f66c5e288e96b5173c553b3bb'}
  value={'status':'PASS','scope':'Explicit bounded development root renewal, existing immutable operator, no automatic signer or data restore','operatorResult':operation,'before':before,'after':after,'nativePIDs':original_pids,'configSHA256':config_pin,'sourceSHA256':'__SOURCE_SHA__','publicSeedSHA256':hashlib.sha256(public['seed'].encode()).hexdigest(),'rootReceipt':str(receipt)}
  op.atomic(receipt,json.dumps(value,indent=2).encode()+b'\n')
  print(json.dumps({k:v for k,v in value.items() if k not in ['before','after']}|{'preservedKeysAccountsFilesAndCookie':True,'rootReceiptSHA256':sha(receipt)}))
'''

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--plan',action='store_true');parser.add_argument('--confirm-root5',action='store_true');args=parser.parse_args();assert not args.output.exists();assert args.plan or args.confirm_root5,'Explicit Root5 approval required before a signing operation'
    pin=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    bootstrap="import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_bytes());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])"
    child=subprocess.run(['ssh','-o','BatchMode=yes','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(bootstrap)],input=REMOTE.replace('__SOURCE_SHA__',pin).replace('__PLAN__',str(args.plan)),text=True,capture_output=True,timeout=180)
    if child.returncode:raise RuntimeError('Inspect the protected renewal receipt before any retry: '+child.stderr[-4000:])
    value=json.loads(child.stdout)
    if args.plan:
        args.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2));raise SystemExit(0)
    with urllib.request.urlopen('https://ksu.codes/config.json',timeout=30) as response:public=json.load(response)
    assert hashlib.sha256(public['discovery']['seed'].encode()).hexdigest()==value['publicSeedSHA256']
    value['defaultPublicTLS']=True;args.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
