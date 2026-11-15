#!/usr/bin/env python3
"""Actual forward-only migration/crash recovery in the retained private VM.

Does not access box-webhost. Existing fixture accounts/private files/keys/cookie,
permissions and usage are preserved. Every intermediate frontend remains stopped
once old managed guest networking has been disabled. No host netns changes.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).resolve().parent.parent
STAGE=Path('/srv/codi-network-fixture');CONTROL=Path('/etc/codi-native-fixture/managed.json')
NEW_FOLDER=Path('/etc/codi-guest-network/fixture-signin')
WORKER='9f9106e682e51bd5284273fd093994353db6274f887834a12af97828a6907096'
OPERATOR='5c51d2c86c214519c21237c41252d41b20a2536d6cdd46f96af37719e9a076fc'
NATIVE='db96ccb21bbaac684b2dc60cac520e0158dc8165cfb8b76fe429fa96d637542e'
OP_PATH=STAGE/('signin-operator-'+OPERATOR[:16]);WORKER_PATH=STAGE/('signin-worker-'+WORKER[:16])

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def remote_phase(point):
    if os.geteuid()!=0 or not Path('/var/lib/codi-fixture-ready').exists():raise ValueError('Retained VM fixture only')
    c=json.loads(CONTROL.read_text());assert c['manifestSHA256']==NATIVE
    op=module('signin_vm_native_operator',Path(c['release'])/'scripts/manage-services.py')
    from origin_service import signin_migration
    def phase(name):
        if name==point:os._exit(87)
    with op.locked(CONTROL):
        if point=='prepared':result=signin_migration.begin(op,c,CONTROL,operator=OP_PATH,worker=WORKER_PATH,folder=NEW_FOLDER,phase=phase)
        else:result=signin_migration.advance(op,CONTROL,phase=phase)
    print(json.dumps(result))

def snapshot():
    import sqlite3
    c=json.loads(CONTROL.read_text());state=Path(c['stateRoot']);old=Path('/etc/codi-guest-network/fixture/managed.json');backend=json.loads(Path(c.get('guestNetwork',{}).get('configFile',old)).read_text())
    def digest(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()
    keyfiles=[state/'issuer/state/accounts.sqlite3',state/'issuer/state/issuer.pem',state/'steward/service.pem',state/'operator/root/root.pem',state.parent/('guest-cookie-'+c['instance'])/'secret']
    pids={}
    for role in ['issuer','steward','guest']:
        pids[role]=int(subprocess.check_output(['systemctl','show',c['instance']+'-'+role+'.service','-p','MainPID','--value'],text=True))
    for key,unit in [('files','codi-files-network-fixture.service'),('filesProxy','codi-files-network-fixture-proxy.service')]:pids[key]=int(subprocess.check_output(['systemctl','show',unit,'-p','MainPID','--value'],text=True))
    usage={}
    for role in ['anonymous','registered']:
        with sqlite3.connect(Path(backend['stateRoot'])/role/'usage.sqlite3') as db:usage[role]=db.execute('SELECT subject,window,bytes,packets FROM usage ORDER BY subject,window').fetchall()
    permission=Path(backend['operatorRelease']) # Only policy DB digests, never rows, leave this VM.
    permission=Path(c.get('guestNetwork',{}).get('configFile',old)).parent/'policy/permissions.sqlite3'
    with sqlite3.connect(permission.as_uri()+'?mode=ro',uri=True) as db:permission_digest=hashlib.sha256('\n'.join(db.iterdump()).encode()).hexdigest()
    journal=CONTROL.parent/'guest-signin-migration.json'
    return {'configVersion':c['version'],'manifestSHA256':c['manifestSHA256'],'guestPolicyVersion':backend['policy']['version'],'guestPolicySHA256':backend['policySHA256'],'pids':pids,
            'keysAccountDBCookieSHA256':{str(p):digest(p) for p in keyfiles},'fixturePrivateFilesSHA256':{str(p):digest(p) for p in Path('/srv/codi-files-fixture/users').rglob('*') if p.is_file()},
            'permissionsLogicalSHA256':permission_digest,'usage':usage,'migrationPhase':json.loads(journal.read_text())['phase'] if journal.exists() else None,'innerJournalPresent':(CONTROL.parent/'maintenance.json').exists(),
            'nativeUnitBootStates':{role:subprocess.check_output(['systemctl','is-enabled',c['instance']+'-'+role+'.service'],text=True).strip() for role in []}}

def host():
    vm=module('signin_migration_vm',ROOT/'scripts/prepare-native-network-vm.py');vm.status();checks=[]
    def remote(command,*,input=None,check=True):
        return subprocess.run([*vm.ssh_args(),command],input=input,check=check,text=True,capture_output=True,timeout=180)
    def check(label,value):
        assert value,label;checks.append(label);print(json.dumps({'phase':label}),flush=True)
    for source,destination,manifest,pin in [(ROOT/'.build/signin-native-source/.build/guest-workers/signin-r3',WORKER_PATH,'guest-wire.json',WORKER),(ROOT/'.build/signin-native-source/.build/guest-operators/signin-r2',OP_PATH,'guest-operator.json',OPERATOR)]:
        assert hashlib.sha256((source/manifest).read_bytes()).hexdigest()==pin
        existing=remote('test -e '+str(destination),check=False).returncode==0
        if not existing:
            archive=vm.FOLDER/('signin-package-'+pin+'.tar.gz')
            with tarfile.open(archive,'w:gz') as output:output.add(source,arcname=destination.name)
            with archive.open('rb') as data:subprocess.run([*vm.ssh_args(),'tar -xzf - -C '+str(STAGE)],stdin=data,check=True,timeout=45)
            remote('chown -R root:root '+str(destination)+' && chmod -R go-w '+str(destination))
        code='''import hashlib,json,stat
from pathlib import Path
p=Path(DEST);raw=(p/MANIFEST).read_bytes();assert hashlib.sha256(raw).hexdigest()==PIN;m=json.loads(raw)
assert {str(f.relative_to(p)) for f in p.rglob('*') if f.is_file()}==set(m['files'])|{MANIFEST}
for f in [p,*p.rglob('*')]:
 s=f.lstat();assert not f.is_symlink() and s.st_uid==0 and not s.st_mode&0o022
 if f.is_file() and f.name!=MANIFEST:assert m['files'][str(f.relative_to(p))]=={'bytes':s.st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
'''.replace('DEST',repr(str(destination))).replace('MANIFEST',repr(manifest)).replace('PIN',repr(pin))
        remote('/usr/bin/python3 -I -B -c '+shlex.quote(code))
    remote_file=STAGE/'tools/signin-native-vm-migration-check.py';remote('cat > '+str(remote_file),input=Path(__file__).read_text());remote('chmod 0644 '+str(remote_file))
    c=json.loads(remote('cat '+str(CONTROL)).stdout);python=c['python'];tool=Path(c['release'])/'scripts/manage-services.py'
    def snap():return json.loads(remote(shlex.join([python,'-I','-B',str(remote_file),'--snapshot'])).stdout)
    before=snap();assert before['manifestSHA256']==NATIVE and all(before['pids'].values()) and before['guestPolicyVersion']=='codi-guest-egress-policy/1' and before['migrationPhase'] is None
    (ROOT/'.build/checks/signin-migration-before-snapshot.json').write_text(json.dumps(before,indent=2)+'\n')
    check('exact sealed worker2/operator2/native15 staged on same retained VM',True)
    observed=[]
    for phase in ['prepared','disabled','unit-removed:codi-net-network-fixture-guard.service','units-removed','configured','bound','completed']:
        result=remote(shlex.join([python,'-I','-B',str(remote_file),'--phase',phase]),check=False)
        check('actual process interruption at '+phase,result.returncode==87)
        state=snap();observed.append({'interruptedAt':phase,'snapshot':state})
        if phase not in ('prepared','completed'):check('issuer/guest stay stopped at '+phase,state['pids']['issuer']==state['pids']['guest']==0)
        rejected=remote(shlex.join([python,'-I','-B',str(tool),'start','--config',str(CONTROL),'--roles','guest']),check=False)
        check('native Start refuses incomplete migration at '+phase,rejected.returncode!=0 and 'migration pending' in rejected.stderr)
        check('steward and file services retain PIDs at '+phase,all(state['pids'][role]==before['pids'][role] for role in ['steward','files','filesProxy']))
    result=json.loads(remote(shlex.join([python,'-I','-B',str(tool),'recover-guest-signin','--config',str(CONTROL)])).stdout)
    after=snap()
    check('explicit recovery commits strict target and clears both journals',result['status']=='guest-signin-migrated' and after['migrationPhase'] is None and not after['innerJournalPresent'] and after['guestPolicyVersion']=='codi-guest-egress-policy/2')
    check('keys accounts cookie private files and permission rows preserved',before['keysAccountDBCookieSHA256']==after['keysAccountDBCookieSHA256'] and before['fixturePrivateFilesSHA256']==after['fixturePrivateFilesSHA256'] and before['permissionsLogicalSHA256']==after['permissionsLogicalSHA256'])
    for role,rows in before['usage'].items():
        indexed={(row[0],row[1]):row[2:] for row in after['usage'][role]}
        for row in rows:assert (row[0],row[1]) in indexed and all(a>=b for a,b in zip(indexed[(row[0],row[1])],row[2:]))
    check('existing usage counters retained without reset',True)
    check('three native roles online after strict target commits',all(after['pids'].values()))
    return {'status':'PASS','scope':__doc__,'checks':checks,'before':before,'after':after,'interruptedSnapshots':observed,'result':result,'liveWebhostChanged':False,'hostFirewallChanged':False,'browserGuestChainTested':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase');p.add_argument('--snapshot',action='store_true');args=p.parse_args()
    if args.phase:remote_phase(args.phase)
    elif args.snapshot:print(json.dumps(snapshot()))
    else:
        result={'status':'FAIL'}
        try:result=host()
        finally:
            result['sourceSHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();out=ROOT/'.build/checks/signin-native-vm-migration-result.json'
            if out.exists():out.rename(out.with_name('signin-native-vm-migration-before-'+str(time.time_ns())+'.json'))
            out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
