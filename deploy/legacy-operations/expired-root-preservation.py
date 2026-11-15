#!/usr/bin/env python3
"""Capture or verify live preservation fingerprints around one root renewal."""
import argparse,hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REMOTE=r'''
import fcntl,hashlib,importlib.util,json,os,sys
from pathlib import Path
P=Path;assert os.geteuid()==0
helper=P('/srv/codi-connected/publishers/d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88/publish-hosted-peer.py');sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(helper)=='d08b9f7b4137db482577ecc0ac5df619cf62a9678e52a4dd554d575df8a0ce88'
s=importlib.util.spec_from_file_location('root_preservation_helper',helper);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.protected(helper)
config=m.CONTROL;raw=config.read_bytes();c=json.loads(raw);assert sha(config)=='19f15f856ba5e40db865d6e9b4623fa8f680e92a1952d3765484a5fb31839092' and c['manifestSHA256']=='36868e655bc12c61123ec2e7d8562bea511375aa6136d5f5dd610ca81a751d46' and c['origin']=='https://ksu.codes' and c['basePath']==''
release=P(c['release']);m.NATIVE_DIR=release;op=m.module('root_preservation_operator',release/'scripts/manage-services.py')
def tree(folder):
 items=[]
 for p in sorted(folder.rglob('*')):
  name=str(p.relative_to(folder))
  if p.is_symlink():items.append([name,'link',os.readlink(p)])
  elif p.is_dir():items.append([name,'directory'])
  elif p.is_file():items.append([name,'file',sha(p)])
  else:raise ValueError('Unsupported prototype entry')
 return hashlib.sha256(json.dumps(items,separators=(',',':')).encode()).hexdigest()
def pids():
 return {role:op.systemctl('show',op.unit(c,role),'-p','MainPID','--value').strip() for role in ['issuer','guest']}
receipt=P('/srv/codi-connected/expired-root5-preservation-before.json');result=P('/srv/codi-connected/expired-root5-preservation-after.json')
with (m.HOST/'.controller.lock').open('rb') as host_lock:
 fcntl.flock(host_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 with op.locked(config):
  assert op.load(config)==c
  from origin_service import maintenance
  maintenance.require_clean(op,config)
  for name in ['native-rollout.json','site-cutover.json','private-file-code.json']:
   assert not (config.parent/name).exists()
  assert not (config.parent/'expired-root-recovery/journal.json').exists()
  op.ready(c,['issuer','guest']);snapshot=m.capture(c);snapshot['prototypeTreeSHA256']=tree(P(snapshot['website'])/'public/desktop');snapshot['hostingPins']=m.hosting_pins();snapshot['nativePIDs']=pids();snapshot['configSHA256']=sha(config)
  fence=json.loads(op.read_owned(config.parent/'recovery-fence.json',0,0o600));expected=4 if __BEFORE__ else 5;assert snapshot['authorityBinding']['rootRevision']==expected and fence['rootFloor']==expected
  if __BEFORE__:
   assert not receipt.exists() and not receipt.is_symlink();assert op.systemctl('show',op.unit(c,'steward'),'-p','ActiveState','--value').strip()=='failed';op.atomic(receipt,(json.dumps(snapshot,sort_keys=True)+'\n').encode());print(json.dumps({'status':'PASS','phase':'before','rootRevision':expected,'publisherRevision':snapshot['authorityBinding']['publisherRevision'],'receipt':str(receipt),'receiptSHA256':sha(receipt),'prototypeTreeSHA256':snapshot['prototypeTreeSHA256'],'signingPerformed':False}))
  else:
   before=json.loads(op.read_owned(receipt,0,0o600,134217728));assert not result.exists() and not result.is_symlink()
   for key in ['keys','cookie','fileConfig','filesPIDs','website','prototypeManifest','blog','prototypeTreeSHA256','hostingPins','nativePIDs','configSHA256']:assert before[key]==snapshot[key],key
   for key in ['accounts','users','permissions']:assert set(before[key])<=set(snapshot[key]),key
   for name,pin in before['documents'].items():assert snapshot['documents'].get(name)==pin,name
   for key in ['issuerKeyId','rootKeyId','realm','serviceKeyId']:assert before['authorityBinding'][key]==snapshot['authorityBinding'][key],key
   assert snapshot['authorityBinding']['publisherRevision']>=before['authorityBinding']['publisherRevision'];op.ready(c,['steward']);public=op.issuer_config(c)['discovery'];seed_hash=hashlib.sha256(public['seed'].encode()).hexdigest()
   value={'status':'PASS','phase':'after','rootRevision':expected,'publisherRevision':snapshot['authorityBinding']['publisherRevision'],'baselineReceiptSHA256':sha(receipt),'prototypeTreeSHA256':snapshot['prototypeTreeSHA256'],'publicSeedSHA256':seed_hash,'existingKeysAccountsFilesAndHostingPreserved':True};op.atomic(result,(json.dumps(value,sort_keys=True)+'\n').encode());print(json.dumps(value))
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['before','after']);a=p.parse_args();bootstrap="import json,os,pathlib,sys;c=json.loads(pathlib.Path('/etc/codi-connected/ksu/managed.json').read_bytes());code=sys.stdin.read();os.execv(c['python'],[c['python'],'-I','-B','-c',code])";code=REMOTE.replace('__BEFORE__',str(a.phase=='before'))
 child=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=5','box-webhost','sudo','-n','/usr/bin/python3','-I','-B','-c',shlex.quote(bootstrap)],input=code,text=True,capture_output=True,timeout=120)
 if child.returncode:raise RuntimeError('Preservation check failed; inspect state before any action: '+child.stderr[-5000:])
 value=json.loads(child.stdout);value['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/('.build/checks/expired-root-preservation-'+a.phase+'-r1-result.json');assert not out.exists();out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
if __name__=='__main__':main()
