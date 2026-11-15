#!/usr/bin/env python3
"""Git-first authenticated storage foundation installation, without a service."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REMOTE = r'''
import hashlib,json,os,pathlib,shutil,stat,subprocess,sys,tempfile,time
Path=pathlib.Path;inputs=json.load(sys.stdin)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def run(args,**kwargs):return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True,timeout=90,**kwargs).stdout.strip()
assert os.geteuid()==0 and inputs['action'] in ['plan','apply']
checkout=Path('/home/dflanag3/webhost-sites/sites/ksu.codes')
assert run(['runuser','-u','dflanag3','--','git','-C',checkout,'rev-parse','HEAD'])==inputs['commit']
assert not run(['runuser','-u','dflanag3','--','git','-C',checkout,'status','--porcelain'])
source=checkout/'tools/codiserver/storage-candidates'/inputs['manifestSHA256']
raw=(source/'storage.json').read_bytes();assert digest(raw)==inputs['manifestSHA256']
metadata=json.loads(raw);assert metadata['version']=='codi-private-storage/1'
names={'gateway_service/__init__.py','gateway_service/policy.py','gateway_service/user_store.py','scripts/storage-admin.py','scripts/install-user-storage.py','scripts/install-service-accounts.py','scripts/user-storage-check.py'}
assert set(metadata['files'])==names
def verified(folder):
 assert {str(p.relative_to(folder)) for p in folder.rglob('*') if not p.is_dir()}==names|{'storage.json'}
 assert (folder/'storage.json').read_bytes()==raw
 values={}
 for name,record in metadata['files'].items():
  file=folder/name
  for p in [file,*file.parents]:assert not p.is_symlink()
  with os.fdopen(os.open(file,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as stream:
   info=os.fstat(stream.fileno());assert stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==record['bytes'] and info.st_size<262144
   value=stream.read(info.st_size+1);assert len(value)==info.st_size and digest(value)==record['sha256'];values[name]=value
 return values
values=verified(source)
def protected(path):
 for p in [path,*path.parents]:
  info=p.lstat();assert stat.S_ISDIR(info.st_mode) and info.st_uid==0 and not info.st_mode&0o022
def snapshots():
 files=[Path('/etc/caddy/Caddyfile'),checkout.parent.parent/'ops/common.py',checkout.parent.parent/'sites.toml',Path('/etc/codi-connected/ksu/managed.json')]
 website=Path('/srv/webapps/ksu.codes/current').resolve()
 files += [website/'public/desktop'/name for name in ['release.json','app.js','config.json']]
 return {str(p):digest(p.read_bytes()) for p in files}
before=snapshots()
destination=Path('/srv/codi-gateway/releases')/inputs['manifestSHA256']
if destination.exists():
 protected(destination);verified(destination)
else:
 if inputs['action']=='plan':
  print(json.dumps({'status':'PASS','action':'plan','sourceCommit':inputs['commit'],'manifestSHA256':inputs['manifestSHA256'],'scope':'Verified private source bundle only; no accounts, directories, services or routes changed'}));raise SystemExit(0)
 for parent in [destination.parent.parent,destination.parent]:
  if not parent.exists():parent.mkdir(mode=0o755)
  protected(parent)
 stage=Path(tempfile.mkdtemp(prefix='.storage-',dir=destination.parent))
 try:
  for name,value in {**values,'storage.json':raw}.items():
   file=stage/name;file.parent.mkdir(parents=True,exist_ok=True)
   file.write_bytes(value);file.chmod(0o644)
   with file.open('rb') as stream:os.fsync(stream.fileno())
  for p in [stage,*(p for p in stage.rglob('*') if p.is_dir())]:p.chmod(0o755)
  verified(stage);os.rename(stage,destination)
  fd=os.open(destination.parent,os.O_RDONLY|os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if stage.exists():shutil.rmtree(stage)
protected(destination);verified(destination)
for p in destination.rglob('*'):
 info=p.lstat();assert info.st_uid==0 and not info.st_mode&0o022
result=json.loads(run(['/usr/bin/python3','-I','-B',destination/'scripts/install-user-storage.py',*(['--apply'] if inputs['action']=='apply' else [])]))
assert snapshots()==before
result.update(sourceCommit=inputs['commit'],manifestSHA256=inputs['manifestSHA256'],installedRelease=str(destination),hostingNativeConfigAndPrototypeUnchanged=True)
if inputs['action']=='apply':
 receipt=destination.parent.parent/('storage-prepare-'+str(time.time_ns())+'-result.json')
 fd=os.open(receipt,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(result,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 result['rootReceipt']=str(receipt);result['rootReceiptSHA256']=digest(receipt.read_bytes())
print(json.dumps(result))
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--action', choices=['plan', 'apply'], default='plan')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.commit) or not re.fullmatch('[0-9a-f]{64}', args.manifest_sha256):
        parser.error('Exact reviewed commit and storage manifest digest required')
    inputs = {'commit': args.commit, 'manifestSHA256': args.manifest_sha256, 'action': args.action}
    child = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', 'box-webhost', 'sudo', '-n', '/usr/bin/python3', '-I', '-B', '-c', shlex.quote(REMOTE)], input=json.dumps(inputs), text=True, capture_output=True, timeout=180)
    if child.returncode:
        raise SystemExit(child.stderr or child.stdout)
    report = json.loads(child.stdout)
    report['activationSourceSHA256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output = ROOT/'.build/checks'/('user-storage-webhost-'+args.action+'-result.json')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
