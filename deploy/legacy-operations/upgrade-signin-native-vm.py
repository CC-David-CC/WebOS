#!/usr/bin/env python3
"""Stage and code-upgrade native15 through25 in the retained isolated security VM."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).resolve().parent.parent;STAGE='/srv/codi-network-fixture'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('candidate_vm',ROOT/'scripts/prepare-native-network-vm.py');vm=importlib.util.module_from_spec(spec);spec.loader.exec_module(vm)
def remote(command,input=None):
    result=subprocess.run([*vm.ssh_args(),command],input=input,check=True,capture_output=True,text=True,timeout=180);return result.stdout
def runtime():
    code="""import hashlib,json,subprocess
from pathlib import Path
c=json.loads(Path('/etc/codi-native-fixture/managed.json').read_text());p=Path(c['release']);raw=(p/'connected-release.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==c['manifestSHA256'];pids={}
for role in ['issuer','steward','guest']:
 pid=int(subprocess.check_output(['systemctl','show',c['instance']+'-'+role+'.service','-p','MainPID','--value'],text=True));assert pid>0 and str(p).encode() in Path('/proc/'+str(pid)+'/cmdline').read_bytes();pids[role]=pid
print(json.dumps({'manifestSHA256':c['manifestSHA256'],'release':str(p),'version':c['version'],'nativePIDs':pids,'clientSHA256':hashlib.sha256((p/'guest_service/client.mjs').read_bytes()).hexdigest(),'appSHA256':hashlib.sha256((p/'app.js').read_bytes()).hexdigest()}))
"""
    return json.loads(remote('/usr/bin/python3 -I -B -c '+shlex.quote(code)))
def upgrade(source,resume_staged=False,use_current_operator=False):
    vm.status();source=Path(source).resolve();raw=(source/'connected-release.json').read_bytes();key=hashlib.sha256(raw).hexdigest();metadata=json.loads(raw)
    assert metadata['version'] in ('codi-connected-development/15','codi-connected-development/16','codi-connected-development/17','codi-connected-development/18','codi-connected-development/19','codi-connected-development/20','codi-connected-development/21','codi-connected-development/22','codi-connected-development/23','codi-connected-development/24','codi-connected-development/25')
    spec=importlib.util.spec_from_file_location('candidate_contract',source/'origin_service/release.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract);verified=contract.verify(source);assert verified['manifestSHA256']==key and verified['files']==len(metadata['files'])
    for name,record in metadata['files'].items():
        p=source/name;assert not Path(name).is_absolute() and '..' not in Path(name).parts and not p.is_symlink() and p.is_file();assert record=={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    destination=STAGE+'/candidate-'+key[:16]
    if not resume_staged:remote('test ! -e '+destination)
    before=json.loads(remote(STAGE+'/venv/bin/python -I -B '+STAGE+'/tools/native-network-vm-lifecycle-check.py --snapshot'))
    assert before['configVersion']=='codi-managed-instance/5' and before['worker']['active'] and not before['nativeJournalPresent']
    (ROOT/'.build/checks/signin-native-upgrade-before-snapshot.json').write_text(json.dumps(before,indent=2)+'\n')
    if not resume_staged:
        archive=vm.FOLDER/('candidate-'+key+'.tar.gz')
        with tarfile.open(archive,'w:gz',compresslevel=1) as output:output.add(source,arcname='candidate-'+key[:16])
        with archive.open('rb') as stream:subprocess.run([*vm.ssh_args(),'tar -xzf - -C '+STAGE],stdin=stream,check=True,timeout=180)
        remote('chown -R root:root '+destination+' && chmod -R go-w '+destination)
    code="""import hashlib,json,stat
from pathlib import Path
p=Path(DEST);raw=(p/'connected-release.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==DIGEST
m=json.loads(raw)
for f in [p,*p.rglob('*')]:
 s=f.lstat();assert not f.is_symlink() and s.st_uid==0 and not s.st_mode&0o022
 if f.is_file():
  assert s.st_nlink==1;n=str(f.relative_to(p))
  if n!='connected-release.json':assert m['files'][n]=={'bytes':s.st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
assert {str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}==set(m['files'])|{'connected-release.json'}
""".replace('DEST',repr(destination)).replace('DIGEST',repr(key))
    remote('/usr/bin/python3 -I -B -c '+shlex.quote(code))
    # An older target operator cannot validate a future currently-installed
    # profile. Explicit inverse tests use the newer pinned current operator;
    # its policy still validates BOTH releases and performs the same journaled
    # transition. Never weaken an old release's verifier to recognize new code.
    operator=runtime()['release'] if use_current_operator else destination
    assert operator.startswith(STAGE+'/candidate-') and re.fullmatch('[a-f0-9]{16}',operator.rsplit('-',1)[1])
    changed=json.loads(remote(STAGE+'/venv/bin/python -I -B '+operator+'/scripts/manage-services.py upgrade --config /etc/codi-native-fixture/managed.json --release '+destination+' --python '+STAGE+'/venv/bin/python'))
    assert changed['status']=='upgraded',changed
    after=json.loads(remote(STAGE+'/venv/bin/python -I -B '+STAGE+'/tools/native-network-vm-lifecycle-check.py --snapshot'));current=runtime()
    assert current['manifestSHA256']==key and current['release']==destination and current['version']=='codi-managed-instance/5'
    (ROOT/'.build/checks/signin-native-upgrade-after-snapshot.json').write_text(json.dumps(after,indent=2)+'\n')
    assert before['keysAndAccountDBSHA256']==after['keysAndAccountDBSHA256'] and before['privateFixtureFileSHA256']==after['privateFixtureFileSHA256']
    for role in ['issuer','steward','guest']:assert before['pids'][role]!=after['pids'][role]
    for role in ['files','filesProxy']:assert before['pids'][role]==after['pids'][role]
    for role,rows in before['usage'].items():
        counts={(row[0],row[1]):row[2:] for row in after['usage'][role]}
        for row in rows:assert (row[0],row[1]) in counts and all(a>=b for a,b in zip(counts[(row[0],row[1])],row[2:]))
    assert after['worker']['active'] and after['worker']['kernelMatches'] and not after['worker']['guardFault'] and not after['nativeJournalPresent']
    return {'status':'PASS','nativeManifestSHA256':key,'destination':destination,'operatorRelease':operator,'runtime':current,'keysAccountsCookieFilesAndCountersPreserved':True,'privateFileServicesNotRestarted':True,'actualManagedCodeUpgrade':True,'hostFirewallChanged':False,'liveWebhostChanged':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--release-dir',type=Path);parser.add_argument('--status',action='store_true');parser.add_argument('--resume-staged',action='store_true',help='Reuse only an exact root-owned candidate staged by a prior failed upgrade');parser.add_argument('--use-current-operator',action='store_true',help='Use the newer pinned current operator when targeting an older staged release');args=parser.parse_args()
    if args.status:print(json.dumps(runtime(),indent=2))
    else:
        value={'status':'FAIL','scope':__doc__}
        try:value.update(upgrade(args.release_dir,args.resume_staged,args.use_current_operator))
        finally:
            value['sha256']={'scripts/upgrade-signin-native-vm.py':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};out=ROOT/'.build/checks/signin-native-vm-upgrade-result.json'
            if out.exists():out.rename(out.with_name('signin-native-vm-upgrade-before-'+str(time.time_ns())+'.json'))
            out.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value,indent=2))
